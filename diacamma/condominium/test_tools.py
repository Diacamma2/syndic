# -*- coding: utf-8 -*-
'''
diacamma.condominium test_tools package

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
GNU General Public License for more detaamount
You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from lucterios.framework.tools import convert_date
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params

from diacamma.accounting.models import FiscalYear, Budget
from diacamma.accounting.test_tools import create_account, add_entry
from diacamma.payoff.models import Payoff
from diacamma.condominium.models import Set, Owner, Partition, CallFunds, CallDetail, Expense, ExpenseDetail, PropertyLot, RecoverableLoadRatio


def _set_budget(setitem, code, amount):
    year = FiscalYear.get_current()
    cost = setitem.current_cost_accounting
    Budget.objects.create(cost_accounting=cost, year=year, code=code, amount=amount)
    setitem.change_budget_product(cost, year.id)


def _create_owners(set1, set2, set3, set4, with_lots=True):
    def set_partition(setpart, owner, value):
        part = Partition.objects.get(set=setpart, owner=owner)
        part.value = value
        part.save()
    owner1 = Owner.objects.create(third_id=4)
    owner1.editor.before_save(None)
    owner1.save()
    owner2 = Owner.objects.create(third_id=5)
    owner2.editor.before_save(None)
    owner2.save()
    owner3 = Owner.objects.create(third_id=7)
    owner3.editor.before_save(None)
    owner3.save()
    if with_lots:
        PropertyLot.objects.create(num=1, value=45.0, description="Appart A", owner=owner1)
        PropertyLot.objects.create(num=2, value=35.0, description="Appart B", owner=owner2)
        PropertyLot.objects.create(num=3, value=20.0, description="Appart C", owner=owner3)
        set1.set_of_lots.set(PropertyLot.objects.all())
        set1.save()
    else:
        set_partition(setpart=set1, owner=owner1, value=45.0)
        set_partition(setpart=set1, owner=owner2, value=35.0)
        set_partition(setpart=set1, owner=owner3, value=20.0)
    set_partition(setpart=set2, owner=owner1, value=75.0)
    set_partition(setpart=set2, owner=owner2, value=0.0)
    set_partition(setpart=set2, owner=owner3, value=25.0)
    set_partition(setpart=set3, owner=owner1, value=45.0)
    set_partition(setpart=set3, owner=owner2, value=35.0)
    set_partition(setpart=set3, owner=owner3, value=20.0)
    set_partition(setpart=set4, owner=owner1, value=45.0)
    set_partition(setpart=set4, owner=owner2, value=35.0)
    set_partition(setpart=set4, owner=owner3, value=20.0)


def default_setowner_fr(with_lots=True):
    RecoverableLoadRatio.objects.create(code='602', ratio=60)
    RecoverableLoadRatio.objects.create(code='604', ratio=40)

    if Params.getvalue("condominium-old-accounting"):
        create_account(['450'], 0, FiscalYear.get_current())
    else:
        create_account(['4501', '4502', '4503', '4504', '4505'], 0, FiscalYear.get_current())
    create_account(['120', '103', '105'], 2, FiscalYear.get_current())
    create_account(['702'], 3, FiscalYear.get_current())
    set1 = Set.objects.create(name="AAA", budget=1000, revenue_account='701', is_link_to_lots=with_lots, type_load=0)
    _set_budget(set1, '604', 1000)
    set2 = Set.objects.create(name="BBB", budget=100, revenue_account='701', type_load=0)
    _set_budget(set2, '604', 100)
    set3 = Set.objects.create(name="CCC", budget=500, revenue_account='702', type_load=1)
    _set_budget(set3, '604', 500)
    set4 = Set.objects.create(name="OLD", budget=100, revenue_account='702', type_load=1, is_active=False)
    _set_budget(set4, '602', 100)
    _create_owners(set1, set2, set3, set4, with_lots)
    Owner.check_all_account()


def default_setowner_be(with_lots=True):
    RecoverableLoadRatio.objects.create(code='601000', ratio=60)
    RecoverableLoadRatio.objects.create(code='602000', ratio=40)

    create_account(['410000', '410100'], 0, FiscalYear.get_current())
    create_account(['100000', '160000'], 2, FiscalYear.get_current())
    create_account(['700100', '701100', '701200'], 3, FiscalYear.get_current())
    set1 = Set.objects.create(name="AAA", is_link_to_lots=with_lots, type_load=0)
    _set_budget(set1, '602000', 1200)
    set2 = Set.objects.create(name="BBB", type_load=0)
    _set_budget(set2, '602000', 120)
    set3 = Set.objects.create(name="CCC", type_load=1)
    _set_budget(set3, '602000', 600)
    set4 = Set.objects.create(name="OLD", type_load=1, is_active=False)
    _set_budget(set4, '601000', 120)
    _create_owners(set1, set2, set3, set4, with_lots)
    Owner.check_all_account()


def add_test_callfunds(simple=True, with_payoff=False):
    call1 = CallFunds.objects.create(date='2015-06-10', comment='uvw 987')
    CallDetail.objects.create(callfunds=call1, type_call=0, set_id=1, price='250.00', designation='set 1')
    CallDetail.objects.create(callfunds=call1, type_call=0, set_id=2, price='25.00', designation='set 2')
    call1.valid()  # => 5 6 7
    if not simple:
        call2 = CallFunds.objects.create(date='2015-07-14', comment='working...')
        CallDetail.objects.create(callfunds=call2, type_call=1, set_id=3, price='100.00', designation='set 3')
        call2.valid()  # => 9 10 11
    if with_payoff:
        pay1 = Payoff(supporting_id=4, date='2015-06-15', mode=0, amount=100.0)
        pay1.editor.before_save(None)
        pay1.save()
        pay2 = Payoff(supporting_id=7, date='2015-07-21', mode=0, amount=30.0)
        pay2.editor.before_save(None)
        pay2.save()


def _add_test_expenses(expense_account1, expense_account2, simple, with_payoff):
    expense1 = Expense(date=convert_date('2015-05-07'), comment='opq 666', expensetype=0, third_id=2)
    expense1.editor.before_save(None)
    expense1.save()
    ExpenseDetail.objects.create(expense=expense1, set_id=2, designation='set 2', expense_account=expense_account1, price='100')
    expense1.valid()
    if not simple:
        expense2 = Expense(date=convert_date('2015-08-28'), comment='creation', expensetype=0, third_id=2)
        expense2.editor.before_save(None)
        expense2.save()
        ExpenseDetail.objects.create(expense=expense2, set_id=3, designation='set 1', expense_account=expense_account2, price='75')
        expense2.valid()
    if with_payoff:
        pay = Payoff(supporting_id=expense1.id, date='2015-05-11', mode=0, amount=35.0)
        pay.editor.before_save(None)
        pay.save()
        pay = Payoff(supporting_id=expense2.id, date='2015-08-30', mode=0, amount=75.0)
        pay.editor.before_save(None)
        pay.save()


def add_test_expenses_fr(simple=True, with_payoff=False):
    _add_test_expenses('604', '602', simple, with_payoff)


def add_test_expenses_be(simple=True, with_payoff=False):
    _add_test_expenses('602000', '601000', simple, with_payoff)


def old_accounting():
    Parameter.change_value('condominium-old-accounting', True)
    Params.clear()


def init_compta():
    year = FiscalYear.get_current()
    if Params.getvalue("condominium-old-accounting"):
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau', '-1|2|0|23.450000|0|0|None|\n-2|17|4|-23.450000|0|0|None|', True)
    else:
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau', '-1|2|0|16.680000|0|0|None|\n-2|17|4|-23.450000|0|0|None|\n-3|18|4|-5.730000|0|0|None|\n-4|17|5|12.500000|0|0|None|', True)
    add_entry(year.id, 5, '2015-02-20', 'Frais bancaire', '-1|2|0|-12.340000|0|0|None|\n-2|15|0|12.340000|0|0|None|', True)


def add_years():
    year_N_1 = FiscalYear.objects.create(begin='2014-01-01', end='2014-12-31', status=2)
    year = FiscalYear.get_current()
    year.last_fiscalyear = year_N_1
    year.save()
    year_N1 = FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear=year)
    FiscalYear.objects.create(begin='2017-01-01', end='2017-12-31', status=0, last_fiscalyear=year_N1)


def main_fr():
    from diacamma.condominium.views_classload import paramchange_condominium
    from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting
    from diacamma.payoff.test_tools import default_bankaccount_fr
    paramchange_condominium([])
    initial_thirds_fr()
    default_compta_fr(with12=False)
    default_costaccounting()
    default_bankaccount_fr()
    default_setowner_fr()
    init_compta()
    add_test_callfunds(False, True)
    add_test_expenses_fr(False, True)


def main_be():
    from diacamma.condominium.views_classload import paramchange_condominium
    from diacamma.accounting.test_tools import initial_thirds_be, default_compta_be, default_costaccounting
    from diacamma.payoff.test_tools import default_bankaccount_be
    paramchange_condominium([])
    initial_thirds_be()
    default_compta_be(with12=False)
    default_costaccounting()
    default_bankaccount_be()
    default_setowner_be()
    init_compta()
    add_test_callfunds(False, True)
    add_test_expenses_be(False, True)
