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
from datetime import date, datetime

from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Sum, Max
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils import six, formats

from lucterios.framework.models import LucteriosModel, get_value_converted
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.tools import convert_date

from diacamma.accounting.models import CostAccounting, EntryAccount, Journal,\
    ChartsAccount, EntryLineAccount, FiscalYear
from diacamma.accounting.tools import format_devise, currency_round,\
    current_system_account, get_amount_sum, correct_accounting_code
from diacamma.payoff.models import Supporting


class Set(LucteriosModel):
    name = models.CharField(_('name'), max_length=100)
    budget = models.DecimalField(_('budget'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    revenue_account = models.CharField(_('revenue account'), max_length=50)
    cost_accounting = models.ForeignKey(
        CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

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
        if self.date_end < self.date_begin:
            self.date_end = self.date_begin

    def set_context(self, xfer):
        if xfer is not None:
            self.set_dates(convert_date(xfer.getparam("begin_date")), convert_date(
                xfer.getparam("end_date")))

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ["name", (_('budget'), "budget_txt"), "revenue_account", 'cost_accounting', 'partition_set', (_('expense'), 'sumexpense_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "budget", "revenue_account", 'cost_accounting']

    @classmethod
    def get_show_fields(cls):
        return [("name", (_('budget'), "budget_txt")), ("revenue_account", 'cost_accounting'), 'partition_set', ((_('partition sum'), 'total_part'), (_('expense'), 'sumexpense_txt'))]

    def _do_insert(self, manager, using, fields, update_pk, raw):
        new_id = LucteriosModel._do_insert(
            self, manager, using, fields, update_pk, raw)
        for owner in Owner.objects.all():
            Partition.objects.create(set_id=new_id, owner=owner)
        return new_id

    @property
    def budget_txt(self):
        return format_devise(self.budget, 5)

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
        total = self.get_expenselist().aggregate(sum=Sum('price'))
        if 'sum' in total.keys():
            return total['sum']
        else:
            return 0

    @property
    def sumexpense_txt(self):
        return format_devise(self.get_sumexpense(), 5)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.revenue_account = correct_accounting_code(self.revenue_account)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('set')
        verbose_name_plural = _('sets')


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
        if self.date_end < self.date_begin:
            self.date_end = self.date_begin
        if isinstance(self.date_begin, six.text_type):
            self.date_begin = convert_date(self.date_begin)
        if isinstance(self.date_end, six.text_type):
            self.date_end = convert_date(self.date_end)

    def set_context(self, xfer):
        if xfer is not None:
            self.set_dates(convert_date(xfer.getparam("begin_date")), convert_date(
                xfer.getparam("end_date")))

    def get_third_mask(self):
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
    def get_default_fields(cls):
        return ["third", (_('total call for funds'), 'total_call'), (_('total estimate'), 'total_estimate'), (_('initial state'), 'total_initial'), (_('total payoff'), 'total_payed'), (_('total ventilated'), 'total_ventilated'), (_('total real'), 'total_real')]

    @classmethod
    def get_edit_fields(cls):
        return ["third", "information"]

    @classmethod
    def get_show_fields(cls):
        return ["third", "information", 'callfunds_set', ((_('total call for funds'), 'total_call'), (_('total estimate'), 'total_estimate')), 'partition_set', ((_('initial state'), 'total_initial'), (_('total ventilated'), 'total_ventilated')), ((_('total real'), 'total_real'),)]

    @classmethod
    def get_print_fields(cls):
        fields = ["third"]
        fields.extend(["callfunds_set.num", "callfunds_set.date",
                       "callfunds_set.comment", (_('total'), 'callfunds_set.total')])
        fields.extend(["partition_set.set.str", "partition_set.set.budget", (_('expense'), 'partition_set.set.sumexpense_txt'),
                       "partition_set.value", (_("ratio"), 'partition_set.ratio'), (_('ventilated'), 'partition_set.ventilated_txt')])
        fields.extend(['payoff_set'])
        fields.extend([(_('total call for funds'), 'total_call'), (_('total estimate'), 'total_estimate'), (_('initial state'), 'total_initial'), (_(
            'total ventilated'), 'total_ventilated'), (_('total payed'), 'total_payed'), (_('total real'), 'total_real')])
        return fields

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = self.id is None
        Supporting.save(self, force_insert=force_insert,
                        force_update=force_update, using=using, update_fields=update_fields)
        if is_new:
            for setitem in Set.objects.all():
                Partition.objects.create(set=setitem, owner=self)

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

    def get_total_call(self):
        val = 0
        for callfunds in self.callfunds_set.filter(self.callfunds_query):
            val += currency_round(callfunds.get_total())
        return val

    @property
    def total_call(self):
        return format_devise(self.get_total_call(), 5)

    def get_total_initial(self):
        if self.date_begin is None:
            self.set_dates()
        third_total = self.third.get_total(self.date_begin, False)
        third_total -= get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(
            entry__date_value=self.date_begin) & Q(entry__journal__id=1) & Q(account__type_of_account=0)).aggregate(Sum('amount')))
        third_total += get_amount_sum(EntryLineAccount.objects.filter(Q(third=self.third) & Q(
            entry__date_value=self.date_begin) & Q(entry__journal__id=1) & Q(account__type_of_account=1)).aggregate(Sum('amount')))
        return third_total

    @property
    def total_initial(self):
        return format_devise(self.get_total_initial(), 5)

    @property
    def total_estimate(self):
        return format_devise(-1 * self.get_total_rest_topay(), 5)

    def get_total(self):
        return self.get_total_call() - self.get_total_initial()

    def get_total_ventilated(self):
        return self.get_total_payed() + self.get_total_initial() - self.third.get_total(self.date_end)

    @property
    def total_ventilated(self):
        return format_devise(self.get_total_ventilated(), 5)

    @property
    def total_real(self):
        return format_devise(self.third.get_total(self.date_end), 5)

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
        return currency_round(max(0, self.get_total_rest_topay()))

    def payoff_have_payment(self):
        return (self.get_total_rest_topay() > 0.001)

    @classmethod
    def get_payment_fields(cls):
        return ["third", "information", 'callfunds_set', ((_('total estimate'), 'total_estimate'),)]

    def get_payment_name(self):
        return _('codominium of %s') % six.text_type(self.third)

    def get_docname(self):
        return _('your situation')


class Partition(LucteriosModel):
    set = models.ForeignKey(
        Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        Owner, verbose_name=_('owner'), null=False, db_index=True, on_delete=models.CASCADE)
    value = models.DecimalField(_('value'), max_digits=7, decimal_places=2, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(1000.00)])

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
            self.set.set_dates(convert_date(xfer.getparam("begin_date")), convert_date(
                xfer.getparam("end_date")))

    def get_ventilated(self):
        value = 0
        ratio = self.get_ratio()
        if abs(ratio) > 0.01:
            for expensedetail in self.set.get_expenselist():
                if expensedetail.entry is None:
                    value += currency_round(float(expensedetail.price)
                                            * ratio / 100.00)
                else:
                    total = expensedetail.entry.entrylineaccount_set.filter(
                        third=self.owner.third).aggregate(sum=Sum('amount'))
                    if ('sum' in total.keys()) and (total['sum'] is not None):
                        value += currency_round(total['sum'])
        return value

    @property
    def ventilated_txt(self):
        return format_devise(self.get_ventilated(), 5)

    @property
    def ratio(self):
        return "%.1f %%" % self.get_ratio()

    class Meta(object):
        verbose_name = _('partition')
        verbose_name_plural = _('partitions')
        default_permissions = []


class CallFunds(LucteriosModel):
    owner = models.ForeignKey(
        Owner, verbose_name=_('owner'), null=True, db_index=True, on_delete=models.PROTECT)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    comment = models.TextField(_('comment'), null=True, default="")
    status = models.IntegerField(verbose_name=_('status'),
                                 choices=((0, _('building')), (1, _('valid')), (2, _('ended'))), null=False, default=0, db_index=True)

    def __str__(self):
        return _('call of funds #%(num)d - %(date)s') % {'num': self.num, 'date': get_value_converted(self.date)}

    @classmethod
    def get_default_fields(cls):
        return ["num", "date", "owner", "comment", (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ["status", "date", "comment"]

    @classmethod
    def get_show_fields(cls):
        return [("num", "date"), "owner", "calldetail_set", "comment", ("status", (_('total'), 'total'))]

    def get_total(self):
        val = 0
        for calldetail in self.calldetail_set.all():
            val += currency_round(calldetail.price)
        return val

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    def valid(self):
        if self.status == 0:
            val = CallFunds.objects.exclude(status=0).aggregate(Max('num'))
            if val['num__max'] is None:
                new_num = 1
            else:
                new_num = val['num__max'] + 1
            calls_by_owner = {}
            for owner in Owner.objects.all():
                calls_by_owner[owner.id] = CallFunds.objects.create(
                    num=new_num, date=self.date, owner=owner, comment=self.comment, status=1)
            for calldetail in self.calldetail_set.all():
                amount = float(calldetail.price)
                new_detail = None
                for part in calldetail.set.partition_set.all().order_by('value'):
                    if part.value > 0.001:
                        new_detail = CallDetail.objects.create(
                            set=calldetail.set, designation=calldetail.designation)
                        new_detail.callfunds = calls_by_owner[part.owner.id]
                        new_detail.price = currency_round(float(
                            calldetail.price) * part.get_ratio() / 100.0)
                        amount -= new_detail.price
                        new_detail.save()
                if abs(amount) > 0.0001:
                    new_detail.price += amount
                    new_detail.save()
            for new_call in calls_by_owner.values():
                if new_call.get_total() < 0.0001:
                    new_call.delete()
            self.delete()

    def can_delete(self):
        if self.status != 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    def close(self):
        if self.status == 1:
            self.status = 2
            self.save()

    class Meta(object):
        verbose_name = _('call of funds')
        verbose_name_plural = _('calls of funds')


class CallDetail(LucteriosModel):
    callfunds = models.ForeignKey(
        CallFunds, verbose_name=_('call of funds'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    set = models.ForeignKey(
        Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])

    @classmethod
    def get_default_fields(cls):
        return ["set", "designation", (_('price'), 'price_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["set", "designation", "price"]

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

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
    status = models.IntegerField(verbose_name=_('status'),
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

    def payoff_is_revenu(self):
        return self.expensetype == 1

    def default_date(self):
        return self.date

    def entry_links(self):
        if self.entries is None:
            return []
        else:
            return list(self.entries.all())

    def can_delete(self):
        if self.status != 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    def valid(self):
        if self.status == 0:
            if self.expensetype == 0:
                is_asset = 1
            else:
                is_asset = -1
            fiscal_year = FiscalYear.get_current()
            val = Expense.objects.exclude(status=0).aggregate(Max('num'))
            if val['num__max'] is None:
                self.num = 1
            else:
                self.num = val['num__max'] + 1
            self.generate_expense_entry(is_asset, fiscal_year)
            self.generate_revenue_entry(is_asset, fiscal_year)
            self.status = 1
            self.save()

    def generate_revenue_entry(self, is_asset, fiscal_year):
        for detail in self.expensedetail_set.all():
            detail.generate_revenue_entry(is_asset, fiscal_year)

    def generate_expense_entry(self, is_asset, fiscal_year):
        third_account = self.get_third_account(
            current_system_account().get_provider_mask(), fiscal_year)
        detail_sums = {}
        for detail in self.expensedetail_set.all():
            cost_accounting = detail.set.cost_accounting_id
            if cost_accounting == 0:
                cost_accounting = None
            if cost_accounting not in detail_sums.keys():
                detail_sums[cost_accounting] = {}
            detail_account = ChartsAccount.get_account(
                detail.expense_account, fiscal_year)
            if detail_account is None:
                raise LucteriosException(
                    IMPORTANT, _("code account %s unknown!") % detail.expense_account)
            if detail_account.id not in detail_sums[cost_accounting].keys():
                detail_sums[cost_accounting][detail_account.id] = 0
            detail_sums[cost_accounting][
                detail_account.id] += currency_round(detail.price)
        entries = []
        for cost_accounting, detail_sum in detail_sums.items():
            new_entry = EntryAccount.objects.create(
                year=fiscal_year, date_value=self.date, designation=self.__str__(),
                journal=Journal.objects.get(id=2), costaccounting_id=cost_accounting)
            total = 0
            for detail_accountid, price in detail_sum.items():
                EntryLineAccount.objects.create(
                    account_id=detail_accountid, amount=is_asset * price, entry=new_entry)
                total += price
            EntryLineAccount.objects.create(
                account=third_account, amount=is_asset * total, third=self.third, entry=new_entry)
            no_change, debit_rest, credit_rest = new_entry.serial_control(
                new_entry.get_serial())
            if not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
                raise LucteriosException(GRAVE, _("Error in accounting generator!") +
                                         "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest))
            entries.append(six.text_type(new_entry.id))
        self.entries = EntryAccount.objects.filter(id__in=entries)

    def close(self):
        if self.status == 1:
            if self.entries is not None:
                for entry in self.entries.all():
                    entry.closed()
            for detail in self.expensedetail_set.all():
                if detail.entry is not None:
                    detail.entry.closed()
            for payoff in self.payoff_set.all():
                if payoff.entry is not None:
                    payoff.entry.closed()
            self.status = 2
            self.save()

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
    expense = models.ForeignKey(
        Expense, verbose_name=_('expense'), null=True, default=None, db_index=True, on_delete=models.CASCADE)
    set = models.ForeignKey(
        Set, verbose_name=_('set'), null=False, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    expense_account = models.CharField(
        verbose_name=_('account'), max_length=50)
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    entry = models.ForeignKey(
        EntryAccount, verbose_name=_('entry'), null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "%s: %s" % (self.expense, self.designation)

    @classmethod
    def get_default_fields(cls):
        return ["set", "designation", "expense_account", (_('price'), 'price_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["set", "designation", "expense_account", "price"]

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

    def generate_revenue_entry(self, is_asset, fiscal_year):
        cost_accounting = self.set.cost_accounting_id
        if cost_accounting == 0:
            cost_accounting = None
        detail_account = ChartsAccount.get_account(
            self.set.revenue_account, fiscal_year)
        if detail_account is None:
            raise LucteriosException(
                IMPORTANT, _("code account %s unknown!") % self.set.revenue_account)
        price = currency_round(self.price)
        new_entry = EntryAccount.objects.create(
            year=fiscal_year, date_value=self.expense.date, designation=self.__str__(),
            journal=Journal.objects.get(id=3), costaccounting_id=cost_accounting)
        EntryLineAccount.objects.create(
            account=detail_account, amount=is_asset * price, entry=new_entry)
        last_line = None
        total = 0
        for part in Partition.objects.filter(set=self.set).order_by('value'):
            amount = currency_round(price * part.get_ratio() / 100.0)
            if amount > 0.0001:
                third_account = self.expense.get_third_account(
                    current_system_account().get_societary_mask(), fiscal_year, part.owner.third)
                last_line = EntryLineAccount.objects.create(
                    account=third_account, amount=is_asset * amount, entry=new_entry, third=part.owner.third)
                total += amount
        if (last_line is not None) and (abs(price - total) > 0.0001):
            last_line.amount += is_asset * (price - total)
            last_line.save()
        no_change, debit_rest, credit_rest = new_entry.serial_control(
            new_entry.get_serial())
        if not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
            raise LucteriosException(GRAVE, _("Error in accounting generator!") +
                                     "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest))
        self.entry = new_entry
        self.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.expense_account = correct_accounting_code(self.expense_account)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('detail of expense')
        verbose_name_plural = _('details of expense')
        default_permissions = []
