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
from diacamma.condominium.models import Set, Owner, Partition, CallFunds,\
    CallDetail
from lucterios.CORE.models import Parameter
from diacamma.accounting.test_tools import create_account
from diacamma.accounting.models import FiscalYear


def default_setowner():
    create_account(['455'], 0, FiscalYear.get_current())
    create_account(['704'], 3, FiscalYear.get_current())
    Parameter.change_value('condominium-frequency', '1')
    set1 = Set.objects.create(
        name="AAA", budget=1000, revenue_account='704', cost_accounting_id=2)
    set2 = Set.objects.create(
        name="BBB", budget=100, revenue_account='704', cost_accounting_id=0)
    owner1 = Owner.objects.create(third_id=4)
    owner1.editor.before_save(None)
    owner1.save()
    owner2 = Owner.objects.create(third_id=5)
    owner2.editor.before_save(None)
    owner2.save()
    owner3 = Owner.objects.create(third_id=7)
    owner3.editor.before_save(None)
    owner3.save()
    Partition.objects.create(set=set1, owner=owner1, value=45.0)
    Partition.objects.create(set=set1, owner=owner2, value=35.0)
    Partition.objects.create(set=set1, owner=owner3, value=20.0)
    Partition.objects.create(set=set2, owner=owner1, value=75.0)
    Partition.objects.create(set=set2, owner=owner2, value=0.0)
    Partition.objects.create(set=set2, owner=owner3, value=25.0)


def add_simple_callfunds():
    call = CallFunds.objects.create(date='2015-06-10', comment='abc 123')
    CallDetail.objects.create(
        callfunds=call, set_id=1, price='250.00', designation='set 1')
    CallDetail.objects.create(
        callfunds=call, set_id=2, price='25.00', designation='set 2')
    call.valid()
