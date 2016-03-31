# -*- coding: utf-8 -*-
'''
diacamma.condominium tests package

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
from shutil import rmtree

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.test_tools import initial_thirds, default_compta,\
    default_costaccounting
from diacamma.payoff.test_tools import default_bankaccount
from diacamma.condominium.views import SetOwnerList, SetAddModify, SetDel,\
    OwnerAdd, OwnerDel, SetShow, PartitionAddModify
from diacamma.accounting.views import ThirdShow


class SetOwnerTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_costaccounting()
        default_bankaccount()
        rmtree(get_user_dir(), True)

    def test_add_set(self):
        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 6)

        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal(
            'COMPONENTS/EDIT[@name="revenue_account"]/REG_EXPR', r'^7[0-9][0-9][0-9a-zA-Z]*$')

        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "abc123", "budget": '1200', "revenue_account": '704', 'cost_accounting': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setAddModify')

        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 6)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="name"]', 'abc123')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="budget_txt"]', '1200.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="revenue_account"]', '704')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="cost_accounting"]', 'open')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="sumexpense_txt"]', "0.00€")

        self.factory.xfer = SetDel()
        self.call('/diacamma.condominium/setDel',
                  {'CONFIRME': 'YES', "set": 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setDel')

        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 6)

    def test_add_owner(self):
        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 7)

        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAddModify')
        self.assert_count_equal('COMPONENTS/*', 6)
        self.assert_count_equal('COMPONENTS/SELECT[@name="third"]/CASE', 7)

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="contact"]', 'Minimum')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 2)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="code"]', '411')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[2]/VALUE[@name="code"]', '401')

        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')

        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 7)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="third"]', 'Minimum')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_initial"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_call"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_payed"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_ventilated"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_estimate"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_real"]', '0.00€')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="contact"]', 'Minimum')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[3]/VALUE[@name="code"]', '455')

        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAddModify')
        self.assert_count_equal('COMPONENTS/*', 6)
        self.assert_count_equal('COMPONENTS/SELECT[@name="third"]/CASE', 6)

        self.factory.xfer = OwnerDel()
        self.call('/diacamma.condominium/ownerDel',
                  {'CONFIRME': 'YES', "owner": 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerDel')

        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 7)

    def test_show_partition(self):
        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 7)

        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "AAA", "budget": '1000', "revenue_account": '704', 'cost_accounting': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setAddModify')
        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')
        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "BBB", "budget": '200', "revenue_account": '705', 'cost_accounting': 0}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setAddModify')
        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 5}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')
        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 7}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')

        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="name"]', 'AAA')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="budget_txt"]', '1000.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="revenue_account"]', '704')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="cost_accounting"]', 'open')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %{[br/]}Dalton Joe : 0.0 %")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="sumexpense_txt"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="name"]', 'BBB')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="budget_txt"]', '200.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="revenue_account"]', '705')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="cost_accounting"]', '---')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %{[br/]}Dalton Joe : 0.0 %")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="sumexpense_txt"]', "0.00€")

        self.factory.xfer = OwnerDel()
        self.call('/diacamma.condominium/ownerDel',
                  {'CONFIRME': 'YES', "owner": 3}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerDel')

        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 2)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %")

    def test_modify_partition(self):
        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "AAA", "budget": '1000', "revenue_account": '704', 'cost_accounting': 2}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setAddModify')
        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')
        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 5}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')
        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 7}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')

        self.factory.xfer = SetShow()
        self.call('/diacamma.condominium/setShow', {'set': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_count_equal('COMPONENTS/GRID[@name="partition"]/RECORD', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="partition"]/HEADER', 4)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="partition"]/ACTIONS/ACTION', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[1]/VALUE[@name="value"]', '0.00')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[1]/VALUE[@name="ratio"]', '0.0 %')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[1]/VALUE[@name="ventilated_txt"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[2]/VALUE[@name="value"]', '0.00')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[2]/VALUE[@name="ratio"]', '0.0 %')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[2]/VALUE[@name="ventilated_txt"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[3]/VALUE[@name="value"]', '0.00')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[3]/VALUE[@name="ratio"]', '0.0 %')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[2]/VALUE[@name="ventilated_txt"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_part"]', '0.00')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="sumexpense_txt"]', "0.00€")

        self.factory.xfer = PartitionAddModify()
        self.call(
            '/diacamma.condominium/partitionAddModify', {'partition': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'partitionAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)

        self.factory.xfer = PartitionAddModify()
        self.call(
            '/diacamma.condominium/partitionAddModify', {'partition': 1, 'SAVE': 'YES', 'value': 10}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'partitionAddModify')
        self.factory.xfer = PartitionAddModify()
        self.call(
            '/diacamma.condominium/partitionAddModify', {'partition': 2, 'SAVE': 'YES', 'value': 20}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'partitionAddModify')
        self.factory.xfer = PartitionAddModify()
        self.call(
            '/diacamma.condominium/partitionAddModify', {'partition': 3, 'SAVE': 'YES', 'value': 30}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'partitionAddModify')

        self.factory.xfer = SetShow()
        self.call('/diacamma.condominium/setShow', {'set': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setShow')
        self.assert_count_equal('COMPONENTS/GRID[@name="partition"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[1]/VALUE[@name="value"]', '10.00')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[1]/VALUE[@name="ratio"]', '16.7 %')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[2]/VALUE[@name="value"]', '20.00')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[2]/VALUE[@name="ratio"]', '33.3 %')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[3]/VALUE[@name="value"]', '30.00')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="partition"]/RECORD[3]/VALUE[@name="ratio"]', '50.0 %')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_part"]', '60.00')

        self.factory.xfer = SetOwnerList()
        self.call('/diacamma.condominium/setOwnerList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setOwnerList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', "Minimum : 16.7 %{[br/]}Dalton William : 33.3 %{[br/]}Dalton Joe : 50.0 %")
