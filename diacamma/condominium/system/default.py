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
from django.db.models.aggregates import Sum

from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.parameters import Params
from lucterios.framework.tools import get_date_formating

from diacamma.accounting.tools import currency_round
from diacamma.accounting.models import FiscalYear, EntryAccount, EntryLineAccount, ChartsAccount

from diacamma.condominium.models import CallDetail, Owner, PropertyLot


class DefaultSystemCondo(object):

    def __init__(self):
        pass

    def initialize_system(self):
        pass

    def get_config_params(self, _new_params):
        return []

    def get_param_titles(self, names):
        titles = {}
        params = self.get_config_params(False)
        for name in names:
            if name in params:
                titles[name] = _(name)
        return titles

    def get_callfunds_list(self):
        return {}

    def CurrentCallFundsAdding(self):
        return False

    def owner_account_changed(self, account_item):
        pass

    def _generate_account_callfunds_by_type(self, new_entry, type_call, calldetails):
        raise LucteriosException(IMPORTANT, _('This system condomium is not implemented'))

    def generate_account_callfunds(self, call_funds, fiscal_year):
        for type_call, type_title in self.get_callfunds_list():
            calldetails = call_funds.calldetail_set.filter(type_call=type_call)
            if len(calldetails) > 0:
                designation = _('call of funds "%(type)s" #%(num)d - %(date)s') % {'num': call_funds.num, 'type': type_title,
                                                                                   'date': get_date_formating(call_funds.date)}
                new_entry = EntryAccount.objects.create(year=fiscal_year, date_value=call_funds.date, designation=designation, journal_id=3)
                owner_account_filter = call_funds.supporting.get_third_mask(type_owner=type_call + 1)
                owner_account = call_funds.owner.third.get_account(fiscal_year, owner_account_filter)
                total = self._generate_account_callfunds_by_type(new_entry, type_call, calldetails)
                EntryLineAccount.objects.create(account=owner_account, amount=total, entry=new_entry, third=call_funds.owner.third)

    def generate_revenue_for_expense(self, expense, is_asset, fiscal_year):
        raise LucteriosException(IMPORTANT, _('This system condomium is not implemented'))

    def generate_expense_for_expense(self, expense, is_asset, fiscal_year):
        raise LucteriosException(IMPORTANT, _('This system condomium is not implemented'))

    def ventilate_costaccounting(self, own_set, cost_accounting, type_owner, initial_code):
        if type_owner == 2:
            result = currency_round(CallDetail.objects.filter(set=own_set).aggregate(sum=Sum('price'))['sum'])
        else:
            result = cost_accounting.get_total_revenue()
        result -= cost_accounting.get_total_expense()
        if abs(result) > 0.0001:
            fiscal_year = FiscalYear.get_current()
            close_entry = EntryAccount(year=fiscal_year, designation=_("Ventilation for %s") % own_set, journal_id=5)
            close_entry.check_date()
            close_entry.save()
            amount = 0
            last_line = None
            for part in own_set.partition_set.all().order_by('value'):
                value = currency_round(result * part.get_ratio() / 100.0)
                if abs(value) > 0.0001:
                    owner_account = part.owner.third.get_account(fiscal_year, part.owner.get_third_mask(type_owner))
                    last_line = EntryLineAccount.objects.create(account=owner_account, amount=-1 * value, entry=close_entry, third=part.owner.third)
                    amount += value
            if last_line is None:
                raise LucteriosException(IMPORTANT, _('The class load %s has no owner') % own_set)
            diff = currency_round(result - amount)
            if abs(diff) > 0.0001:
                last_line.amount -= diff
                last_line.save()
            reserve_account = ChartsAccount.get_account(initial_code, fiscal_year)
            EntryLineAccount.objects.create(account=reserve_account, amount=-1 * result, entry=close_entry, costaccounting=cost_accounting)
            close_entry.closed()

    def ventilate_result(self, fiscal_year, ventilate):
        Owner.throw_not_allowed()
        result = fiscal_year.total_revenue - fiscal_year.total_expense
        if abs(result) > 0.001:
            total_part = PropertyLot.get_total_part()
            if total_part > 0:
                close_entry = EntryAccount(year=fiscal_year, designation=_("Ventilation for %s") % fiscal_year, journal_id=5)
                close_entry.check_date()
                close_entry.save()
                if ventilate == 0:
                    amount = 0
                    biggerowner_val = 0
                    biggerowner_line = None
                    for owner in Owner.objects.all():
                        total = owner.propertylot_set.aggregate(sum=Sum('value'))
                        if ('sum' in total.keys()) and (total['sum'] is not None):
                            value = currency_round(result * total['sum'] / total_part)
                            if abs(value) > 0.0001:
                                owner_account = owner.third.get_account(fiscal_year, owner.get_third_mask(1))
                                last_line = EntryLineAccount.objects.create(account=owner_account, amount=-1 * value, entry=close_entry, third=owner.third)
                                if biggerowner_val < total['sum']:
                                    biggerowner_val = total['sum']
                                    biggerowner_line = last_line
                                amount += value
                    diff = currency_round(result - amount)
                    if abs(diff) > 0.0001:
                        biggerowner_line.amount -= diff
                        biggerowner_line.save()
                else:
                    EntryLineAccount.objects.create(account_id=ventilate, amount=result, entry=close_entry)
                reserve_account = ChartsAccount.get_account(Params.getvalue("condominium-current-revenue-account"), fiscal_year)
                EntryLineAccount.objects.create(account=reserve_account, amount=-1 * result, entry=close_entry)
                close_entry.closed()
