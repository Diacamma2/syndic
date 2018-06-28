# -*- coding: utf-8 -*-
'''
diacamma.condominium models package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from datetime import date
from logging import getLogger

from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum, Max
from django.db.utils import IntegrityError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils import six, formats
from django.core.exceptions import ObjectDoesNotExist
from django_fsm import FSMIntegerField, transition

from lucterios.framework.models import LucteriosModel, get_value_converted, get_subfield_show
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.tools import convert_date
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params

from diacamma.accounting.models import CostAccounting, EntryAccount, ChartsAccount, EntryLineAccount, FiscalYear, Budget, AccountThird, Third
from diacamma.accounting.tools import format_devise, currency_round, current_system_account, get_amount_sum, correct_accounting_code
from diacamma.payoff.models import Supporting, Payoff
from django.conf import settings
from lucterios.contacts.models import AbstractContact
from diacamma.condominium.system import current_system_condo


class Set(LucteriosModel):
    name = models.CharField(_('name'), max_length=100)
    budget = models.DecimalField(_('budget'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    revenue_account = models.CharField(_('revenue account'), max_length=50)
    cost_accounting = models.ForeignKey(
        CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    is_link_to_lots = models.BooleanField(_('is link to lots'), default=False)
    type_load = models.IntegerField(verbose_name=_('type of load'),
                                    choices=((0, _('current')), (1, _('exceptional'))), null=False, default=0, db_index=True)
    is_active = models.BooleanField(_('is active'), default=True)
    set_of_lots = models.ManyToManyField('PropertyLot', verbose_name=_('set of lots'), blank=True)

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.date_begin = None
        self.date_end = None

    def set_dates(self, begin_date=None, end_date=None):
        if begin_date is None:
            self.date_begin = six.text_type(FiscalYear.get_current().begin)
        else:
            self.date_begin = begin_date
        if end_date is None:
            self.date_end = six.text_type(FiscalYear.get_current().end)
        else:
            self.date_end = end_date
        if isinstance(self.date_begin, six.text_type):
            self.date_begin = convert_date(self.date_begin)
        if isinstance(self.date_end, six.text_type):
            self.date_end = convert_date(self.date_end)
        if self.date_end < self.date_begin:
            self.date_end = self.date_begin

    def set_context(self, xfer):
        if xfer is not None:
            self.set_dates(xfer.getparam("begin_date"), xfer.getparam("end_date"))

    def __str__(self):
        return self.identify

    @property
    def partitionfill_set(self):
        return self.partition_set.filter(Q(value__gt=0.001))

    @property
    def identify(self):
        return "[%d] %s" % (self.id, self.name)

    @classmethod
    def get_default_fields(cls):
        return [(_('name'), "identify"), 'type_load', (_('divisions'), 'partitionfill_set'), (_('budget'), "budget_txt"), (_('expense'), 'sumexpense_txt')]

    @classmethod
    def get_edit_fields(cls):
        fields = ["name", "type_load", 'is_link_to_lots']
        if Params.getvalue("condominium-old-accounting"):
            fields.append("revenue_account")
        return fields

    @classmethod
    def get_show_fields(cls):
        if Params.getvalue("condominium-old-accounting"):
            return [("name", ), ("revenue_account", (_('cost accounting'), 'current_cost_accounting')), ("type_load", 'is_active'), ('is_link_to_lots',
                                                                                                                                     (_('tantime sum'), 'total_part')), 'partition_set', 'partitionfill_set', ((_('budget'), "budget_txt"), (_('expense'), 'sumexpense_txt'),)]
        else:
            return [("name", (_('cost accounting'), 'current_cost_accounting')), ("type_load", 'is_active'), ('is_link_to_lots', (_('tantime sum'), 'total_part')),
                    'partition_set', 'partitionfill_set', ((_('budget'), "budget_txt"), (_('expense'), 'sumexpense_txt'),)]

    def _do_insert(self, manager, using, fields, update_pk, raw):
        new_id = LucteriosModel._do_insert(
            self, manager, using, fields, update_pk, raw)
        for owner in Owner.objects.all():
            Partition.objects.create(set_id=new_id, owner=owner)
        return new_id

    @property
    def current_cost_accounting(self):
        if self.type_load == 0:
            costs = self.setcost_set.filter(year=FiscalYear.get_current())
        else:
            costs = self.setcost_set.all()
        if len(costs) > 0:
            cost = costs[0].cost_accounting
        else:
            new_set_cost = self.create_new_cost()
            if new_set_cost is None:
                cost = None
            else:
                cost = new_set_cost.cost_accounting
        return cost

    def get_cost_accounting_name(self, year):
        if self.type_load == 1:
            cost_accounting_name = "[%d] %s" % (self.id, self.name)
        else:
            if year.begin.year == year.end.year:
                cost_accounting_name = "[%d] %s %s" % (self.id, self.name, year.begin.year)
                years_same = FiscalYear.objects.filter(begin__gte='%d-01-01' % year.begin.year, end__lte='%d-12-31' % year.begin.year)
                if len(years_same) > 1:
                    cost_accounting_name += '[%d]' % year.id
            else:
                cost_accounting_name = "[%d] %s %s/%s" % (self.id, self.name, year.begin.year, year.end.year)
        return cost_accounting_name

    def rename_all_cost_accounting(self):
        for setcost in self.setcost_set.all():
            try:
                setcost.cost_accounting.name = self.get_cost_accounting_name(setcost.year)
                setcost.cost_accounting.save()
            except IntegrityError:
                getLogger("diacamma.condominium").warning("Bad integity for cost accounting name %s", setcost.cost_accounting.name)
                try:
                    setcost.cost_accounting.name = "%s [multi #%d]" % (self.get_cost_accounting_name(setcost.year), setcost.cost_accounting.id)
                    setcost.cost_accounting.save()
                except IntegrityError:
                    getLogger("diacamma.condominium").error("Bad integity for cost accounting name %s", setcost.cost_accounting.name)

    def create_new_cost(self, year=None):
        if self.type_load == 1:
            year = None
            last_cost = None
        else:
            if isinstance(year, int) or (year is None):
                year = FiscalYear.get_current(year)
            costs = self.setcost_set.filter(year=year.last_fiscalyear)
            if len(costs) > 0:
                last_cost = costs[0].cost_accounting
            else:
                last_cost = None
        cost_accounting_name = self.get_cost_accounting_name(year)
        cost_accounting = CostAccounting.objects.create(name=cost_accounting_name, description=cost_accounting_name,
                                                        last_costaccounting=last_cost, year=year, is_protected=True)
        if (year is not None) and (year.status == 2):
            cost_accounting.close()
        return SetCost.objects.create(set=self, year=year, cost_accounting=cost_accounting)

    @classmethod
    def delete_orphelin_costaccounting(cls):
        for cost in CostAccounting.objects.filter(setcost=None, is_protected=True):
            try:
                cost.delete()
            except LucteriosException as exp:
                getLogger("diacamma.condominium").error("[%s] %s", cost, exp)
                cost.is_protected = False
                cost.save()

    @classmethod
    def correct_costaccounting(cls):
        EntryAccount.clear_ghost()
        cls.delete_orphelin_costaccounting()
        for cost in CostAccounting.objects.filter(year=None, is_protected=True, setcost__year__isnull=False):
            try:
                setcost_item = cost.setcost_set.filter(year__isnull=False)
                cost.year = setcost_item[0].year
                cost.save()
            except LucteriosException as exp:
                getLogger("diacamma.condominium").error("[%s] %s", cost, exp)

    def convert_cost(self):
        if (len(self.setcost_set.all()) == 0) and (self.cost_accounting_id is not None):
            if self.type_load == 1:
                SetCost.objects.create(set=self, year=None, cost_accounting_id=self.cost_accounting_id)
            else:
                year = FiscalYear.get_current()
                cost = self.cost_accounting
                while (year is not None) and (cost is not None):
                    SetCost.objects.create(set=self, year=year, cost_accounting=cost)
                    year = year.last_fiscalyear
                    cost = cost.last_costaccounting

    @property
    def budget_txt(self):
        return format_devise(self.get_current_budget(), 5)

    def get_current_budget(self):
        if self.type_load == 1:
            account = Params.getvalue("condominium-exceptional-revenue-account")
            costs = self.setcost_set.all()
        else:
            account = Params.getvalue("condominium-current-revenue-account")
            costs = self.setcost_set.filter(year=FiscalYear.get_current())
        revenue = 0
        if len(costs) == 1:
            cost = costs[0].cost_accounting
            for budget in Budget.objects.filter(cost_accounting=cost, code=account):
                revenue += budget.amount
        return revenue

    def get_new_current_callfunds(self):
        nb_seq = 0
        if Params.getvalue("condominium-mode-current-callfunds") == 0:
            nb_seq = 4
        if Params.getvalue("condominium-mode-current-callfunds") == 1:
            nb_seq = 12
        year = FiscalYear.get_current()
        nb_current = len(CallDetail.objects.filter(set=self, callfunds__date__gte=year.begin, callfunds__date__lte=year.end, callfunds__type_call=0))
        amount_current = CallDetail.objects.filter(set=self, callfunds__date__gte=year.begin, callfunds__date__lte=year.end, callfunds__type_call=0).aggregate(Sum('price'))
        if amount_current['price__sum'] is None:
            amount_current = 0.0
        else:
            amount_current = amount_current['price__sum']
        if nb_current < nb_seq:
            return currency_round(max(0.0, (float(self.get_current_budget()) - float(amount_current)) / (nb_seq - nb_current)))
        else:
            return 0.0

    def convert_budget(self):
        year = FiscalYear.get_current()
        cost = self.current_cost_accounting
        Budget.objects.create(cost_accounting=cost, year=year, code='600', amount=self.budget)
        self.change_budget_product(cost, year.id)

    def change_budget_product(self, cost_item, year=None):
        set_costs = SetCost.objects.filter(cost_accounting=cost_item)
        if (year is None) and (len(set_costs) == 1):
            year = set_costs[0].year_id
        if self.type_load == 1:
            account = Params.getvalue("condominium-exceptional-revenue-account")
        else:
            account = Params.getvalue("condominium-current-revenue-account")
        for budget in Budget.objects.filter(cost_accounting=cost_item, code=account, year_id=year):
            budget.delete()
        revenue = -1 * Budget.get_total(year=year, cost=cost_item.id)
        if abs(revenue) > 0.0001:
            Budget.objects.create(cost_accounting=cost_item, code=account, year_id=year, amount=revenue)

    @property
    def total_part(self):
        total = self.partition_set.all().aggregate(sum=Sum('value'))
        if 'sum' in total.keys():
            return total['sum']
        else:
            return 0

    def get_expenselist(self):
        if self.date_begin is None:
            self.set_dates()
        return self.expensedetail_set.filter(expense__date__gte=self.date_begin, expense__date__lte=self.date_end)

    def get_sumexpense(self):
        total = 0
        for expense_detail in self.get_expenselist():
            if expense_detail.expense.status != 0:
                if expense_detail.expense.expensetype == 0:
                    total += expense_detail.price
                else:
                    total -= expense_detail.price
        return total

    @property
    def sumexpense_txt(self):
        return format_devise(self.get_sumexpense(), 5)

    def refresh_ratio_link_lots(self):
        if self.is_link_to_lots:
            for part in self.partition_set.all():
                value = 0
                for lot in self.set_of_lots.filter(owner=part.owner):
                    value += lot.value
                part.value = value
                part.save()

    def check_close(self):
        for set_cost in self.setcost_set.all():
            set_cost.cost_accounting.check_before_close()
        ret = None
        if not Params.getvalue("condominium-old-accounting") and (self.type_load == 1):
            cost = self.setcost_set.all().order_by('year__begin')[0]
            result = currency_round(CallDetail.objects.filter(set=self).aggregate(sum=Sum('price'))['sum'])
            result -= cost.cost_accounting.get_total_expense()
            if abs(result) > 0.0001:
                ret = format_devise(result, 5)
        return ret

    def close_exceptional(self, with_ventil=False):
        self.close(2, Params.getvalue("condominium-exceptional-reserve-account"), with_ventil and (self.type_load == 1))

    def close_current(self, with_ventil=False):
        self.close(1, Params.getvalue("condominium-current-revenue-account"), with_ventil and (self.type_load == 0))

    def close(self, type_owner, initial_code, with_ventil):
        if with_ventil:
            own_set = self.setcost_set.all().order_by('year__begin')[0]
            current_system_condo().ventilate_costaccounting(self, own_set.cost_accounting, type_owner, initial_code)
        for set_cost in self.setcost_set.all():
            set_cost.cost_accounting.close()
        self.is_active = False
        self.save()

    def get_total_calloffund(self, year):
        value = 0
        for calldetail in CallDetail.objects.filter(set=self, callfunds__date__gte=year.begin, callfunds__date__lte=year.end):
            value += currency_round(calldetail.price)
        return value

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is not None:
            last_set_name = Set.objects.get(id=self.id).name
        else:
            last_set_name = self.name
        self.revenue_account = correct_accounting_code(self.revenue_account)
        self.refresh_ratio_link_lots()
        LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        if last_set_name != self.name:
            self.rename_all_cost_accounting()

    def delete(self, using=None):
        LucteriosModel.delete(self, using=using)
        Set.delete_orphelin_costaccounting()

    class Meta(object):
        verbose_name = _('class load')
        verbose_name_plural = _('class loads')


class SetCost(LucteriosModel):
    year = models.ForeignKey(FiscalYear, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    set = models.ForeignKey(Set, verbose_name=_('class load'), null=False, default=None, db_index=True, on_delete=models.CASCADE)
    cost_accounting = models.ForeignKey(CostAccounting, verbose_name=_('cost accounting'),
                                        null=True, default=None, db_index=True, on_delete=models.PROTECT)

    def __str__(self):
        return six.text_type(self.cost_accounting)

    @classmethod
    def get_default_fields(cls):
        return ["year", "set", "cost_accounting"]

    class Meta(object):
        verbose_name = _('cost of class load')
        verbose_name_plural = _('costs of class load')
        default_permissions = []
        ordering = ['year_id', 'set_id']


class OwnerEntryLineAccount(EntryLineAccount):

    @classmethod
    def get_default_fields(cls):
        return ['entry.date_value', (_('name'), 'designation_ref'), (_('debit'), 'debit'), (_('credit'), 'credit')]

    class Meta(object):
        proxy = True


class Owner(Supporting):
    information = models.CharField(
        _('information'), max_length=200, null=True, default='')

    def __init__(self, *args, **kwargs):
        Supporting.__init__(self, *args, **kwargs)
        self.date_begin = None
        self.date_end = None

    def set_dates(self, begin_date=None, end_date=None):
        if begin_date is None:
            self.date_begin = six.text_type(FiscalYear.get_current().begin)
        else:
            self.date_begin = begin_date
        if end_date is None:
            self.date_end = six.text_type(FiscalYear.get_current().end)
        else:
            self.date_end = end_date
        if isinstance(self.date_begin, six.text_type):
            self.date_begin = convert_date(self.date_begin)
        if isinstance(self.date_end, six.text_type):
            self.date_end = convert_date(self.date_end)
        if self.date_end < self.date_begin:
            self.date_end = self.date_begin

    def set_context(self, xfer):
        if xfer is not None:
            self.set_dates(xfer.getparam("begin_date"), xfer.getparam("end_date"))

    def get_third_mask(self, type_owner=1):
        if Params.getvalue("condominium-old-accounting"):
            return current_system_account().get_societary_mask()
        else:
            try:
                account = Params.getvalue("condominium-default-owner-account%d" % type_owner)
                return "^" + account + "[0-9a-zA-Z]*$"
            except BaseException:
                return current_system_account().get_societary_mask()

    def default_date(self):
        if self.date_begin is None:
            self.set_dates()
        ret_date = date.today()
        if ret_date < self.date_begin:
            ret_date = self.date_begin
        if ret_date > self.date_end:
            ret_date = self.date_end
        return ret_date

    @property
    def date_current(self):
        if self.date_begin is None:
            self.set_dates()
        if isinstance(self.date_end, six.text_type):
            self.date_end = convert_date(self.date_end)
        return formats.date_format(self.date_end, "DATE_FORMAT")

    def __str__(self):
        return six.text_type(self.third)

    @classmethod
    def throw_not_allowed(cls):
        if hasattr(settings, "DIACAMMA_MAXOWNER") and (len(cls.objects.all()) > getattr(settings, "DIACAMMA_MAXOWNER")):
            raise LucteriosException(IMPORTANT, _("You have too many owners declared!"))

    @classmethod
    def get_default_fields(cls):
        fields = ["third", (_('property tantime'), 'property_part'), (_('total owner initial'), 'thirdinitial'), (_('total call for funds'), 'total_all_call'),
                  (_('total payoff'), 'total_payoff'), (_('total owner'), 'thirdtotal'), (_('sum to pay'), 'sumtopay')]
        return fields

    @classmethod
    def get_show_fields_in_third(cls):
        return [((_('current initial state'), 'total_current_initial'),), ((_('current total call for funds'), 'total_current_call'),), ((_('current total owner'), 'total_current_owner'),)]

    @classmethod
    def get_edit_fields(cls):
        return []

    @classmethod
    def is_owner_account_doubled(cls, owner_type):
        account = Params.getvalue("condominium-default-owner-account%d" % owner_type)
        for other_owner_type in range(1, 6):
            if other_owner_type != owner_type:
                if account == Params.getvalue("condominium-default-owner-account%d" % other_owner_type):
                    return True
        return False

    @classmethod
    def get_show_fields(cls):
        fields = {"": [((_('name'), 'third'),), ],
                  _("001@Information"): [],
                  _("002@Lots"): ['propertylot_set'],
                  _("003@Contacts"): ['ownercontact_set'],
                  _("004@Accounting"): [((_('total owner initial'), 'thirdinitial'),), 'entryline_set', ((_('total owner'), 'thirdtotal'),), ((_('sum to pay'), 'sumtopay'),)],
                  _("005@Situation"): [('partition_set',),
                                       ((_('current initial state'), 'total_current_initial'), ),
                                       ((_('current total call for funds'), 'total_current_call'), (_('current total payoff'), 'total_current_payoff')),
                                       ((_('current total owner'), 'total_current_owner'), ),
                                       ((_('current total ventilated'), 'total_current_ventilated'), (_('estimated regularization'), 'total_current_regularization')),
                                       ((_('extra revenus/expenses'), 'total_extra'),),
                                       ],
                  _("006@Exceptional"): ['exceptionnal_set',
                                         ((_('exceptional initial state'), 'total_exceptional_initial'),),
                                         ((_('exceptional total call for funds'), 'total_exceptional_call'), (_('exceptional total payoff'), 'total_exceptional_payoff')),
                                         ((_('exceptional total owner'), 'total_exceptional_owner'), )],
                  _("007@callfunds"): ['callfunds_set', 'payoff_set'],
                  }
        if Params.getvalue("condominium-old-accounting"):
            del fields[_("005@Situation")][5]
            fields[_("005@Situation")][4] = (fields[_("005@Situation")][4][0],)
            del fields[_("006@Exceptional")][3]
            del fields[_("006@Exceptional")][2]
            del fields[_("006@Exceptional")][1]
        else:
            if cls.is_owner_account_doubled(1):
                del fields[_("005@Situation")][3]
                del fields[_("005@Situation")][1]
            if cls.is_owner_account_doubled(2):
                del fields[_("006@Exceptional")][3]
                del fields[_("006@Exceptional")][1]
        fields[_("001@Information")].append(((_('name'), 'third'),))
        fields[_("001@Information")].extend(get_subfield_show(AbstractContact.get_show_fields(), "third.contact"))
        fields[_("001@Information")].extend(get_subfield_show(Third.get_fields_to_show(), "third"))
        fields[_("001@Information")].append("information")
        return fields

    @classmethod
    def get_print_fields(cls):
        fields = ["third", "information"]
        fields.extend([(_('total owner initial'), 'thirdinitial'), 'entryline_set', (_('total owner'), 'thirdtotal'), (_('sum to pay'), 'sumtopay')])
        fields.extend(['ownercontact_set'])
        fields.extend(['propertylot_set.num', 'propertylot_set.value', 'propertylot_set.ratio', 'propertylot_set.description'])
        fields.extend(["callfunds_set.num", "callfunds_set.date",
                       "callfunds_set.comment", (_('total'), 'callfunds_set.total')])
        fields.extend(["partition_set.set.str", "partition_set.set.budget", (_('expense'), 'partition_set.set.sumexpense_txt'),
                       "partition_set.value", (_("ratio"), 'partition_set.ratio'), (_('ventilated'), 'partition_set.ventilated_txt')])
        fields.extend(["exceptionnal_set.set.str", "exceptionnal_set.set.budget", (_('expense'), 'exceptionnal_set.set.sumexpense_txt'),
                       (_('total call for funds'), 'exceptionnal_set.total_callfunds'),
                       "exceptionnal_set.value", (_("ratio"), 'exceptionnal_set.ratio'), (_('ventilated'), 'exceptionnal_set.ventilated_txt')])
        fields.extend(['payoff_set'])
        fields.extend([(_('current total call for funds'), 'total_current_call'), (_('current total payoff'), 'total_current_payoff'),
                       (_('current initial state'), 'total_current_initial'), (_('current total ventilated'), 'total_current_ventilated'),
                       (_('estimated regularization'), 'total_current_regularization'), (_('extra revenus/expenses'), 'total_extra'),
                       (_('current total owner'), 'total_current_owner')])
        fields.extend([(_('exceptional initial state'), 'total_exceptional_initial'),
                       (_('exceptional total call for funds'), 'total_exceptional_call'),
                       (_('exceptional total payoff'), 'total_exceptional_payoff'),
                       (_('exceptional total owner'), 'total_exceptional_owner')])
        return fields

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = self.id is None
        Supporting.save(self, force_insert=force_insert,
                        force_update=force_update, using=using, update_fields=update_fields)
        if is_new:
            for setitem in Set.objects.all():
                Partition.objects.create(set=setitem, owner=self)

    @property
    def thirdinitial(self):
        if self.date_begin is None:
            self.set_dates()
        third_total = get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__lt=self.date_begin)).aggregate(Sum('amount')))
        third_total -= get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value=self.date_begin) & Q(entry__journal__id=1)).aggregate(Sum('amount')))
        return format_devise(third_total, 5)

    @property
    def entryline_set(self):
        if self.date_begin is None:
            self.set_dates()
        return OwnerEntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__gte=self.date_begin) & Q(entry__date_value__lte=self.date_end) & ~Q(entry__journal__id=1))

    @property
    def thirdtotal(self):
        if self.date_begin is None:
            self.set_dates()
        return format_devise(self.third.get_total(self.date_end), 5)

    @property
    def sumtopay(self):
        if self.date_begin is None:
            self.set_dates()
        return format_devise(max(0, -1 * self.third.get_total(self.date_end)), 5)

    @property
    def total_all_call(self):
        return format_devise(self.get_total_call(-1), 5)

    @property
    def total_payoff(self):
        if self.date_begin is None:
            self.set_dates()
        third_total = -1 * get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__gte=self.date_begin) &
                                                                          Q(entry__date_value__lte=self.date_end) & Q(amount__lt=0)).aggregate(Sum('amount')))
        third_total += get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value=self.date_begin) & Q(entry__journal__id=1) & Q(amount__lt=0)).aggregate(Sum('amount')))
        return format_devise(third_total, 5)

    @property
    def exceptionnal_set(self):
        return PartitionExceptional.objects.filter(Q(owner=self) & Q(set__is_active=True) & Q(set__type_load=1))

    @property
    def partition_query(self):
        return Q(set__is_active=True) & Q(set__type_load=0)

    @property
    def callfunds_query(self):
        if self.date_begin is None:
            self.set_dates()
        return Q(date__gte=self.date_begin) & Q(date__lte=self.date_end)

    @property
    def payoff_query(self):
        if self.date_begin is None:
            self.set_dates()
        return Q(date__gte=self.date_begin) & Q(date__lte=self.date_end)

    def get_property_part(self):
        total_part = PropertyLot.get_total_part()
        if total_part > 0:
            total = self.propertylot_set.aggregate(sum=Sum('value'))
            if ('sum' in total.keys()) and (total['sum'] is not None):
                value = total['sum']
            else:
                value = 0
            return (value, total_part)
        else:
            return (None, None)

    @property
    def property_part(self):
        value, total_part = self.get_property_part()
        if value is not None:
            return "%d/%d{[br/]}%.1f %%" % (value, total_part, 100.0 * float(value) / float(total_part))
        else:
            return "---"

    def get_current_date(self):
        return date(2100, 12, 31)

    def get_total_call(self, type_call=0):
        val = 0
        if type_call < 0:
            totalfilter = Q()
        else:
            totalfilter = Q(type_call=type_call)
        for callfunds in self.callfunds_set.filter(self.callfunds_query & totalfilter):
            val += currency_round(callfunds.get_total())
        return val

    def get_total_payed(self, ignore_payoff=-1, type_call=1):
        val = Supporting.get_total_payed(self, ignore_payoff=ignore_payoff)
        if type_call < 0:
            totalfilter = Q()
        else:
            totalfilter = ~Q(type_call=type_call)
        for callfunds in self.callfunds_set.filter(self.callfunds_query & totalfilter):
            callfunds.check_supporting()
            val += currency_round(callfunds.supporting.get_total_payed(ignore_payoff))
        return val

    def get_total_initial(self, owner_type=1):
        if self.date_begin is None:
            self.set_dates()
        third_total = get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__lt=self.date_begin) &
                                                                     Q(account__code__regex=self.get_third_mask(owner_type))).aggregate(Sum('amount')))
        third_total -= get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value=self.date_begin) &
                                                                      Q(entry__journal__id=1) & Q(account__code__regex=self.get_third_mask(owner_type))).aggregate(Sum('amount')))
        return third_total

    def get_total_payoff(self, owner_type=1):
        if self.date_begin is None:
            self.set_dates()
        third_total = -1 * get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__gte=self.date_begin) &
                                                                          Q(entry__date_value__lte=self.date_end) & Q(entry__journal__id=4) &
                                                                          Q(account__code__regex=self.get_third_mask(owner_type))).aggregate(Sum('amount')))
        return third_total

    def get_total(self):
        return self.get_total_call() - self.get_total_initial()

    def get_total_current_ventilated(self):
        value = 0.0
        for part in self.partition_set.filter(self.partition_query):
            part.set.set_dates(self.date_begin, self.date_end)
            value += part.get_ventilated()
        return value

    def get_total_extra(self):
        value, total_part = self.get_property_part()
        if value is not None:
            try:
                year = FiscalYear.objects.get(begin__lte=self.date_end, end__gte=self.date_end)
                result = year.total_revenue - year.total_expense
                for set_cost in SetCost.objects.filter(year=year, set__is_active=True):
                    result -= set_cost.cost_accounting.get_total_revenue() - set_cost.cost_accounting.get_total_expense()
                return result * value / total_part
            except ObjectDoesNotExist:
                return None
        else:
            return None

    @property
    def total_extra(self):
        extra = self.get_total_extra()
        if extra is None:
            return extra
        else:
            return format_devise(self.get_total_extra(), 5)

    @property
    def total_current_call(self):
        return format_devise(self.get_total_call(0), 5)

    @property
    def total_current_payoff(self):
        if Params.getvalue("condominium-old-accounting"):
            return format_devise(self.get_total_payed(), 5)
        else:
            return format_devise(self.get_total_payoff(1), 5)

    @property
    def total_current_initial(self):
        return format_devise(self.get_total_initial(1), 5)

    @property
    def total_current_owner(self):
        if self.date_begin is None:
            self.set_dates()
        third_total = get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__lte=self.date_end) &
                                                                     Q(account__code__regex=self.get_third_mask(1))).aggregate(Sum('amount')))
        return format_devise(-1 * third_total, 5)

    @property
    def total_current_ventilated(self):
        return format_devise(self.get_total_current_ventilated(), 5)

    @property
    def total_current_regularization(self):
        return format_devise(self.get_total_call() - self.get_total_current_ventilated(), 5)

    @property
    def total_exceptional_call(self):
        return format_devise(self.get_total_call(1), 5)

    @property
    def total_exceptional_payoff(self):
        return format_devise(self.get_total_payoff(2), 5)

    @property
    def total_exceptional_initial(self):
        return format_devise(self.get_total_initial(2), 5)

    @property
    def total_exceptional_owner(self):
        if self.date_begin is None:
            self.set_dates()
        third_total = get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__lte=self.date_end) &
                                                                     Q(account__code__regex=self.get_third_mask(2))).aggregate(Sum('amount')))
        return format_devise(-1 * third_total, 5)

    def get_max_payoff(self, ignore_payoff=-1):
        return 1000000

    def payoff_is_revenu(self):
        return True

    class Meta(object):
        verbose_name = _('owner')
        verbose_name_plural = _('owners')

    def support_validated(self, validate_date):
        return self

    def get_tax(self):
        return 0.0

    def get_payable_without_tax(self):
        return currency_round(max(0, Supporting.get_total_rest_topay(self)))

    def get_total_rest_topay(self):
        val = Supporting.get_total_rest_topay(self)
        for callfunds in self.callfunds_set.filter(self.callfunds_query & ~Q(type_call=1)):
            callfunds.check_supporting()
            val -= currency_round(callfunds.supporting.get_total_rest_topay())
        return val

    def payoff_have_payment(self):
        return (Supporting.get_total_rest_topay(self) > 0.001)

    @classmethod
    def get_payment_fields(cls):
        return ["third", "information", 'callfunds_set', ((_('total owner'), 'total_current_owner'),)]

    def get_payment_name(self):
        return _('codominium of %s') % six.text_type(self.third)

    def get_docname(self):
        return _('your situation')

    def check_account(self):
        if Params.getvalue("condominium-old-accounting"):
            AccountThird.objects.get_or_create(third=self.third, code=correct_accounting_code(Params.getvalue("condominium-default-owner-account")))
        else:
            for num_account in range(1, 6):
                AccountThird.objects.get_or_create(third=self.third, code=correct_accounting_code(Params.getvalue("condominium-default-owner-account%d" % num_account)))

    @classmethod
    def check_all_account(cls):
        for owner in cls.objects.all():
            owner.check_account()


class Partition(LucteriosModel):
    set = models.ForeignKey(
        Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)
    value = models.DecimalField(_('tantime'), max_digits=7, decimal_places=2, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(100000.00)])

    def __str__(self):
        return "%s : %s" % (self.owner, self.ratio)

    @classmethod
    def get_default_fields(cls):
        return ["set", "set.budget", (_('expense'), 'set.sumexpense_txt'), "owner", "value", (_("ratio"), 'ratio'), (_('ventilated'), 'ventilated_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["set", "owner", "value"]

    def get_ratio(self):
        total = self.set.total_part
        if abs(total) < 0.01:
            return 0.0
        else:
            return float(100 * self.value / total)

    def set_context(self, xfer):
        if xfer is not None:
            self.set.set_dates(xfer.getparam("begin_date"), xfer.getparam("end_date"))

    def get_ventilated(self):
        value = 0
        ratio = self.get_ratio()
        if abs(ratio) > 0.01:
            try:
                year = FiscalYear.objects.get(begin__lte=self.set.date_end, end__gte=self.set.date_end)
            except ObjectDoesNotExist:
                year = FiscalYear.get_current()
                if self.set.date_end < year.begin:
                    return 0
            result = 0
            for set_cost in SetCost.objects.filter((Q(year=year) | Q(year__isnull=True)) & Q(set=self.set)):
                result += set_cost.cost_accounting.get_total_expense()
            value = result * ratio / 100.0
        return value

    @property
    def ventilated_txt(self):
        return format_devise(self.get_ventilated(), 5)

    def get_callfunds(self):
        value = 0
        ratio = self.get_ratio()
        if abs(ratio) > 0.01:
            for calldetail in CallDetail.objects.filter(callfunds__owner=self.owner, set=self.set, callfunds__date__gte=self.set.date_begin, callfunds__date__lte=self.set.date_end):
                value += currency_round(calldetail.price)
        return value

    @property
    def total_callfunds(self):
        return format_devise(self.get_callfunds(), 5)

    def get_total_current_regularization(self):
        return currency_round(self.get_callfunds() - self.get_ventilated())

    @property
    def total_current_regularization(self):
        return format_devise(self.get_total_current_regularization(), 5)

    @property
    def ratio(self):
        return "%.1f %%" % self.get_ratio()

    class Meta(object):
        verbose_name = _("division")
        verbose_name_plural = _("divisions")
        default_permissions = []
        ordering = ['owner__third_id', 'set_id']


class OwnerLink(LucteriosModel):
    name = models.CharField(_('name'), max_length=50, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ["name"]

    class Meta(object):
        verbose_name = _('owner link')
        verbose_name_plural = _('owner links')
        default_permissions = []


class OwnerContact(LucteriosModel):
    owner = models.ForeignKey(Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)
    contact = models.ForeignKey(AbstractContact, verbose_name=_('contact'), null=False, db_index=True, on_delete=models.CASCADE)
    link = models.ForeignKey(OwnerLink, verbose_name=_('owner link'), null=False, db_index=True, on_delete=models.PROTECT)

    def __str__(self):
        return six.text_type(self.contact)

    @classmethod
    def get_default_fields(cls):
        return ["contact", "link", "contact.email", "contact.tel1", "contact.tel2"]

    @classmethod
    def get_edit_fields(cls):
        return ["contact", "link"]

    class Meta(object):
        verbose_name = _('owner contact')
        verbose_name_plural = _('owner contacts')
        default_permissions = []


class PartitionExceptional(Partition):
    @classmethod
    def get_default_fields(cls):
        return ["set", (_("ratio"), 'ratio'), (_('total call for funds'), 'total_callfunds'),
                (_('ventilated'), 'ventilated_txt'), (_('estimated regularization'), 'total_current_regularization')]

    def set_context(self, xfer):
        if xfer is not None:
            self.set.set_dates("1900-01-01", xfer.getparam("end_date"))
        else:
            self.set.set_dates("1900-01-01", "2199-12-31")

    class Meta(object):
        verbose_name = _("exceptional class load")
        verbose_name_plural = _("exceptional class loads")
        default_permissions = []
        proxy = True
        ordering = ['owner__third_id', 'set_id']


class PropertyLot(LucteriosModel):
    num = models.IntegerField(verbose_name=_('numeros'), null=False, default=1)
    value = models.IntegerField(_('tantime'), default=0, validators=[MinValueValidator(0), MaxValueValidator(1000000)])
    description = models.TextField(_('description'), null=True, default="")
    owner = models.ForeignKey(
        Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)

    def __str__(self):
        return "[%s] %s" % (self.num, self.description)

    @classmethod
    def get_default_fields(cls):
        return ["num", "value", (_("ratio"), 'ratio'), "description", "owner"]

    @classmethod
    def get_edit_fields(cls):
        return ["num", "value", "description", "owner"]

    @classmethod
    def get_total_part(cls):
        total = cls.objects.all().aggregate(sum=Sum('value'))
        if ('sum' in total.keys()) and (total['sum'] is not None):
            return total['sum']
        else:
            return 0

    def get_ratio(self):
        total = self.get_total_part()
        if abs(total) < 0.01:
            return 0.0
        else:
            return 100.0 * float(self.value) / float(total)

    @property
    def ratio(self):
        return "%.1f %%" % self.get_ratio()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        for set_linked in Set.objects.filter(is_link_to_lots=True, set_of_lots__id=self.id):
            set_linked.refresh_ratio_link_lots()

    class Meta(object):
        verbose_name = _('property lot')
        verbose_name_plural = _('property lots')
        default_permissions = []
        ordering = ['num']


class CallFundsSupporting(Supporting):

    def __str__(self):
        return self.callfunds.__str__()

    def get_total(self):
        return self.callfunds.get_total()

    def get_third_mask(self):
        if Params.getvalue("condominium-old-accounting"):
            return current_system_account().get_societary_mask()
        else:
            try:
                account = Params.getvalue("condominium-default-owner-account%d" % (self.callfunds.type_call + 1))
                return "^" + account + "[0-9a-zA-Z]*$"
            except BaseException:
                return current_system_account().get_societary_mask()

    def payoff_is_revenu(self):
        return True

    @classmethod
    def get_long_name(cls):
        return CallFunds.get_long_name()

    @classmethod
    def get_payment_fields(cls):
        return ["callfunds.num", "callfunds.date", "callfunds.comment", "third", ((_('total'), 'callfunds.total'),)]

    def support_validated(self, validate_date):
        return self

    def get_current_date(self):
        return self.callfunds.date

    def get_tax(self):
        return 0

    def get_payable_without_tax(self):
        return self.get_total_rest_topay()

    def payoff_have_payment(self):
        return (self.callfunds.status == 1) and (self.get_total_rest_topay() > 0.001)

    class Meta(object):
        default_permissions = []


class CallFunds(LucteriosModel):
    owner = models.ForeignKey(Owner, verbose_name=_('owner'), null=True, db_index=True, on_delete=models.PROTECT)
    supporting = models.OneToOneField(CallFundsSupporting, on_delete=models.CASCADE, default=None, null=True)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    comment = models.TextField(_('comment'), null=True, default="")
    type_call = models.IntegerField(verbose_name=_('type of call'),
                                    choices=((0, _('current')), (1, _('exceptional')), (2, _('cash advance')), (3, _('borrowing')), (4, _('fund for works'))), null=False, default=0, db_index=True)
    status = FSMIntegerField(verbose_name=_('status'),
                             choices=((0, _('building')), (1, _('valid')), (2, _('ended'))), null=False, default=0, db_index=True)

    def __str__(self):
        return _('call of funds #%(num)d - %(date)s') % {'num': self.num, 'date': get_value_converted(self.date)}

    @classmethod
    def get_default_fields(cls):
        return ["num", (_('type of call'), 'type_call_ex'), "date", "owner", "comment", (_('total'), 'total'), (_('rest to pay'), 'supporting.total_rest_topay')]

    @classmethod
    def get_edit_fields(cls):
        return ["status", 'type_call', "date", "comment"]

    @classmethod
    def get_show_fields(cls):
        return [("num", "date"), ("owner", (_('type of call'), 'type_call_ex')), "calldetail_set", "comment", ("status", (_('total'), 'total'))]

    def get_total(self):
        self.check_supporting()
        val = 0
        for calldetail in self.calldetail_set.all():
            val += currency_round(calldetail.price)
        return val

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    @property
    def type_call_ex(self):
        result = "#%d" % self.type_call
        for callfunds_id, callfunds_title in current_system_condo().get_callfunds_list():
            if callfunds_id == self.type_call:
                result = callfunds_title
                break
        return result

    def can_delete(self):
        if self.status != 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    transitionname__valid = _("Valid")

    @transition(field=status, source=0, target=1, conditions=[lambda item:(len(Owner.objects.all()) > 0) and (len(item.calldetail_set.all()) > 0)])
    def valid(self):
        Owner.throw_not_allowed()
        val = CallFunds.objects.exclude(status=0).aggregate(Max('num'))
        if val['num__max'] is None:
            new_num = 1
        else:
            new_num = val['num__max'] + 1
        last_call = None
        calls_by_owner = {}
        for owner in Owner.objects.all():
            calls_by_owner[owner.id] = CallFunds.objects.create(num=new_num, date=self.date, owner=owner, comment=self.comment, type_call=self.type_call,
                                                                status=1, supporting=CallFundsSupporting.objects.create(third=owner.third))
            last_call = calls_by_owner[owner.id]
        for calldetail in self.calldetail_set.all():
            amount = float(calldetail.price)
            new_detail = None
            for part in calldetail.set.partition_set.all().order_by('value'):
                if part.value > 0.001:
                    new_detail = CallDetail.objects.create(
                        set=calldetail.set, designation=calldetail.designation)
                    new_detail.callfunds = calls_by_owner[part.owner.id]
                    new_detail.price = currency_round(float(calldetail.price) * part.get_ratio() / 100.0)
                    amount -= new_detail.price
                    new_detail.save()
            if new_detail is None:
                raise LucteriosException(IMPORTANT, _("Category of charge not fill!"))
            if abs(amount) > 0.0001:
                new_detail.price += amount
                new_detail.save()
        for new_call in calls_by_owner.values():
            if new_call.get_total() < 0.0001:
                new_call.delete()
            else:
                new_call.generate_accounting()
        self.delete()
        if last_call is not None:
            self.__dict__ = last_call.__dict__

    transitionname__close = _("Closed")

    @transition(field=status, source=1, target=2)
    def close(self):
        pass

    def generate_accounting(self, fiscal_year=None):
        if (self.owner is not None) and (self.status == 1) and not Params.getvalue("condominium-old-accounting"):
            if fiscal_year is None:
                fiscal_year = FiscalYear.get_current()
            current_system_condo().generate_account_callfunds(self, fiscal_year)

    def check_supporting(self):
        if (self.owner is not None) and (self.supporting is None):
            self.supporting = CallFundsSupporting.objects.create(third=self.owner.third)
            self.save()

    def payoff_have_payment(self):
        if (self.supporting is not None):
            return self.supporting.payoff_have_payment()
        else:
            return False

    class Meta(object):
        verbose_name = _('call of funds')
        verbose_name_plural = _('calls of funds')


class CallDetail(LucteriosModel):
    callfunds = models.ForeignKey(CallFunds, verbose_name=_('call of funds'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    price = models.DecimalField(verbose_name=_('amount'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    entry = models.ForeignKey(EntryAccount, verbose_name=_('entry'), null=True, on_delete=models.PROTECT)

    def __str__(self):
        return "%s - %s" % (self.callfunds, self.designation)

    @classmethod
    def get_default_fields(cls):
        return ["set", "designation", (_('total'), 'total_amount'), (_('tantime sum'), 'set.total_part'), (_('tantime'), 'owner_part'), (_('amount'), 'price_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["set", "designation", "price"]

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

    @property
    def total_amount(self):
        totamount = 0
        num = -1
        index = 0
        for det in self.callfunds.calldetail_set.filter(set=self.set):
            if det.id == self.id:
                num = index
            index += 1
        for fund in CallFunds.objects.filter(date=self.callfunds.date, num=self.callfunds.num):
            details = fund.calldetail_set.filter(set=self.set)
            if len(details) > num:
                det = details[num]
                totamount += det.price
        return format_devise(totamount, 5)

    @property
    def owner_part(self):
        value = 0
        for part in Partition.objects.filter(set=self.set, owner=self.callfunds.owner):
            value = part.value
        return value

    class Meta(object):
        verbose_name = _('detail of call')
        verbose_name_plural = _('details of call')
        default_permissions = []


class Expense(Supporting):
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    comment = models.TextField(_('comment'), null=True, default="")
    expensetype = models.IntegerField(verbose_name=_('expense type'),
                                      choices=((0, _('expense')), (1, _('asset of expense'))), null=False, default=0, db_index=True)
    status = FSMIntegerField(verbose_name=_('status'),
                             choices=((0, _('building')), (1, _('valid')), (2, _('ended'))), null=False, default=0, db_index=True)
    entries = models.ManyToManyField(EntryAccount, verbose_name=_('entries'))

    def __str__(self):
        if self.expensetype == 0:
            typetxt = _('expense')
        else:
            typetxt = _('asset of expense')
        return "%s %s - %s" % (typetxt, self.num, self.comment)

    @classmethod
    def get_default_fields(cls, status=-1):
        fields = ["num", "date", "third", "comment", (_('total'), 'total')]
        if status == 1:
            fields.append(Supporting.get_payoff_fields()[-1][-1])
        return fields

    def get_third_mask(self):
        return current_system_account().get_provider_mask()

    @classmethod
    def get_edit_fields(cls):
        return ["status", 'expensetype', "date", "comment"]

    @classmethod
    def get_show_fields(cls):
        return ["third", ("num", "date"), "expensetype", "expensedetail_set", "comment", ("status", (_('total'), 'total'))]

    def get_total(self):
        val = 0
        for expensedetail in self.expensedetail_set.all():
            val += currency_round(expensedetail.price)
        return val

    def get_current_date(self):
        return self.date

    def payoff_is_revenu(self):
        return self.expensetype == 1

    def default_date(self):
        return self.date

    def entry_links(self):
        ret = []
        if self.id is not None:
            ret.extend(list(self.entries.all()))
            for detail in self.expensedetail_set.all():
                if detail.entry_id is not None:
                    ret.append(detail.entry)
        return ret

    def can_delete(self):
        if self.status != 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    def generate_revenue_entry(self, is_asset, fiscal_year):
        for detail in self.expensedetail_set.all():
            detail.generate_ratio(is_asset)
        current_system_condo().generate_revenue_for_expense(self, is_asset, fiscal_year)

    def generate_expense_entry(self, is_asset, fiscal_year):
        current_system_condo().generate_expense_for_expense(self, is_asset, fiscal_year)

    def check_if_can_reedit(self):
        is_close = False
        for detail in self.expensedetail_set.all():
            is_close = is_close or ((detail.entry is not None) and detail.entry.close)
        for entry in self.entries.all():
            is_close = is_close or entry.close
        for payoff in self.payoff_set.all():
            is_close = is_close or ((payoff.entry is not None) and payoff.entry.close)
        return not is_close

    transitionname__reedit = _("Re-edit")

    @transition(field=status, source=1, target=0, conditions=[lambda item:item.check_if_can_reedit()])
    def reedit(self, clean_payoff=True):
        def del_entry(entry_id):
            current_entry = EntryAccount.objects.get(id=entry_id)
            current_entry.delete()
        if clean_payoff:
            for payoff in self.payoff_set.all():
                payoff.delete()
        for detail in self.expensedetail_set.filter(entry__isnull=False):
            old_entityid = detail.entry_id
            detail.entry = None
            detail.save()
            del_entry(old_entityid)
        for entry in self.entries.all():
            del_entry(entry.id)

    transitionname__valid = _("Valid")

    @transition(field=status, source=0, target=1, conditions=[lambda item:item.get_info_state() == ''])
    def valid(self):
        if self.expensetype == 0:
            is_asset = 1
        else:
            is_asset = -1
        fiscal_year = FiscalYear.get_current()
        val = Expense.objects.filter(date__gte=fiscal_year.begin, date__lte=fiscal_year.end).exclude(status=0).aggregate(Max('num'))
        if val['num__max'] is None:
            self.num = 1
        else:
            self.num = val['num__max'] + 1
        self.generate_expense_entry(is_asset, fiscal_year)
        self.generate_revenue_entry(is_asset, fiscal_year)

    transitionname__close = _("Closed")

    @transition(field=status, source=1, target=2)
    def close(self):
        if self.entries is not None:
            for entry in self.entries.all():
                entry.closed()
        for detail in self.expensedetail_set.all():
            if detail.entry is not None:
                detail.entry.closed()
        for payoff in self.payoff_set.all():
            if payoff.entry is not None:
                payoff.entry.closed()

    def get_info_state(self):
        info = []
        if self.status == 0:
            info = Supporting.get_info_state(
                self, current_system_account().get_provider_mask())
        info.extend(self.check_date(self.date.isoformat()))
        return "{[br/]}".join(info)

    class Meta(object):
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')
        ordering = ['-date']


class ExpenseDetail(LucteriosModel):
    expense = models.ForeignKey(Expense, verbose_name=_('expense'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    expense_account = models.CharField(verbose_name=_('account'), max_length=50)
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    entry = models.ForeignKey(EntryAccount, verbose_name=_('entry'), null=True, on_delete=models.PROTECT)

    def __str__(self):
        return "%s: %s" % (self.expense, self.designation)

    @classmethod
    def get_default_fields(cls):
        return ["set", "designation", "expense_account", (_('price'), 'price_txt'), (_('ratio'), 'ratio_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["set", "designation", "expense_account", "price"]

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

    @property
    def ratio_txt(self):
        ratio = ""
        if self.expense.status == 0:
            for part in self.set.partition_set.exclude(value=0.0):
                ratio += six.text_type(part)
                ratio += "{[br/]}"
        else:
            for part in self.expenseratio_set.all():
                ratio += six.text_type(part)
                ratio += "{[br/]}"
        return ratio

    def generate_ratio(self, is_asset):
        price = currency_round(self.price)
        last_line = None
        total = 0
        for part in Partition.objects.filter(set=self.set).order_by('value'):
            amount = currency_round(price * part.get_ratio() / 100.0)
            if amount > 0.0001:
                last_line, _created = ExpenseRatio.objects.get_or_create(expensedetail=self, owner=part.owner)
                last_line.value = is_asset * amount
                last_line.save()
                total += amount
        if (last_line is not None) and (abs(price - total) > 0.0001):
            last_line.value += is_asset * (price - total)
            last_line.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.expense_account = correct_accounting_code(self.expense_account)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('detail of expense')
        verbose_name_plural = _('details of expense')
        default_permissions = []


class ExpenseRatio(LucteriosModel):
    expensedetail = models.ForeignKey(
        ExpenseDetail, verbose_name=_('detail of expense'), null=False, db_index=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)
    value = models.DecimalField(_('value'), max_digits=7, decimal_places=2, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(1000.00)])

    def __str__(self):
        return "%s : %.1f %%" % (six.text_type(self.owner.third), 100.0 * float(abs(self.value)) / float(self.expensedetail.price))

    class Meta(object):
        verbose_name = _('detail of expense')
        verbose_name_plural = _('details of expense')
        default_permissions = []
        ordering = ['owner__third_id']


def convert_accounting(year, thirds_convert):
    year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account1')),
                                  'Copropriétaire - budget prévisionnel')
    year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account2')),
                                  'Copropriétaire - travaux et opération exceptionnelles')
    year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account3')),
                                  'Copropriétaire - avances')
    year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account4')),
                                  'Copropriétaire - emprunts')
    year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account5')),
                                  'Copropriétaire - fond travaux')
    for code_init, code_target in thirds_convert.items():
        try:
            account_init = ChartsAccount.objects.get(year=year, code=code_init)
            account_target = ChartsAccount.objects.get(year=year, code=code_target)
            account_target.merge_objects(account_init)
        except BaseException:
            pass
    for entry in year.entryaccount_set.exclude(journal_id=1):
        entry.num = None
        entry.close = False
        entry.date_entry = None
        entry.save()
    for call_funds in CallFunds.objects.filter(status__gte=1, date__gte=year.begin, date__lte=year.end):
        if (call_funds.status == 2):
            call_funds.status = 1
        call_funds.check_supporting()
        type_call = 0
        for call_detail in call_funds.calldetail_set.all():
            if call_detail.set.type_load == 1:
                type_call = 1
                break
        call_funds.type_call = type_call
        call_funds.save()
        call_funds.generate_accounting(year)
    expense_list = []
    for expense in Expense.objects.filter(status__gte=1, date__gte=year.begin, date__lte=year.end):
        if (expense.status == 2):
            expense.status = 1
            expense.save()
        expense.reedit(clean_payoff=False)
        expense.num = None
        expense.save()
        expense_list.append(expense)
    for expense in expense_list:
        expense.valid()
    for pay_off in Payoff.objects.filter(date__gte=year.begin, date__lte=year.end):
        pay_off.save()


@Signal.decorate('checkparam')
def condominium_checkparam():
    Parameter.check_and_create(
        name='condominium-default-owner-account',
        typeparam=0,
        title=_("condominium-default-owner-account"),
        args="{'Multi':False}",
        value=correct_accounting_code('450'),
        meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_societary_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    Parameter.check_and_create(
        name='condominium-default-owner-account1',
        typeparam=0,
        title=_("condominium-default-owner-account1"),
        args="{'Multi':False}",
        value=correct_accounting_code('4501'),
        meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_societary_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    Parameter.check_and_create(
        name='condominium-default-owner-account2',
        typeparam=0,
        title=_("condominium-default-owner-account2"),
        args="{'Multi':False}",
        value=correct_accounting_code('4502'),
        meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_societary_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    Parameter.check_and_create(
        name='condominium-default-owner-account3',
        typeparam=0,
        title=_("condominium-default-owner-account3"),
        args="{'Multi':False}",
        value=correct_accounting_code('4503'),
        meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_societary_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    Parameter.check_and_create(
        name='condominium-default-owner-account4',
        typeparam=0,
        title=_("condominium-default-owner-account4"),
        args="{'Multi':False}",
        value=correct_accounting_code('4504'),
        meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_societary_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    Parameter.check_and_create(
        name='condominium-default-owner-account5',
        typeparam=0,
        title=_("condominium-default-owner-account5"),
        args="{'Multi':False}",
        value=correct_accounting_code('4505'),
        meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_societary_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    Parameter.check_and_create(name='condominium-current-revenue-account', typeparam=0, title=_("condominium-current-revenue-account"),
                               args="{'Multi':False}", value=correct_accounting_code('701'), meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='condominium-exceptional-revenue-account', typeparam=0, title=_("condominium-exceptional-revenue-account"),
                               args="{'Multi':False}", value=correct_accounting_code('702'), meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='condominium-fundforworks-revenue-account', typeparam=0, title=_("condominium-fundforworks-revenue-account"),
                               args="{'Multi':False}", value=correct_accounting_code('705'), meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='condominium-exceptional-reserve-account', typeparam=0, title=_("condominium-exceptional-reserve-account"),
                               args="{'Multi':False}", value=correct_accounting_code('120'), meta='("accounting","ChartsAccount", Q(type_of_account=2) & Q(year__is_actif=True), "code", False)')
    Parameter.check_and_create(name='condominium-advance-reserve-account', typeparam=0, title=_("condominium-advance-reserve-account"),
                               args="{'Multi':False}", value=correct_accounting_code('103'), meta='("accounting","ChartsAccount", Q(type_of_account=2) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='condominium-fundforworks-reserve-account', typeparam=0, title=_("condominium-fundforworks-reserve-account"),
                               args="{'Multi':False}", value=correct_accounting_code('105'), meta='("accounting","ChartsAccount", Q(type_of_account=2) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='condominium-mode-current-callfunds', typeparam=4, title=_("condominium-mode-current-callfunds"),
                               args="{'Enum':2}", value=0, param_titles=(_("condominium-mode-current-callfunds.0"), _("condominium-mode-current-callfunds.1")))
    if Parameter.check_and_create(name='condominium-old-accounting', typeparam=3, title=_("condominium-old-accounting"), args="{}", value='False'):
        Parameter.change_value('condominium-old-accounting', len(Owner.objects.all()) != 0)
        for current_set in Set.objects.all():
            current_set.convert_cost()
    set_list = Set.objects.filter(is_active=True)
    for setitem in set_list:
        setitem.rename_all_cost_accounting()
        if len(setitem.current_cost_accounting.budget_set.all()) == 0:
            setitem.convert_budget()
    for budget_item in Budget.objects.filter(year__isnull=True):
        budget_item.year = FiscalYear.get_current()
        budget_item.save()
    Set.correct_costaccounting()
