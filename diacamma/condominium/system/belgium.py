# -*- coding: utf-8 -*-
"""
diacamma.condominium.system package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2018 sd-libre.fr
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
"""

from django.utils.translation import ugettext_lazy as _

from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.tools import get_date_formating
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import CustomField

from diacamma.accounting.tools import correct_accounting_code, currency_round, current_system_account
from diacamma.accounting.models import ChartsAccount, EntryAccount, EntryLineAccount, Journal,\
    FiscalYear
from diacamma.condominium.system.default import DefaultSystemCondo
from diacamma.condominium.models import CallFunds, Set, CallDetail
from lucterios.framework.tools import same_day_months_after


class BelgiumSystemCondo(DefaultSystemCondo):

    def initialize_system(self):
        Parameter.change_value('accounting-sizecode', 6)
        Parameter.change_value('condominium-default-owner-account', correct_accounting_code(''))
        Parameter.change_value('condominium-default-owner-account1', correct_accounting_code('410100'))
        Parameter.change_value('condominium-default-owner-account2', correct_accounting_code('410000'))
        Parameter.change_value('condominium-default-owner-account3', correct_accounting_code('410100'))
        Parameter.change_value('condominium-default-owner-account4', correct_accounting_code(''))
        Parameter.change_value('condominium-default-owner-account5', correct_accounting_code('410000'))
        Parameter.change_value('condominium-current-revenue-account', correct_accounting_code('701100'))
        Parameter.change_value('condominium-exceptional-revenue-account', correct_accounting_code('700100'))
        Parameter.change_value('condominium-advance-revenue-account', correct_accounting_code('701200'))
        Parameter.change_value('condominium-fundforworks-revenue-account', correct_accounting_code('700000'))
        Parameter.change_value('condominium-exceptional-reserve-account', correct_accounting_code('160000'))
        Parameter.change_value('condominium-advance-reserve-account', correct_accounting_code('100000'))
        Parameter.change_value('condominium-fundforworks-reserve-account', correct_accounting_code('100000'))
        Parameter.change_value('condominium-mode-current-callfunds', 1)
        Params.clear()
        CustomField.objects.get_or_create(modelname='accounting.Third', name='IBAN', kind=0, args="{'multi': False}")
        CustomField.objects.get_or_create(modelname='accounting.Third', name='SWIFT', kind=0, args="{'multi': False}")

    def get_config_params(self, _new_params):
        param_lists = ['condominium-default-owner-account1', 'condominium-default-owner-account2',
                       'condominium-default-owner-account3', 'condominium-default-owner-account5',
                       'condominium-current-revenue-account', 'condominium-exceptional-revenue-account',
                       'condominium-advance-revenue-account', 'condominium-fundforworks-revenue-account',
                       'condominium-exceptional-reserve-account', 'condominium-advance-reserve-account',
                       'condominium-fundforworks-reserve-account', 'condominium-mode-current-callfunds']
        return param_lists

    def get_param_titles(self, names):
        title_lists = {'condominium-default-owner-account1': _('default current owner account'), 'condominium-default-owner-account2': _('default working owner account'),
                       'condominium-default-owner-account3': _('default rolling owner account'), 'condominium-default-owner-account5': _('default reserved owner account'),
                       'condominium-current-revenue-account': _('current revenue account'), 'condominium-exceptional-revenue-account': _('working revenue account'),
                       'condominium-advance-revenue-account': _('rolling revenue account'), 'condominium-fundforworks-revenue-account': _('reserved revenue account'),
                       'condominium-exceptional-reserve-account': _('working reserved account'), 'condominium-advance-reserve-account': _('rolling reserved account'),
                       'condominium-fundforworks-reserve-account': _('reserved account')}
        titles = {}
        params = self.get_config_params(False)
        for name in title_lists:
            if name in params:
                titles[name] = title_lists[name]
        return titles

    def get_callfunds_list(self):
        return [(0, _('current')), (1, _('working')), (2, _('rolling')), (4, _('reserved'))]

    def CurrentCallFundsAdding(self, to_create):
        nb_seq = 0
        if Params.getvalue("condominium-mode-current-callfunds") == 0:
            nb_seq = 4
        if Params.getvalue("condominium-mode-current-callfunds") == 1:
            nb_seq = 12
        year = FiscalYear.get_current()
        calls = CallFunds.objects.filter(date__gte=year.begin, date__lte=year.end, calldetail__type_call=0).distinct()
        nb_curent = len(calls)
        if to_create:
            year = FiscalYear.get_current()
            date = same_day_months_after(year.begin, int(nb_curent * 12 / nb_seq))
            new_call = CallFunds.objects.create(date=date, comment=_("Call of funds #%(num)d of year from %(begin)s to %(end)s") % {'num': nb_curent + 1, 'begin': get_date_formating(year.begin), 'end': get_date_formating(year.end)}, status=0)
            for category in Set.objects.filter(type_load=0, is_active=True):
                CallDetail.objects.create(set=category, type_call=0, callfunds=new_call, price=category.get_new_current_callfunds(), designation=_("%(type)s - #%(num)d") % {'type': _('current'), 'num': nb_curent + 1})
        else:
            return nb_curent < nb_seq

    def _generate_account_callfunds_by_type(self, new_entry, type_call, calldetails):
        detail_account_filter = None
        if type_call == 0:
            detail_account_filter = Params.getvalue("condominium-current-revenue-account")
        if type_call == 1:
            detail_account_filter = Params.getvalue("condominium-exceptional-revenue-account")
        if type_call == 2:
            detail_account_filter = Params.getvalue("condominium-advance-revenue-account")
        if type_call == 4:
            detail_account_filter = Params.getvalue("condominium-fundforworks-revenue-account")
        detail_account = ChartsAccount.get_account(detail_account_filter, new_entry.year)
        if detail_account is None:
            raise LucteriosException(IMPORTANT, _("incorrect account for call of found"))
        total = 0
        for calldetail in calldetails:
            EntryLineAccount.objects.create(account=detail_account, amount=calldetail.price, entry=new_entry,
                                            costaccounting=calldetail.set.current_cost_accounting)
            total += calldetail.price
            calldetail.entry = new_entry
            calldetail.save()
        return total

    def generate_revenue_for_expense(self, expense, is_asset, fiscal_year):
        pass

    def generate_expense_for_expense(self, expense, is_asset, fiscal_year):
        third_account = expense.get_third_account(current_system_account().get_provider_mask(), fiscal_year)
        new_entry = EntryAccount.objects.create(year=fiscal_year, date_value=expense.date, designation=expense.__str__(), journal=Journal.objects.get(id=2))
        total = 0
        for detail in expense.expensedetail_set.all():
            detail_account = ChartsAccount.get_account(detail.expense_account, fiscal_year)
            if detail_account is None:
                raise LucteriosException(IMPORTANT, _("code account %s unknown!") % detail.expense_account)
            price = currency_round(detail.price)
            EntryLineAccount.objects.create(account=detail_account, amount=is_asset * price, entry=new_entry, costaccounting_id=detail.set.current_cost_accounting.id)
            total += price
        EntryLineAccount.objects.create(account=third_account, amount=is_asset * total, third=expense.third, entry=new_entry)
        no_change, debit_rest, credit_rest = new_entry.serial_control(new_entry.get_serial())
        if not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
            message = _("Error in accounting generator!")
            message += "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest)
            raise LucteriosException(GRAVE, message)
        expense.entries.set(EntryAccount.objects.filter(id=new_entry.id))
