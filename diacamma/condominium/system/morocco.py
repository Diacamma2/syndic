"""
diacamma.condominium.system package

Created on 21 janv. 2026

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2025 sd-libre.fr
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
from django.utils.translation import gettext_lazy as _

from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.framework.tools import same_day_months_after, get_date_formating

from diacamma.accounting.tools import correct_accounting_code
from diacamma.accounting.models import ChartsAccount, EntryLineAccount, FiscalYear
from diacamma.condominium.system.default import DefaultSystemCondo
from diacamma.condominium.models import CallFunds, Set, CallDetail


class MoroccoSystemCondo(DefaultSystemCondo):

    def initialize_system(self):
        Parameter.change_value('condominium-default-owner-account', correct_accounting_code(''))
        Parameter.change_value('condominium-default-owner-account1', correct_accounting_code('3421'))
        Parameter.change_value('condominium-default-owner-account2', correct_accounting_code('3422'))
        Parameter.change_value('condominium-default-owner-account3', correct_accounting_code('3423'))
        Parameter.change_value('condominium-default-owner-account4', correct_accounting_code(''))
        Parameter.change_value('condominium-default-owner-account5', correct_accounting_code('3424'))
        Parameter.change_value('condominium-current-revenue-account', correct_accounting_code('7111'))
        Parameter.change_value('condominium-exceptional-revenue-account', correct_accounting_code('7112'))
        Parameter.change_value('condominium-advance-revenue-account', correct_accounting_code('7113'))
        Parameter.change_value('condominium-fundforworks-revenue-account', correct_accounting_code('7511'))
        Parameter.change_value('condominium-exceptional-reserve-account', correct_accounting_code('1111'))
        Parameter.change_value('condominium-advance-reserve-account', correct_accounting_code('1112'))
        Parameter.change_value('condominium-fundforworks-reserve-account', correct_accounting_code('1511'))
        Parameter.change_value('condominium-mode-current-callfunds', 0)
        Params.clear()

    def get_config_params(self, _new_params):
        param_lists = ['condominium-default-owner-account1', 'condominium-default-owner-account2',
                       'condominium-default-owner-account3', 'condominium-default-owner-account5',
                       'condominium-current-revenue-account', 'condominium-exceptional-revenue-account',
                       'condominium-advance-revenue-account', 'condominium-fundforworks-revenue-account',
                       'condominium-exceptional-reserve-account', 'condominium-advance-reserve-account',
                       'condominium-fundforworks-reserve-account', 'condominium-mode-current-callfunds',
                       'condominium-payoff-calloffunds']
        return param_lists

    def get_callfunds_list(self, complete=False):
        return [(0, _('current')), (1, _('working')), (2, _('rolling')), (4, _('reserved'))]

    def CurrentCallFundsAdding(self, to_create):
        if to_create:
            nb_seq = CallFunds.getNbSequence()
            year = FiscalYear.get_current()
            for num in range(nb_seq):
                date = same_day_months_after(year.begin, int(num * 12 / nb_seq))
                new_call = CallFunds.objects.create(date=date, comment=_("Call of funds #%(num)d of year from %(begin)s to %(end)s") % {'num': num + 1, 'begin': get_date_formating(year.begin), 'end': get_date_formating(year.end)}, status=0)
                for category in Set.objects.filter(type_load=0, is_active=True):
                    CallDetail.objects.create(set=category, type_call=0, callfunds=new_call, price=category.get_current_budget() / nb_seq, designation=_("%(type)s - #%(num)d") % {'type': _('current'), 'num': num + 1})
        else:
            year = FiscalYear.get_current()
            calls = CallFunds.objects.filter(date__gte=year.begin, date__lte=year.end, calldetail__type_call=0, calldetail__set__isnull=False).distinct()
            return len(calls) == 0

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
