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

from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import CustomField

from diacamma.accounting.tools import correct_accounting_code, currency_round, current_system_account
from diacamma.accounting.models import ChartsAccount, EntryAccount, EntryLineAccount, Journal
from diacamma.condominium.models import Owner, PropertyLot


class BelgiumSystemCondo(object):

    def initialize_system(self):
        Parameter.change_value('condominium-default-owner-account', correct_accounting_code('4101'))
        Parameter.change_value('condominium-default-owner-account1', correct_accounting_code('4101'))
        Parameter.change_value('condominium-default-owner-account2', correct_accounting_code('4100'))
        Parameter.change_value('condominium-default-owner-account3', correct_accounting_code('4100'))
        Parameter.change_value('condominium-default-owner-account4', correct_accounting_code('4101'))
        Parameter.change_value('condominium-default-owner-account5', correct_accounting_code('4100'))
        Parameter.change_value('condominium-current-revenue-account', correct_accounting_code('701'))
        Parameter.change_value('condominium-exceptional-revenue-account', correct_accounting_code('700'))
        Parameter.change_value('condominium-fundforworks-revenue-account', correct_accounting_code(''))
        Parameter.change_value('condominium-exceptional-reserve-account', correct_accounting_code(''))
        Parameter.change_value('condominium-advance-reserve-account', correct_accounting_code(''))
        Parameter.change_value('condominium-fundforworks-reserve-account', correct_accounting_code(''))
        Params.clear()
        CustomField.objects.get_or_create(modelname='accounting.Third', name='IBAN', kind=0, args="{'multi': False}")
        CustomField.objects.get_or_create(modelname='accounting.Third', name='SWIFT', kind=0, args="{'multi': False}")

    def generate_account_callfunds(self, call_funds, fiscal_year):
        owner_account_filter = call_funds.supporting.get_third_mask()
        detail_account_filter = None
        if call_funds.type_call == 0:
            detail_account_filter = Params.getvalue("condominium-current-revenue-account")
        if call_funds.type_call == 1:
            detail_account_filter = Params.getvalue("condominium-exceptional-reserve-account")
        if call_funds.type_call == 2:
            detail_account_filter = Params.getvalue("condominium-advance-reserve-account")
        if call_funds.type_call == 4:
            detail_account_filter = Params.getvalue("condominium-fundforworks-reserve-account")
        owner_account = call_funds.owner.third.get_account(fiscal_year, owner_account_filter)
        detail_account = ChartsAccount.get_account(detail_account_filter, fiscal_year)
        if detail_account is None:
            raise LucteriosException(IMPORTANT, _("incorrect account for call of found"))
        new_entry = EntryAccount.objects.create(year=fiscal_year, date_value=call_funds.date, designation=call_funds.__str__(), journal_id=3)
        total = 0
        for calldetail in call_funds.calldetail_set.all():
            EntryLineAccount.objects.create(account=detail_account, amount=calldetail.price, entry=new_entry, costaccounting=calldetail.set.current_cost_accounting)
            total += calldetail.price
            calldetail.entry = new_entry
            calldetail.save()
        EntryLineAccount.objects.create(account=owner_account, amount=total, entry=new_entry, third=call_funds.owner.third)

    def generate_revenue_for_expense(self, expense, is_asset, fiscal_year):
        if len(expense.expensedetail_set.filter(set__type_load=1)) > 0:
            total = 0
            revenue_code = Params.getvalue("condominium-exceptional-revenue-account")
            revenue_account = ChartsAccount.get_account(revenue_code, fiscal_year)
            if revenue_account is None:
                raise LucteriosException(IMPORTANT, _("code account %s unknown!") % revenue_code)
            reserve_code = Params.getvalue("condominium-exceptional-reserve-account")
            reserve_account = ChartsAccount.get_account(reserve_code, fiscal_year)
            if revenue_account is None:
                raise LucteriosException(IMPORTANT, _("code account %s unknown!") % reserve_code)
            new_entry = EntryAccount.objects.create(year=fiscal_year, date_value=expense.expense.date, designation=expense.__str__(), journal=Journal.objects.get(id=3))
            for detail in expense.expensedetail_set.all():
                detail.generate_ratio(is_asset)
                if detail.set.type_load == 1:
                    cost_accounting = detail.set.current_cost_accounting
                    price = currency_round(detail.price)
                    EntryLineAccount.objects.create(account=revenue_account, amount=is_asset * price, entry=new_entry, costaccounting=cost_accounting)
                    total += price
                    detail.entry = new_entry
                    detail.save()
            EntryLineAccount.objects.create(account=reserve_account, amount=-1 * is_asset * total, entry=new_entry)
            no_change, debit_rest, credit_rest = new_entry.serial_control(new_entry.get_serial())
            if not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
                raise LucteriosException(GRAVE, _("Error in accounting generator!") +
                                         "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest))

    def generate_expense_for_expense(self, expense, is_asset, fiscal_year):
        third_account = expense.get_third_account(current_system_account().get_provider_mask(), fiscal_year)
        new_entry = EntryAccount.objects.create(year=fiscal_year, date_value=expense.date, designation=expense.__str__(), journal=Journal.objects.get(id=2))
        total = 0
        for detail in expense.expensedetail_set.all():
            detail_account = ChartsAccount.get_account(detail.expense_account, fiscal_year)
            price = currency_round(detail.price)
            EntryLineAccount.objects.create(account=detail_account, amount=is_asset * price, entry=new_entry, costaccounting_id=detail.set.current_cost_accounting.id)
            total += price
        EntryLineAccount.objects.create(account=third_account, amount=is_asset * total, third=expense.third, entry=new_entry)
        no_change, debit_rest, credit_rest = new_entry.serial_control(new_entry.get_serial())
        if not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
            raise LucteriosException(GRAVE, _("Error in accounting generator!") +
                                     "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest))
        expense.entries = EntryAccount.objects.filter(id=new_entry.id)

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
