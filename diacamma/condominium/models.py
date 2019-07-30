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
from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum, Max
from django.db.utils import IntegrityError
from django.db.models.query import QuerySet
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils import six, formats
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django_fsm import FSMIntegerField, transition

from lucterios.framework.models import LucteriosModel, get_subfield_show,\
    LucteriosVirtualField, LucteriosDecimalField
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.tools import convert_date, get_date_formating,\
    format_to_string
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import AbstractContact

from diacamma.accounting.models import CostAccounting, EntryAccount, ChartsAccount, EntryLineAccount, FiscalYear, Budget, AccountThird, Third
from diacamma.accounting.tools import currency_round, current_system_account, get_amount_sum, correct_accounting_code, format_with_devise
from diacamma.payoff.models import Supporting, Payoff
from diacamma.condominium.system import current_system_condo
from diacamma.accounting.tools_reports import get_spaces
from lucterios.framework.auditlog import auditlog


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

    identify = LucteriosVirtualField(verbose_name=_('name'), compute_from="get_identify")
    budget_txt = LucteriosVirtualField(verbose_name=_('budget'), compute_from="get_current_budget", format_string=lambda: format_with_devise(5))
    sumexpense = LucteriosVirtualField(verbose_name=_('expense'), compute_from='get_sumexpense', format_string=lambda: format_with_devise(5))
    total_part = LucteriosVirtualField(verbose_name=_('tantime sum'), compute_from='get_total_part', format_string="N2")
    current_cost_accounting = LucteriosVirtualField(verbose_name=_('cost accounting'), compute_from='get_current_cost_accounting')

    # for legacy
    sumexpense_txt = LucteriosVirtualField(verbose_name=_('expense'), compute_from='get_sumexpense', format_string=lambda: format_with_devise(5))

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

    def get_identify(self):
        if self.id is None:
            return None
        return "[%d] %s" % (self.id, self.name)

    @classmethod
    def get_default_fields(cls):
        return ["identify", 'type_load', (_('divisions'), 'partitionfill_set'), "budget_txt", 'sumexpense']

    @classmethod
    def get_edit_fields(cls):
        fields = ["name", "type_load", 'is_link_to_lots']
        if Params.getvalue("condominium-old-accounting"):
            fields.append("revenue_account")
        return fields

    @classmethod
    def get_show_fields(cls):
        if Params.getvalue("condominium-old-accounting"):
            return [("name", ), ("revenue_account", 'current_cost_accounting'), ("type_load", 'is_active'),
                    ('is_link_to_lots', 'total_part'), 'partition_set', 'partitionfill_set', ("budget_txt", 'sumexpense',)]
        else:
            return [("name", 'current_cost_accounting'), ("type_load", 'is_active'), ('is_link_to_lots', 'total_part'),
                    'partition_set', 'partitionfill_set', ("budget_txt", 'sumexpense',)]

    def _do_insert(self, manager, using, fields, update_pk, raw):
        new_id = LucteriosModel._do_insert(
            self, manager, using, fields, update_pk, raw)
        for owner in Owner.objects.all():
            Partition.objects.create(set_id=new_id, owner=owner)
        return new_id

    def get_current_cost_accounting(self):
        if self.id is None:
            return None
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

    def get_current_budget(self):
        if self.id is None:
            return None
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
        nb_current = len(CallDetail.objects.filter(set=self, callfunds__date__gte=year.begin, callfunds__date__lte=year.end, type_call=0))
        amount_current = CallDetail.objects.filter(set=self, callfunds__date__gte=year.begin, callfunds__date__lte=year.end, type_call=0).aggregate(Sum('price'))
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

    def get_total_part(self):
        if self.id is None:
            return None
        total = self.partition_set.all().aggregate(sum=Sum('value'))
        if 'sum' in total.keys():
            res = total['sum']
        else:
            res = Decimal(0.0)
        return res

    def get_expenselist(self):
        if self.date_begin is None:
            self.set_dates()
        return self.expensedetail_set.filter(expense__date__gte=self.date_begin, expense__date__lte=self.date_end)

    def get_sumexpense(self):
        if self.id is None:
            return None
        total = 0
        for expense_detail in self.get_expenselist():
            if expense_detail.expense.status != 0:
                if expense_detail.expense.expensetype == 0:
                    total += expense_detail.price
                else:
                    total -= expense_detail.price
        return total

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
                ret = result
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
        return ['entry.date_value', 'designation_ref', 'debit', 'credit']

    class Meta(object):
        proxy = True


class LoadCount(LucteriosModel):

    id = models.IntegerField(verbose_name=_('id'), null=False, default=0, db_index=True)
    designation = models.TextField(_('designation'), null=False, default="")
    total = LucteriosDecimalField(_('total'), null=False, max_digits=10, decimal_places=3, default=0.0,
                                  validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    ratio = models.TextField(_('ratio'), null=True, default=None)
    ventilated = LucteriosDecimalField(_('ventilated'), null=False, max_digits=10, decimal_places=3, default=0.0,
                                       validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    recoverable_load = LucteriosDecimalField(_('recoverable load'), null=False, max_digits=10, decimal_places=3, default=0.0,
                                             validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))

    @classmethod
    def get_default_fields(cls, status=-1):
        return ['designation', 'total', 'ratio', 'ventilated', 'recoverable_load']

    class Meta(object):
        abstract = True
        verbose_name = _('load count')
        verbose_name_plural = _('load counts')


class LoadCountSet(QuerySet):

    def __init__(self, model=None, query=None, using=None, hints=None):
        QuerySet.__init__(self, model=LoadCount, query=query, using=using, hints=hints)
        self._result_cache = None
        self.pt_id = 0
        self.model._meta.pk = Set()._meta.pk
        self.owner = self._hints['owner']

        self.partition_query = Q(owner=self.owner) & Q(value__gt=0)
        self.partition_query &= Q(set__setcost__cost_accounting__entrylineaccount__entry__date_value__gte=self.owner.date_begin) & Q(set__setcost__cost_accounting__entrylineaccount__entry__date_value__lte=self.owner.date_end)
        self.account_query = Q(type_of_account=4)
        self.account_query &= Q(entrylineaccount__entry__date_value__gte=self.owner.date_begin) & Q(entrylineaccount__entry__date_value__lte=self.owner.date_end)
        self.account_query &= Q(entrylineaccount__costaccounting__setcost__set__partition__owner=self.owner) & Q(entrylineaccount__costaccounting__setcost__set__partition__value__gt=0)
        self.line_query = Q(entry__date_value__gte=self.owner.date_begin) & Q(entry__date_value__lte=self.owner.date_end)

        self.general_total = 0
        self.ventilated_total = 0
        self.recoverable_load_total = 0

        self.partition_general_total = 0
        self.partition_ventilated_total = 0
        self.partition_recoverable_load_total = 0

    def fill_title(self, designation, total='', ratio=None, ventilated='', recoverable_load=''):
        self._result_cache.append(LoadCount(id=self.pt_id, designation=designation, total=total,
                                            ratio=ratio, ventilated=ventilated, recoverable_load=recoverable_load))
        self.pt_id += 1
        return self.pt_id - 1, len(self._result_cache) - 1

    def change_value(self, ident, total='', ratio='', ventilated='', recoverable_load=''):
        pt_id, result_cache_id = ident
        designation = self._result_cache[result_cache_id].designation
        self._result_cache[result_cache_id] = LoadCount(id=pt_id, designation=designation, total=total, ratio=ratio,
                                                        ventilated=ventilated, recoverable_load=recoverable_load)

    def fill_account(self, partition_item, account, ratio):
        recovery_load_ratio = RecoverableLoadRatio.objects.filter(code=account.code)
        if len(recovery_load_ratio) > 0:
            load_ratio = float(recovery_load_ratio[0].ratio) / 100.0
        else:
            load_ratio = 0
        total = 0
        designation = get_spaces(8) + "{[b]}%s{[/b]}" % account
        code_ident = self.fill_title(designation)
        for entry_line in EntryLineAccount.objects.filter(self.line_query & Q(account=account) & Q(costaccounting__setcost__set__partition=partition_item)).distinct().order_by('entry__date_value'):
            designation = get_spaces(15) + "{[i]}%s{[/i]} - %s" % (get_date_formating(entry_line.entry.date_value), entry_line.entry.designation.replace('{[br/]}', ' - '))
            self.fill_title(designation, total=entry_line.amount)
            total += entry_line.amount
        self.change_value(code_ident,
                          total={'format': "{[b]}{0}[/b]}", 'value': total},
                          ratio={'format': "{[b]}{0}[/b]}", 'value': "%d/%d" % (partition_item.value, partition_item.set.total_part)},
                          ventilated={'format': "{[b]}{0}[/b]}", 'value': total * ratio},
                          recoverable_load={'format': "{[b]}{0}[/b]}", 'value': total * ratio * load_ratio})
        self.partition_general_total += total
        self.partition_ventilated_total += total * ratio
        self.partition_recoverable_load_total += total * ratio * load_ratio
        self.fill_title('')

    def fill_partition(self, partition_item):
        ratio = float(partition_item.value / partition_item.set.total_part)
        partition_description = "{[i]}%s{[/i]}" % partition_item.set
        self.partition_general_total = 0
        self.partition_ventilated_total = 0
        self.partition_recoverable_load_total = 0
        partition_ident = None
        for account in ChartsAccount.objects.filter(self.account_query & Q(entrylineaccount__costaccounting__setcost__set__partition=partition_item)).order_by('code').distinct():
            if partition_description != '':
                partition_ident = self.fill_title(partition_description)
                partition_description = ''
            self.fill_account(partition_item, account, ratio)
        if partition_ident is not None:
            self.change_value(partition_ident,
                              total={'format': "{[i]}{0}[/i]}", 'value': self.partition_general_total},
                              ratio={'format': "{[i]}{0}[/i]}", 'value': "%d/%d" % (partition_item.value, partition_item.set.total_part)},
                              ventilated={'format': "{[i]}{0}[/i]}", 'value': self.partition_ventilated_total},
                              recoverable_load={'format': "{[i]}{0}[/i]}", 'value': self.partition_recoverable_load_total})
        self.general_total += self.partition_general_total
        self.ventilated_total += self.partition_ventilated_total
        self.recoverable_load_total += self.partition_recoverable_load_total

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = []
            self.pt_id = 1
            self.general_total = 0
            self.ventilated_total = 0
            self.recoverable_load_total = 0
            for partition_item in Partition.objects.filter(self.partition_query).distinct():
                self.fill_partition(partition_item)
            self.fill_title('',
                            total={'format': "{[u]}{0}[/u]}", 'value': self.general_total},
                            ventilated={'format': "{[u]}{0}[/u]}", 'value': self.ventilated_total},
                            recoverable_load={'format': "{[u]}{0}[/u]}", 'value': self.recoverable_load_total})


class Owner(Supporting):
    information = models.CharField(_('information'), max_length=200, null=True, default='')

    property_part = LucteriosVirtualField(verbose_name=_('property tantime'), compute_from='get_property_part', format_string="N1;{0}/{1}{[br/]}{2} %")
    thirdinitial = LucteriosVirtualField(verbose_name=_('total owner initial'), compute_from='get_third_initial', format_string=lambda: format_with_devise(5))
    total_all_call = LucteriosVirtualField(verbose_name=_('total call for funds'), compute_from=lambda item: item.get_total_call(-1), format_string=lambda: format_with_devise(5))
    total_payoff = LucteriosVirtualField(verbose_name=_('total payoff'), compute_from='get_total_payoff_calculated', format_string=lambda: format_with_devise(5))
    thirdtotal = LucteriosVirtualField(verbose_name=_('total owner'), compute_from='get_thirdtotal', format_string=lambda: format_with_devise(5))
    sumtopay = LucteriosVirtualField(verbose_name=_('sum to pay'), compute_from='get_sumtopay', format_string=lambda: format_with_devise(5))

    total_current_initial = LucteriosVirtualField(verbose_name=_('current initial state'), compute_from=lambda item: item.get_total_initial(1), format_string=lambda: format_with_devise(5))
    total_current_call = LucteriosVirtualField(verbose_name=_('current total call for funds'), compute_from=lambda item: item.get_total_call(0), format_string=lambda: format_with_devise(5))
    total_current_owner = LucteriosVirtualField(verbose_name=_('current total owner'), compute_from='get_total_current_owner', format_string=lambda: format_with_devise(5))

    total_current_payoff = LucteriosVirtualField(verbose_name=_('current total payoff'), compute_from='get_total_current_payoff', format_string=lambda: format_with_devise(5))
    total_current_ventilated = LucteriosVirtualField(verbose_name=_('current total ventilated'), compute_from='get_total_current_ventilated', format_string=lambda: format_with_devise(5))
    total_current_regularization = LucteriosVirtualField(verbose_name=_('estimated regularization'), compute_from='get_total_current_regularization', format_string=lambda: format_with_devise(5))
    total_recoverable_load = LucteriosVirtualField(verbose_name=_('total recoverable load'), compute_from='get_total_recoverable_load', format_string=lambda: format_with_devise(5))
    total_extra = LucteriosVirtualField(verbose_name=_('extra revenus/expenses'), compute_from='get_total_extra', format_string=lambda: format_with_devise(5))

    total_exceptional_initial = LucteriosVirtualField(verbose_name=_('exceptional initial state'), compute_from=lambda item: item.get_total_initial(2), format_string=lambda: format_with_devise(5))
    total_exceptional_call = LucteriosVirtualField(verbose_name=_('exceptional total call for funds'), compute_from=lambda item: item.get_total_call(1), format_string=lambda: format_with_devise(5))
    total_exceptional_payoff = LucteriosVirtualField(verbose_name=_('exceptional total payoff'), compute_from=lambda item: item.get_total_payoff(2), format_string=lambda: format_with_devise(5))
    total_exceptional_owner = LucteriosVirtualField(verbose_name=_('exceptional total owner'), compute_from='get_total_exceptional_owner', format_string=lambda: format_with_devise(5))

    total_cash_advance_call = LucteriosVirtualField(verbose_name=_('cash advance total call for funds'), compute_from=lambda item: item.get_total_call(2), format_string=lambda: format_with_devise(5))
    total_cash_advance_payoff = LucteriosVirtualField(verbose_name=_('cash advance total payoff'), compute_from=lambda item: item.get_total_payoff(3), format_string=lambda: format_with_devise(5))
    total_fund_works_call = LucteriosVirtualField(verbose_name=_('fund for works total call for funds'), compute_from=lambda item: item.get_total_call(4), format_string=lambda: format_with_devise(5))
    total_fund_works_payoff = LucteriosVirtualField(verbose_name=_('fund for works total payoff'), compute_from=lambda item: item.get_total_payoff(5), format_string=lambda: format_with_devise(5))

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
        def add_account_rex(typeowner):
            account = Params.getvalue("condominium-default-owner-account%d" % typeowner)
            account_rex_list.append("^" + account + "[0-9a-zA-Z]*$")

        if Params.getvalue("condominium-old-accounting"):
            return current_system_account().get_societary_mask()
        else:
            try:
                account_rex_list = []
                if type_owner == 0:
                    for typeowner in range(1, 6):
                        add_account_rex(typeowner)
                else:
                    add_account_rex(type_owner)
                return "|".join(account_rex_list)
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

    @property
    def reference(self):
        return _("Situation of '%s'") % self.third

    @classmethod
    def throw_not_allowed(cls):
        if hasattr(settings, "DIACAMMA_MAXOWNER") and (len(cls.objects.all()) > getattr(settings, "DIACAMMA_MAXOWNER")):
            raise LucteriosException(IMPORTANT, _("You have too many owners declared!"))

    @classmethod
    def get_default_fields(cls):
        fields = ["third", 'property_part', 'thirdinitial', 'total_all_call', 'total_payoff', 'thirdtotal', 'sumtopay']
        return fields

    @classmethod
    def get_show_fields_in_third(cls):
        return ['total_current_initial', 'total_current_call', 'total_current_owner']

    @classmethod
    def get_edit_fields(cls):
        return []

    @classmethod
    def get_search_fields(cls):
        result = []
        for field_name in Third.get_search_fields():
            result.append(cls.convert_field_for_search('third', field_name))
        return result

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
                  _("004@Accounting"): ['thirdinitial', 'entryline_set', 'thirdtotal', 'sumtopay'],
                  _("005@Situation"): [('partition_set',),
                                       'total_current_initial',
                                       ('total_current_call', 'total_current_payoff'),
                                       'total_current_owner',
                                       ('total_current_ventilated', 'total_current_regularization'),
                                       ('total_recoverable_load', 'total_extra'),
                                       ],
                  _("006@Exceptional"): ['exceptionnal_set',
                                         'total_exceptional_initial',
                                         ('total_exceptional_call', 'total_exceptional_payoff'),
                                         'total_exceptional_owner'],
                  _("007@Funds"): [('total_cash_advance_call', 'total_cash_advance_payoff'),
                                   ('total_fund_works_call', 'total_fund_works_payoff')
                                   ],
                  _("008@callfunds"): ['callfunds_set', 'payoff_set'],
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
        fields.extend(['thirdinitial', 'entryline_set', 'thirdtotal', 'sumtopay'])
        fields.extend(['ownercontact_set'])
        fields.extend(['propertylot_set.num', 'propertylot_set.value', 'propertylot_set.ratio', 'propertylot_set.description'])
        fields.extend(["callfunds_set.num", "callfunds_set.date",
                       "callfunds_set.comment", 'callfunds_set.total'])
        fields.extend(["partition_set.set.str", "partition_set.set.budget_txt", 'partition_set.set.sumexpense',
                       "partition_set.value", 'partition_set.ratio', 'partition_set.ventilated'])
        fields.extend(["exceptionnal_set.set.str", "exceptionnal_set.set.budget_txt", 'exceptionnal_set.set.sumexpense',
                       'exceptionnal_set.total_callfunds',
                       "exceptionnal_set.value", 'exceptionnal_set.ratio', 'exceptionnal_set.ventilated'])
        fields.extend(['payoff_set'])
        fields.extend(['total_current_call', 'total_current_payoff',
                       'total_current_initial', 'total_current_ventilated',
                       'total_current_regularization', 'total_extra',
                       'total_current_owner'])
        fields.extend(['total_exceptional_initial',
                       'total_exceptional_call',
                       'total_exceptional_payoff',
                       'total_exceptional_owner'])
        fields.extend(['total_cash_advance_call',
                       'total_cash_advance_payoff',
                       'total_fund_works_call',
                       'total_fund_works_payoff'])

        return fields

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = self.id is None
        Supporting.save(self, force_insert=force_insert,
                        force_update=force_update, using=using, update_fields=update_fields)
        if is_new:
            for setitem in Set.objects.all():
                Partition.objects.create(set=setitem, owner=self)

    def get_third_initial(self):
        if self.id is None:
            return None
        if self.date_begin is None:
            self.set_dates()
        third_total = get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value__lt=self.date_begin)).aggregate(Sum('amount')))
        third_total -= get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value=self.date_begin) & Q(entry__journal__id=1)).aggregate(Sum('amount')))
        return third_total

    def check_initial_operation(self):
        if FiscalYear.get_current().status != 2:
            self.date_begin = FiscalYear.get_current().begin
            entries_init = EntryAccount.objects.filter(Q(entrylineaccount__third=self.third) & Q(date_value=self.date_begin) & Q(journal__id=1)).distinct()
            if len(entries_init) > 0:
                third_initial = self.get_third_initial()
                if (third_initial > 0.0001) and (len(Payoff.objects.filter((Q(supporting=self) | Q(supporting__callfundssupporting__third=self.third)) & Q(entry=entries_init[0]))) == 0):
                    init_paypoff = Payoff(supporting=self, date=self.date_begin, payer=six.text_type(self.third), mode=4,
                                          reference=_('Last year report'), bank_fee=0)
                    init_paypoff.amount = third_initial
                    init_paypoff.entry = entries_init[0]
                    init_paypoff.save(do_generate=False)
                elif (third_initial < 0.0001) and (len(CallDetail.objects.filter(callfunds__owner=self, entry=entries_init[0])) == 0):
                    init_call = CallFunds(owner=self, num=None, date=self.date_begin, comment=_('Last year report'), status=2, supporting=CallFundsSupporting.objects.create(third=self.third))
                    init_call.save()
                    init_detail = CallDetail(callfunds=init_call, set=None, designation=_('Last year report'), type_call=0)
                    init_detail.price = abs(third_initial)
                    init_detail.entry = entries_init[0]
                    init_detail.save()

    def check_ventilate_payoff(self):
        # move payoff in owner general list
        support_query = Q(third=self.third) & Q(callfundssupporting__callfunds__date__gte=self.date_begin)
        support_query &= Q(callfundssupporting__callfunds__date__lte=self.date_end) & Q(payoff__entry__close=False)
        callfunds_supportings = Supporting.objects.filter(support_query).distinct()
        export_payoff_filter = Q(supporting__in=callfunds_supportings) & Q(entry__close=False)
        export_payoff_list = Payoff.objects.filter(export_payoff_filter).values('entry_id', 'mode',
                                                                                'payer', 'reference',
                                                                                'bank_account_id', 'date').annotate(amount=Sum('amount'), bank_fee=Sum('bank_fee'))
        supportings = [six.text_type(self.id)]
        for export_payoff in export_payoff_list:
            entry = EntryAccount.objects.get(id=export_payoff['entry_id'])
            amount = get_amount_sum(entry.entrylineaccount_set.filter(account__code__regex=current_system_account().get_cash_mask()).aggregate(Sum('amount')))
            Payoff.multi_save(supportings=supportings, amount=abs(amount),
                              mode=export_payoff['mode'], payer=export_payoff['payer'],
                              reference=export_payoff['reference'],
                              bank_account=export_payoff['bank_account_id'] if export_payoff['bank_account_id'] is not None else 0,
                              date=export_payoff['date'], bank_fee=export_payoff['bank_fee'], repartition=1)
            entry.delete()
        # move payoff from general to call of funds
        for call_fund in self.callfunds_set.filter(date__gte=self.date_begin, date__lte=self.date_end):
            if call_fund.supporting.get_total_rest_topay() > 0.0001:
                supportings.append(six.text_type(call_fund.supporting_id))
        payoffs_filter = Q(date__gte=self.date_begin) & Q(date__lte=self.date_end) & (Q(entry__close=False) | (Q(entry__entrylineaccount__third=self.third) & Q(entry__date_value=FiscalYear.get_current().begin) & Q(entry__journal__id=1)))
        payoffs = self.payoff_set.filter(payoffs_filter).distinct().order_by('date')
        for payoff in payoffs:
            Payoff.multi_save(supportings=supportings, amount=payoff.amount, mode=payoff.mode,
                              payer=payoff.payer, reference=payoff.reference,
                              bank_account=payoff.bank_account_id if payoff.bank_account_id is not None else 0,
                              date=payoff.date, bank_fee=payoff.bank_fee, repartition=1,
                              entry=payoff.entry if (payoff.entry_id is not None) and payoff.entry.close else None)
            if payoff.entry.close:
                payoff.entry = None
                payoff.save(do_generate=False)
            payoff.delete()

    @property
    def entryline_set(self):
        if self.date_begin is None:
            self.set_dates()
        query = Q(third=self.third)
        query &= Q(account__code__regex=self.get_third_mask(0))
        query &= Q(entry__date_value__gte=self.date_begin)
        query &= Q(entry__date_value__lte=self.date_end)
        query &= ~Q(entry__journal__id=1)
        return OwnerEntryLineAccount.objects.filter(query).distinct()

    @property
    def loadcount_set(self):
        if self.date_begin is None:
            self.set_dates()
        return LoadCountSet(hints={'owner': self})

    def get_thirdtotal(self):
        if self.id is None:
            return None
        if self.date_begin is None:
            self.set_dates()
        return self.third.get_total(self.date_end)

    def get_sumtopay(self):
        if self.id is None:
            return None
        if self.date_begin is None:
            self.set_dates()
        return max(0, -1 * self.third.get_total(self.date_end))

    def get_total_payoff_calculated(self):
        if self.id is None:
            return None
        if self.date_begin is None:
            self.set_dates()
        entry_query = Q(third=self.third) & Q(entry__date_value__gte=self.date_begin)
        entry_query &= Q(entry__date_value__lte=self.date_end) & Q(amount__lt=0)
        third_total = -1 * get_amount_sum(EntryLineAccount.objects.filter(entry_query).aggregate(Sum('amount')))
        third_total += get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(entry__date_value=self.date_begin) & Q(entry__journal__id=1) & Q(amount__lt=0)).aggregate(Sum('amount')))
        return third_total

    @property
    def exceptionnal_set(self):
        return PartitionExceptional.objects.filter(Q(owner=self) & Q(set__is_active=True) & Q(set__type_load=1)).distinct()

    @property
    def partition_query(self):
        return Q(set__is_active=True) & Q(set__type_load=0) & Q(value__gt=0)

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
        if self.id is None:
            return None
        total_part = PropertyLot.get_total_part()
        if total_part > 0:
            total = self.propertylot_set.aggregate(sum=Sum('value'))
            if ('sum' in total.keys()) and (total['sum'] is not None):
                value = total['sum']
            else:
                value = 0
            return (value, total_part, 100.0 * float(value) / float(total_part))
        else:
            return (None, None, None)

    def get_current_date(self):
        return date(2100, 12, 31)

    def get_total_call(self, type_call=0):
        if self.id is None:
            return None
        val = 0
        if type_call < 0:
            totalfilter = Q()
        else:
            totalfilter = Q(calldetail__type_call=type_call) & Q(calldetail__set__isnull=False)
        for callfunds in self.callfunds_set.filter(self.callfunds_query & totalfilter).distinct():
            if type_call < 0:
                val += currency_round(callfunds.get_total())
            else:
                for calldetail in callfunds.calldetail_set.filter(type_call=type_call, set__isnull=False):
                    val += currency_round(calldetail.price)
        return val

    def get_total_payed(self, ignore_payoff=-1, type_call=0):
        val = Supporting.get_total_payed(self, ignore_payoff=ignore_payoff)
        if type_call < 0:
            totalfilter = Q()
        else:
            totalfilter = Q(calldetail__type_call=type_call)
        for callfunds in self.callfunds_set.filter(self.callfunds_query & totalfilter).distinct():
            callfunds.check_supporting()
            total_payed = callfunds.supporting.get_total_payed(ignore_payoff)
            if type_call < 0:
                val += currency_round(total_payed)
            else:
                total = callfunds.get_total()
                for calldetail in callfunds.calldetail_set.filter(type_call=type_call):
                    val += currency_round(float(calldetail.price) * total_payed / total)
        return val

    def get_total_initial(self, owner_type=1):
        if self.id is None:
            return None
        if self.date_begin is None:
            self.set_dates()
        entry_query = Q(third=self.third) & Q(entry__date_value__lt=self.date_begin)
        entry_query &= Q(account__code__regex=self.get_third_mask(owner_type))
        third_total = get_amount_sum(EntryLineAccount.objects.filter(entry_query).aggregate(Sum('amount')))

        entry_query = Q(third=self.third) & Q(entry__date_value=self.date_begin)
        entry_query &= Q(entry__journal__id=1) & Q(account__code__regex=self.get_third_mask(owner_type))
        third_total -= get_amount_sum(EntryLineAccount.objects.filter(entry_query).aggregate(Sum('amount')))
        return third_total

    def get_total_payoff(self, owner_type=1):
        if self.id is None:
            return None
        if self.date_begin is None:
            self.set_dates()
        entry_query = Q(third=self.third) & Q(entry__date_value__gte=self.date_begin)
        entry_query &= Q(entry__date_value__lte=self.date_end) & Q(entry__journal__id=4)
        entry_query &= Q(account__code__regex=self.get_third_mask(owner_type))
        third_total = -1 * get_amount_sum(EntryLineAccount.objects.filter(entry_query).aggregate(Sum('amount')))
        return third_total

    def get_total(self):
        if self.id is None:
            return None
        return self.get_total_call() - self.get_total_initial()

    def get_total_current_ventilated(self):
        if self.id is None:
            return None
        value = 0.0
        for part in self.partition_set.filter(self.partition_query):
            part.set.set_dates(self.date_begin, self.date_end)
            value += part.get_ventilated()
        return value

    def get_total_recoverable_load(self):
        if self.id is None:
            return None
        value = 0.0
        for part in self.partition_set.filter(self.partition_query):
            part.set.set_dates(self.date_begin, self.date_end)
            value += part.get_recovery_load()
        return value

    def get_total_extra(self):
        if self.id is None:
            return None
        value, total_part, _ratio = self.get_property_part()
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

    def get_total_current_payoff(self):
        if Params.getvalue("condominium-old-accounting"):
            return self.get_total_payed()
        else:
            return self.get_total_payoff(1)

    def get_total_current_owner(self):
        if self.date_begin is None:
            self.set_dates()
        entry_query = Q(third=self.third) & Q(entry__date_value__lte=self.date_end)
        entry_query &= Q(account__code__regex=self.get_third_mask(1))
        third_total = get_amount_sum(EntryLineAccount.objects.filter(entry_query).aggregate(Sum('amount')))
        return -1 * third_total

    def get_total_current_regularization(self):
        if self.id is None:
            return None
        return self.get_total_call() - self.get_total_current_ventilated()

    def get_total_exceptional_owner(self):
        if self.id is None:
            return None
        if self.date_begin is None:
            self.set_dates()
        entry_query = Q(third=self.third) & Q(entry__date_value__lte=self.date_end)
        entry_query &= Q(account__code__regex=self.get_third_mask(2))
        third_total = get_amount_sum(EntryLineAccount.objects.filter(entry_query).aggregate(Sum('amount')))
        return -1 * third_total

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
        return -1 * Supporting.get_total_payed(self)

    def payoff_have_payment(self):
        return (Supporting.get_total_rest_topay(self) > 0.001)

    @classmethod
    def get_payment_fields(cls):
        return ["third", "information", 'callfunds_set', 'total_current_owner']

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
    set = models.ForeignKey(Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)
    value = LucteriosDecimalField(_('tantime'), max_digits=7, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100000.00)], format_string="N2")

    ratio = LucteriosVirtualField(verbose_name=_("ratio"), compute_from='get_ratio', format_string='N1;{0} %')
    ventilated = LucteriosVirtualField(verbose_name=_('ventilated'), compute_from='get_ventilated', format_string=lambda: format_with_devise(5))
    recovery_load = LucteriosVirtualField(verbose_name=_('recoverable load'), compute_from='get_recovery_load', format_string=lambda: format_with_devise(5))

    total_callfunds = LucteriosVirtualField(verbose_name=_("total call for funds"), compute_from='get_callfunds', format_string=lambda: format_with_devise(5))
    total_current_regularization = LucteriosVirtualField(verbose_name=_('estimated regularization'), compute_from='get_total_current_regularization', format_string=lambda: format_with_devise(5))

    # for legacy
    ventilated_txt = LucteriosVirtualField(verbose_name=_('ventilated'), compute_from='get_ventilated', format_string=lambda: format_with_devise(5))
    recovery_load_txt = LucteriosVirtualField(verbose_name=_('recoverable load'), compute_from='get_recovery_load', format_string=lambda: format_with_devise(5))

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.ventilated_value = 0.0
        self.recovery_load_value = 0.0

    def __str__(self):
        return "%s : %s" % (self.owner, format_to_string(self.ratio, 'N1', '{0} %'))

    @classmethod
    def get_default_fields(cls):
        return ["set", "set.budget_txt", 'set.sumexpense', "owner", "value", 'ratio', 'ventilated', 'recovery_load']

    @classmethod
    def get_edit_fields(cls):
        return ["set", "owner", "value"]

    def get_ratio(self):
        if self.id is None:
            return 0.0
        total = self.set.total_part
        if abs(total) < 0.01:
            return 0.0
        else:
            return float(100 * float(self.value) / float(total))

    def set_context(self, xfer):
        if xfer is not None:
            self.set.set_dates(xfer.getparam("begin_date"), xfer.getparam("end_date"))

    def compute_values(self):
        self.ventilated_value = 0.0
        self.recovery_load_value = 0.0
        ratio = self.get_ratio()
        if abs(ratio) > 0.01:
            try:
                year = FiscalYear.objects.get(begin__lte=self.set.date_end, end__gte=self.set.date_end)
            except (ObjectDoesNotExist, ValueError):
                year = FiscalYear.get_current()
                if (year is None) or (self.set is None) or (self.set.date_end is None) or (self.set.date_end < year.begin):
                    return 0
            recovery_load_result = 0
            self.ventilated_result = 0
            for entry in EntryLineAccount.objects.filter(Q(account__type_of_account=4) & (Q(entry__year=year) | Q(entry__year__isnull=True)) & Q(costaccounting__setcost__set=self.set)).distinct():
                recovery_load_ratio = RecoverableLoadRatio.objects.filter(code=entry.account.code)
                self.ventilated_result += float(entry.amount)
                if len(recovery_load_ratio) > 0:
                    load_ratio = recovery_load_ratio[0].ratio
                    recovery_load_result += float(entry.amount) * float(load_ratio) / 100.0
            self.ventilated_value = self.ventilated_result * ratio / 100.0
            self.recovery_load_value = recovery_load_result * ratio / 100.0

    def get_ventilated(self):
        if self.id is None:
            return None
        self.compute_values()
        return self.ventilated_value

    def get_recovery_load(self):
        if self.id is None:
            return None
        self.compute_values()
        return self.recovery_load_value

    def get_callfunds(self):
        if (self.id is None) or (self.set is None) or (self.set.date_begin is None) or (self.set.date_end is None):
            return 0
        value = 0
        ratio = self.get_ratio()
        if abs(ratio) > 0.01:
            for calldetail in CallDetail.objects.filter(callfunds__owner=self.owner, set=self.set, callfunds__date__gte=self.set.date_begin, callfunds__date__lte=self.set.date_end).distinct():
                value += currency_round(calldetail.price)
        return value

    def get_total_current_regularization(self):
        if self.id is None:
            return None
        return currency_round(self.get_callfunds() - self.get_ventilated())

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


class RecoverableLoadRatio(LucteriosModel):
    code = models.CharField(_('account'), max_length=50)
    ratio = models.DecimalField(_('ratio'), max_digits=4, decimal_places=0, default=100, validators=[MinValueValidator(1.0), MaxValueValidator(100.0)])

    code_txt = LucteriosVirtualField(verbose_name=_('account'), compute_from="get_code")

    def __str__(self):
        return self.code

    @classmethod
    def get_default_fields(cls):
        return ["code_txt", "ratio"]

    @classmethod
    def get_edit_fields(cls):
        return ["code", "ratio"]

    def get_code(self):
        chart = ChartsAccount.get_chart_account(self.code)
        return six.text_type(chart)

    class Meta(object):
        verbose_name = _('recoverable load ratio')
        verbose_name_plural = _('recoverable load ratios')
        default_permissions = []
        ordering = ["code"]


class PartitionExceptional(Partition):
    @classmethod
    def get_default_fields(cls):
        return ["set", 'ratio', 'total_callfunds', 'ventilated', 'total_current_regularization']

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
    owner = models.ForeignKey(Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)

    ratio = LucteriosVirtualField(verbose_name=_("ratio"), compute_from='get_ratio', format_string='N1;{0} %')

    def __str__(self):
        return "[%s] %s" % (self.num, self.description)

    @classmethod
    def get_default_fields(cls):
        return ["num", "value", 'ratio', "description", "owner"]

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

    @property
    def reference(self):
        try:
            return self.callfunds.reference
        except Exception:
            return ""

    def get_total(self):
        try:
            return self.callfunds.get_total()
        except Exception:
            return 0

    def get_third_mask(self, type_owner=1):
        try:
            third_mask = self.callfunds.owner.get_third_mask(type_owner)
            return third_mask
        except Exception:
            return ""

    def get_third_masks_by_amount(self, amount):
        try:
            masks = {}
            total = self.callfunds.get_total()
            for calldetail in self.callfunds.calldetail_set.all():
                mask = self.get_third_mask(type_owner=calldetail.type_call + 1)
                if mask not in masks:
                    masks[mask] = 0
                masks[mask] += float(calldetail.price) * amount / total
            return masks.items()
        except Exception:
            return []

    def payoff_is_revenu(self):
        return True

    @classmethod
    def get_long_name(cls):
        return CallFunds.get_long_name()

    @classmethod
    def get_payment_fields(cls):
        return ["callfunds.num", "callfunds.date", "callfunds.comment", "third", 'callfunds.total']

    def support_validated(self, validate_date):
        return self

    def get_current_date(self):
        try:
            return self.callfunds.date
        except Exception:
            return None

    def get_tax(self):
        return 0

    def get_payable_without_tax(self):
        return self.get_total_rest_topay()

    def payoff_have_payment(self):
        try:
            return (self.callfunds.status == 1) and (self.get_total_rest_topay() > 0.001)
        except Exception:
            return False

    def get_send_email_objects(self):
        try:
            return [self.callfunds]
        except Exception:
            return []

    class Meta(object):
        default_permissions = []


class CallFunds(LucteriosModel):
    owner = models.ForeignKey(Owner, verbose_name=_('owner'), null=True, db_index=True, on_delete=models.PROTECT)
    supporting = models.OneToOneField(CallFundsSupporting, on_delete=models.CASCADE, default=None, null=True)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    comment = models.TextField(_('comment'), null=True, default="")
    type_call = models.IntegerField(verbose_name=_('type of call'), choices=(), null=True, default=None, db_index=True)
    status = FSMIntegerField(verbose_name=_('status'),
                             choices=((0, _('building')), (1, _('valid')), (2, _('ended'))), null=False, default=0, db_index=True)

    total = LucteriosVirtualField(verbose_name=_('total'), compute_from='get_total', format_string=lambda: format_with_devise(5))

    def __str__(self):
        if self.num is not None:
            return _('call of funds #%(num)d - %(date)s') % {'num': self.num, 'date': get_date_formating(self.date)}
        else:
            return _('call of funds "last year report" - %(date)s') % {'date': get_date_formating(self.date)}

    @property
    def reference(self):
        if self.num is not None:
            return _('call of funds #%(num)d') % {'num': self.num}
        else:
            return _('call of funds')

    @classmethod
    def get_default_fields(cls):
        return ["num", "date", "owner", "comment", 'total', 'supporting.total_rest_topay']

    @classmethod
    def get_edit_fields(cls):
        return ["status", "date", "comment"]

    @classmethod
    def get_show_fields(cls):
        return [("num", "date"), "owner", "calldetail_set", "comment", ("status", 'total')]

    @classmethod
    def get_search_fields(cls):
        return []

    def __getattr__(self, name):
        if hasattr(self.supporting, name):
            return getattr(self.supporting, name)
        raise AttributeError(name)

    def __call__(self, *args, **kwargs):
        return self.supporting.__call__(*args, **kwargs)

    def get_total(self):
        self.check_supporting()
        val = 0
        for calldetail in self.calldetail_set.all():
            val += currency_round(calldetail.price)
        return val

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
            calls_by_owner[owner.id] = CallFunds.objects.create(num=new_num, date=self.date, owner=owner, comment=self.comment,
                                                                status=1, supporting=CallFundsSupporting.objects.create(third=owner.third))
            last_call = calls_by_owner[owner.id]
        for calldetail in self.calldetail_set.all():
            amount = float(calldetail.price)
            new_detail = None
            for part in calldetail.set.partition_set.all().order_by('value'):
                if part.value > 0.001:
                    new_detail = CallDetail.objects.create(type_call=calldetail.type_call,
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
        is_modify = False
        if self.owner is not None:
            try:
                support = self.supporting
            except ObjectDoesNotExist:
                support = None
            if support is None:
                self.supporting = CallFundsSupporting.objects.create(third=self.owner.third)
                is_modify = True
        if self.type_call is not None:
            for detail in self.calldetail_set.all():
                detail.type_call = self.type_call
                detail.save()
            self.type_call = None
            is_modify = True
        if is_modify:
            self.save()

    def payoff_have_payment(self):
        if (self.supporting is not None):
            return self.supporting.payoff_have_payment()
        else:
            return False

    class Meta(object):
        verbose_name = _('call of funds')
        verbose_name_plural = _('calls of funds')
        ordering = ['date', 'num']


class CallDetail(LucteriosModel):
    callfunds = models.ForeignKey(CallFunds, verbose_name=_('call of funds'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, verbose_name=_('set'), null=True, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    price = LucteriosDecimalField(verbose_name=_('amount'), max_digits=10, decimal_places=3, default=0.0,
                                  validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    entry = models.ForeignKey(EntryAccount, verbose_name=_('entry'), null=True, on_delete=models.PROTECT)
    type_call = models.IntegerField(verbose_name=_('type of call'),
                                    choices=((0, _('current')), (1, _('exceptional')), (2, _('cash advance')), (3, _('borrowing')), (4, _('fund for works'))), null=False, default=0, db_index=True)

    type_call_ex = LucteriosVirtualField(verbose_name=_('type of call'), compute_from='get_type_call_ex')
    total_amount = LucteriosVirtualField(verbose_name=_('total'), compute_from='get_total_amount', format_string=lambda: format_with_devise(5))
    owner_part = LucteriosVirtualField(verbose_name=_('tantime'), compute_from='get_owner_part', format_string='N2')
    price_txt = LucteriosVirtualField(verbose_name=_('amount'), compute_from='price', format_string=lambda: format_with_devise(5))

    def __str__(self):
        return "%s - %s" % (self.callfunds, self.designation)

    def get_auditlog_object(self):
        if self.callfunds is None:
            raise CallFunds.DoesNotExist("")
        return self.callfunds

    @classmethod
    def get_default_fields(cls):
        return ['type_call_ex', "set", "designation", 'total_amount', 'set.total_part', 'owner_part', 'price']

    @classmethod
    def get_edit_fields(cls):
        return ['type_call', "set", "designation", "price"]

    def get_type_call_ex(self):
        if self.id is None:
            return None
        result = "#%d" % self.type_call
        for callfunds_id, callfunds_title in current_system_condo().get_callfunds_list():
            if callfunds_id == self.type_call:
                result = callfunds_title
                break
        return result

    def get_total_amount(self):
        if self.id is None:
            return None
        totamount = 0
        num = -1
        index = 0
        for det in self.callfunds.calldetail_set.filter(set=self.set):
            if det.id == self.id:
                num = index
            index += 1
        if num >= 0:
            for fund in CallFunds.objects.filter(date=self.callfunds.date, num=self.callfunds.num):
                details = fund.calldetail_set.filter(set=self.set)
                if len(details) > num:
                    det = details[num]
                    totamount += float(det.price)
        return totamount

    def get_owner_part(self):
        if self.id is None:
            return None
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

    total = LucteriosVirtualField(verbose_name=_('total'), compute_from='get_total', format_string=lambda: format_with_devise(5))

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
            fields.append(Supporting.get_payoff_fields()[-1])
        return fields

    def get_third_mask(self):
        return current_system_account().get_provider_mask()

    @classmethod
    def get_edit_fields(cls):
        return ["status", 'expensetype', "date", "comment"]

    @classmethod
    def get_show_fields(cls):
        return ["third", ("num", "date"), "expensetype", "expensedetail_set", "comment", ("status", 'total')]

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

    @transition(field=status, source=0, target=1, conditions=[lambda item:item.get_info_state() == []])
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
            info = Supporting.get_info_state(self, current_system_account().get_provider_mask())
        info.extend(self.check_date(self.date.isoformat()))
        return info

    class Meta(object):
        verbose_name = _('expense')
        verbose_name_plural = _('expenses')
        ordering = ['-date']


class ExpenseDetail(LucteriosModel):
    expense = models.ForeignKey(Expense, verbose_name=_('expense'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    expense_account = models.CharField(verbose_name=_('account'), max_length=50)
    price = LucteriosDecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3, default=0.0,
                                  validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)], format_string=lambda: format_with_devise(5))
    entry = models.ForeignKey(EntryAccount, verbose_name=_('entry'), null=True, on_delete=models.PROTECT)

    ratio_txt = LucteriosVirtualField(verbose_name=_('ratio'), compute_from='get_ratio', format_string="N1;{0} %")

    # for legacy
    price_txt = LucteriosVirtualField(verbose_name=_('price'), compute_from=lambda item: item.price, format_string=lambda: format_with_devise(5))

    def __str__(self):
        return "%s: %s" % (self.expense, self.designation)

    def get_auditlog_object(self):
        return self.expense

    @classmethod
    def get_default_fields(cls):
        return ["set", "designation", "expense_account", 'price', 'ratio_txt']

    @classmethod
    def get_edit_fields(cls):
        return ["set", "designation", "expense_account", "price"]

    def get_ratio(self):
        ratio = []
        if self.expense.status == 0:
            for part in self.set.partition_set.exclude(value=0.0):
                ratio.append({'value': part.ratio, 'format': "%s : {0}" % part.owner})
        else:
            for part in self.expenseratio_set.all():
                ratio.append({'value': part.ratio, 'format': "%s : {0}" % part.owner})
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
    expensedetail = models.ForeignKey(ExpenseDetail, verbose_name=_('detail of expense'), null=False, db_index=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)
    value = LucteriosDecimalField(_('value'), max_digits=7, decimal_places=2, default=0.0,
                                  validators=[MinValueValidator(0.0), MaxValueValidator(1000.00)], format_string="N2")

    @property
    def ratio(self):
        return 100.0 * float(abs(self.value)) / float(self.expensedetail.price)

    def __str__(self):
        return "%s : %s" % (six.text_type(self.owner.third), format_to_string(self.ratio, "N2", "{0} %"))

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
        for call_detail in call_funds.calldetail_set.all():
            if call_detail.set.type_load == 1:
                call_funds.type_call = 1
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


def migrate_budget():
    set_list = Set.objects.filter(is_active=True)
    for setitem in set_list:
        setitem.rename_all_cost_accounting()
        if len(setitem.current_cost_accounting.budget_set.all()) == 0:
            setitem.convert_budget()
    for budget_item in Budget.objects.filter(year__isnull=True):
        budget_item.year = FiscalYear.get_current()
        budget_item.save()


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
    Parameter.check_and_create(name='condominium-advance-revenue-account', typeparam=0, title=_("condominium-fundforworks-revenue-account"),
                               args="{'Multi':False}", value=correct_accounting_code('705'), meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
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
    migrate_budget()
    Set.correct_costaccounting()


@Signal.decorate('auditlog_register')
def condominium_auditlog_register():
    auditlog.register(OwnerLink)
    auditlog.register(OwnerContact)
    auditlog.register(RecoverableLoadRatio, include_fields=['ratio', 'code_txt'])
    auditlog.register(Set, include_fields=["name", "type_load", 'is_link_to_lots'])
    auditlog.register(Owner, include_fields=["third", "information"])
    auditlog.register(Partition, include_fields=["set", "owner", "value"])
    auditlog.register(PropertyLot, include_fields=["num", "value", "description", "owner"])
    auditlog.register(CallFunds, include_fields=["num", "date", "owner", "comment", "status"])
    auditlog.register(CallDetail, include_fields=['type_call_ex', "set", "designation", 'price'])
    auditlog.register(Expense, include_fields=["third", "num", "date", "expensetype", "comment", "status"])
    auditlog.register(ExpenseDetail, include_fields=["set", "designation", "expense_account", "price"])
