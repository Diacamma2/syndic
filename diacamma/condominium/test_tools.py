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
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from lucterios.framework.tools import convert_date
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params

from diacamma.accounting.models import FiscalYear
from diacamma.accounting.test_tools import create_account, add_entry
from diacamma.payoff.models import Payoff
from diacamma.condominium.models import Set, Owner, Partition, CallFunds, CallDetail, Expense, ExpenseDetail,\
    PropertyLot


def default_setowner(with_lots=True):
    def set_partition(setpart, owner, value):
        part = Partition.objects.get(set=setpart, owner=owner)
        part.value = value
        part.save()
    if Params.getvalue("condominium-old-accounting"):
        create_account(['450'], 0, FiscalYear.get_current())
    else:
        create_account(['4501', '4502', '4503', '4504'], 0, FiscalYear.get_current())
    create_account(['120', '103'], 2, FiscalYear.get_current())
    create_account(['702'], 3, FiscalYear.get_current())

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

    set1 = Set.objects.create(
        name="AAA", budget=1000, revenue_account='701', is_link_to_lots=with_lots, type_load=0, cost_accounting_id=2)
    set1.convert_budget()
    set2 = Set.objects.create(
        name="BBB", budget=100, revenue_account='701', type_load=0, cost_accounting_id=0)
    set2.convert_budget()
    set3 = Set.objects.create(
        name="CCC", budget=500, revenue_account='702', type_load=1, cost_accounting_id=0)
    set3.convert_budget()
    set4 = Set.objects.create(
        name="OLD", budget=100, revenue_account='702', type_load=1, cost_accounting_id=0, is_active=False)
    set4.convert_budget()
    if with_lots:
        set1.set_of_lots = PropertyLot.objects.all()
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


def add_test_callfunds(simple=True, with_payoff=False):
    call1 = CallFunds.objects.create(date='2015-06-10', comment='uvw 987', type_call=0)
    CallDetail.objects.create(callfunds=call1, set_id=1, price='250.00', designation='set 1')
    CallDetail.objects.create(callfunds=call1, set_id=2, price='25.00', designation='set 2')
    call1.valid()  # => 5 6 7
    if not simple:
        call2 = CallFunds.objects.create(date='2015-07-14', comment='working...', type_call=1)
        CallDetail.objects.create(callfunds=call2, set_id=3, price='100.00', designation='set 3')
        call2.valid()  # => 9 10 11
    if with_payoff:
        pay = Payoff(supporting_id=4, date='2015-06-15', mode=0, amount=100.0)
        pay.editor.before_save(None)
        pay.save()
        pay = Payoff(supporting_id=7, date='2015-07-21', mode=0, amount=30.0)
        pay.editor.before_save(None)
        pay.save()


def add_test_expenses(simple=True, with_payoff=False):
    expense1 = Expense(date=convert_date('2015-05-07'), comment='opq 666', expensetype=0, third_id=2)
    expense1.editor.before_save(None)
    expense1.save()
    ExpenseDetail.objects.create(expense=expense1, set_id=2, designation='set 2', expense_account='604', price='100')
    expense1.valid()
    if not simple:
        expense2 = Expense(date=convert_date('2015-08-28'), comment='creation', expensetype=0, third_id=2)
        expense2.editor.before_save(None)
        expense2.save()
        ExpenseDetail.objects.create(expense=expense2, set_id=3, designation='set 1', expense_account='602', price='75')
        expense2.valid()
    if with_payoff:
        pay = Payoff(supporting_id=expense1.id, date='2015-05-11', mode=0, amount=35.0)
        pay.editor.before_save(None)
        pay.save()
        pay = Payoff(supporting_id=expense2.id, date='2015-08-30', mode=0, amount=75.0)
        pay.editor.before_save(None)
        pay.save()


def old_accounting():
    Parameter.change_value('condominium-old-accounting', True)
    Params.clear()


def init_compta():
    year = FiscalYear.get_current()
    if Params.getvalue("condominium-old-accounting"):
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau',
                  '-1|2|0|23.450000|None|\n-2|17|4|-23.450000|None|', True)
    else:
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau',
                  '-1|2|0|29.180000|None|\n-2|17|4|-23.450000|None|\n-3|18|4|-5.730000|None|', True)
    add_entry(year.id, 5, '2015-02-20', 'Frais bancaire',
              '-1|2|0|-12.340000|None|\n-2|15|0|12.340000|None|', True)


def add_years():
    year_N_1 = FiscalYear.objects.create(begin='2014-01-01', end='2014-12-31', status=2)
    year = FiscalYear.get_current()
    year.last_fiscalyear = year_N_1
    year.save()
    year_N1 = FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear=year)
    FiscalYear.objects.create(begin='2017-01-01', end='2017-12-31', status=0, last_fiscalyear=year_N1)
