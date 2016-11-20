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
from base64 import b64decode

from django.utils import six

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.test_tools import initial_thirds, default_compta, default_costaccounting
from diacamma.accounting.views import ThirdShow
from diacamma.accounting.models import EntryAccount, FiscalYear
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.accounting.views_accounts import FiscalYearClose, FiscalYearBegin, FiscalYearReportLastYear

from diacamma.payoff.test_tools import default_bankaccount, default_paymentmethod, PaymentTest
from diacamma.payoff.views import PayableShow, PayableEmail

from diacamma.condominium.views_classload import SetList, SetAddModify, SetDel, SetShow, PartitionAddModify, CondominiumConf, SetClose
from diacamma.condominium.views import OwnerAndPropertyLotList, OwnerAdd, OwnerDel, OwnerShow, PropertyLotAddModify, CondominiumConvert
from diacamma.condominium.test_tools import default_setowner, add_test_callfunds, old_accounting, add_test_expenses, init_compta,\
    add_years
from diacamma.condominium.views_report import FinancialStatus,\
    GeneralManageAccounting, CurrentManageAccounting,\
    ExceptionalManageAccounting


class SetOwnerTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_costaccounting()
        default_bankaccount()
        rmtree(get_user_dir(), True)

    def test_config(self):
        self.factory.xfer = CondominiumConf()
        self.call('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('COMPONENTS/*', 17)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-default-owner-account1"]', '4501')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-default-owner-account2"]', '4502')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-default-owner-account3"]', '4503')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-default-owner-account4"]', '4504')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-current-revenue-account"]', '701')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-exceptional-revenue-account"]', '702')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-exceptional-reserve-account"]', '120')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-advance-reserve-account"]', '103')

    def test_config_old_accounting(self):
        old_accounting()
        self.factory.xfer = CondominiumConf()
        self.call('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="condominium-default-owner-account"]', '450')

    def test_add_set(self):
        self.factory.xfer = SetList()
        self.call('/diacamma.condominium/setList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 5)

        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)

        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "abc123", "revenue_account": '704', 'type_load': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setAddModify')

        self.factory.xfer = SetList()
        self.call('/diacamma.condominium/setList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 5)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="name"]', 'abc123')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="budget_txt"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="type_load"]', 'charge exceptionnelle')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', None)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="sumexpense_txt"]', "0.00€")

        self.factory.xfer = SetDel()
        self.call('/diacamma.condominium/setDel',
                  {'CONFIRME': 'YES', "set": 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setDel')

        self.factory.xfer = SetList()
        self.call('/diacamma.condominium/setList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 5)

    def test_add_owner(self):
        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 8)

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

        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 8)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="third"]', 'Minimum')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_current_initial"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_current_call"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_current_payoff"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_current_ventilated"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_current_owner"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="total_current_regularization"]', '0.00€')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="contact"]', 'Minimum')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 6)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[3]/VALUE[@name="code"]', '4501')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[4]/VALUE[@name="code"]', '4502')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[5]/VALUE[@name="code"]', '4503')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[6]/VALUE[@name="code"]', '4504')

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

        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 8)

    def test_add_owner_old_accounting(self):
        old_accounting()
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

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="contact"]', 'Minimum')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[3]/VALUE[@name="code"]', '450')

    def test_add_propertylot(self):
        default_setowner(with_lots=False)
        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="propertylot"]/HEADER', 5)

        self.factory.xfer = PropertyLotAddModify()
        self.call('/diacamma.condominium/propertyLotAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'propertyLotAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_count_equal('COMPONENTS/SELECT[@name="owner"]/CASE', 3)

        self.factory.xfer = PropertyLotAddModify()
        self.call('/diacamma.condominium/propertyLotAddModify',
                  {'SAVE': 'YES', "num": "1", "value": '100', "description": 'Apart A', 'owner': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'propertyLotAddModify')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="propertylot"]/HEADER', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="value"]', '100')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="ratio"]', '100.0 %')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="owner"]', 'Minimum')

        self.factory.xfer = PropertyLotAddModify()
        self.call('/diacamma.condominium/propertyLotAddModify',
                  {'SAVE': 'YES', "num": "2", "value": '150', "description": 'Apart B', 'owner': 2}, False)
        self.factory.xfer = PropertyLotAddModify()
        self.call('/diacamma.condominium/propertyLotAddModify',
                  {'SAVE': 'YES', "num": "3", "value": '125', "description": 'Apart B', 'owner': 3}, False)
        self.factory.xfer = PropertyLotAddModify()
        self.call('/diacamma.condominium/propertyLotAddModify',
                  {'SAVE': 'YES', "num": "4", "value": '15', "description": 'Cave A', 'owner': 1}, False)
        self.factory.xfer = PropertyLotAddModify()
        self.call('/diacamma.condominium/propertyLotAddModify',
                  {'SAVE': 'YES', "num": "5", "value": '15', "description": 'Cave A', 'owner': 2}, False)

        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD', 5)
        self.assert_count_equal('COMPONENTS/GRID[@name="propertylot"]/HEADER', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="num"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="value"]', '100')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="ratio"]', '24.7 %')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[1]/VALUE[@name="owner"]', 'Minimum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[2]/VALUE[@name="num"]', '2')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[2]/VALUE[@name="value"]', '150')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[2]/VALUE[@name="ratio"]', '37.0 %')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[2]/VALUE[@name="owner"]', 'Dalton William')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[3]/VALUE[@name="num"]', '3')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[3]/VALUE[@name="value"]', '125')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[3]/VALUE[@name="ratio"]', '30.9 %')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[3]/VALUE[@name="owner"]', 'Dalton Joe')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[4]/VALUE[@name="num"]', '4')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[4]/VALUE[@name="value"]', '15')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[4]/VALUE[@name="ratio"]', '3.7 %')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[4]/VALUE[@name="owner"]', 'Minimum')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[5]/VALUE[@name="num"]', '5')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[5]/VALUE[@name="value"]', '15')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[5]/VALUE[@name="ratio"]', '3.7 %')
        self.assert_xml_equal('COMPONENTS/GRID[@name="propertylot"]/RECORD[5]/VALUE[@name="owner"]', 'Dalton William')

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="third"]', 'Minimum')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[1]/VALUE[@name="property_part"]', '115/405{[br/]}28.4 %')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[2]/VALUE[@name="third"]', 'Dalton William')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[2]/VALUE[@name="property_part"]', '165/405{[br/]}40.7 %')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[3]/VALUE[@name="third"]', 'Dalton Joe')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="owner"]/RECORD[3]/VALUE[@name="property_part"]', '125/405{[br/]}30.9 %')

    def test_show_partition(self):
        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/HEADER', 8)

        self.factory.xfer = SetList()
        self.call('/diacamma.condominium/setList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/HEADER', 5)

        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "AAA"}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'setAddModify')
        self.factory.xfer = OwnerAdd()
        self.call('/diacamma.condominium/ownerAddModify',
                  {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerAddModify')
        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "BBB"}, False)
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

        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 3)

        self.factory.xfer = SetList()
        self.call('/diacamma.condominium/setList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 2)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="name"]', 'AAA')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="budget_txt"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="type_load"]', 'charge courante')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %{[br/]}Dalton Joe : 0.0 %")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="sumexpense_txt"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="name"]', 'BBB')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="budget_txt"]', '0.00€')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="type_load"]', 'charge courante')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %{[br/]}Dalton Joe : 0.0 %")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="sumexpense_txt"]', "0.00€")

        self.factory.xfer = OwnerDel()
        self.call('/diacamma.condominium/ownerDel',
                  {'CONFIRME': 'YES', "owner": 3}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'ownerDel')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 2)

        self.factory.xfer = SetList()
        self.call('/diacamma.condominium/setList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 2)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[2]/VALUE[@name="partition_set"]', "Minimum : 0.0 %{[br/]}Dalton William : 0.0 %")

    def test_modify_partition(self):
        self.factory.xfer = SetAddModify()
        self.call('/diacamma.condominium/setAddModify',
                  {'SAVE': 'YES', "name": "AAA", "budget": '1000', "revenue_account": '704'}, False)
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
        self.assert_count_equal('COMPONENTS/*', 21)
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
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="current_cost_accounting"]', "AAA 2015")

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

        self.factory.xfer = OwnerAndPropertyLotList()
        self.call('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('COMPONENTS/GRID[@name="owner"]/RECORD', 3)

        self.factory.xfer = SetList()
        self.call('/diacamma.condominium/setList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('COMPONENTS/GRID[@name="set"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="set"]/RECORD[1]/VALUE[@name="partition_set"]', "Minimum : 16.7 %{[br/]}Dalton William : 33.3 %{[br/]}Dalton Joe : 50.0 %")


class ReportTest(PaymentTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_costaccounting()
        default_bankaccount()
        default_setowner()
        rmtree(get_user_dir(), True)
        add_years()

    def test_financial(self):
        self.factory.xfer = FinancialStatus()
        self.call('/diacamma.condominium/financialStatus', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'financialStatus')

    def test_general(self):
        self.factory.xfer = GeneralManageAccounting()
        self.call('/diacamma.condominium/generalManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'generalManageAccounting')

    def test_current(self):
        self.factory.xfer = CurrentManageAccounting()
        self.call('/diacamma.condominium/currentManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'currentManageAccounting')

    def test_exceptionnal(self):
        self.factory.xfer = ExceptionalManageAccounting()
        self.call('/diacamma.condominium/exceptionalManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'exceptionalManageAccounting')


class OwnerTest(PaymentTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_costaccounting()
        default_bankaccount()
        default_setowner()
        rmtree(get_user_dir(), True)

    def test_payment_owner_empty(self):
        default_paymentmethod()
        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "0.00€")
        self.assert_count_equal('ACTIONS/ACTION', 3)

        self.factory.xfer = PayableShow()
        self.call('/diacamma.payoff/supportingPaymentMethod',
                  {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer(
            'core.exception', 'diacamma.payoff', 'supportingPaymentMethod')
        self.assert_xml_equal(
            "EXCEPTION/MESSAGE", "Pas de paiement pour ce document")

    def test_payment_owner_nopayable(self):
        add_test_callfunds()
        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-131.25€")
        self.assert_count_equal('ACTIONS/ACTION', 3)

        self.factory.xfer = PayableShow()
        self.call('/diacamma.payoff/supportingPaymentMethod',
                  {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer(
            'core.exception', 'diacamma.payoff', 'supportingPaymentMethod')
        self.assert_xml_equal(
            "EXCEPTION/MESSAGE", "Pas de paiement pour ce document")

    def test_payment_owner_topay(self):
        default_paymentmethod()
        add_test_callfunds()
        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_initial"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_payoff"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-131.25€")
        self.assert_count_equal('ACTIONS/ACTION', 4)
        self.assert_action_equal('ACTIONS/ACTION[1]', (six.text_type(
            'Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.payoff', 'payableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.call('/diacamma.payoff/supportingPaymentMethod',
                  {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.payoff', 'supportingPaymentMethod')
        self.assert_count_equal('COMPONENTS/*', 20)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-131.25€")
        self.check_payment(1, "copropriete de Minimum", "131.25")

    def test_payment_paypal_owner(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(1, "copropriete de Minimum")

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_initial"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_payoff"]', "100.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-31.25€")
        self.assert_count_equal('ACTIONS/ACTION', 4)

    def test_payment_paypal_callfund(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(4, "appel de fonds pour Minimum")

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_initial"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_payoff"]', "100.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-31.25€")
        self.assert_count_equal('ACTIONS/ACTION', 4)

    def test_send_owner(self):
        from lucterios.mailing.tests import configSMTP, TestReceiver
        default_paymentmethod()
        add_test_callfunds()
        configSMTP('localhost', 1025)

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-131.25€")
        self.assert_count_equal('ACTIONS/ACTION', 5)

        server = TestReceiver()
        server.start(1025)
        try:
            self.assertEqual(0, server.count())
            self.factory.xfer = PayableEmail()
            self.call('/diacamma.payoff/payableEmail',
                      {'item_name': 'owner', 'owner': 1}, False)
            self.assert_observer(
                'core.custom', 'diacamma.payoff', 'payableEmail')
            self.assert_count_equal('COMPONENTS/*', 9)

            self.factory.xfer = PayableEmail()
            self.call('/diacamma.payoff/payableEmail',
                      {'owner': 1, 'OK': 'YES', 'item_name': 'owner', 'subject': 'my bill', 'message': 'this is a bill.', 'model': 8, 'withpayment': 1}, False)
            self.assert_observer(
                'core.acknowledge', 'diacamma.payoff', 'payableEmail')
            self.assertEqual(1, server.count())
            self.assertEqual(
                'mr-sylvestre@worldcompany.com', server.get(0)[1])
            self.assertEqual(
                ['Minimum@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(0)[2])
            msg, msg_file = server.check_first_message('my bill', 2, {'To': 'Minimum@worldcompany.com'})
            self.assertEqual('text/html', msg.get_content_type())
            self.assertEqual('base64', msg.get('Content-Transfer-Encoding', ''))
            self.check_email_msg(msg, 1, "copropriete de Minimum", "131.25")

            self.assertTrue(
                'copropriete_de_Minimum.pdf' in msg_file.get('Content-Type', ''), msg_file.get('Content-Type', ''))
            self.assertEqual(
                "%PDF".encode('ascii', 'ignore'), b64decode(msg_file.get_payload())[:4])
        finally:
            server.stop()

    def test_check_operation(self):
        self.check_account(year_id=1, code='103', value=0.0)
        self.check_account(year_id=1, code='120', value=0.0)
        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='4501', value=0.0)
        self.check_account(year_id=1, code='4502', value=0.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)
        self.check_account(year_id=1, code='701', value=0.0)
        self.check_account(year_id=1, code='702', value=0.0)

        add_test_callfunds(False, True)
        self.check_account(year_id=1, code='120', value=100.0)
        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='4501', value=175.0)
        self.check_account(year_id=1, code='4502', value=70.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=130.0)
        self.check_account(year_id=1, code='701', value=275.0)
        self.check_account(year_id=1, code='702', value=0.0)

        add_test_expenses(False, True)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=175.0)
        self.check_account(year_id=1, code='4502', value=70.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='701', value=275.0)
        self.check_account(year_id=1, code='702', value=75.0)

        init_compta()
        self.check_account(year_id=1, code='103', value=0.0)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=151.55)
        self.check_account(year_id=1, code='4502', value=64.27)
        self.check_account(year_id=1, code='512', value=16.84)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='602', value=75.0)
        self.check_account(year_id=1, code='604', value=100.0)
        self.check_account(year_id=1, code='627', value=12.34)
        self.check_account(year_id=1, code='701', value=275.0)
        self.check_account(year_id=1, code='702', value=75.0)

    def test_owner_situation(self):
        add_test_callfunds(False, True)
        add_test_expenses(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_initial"]', "23.45€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_payoff"]', "100.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-7.80€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_ventilated"]', "75.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_regularization"]', "56.25€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_extra"]', "-5.55€")

        self.assert_count_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="exceptionnal"]/HEADER', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="set"]', "CCC")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="ratio"]', "45.0 %")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="total_callfunds"]', "45.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="ventilated_txt"]', "33.75€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="total_current_regularization"]', "11.25€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_initial"]', "5.73€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_call"]', "45.00€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_payoff"]', "30.00€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_owner"]', "-9.27€")

    def test_close_classload(self):
        add_test_callfunds(False, True)
        add_test_expenses(False, True)
        init_compta()

        self.check_account(year_id=1, code='120', value=25.0)

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 350.00€ - {[b]}Charge:{[/b]} 187.34€ = {[b]}Résultat:{[/b]} 162.66€ | {[b]}Trésorie:{[/b]} 36.84€ - {[b]}Validé:{[/b]} 16.84€{[/center]}')

        self.factory.xfer = SetShow()
        self.call('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="is_active"]', 'Oui')

        self.factory.xfer = SetClose()
        self.call('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'setClose')

        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = SetClose()
        self.call('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setClose')
        self.assert_count_equal('COMPONENTS/*', 5)

        self.factory.xfer = SetClose()
        self.call('/diacamma.condominium/setClose', {'set': 3, 'ventilate': True, 'CLOSE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setClose')

        self.factory.xfer = SetShow()
        self.call('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="is_active"]', 'Non')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 2)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 350.00€ - {[b]}Charge:{[/b]} 187.34€ = {[b]}Résultat:{[/b]} 162.66€ | {[b]}Trésorie:{[/b]} 36.84€ - {[b]}Validé:{[/b]} 36.84€{[/center]}')

        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="costaccounting"]', 'CCC')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[4502 Minimum]' in description, description)
        self.assertTrue('[4502 Dalton William]' in description, description)
        self.assertTrue('[4502 Dalton Joe]' in description, description)
        self.assertTrue('[120] 120' in description, description)

        self.check_account(year_id=1, code='120', value=0.00)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=151.55)
        self.check_account(year_id=1, code='4502', value=39.27)
        self.check_account(year_id=1, code='512', value=16.84)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='701', value=275.0)
        self.check_account(year_id=1, code='702', value=75.0)

    def test_close_year_owner(self):
        add_test_callfunds(False, True)
        add_test_expenses(False, True)
        init_compta()

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'CONFIRME': 'YES', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)
        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearClose',
                  {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearClose')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="title_condo"]', 'Cet exercice a un résultat non nul égal à 162.66€')
        self.assert_count_equal('COMPONENTS/SELECT[@name="ventilate"]/CASE', 6)

        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearClose',
                  {'year': '1', 'type_of_account': '-1', 'CONFIRME': 'YES', 'ventilate': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.check_account(year_id=1, code='103', value=0.0)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=0.0)
        self.check_account(year_id=1, code='4502', value=0.0)
        self.check_account(year_id=1, code='450', value=53.16)
        self.check_account(year_id=1, code='512', value=16.84)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='602', value=75.0)
        self.check_account(year_id=1, code='604', value=100.0)
        self.check_account(year_id=1, code='627', value=12.34)
        self.check_account(year_id=1, code='702', value=75.0)
        self.check_account(year_id=1, code='701', value=112.34)

        self.factory.xfer = FiscalYearReportLastYear()
        self.call('/diacamma.accounting/fiscalYearReportLastYear',
                  {'CONFIRME': 'YES', 'year': "2", 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearReportLastYear')

        self.check_account(year_id=2, code='103', value=None)
        self.check_account(year_id=2, code='110', value=None)
        self.check_account(year_id=2, code='119', value=None)
        self.check_account(year_id=2, code='120', value=25.0)
        self.check_account(year_id=1, code='129', value=None)
        self.check_account(year_id=2, code='401', value=65.0)
        self.check_account(year_id=2, code='450', value=0.0)
        self.check_account(year_id=2, code='4501', value=-11.11)
        self.check_account(year_id=2, code='4502', value=64.27)
        self.check_account(year_id=2, code='512', value=16.84)
        self.check_account(year_id=2, code='531', value=20.0)
        self.check_account(year_id=2, code='602', value=None)
        self.check_account(year_id=2, code='604', value=None)
        self.check_account(year_id=2, code='627', value=None)
        self.check_account(year_id=2, code='701', value=None)
        self.check_account(year_id=2, code='702', value=None)

    def test_close_year_reserve(self):
        add_test_callfunds(False, True)
        add_test_expenses(False, True)
        init_compta()

        self.factory.xfer = FiscalYearBegin()
        self.call('/diacamma.accounting/fiscalYearBegin', {'CONFIRME': 'YES', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)
        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearClose',
                  {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearClose')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="title_condo"]', 'Cet exercice a un résultat non nul égal à 162.66€')
        self.assert_count_equal('COMPONENTS/SELECT[@name="ventilate"]/CASE', 6)

        self.factory.xfer = FiscalYearClose()
        self.call('/diacamma.accounting/fiscalYearClose',
                  {'year': '1', 'type_of_account': '-1', 'CONFIRME': 'YES', 'ventilate': '22'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.check_account(year_id=1, code='103', value=162.66)
        self.check_account(year_id=1, code='110', value=0.0)
        self.check_account(year_id=1, code='119', value=0.0)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='129', value=None)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=0.0)
        self.check_account(year_id=1, code='4502', value=0.0)
        self.check_account(year_id=1, code='450', value=215.82)
        self.check_account(year_id=1, code='512', value=16.84)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='602', value=75.0)
        self.check_account(year_id=1, code='604', value=100.0)
        self.check_account(year_id=1, code='627', value=12.34)
        self.check_account(year_id=1, code='702', value=75.0)
        self.check_account(year_id=1, code='701', value=112.34)

        self.factory.xfer = FiscalYearReportLastYear()
        self.call('/diacamma.accounting/fiscalYearReportLastYear',
                  {'CONFIRME': 'YES', 'year': "2", 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearReportLastYear')

        self.check_account(year_id=2, code='103', value=162.66)
        self.check_account(year_id=2, code='110', value=None)
        self.check_account(year_id=2, code='119', value=None)
        self.check_account(year_id=2, code='120', value=25.0)
        self.check_account(year_id=1, code='129', value=None)
        self.check_account(year_id=2, code='401', value=65.0)
        self.check_account(year_id=2, code='450', value=0.0)
        self.check_account(year_id=2, code='4501', value=151.55)
        self.check_account(year_id=2, code='4502', value=64.27)
        self.check_account(year_id=2, code='512', value=16.84)
        self.check_account(year_id=2, code='531', value=20.0)
        self.check_account(year_id=2, code='602', value=None)
        self.check_account(year_id=2, code='604', value=None)
        self.check_account(year_id=2, code='627', value=None)
        self.check_account(year_id=2, code='701', value=None)
        self.check_account(year_id=2, code='702', value=None)


class OwnerTestOldAccounting(PaymentTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        old_accounting()
        LucteriosTest.setUp(self)
        default_compta()
        default_costaccounting()
        default_bankaccount()
        default_setowner()
        rmtree(get_user_dir(), True)

    def test_payment_paypal_owner(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(1, "copropriete de Minimum")

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_initial"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_payoff"]', "100.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "100.00€")
        self.assert_count_equal(
            'COMPONENTS/LABELFORM[@name="total_current_regularization"]', 0)
        self.assert_count_equal('ACTIONS/ACTION', 4)

    def test_owner_situation(self):
        add_test_callfunds(False, True)
        add_test_expenses(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_current_initial"]', "23.45€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_current_call"]', "131.25€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_current_payoff"]', "100.00€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_current_owner"]', "44.70€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_current_ventilated"]', "75.00€")
        self.assert_count_equal('COMPONENTS/LABELFORM[@name="total_current_regularization"]', 0)
        self.assert_count_equal('COMPONENTS/LABELFORM[@name="total_extra"]', 0)

        self.assert_count_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="exceptionnal"]/HEADER', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="set"]', "CCC")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="ratio"]', "45.0 %")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="total_callfunds"]', "45.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="ventilated_txt"]', "33.75€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="total_current_regularization"]', "11.25€")
        self.assert_count_equal('COMPONENTS/LABELFORM[@name="total_exceptional_initial"]', 0)
        self.assert_count_equal('COMPONENTS/LABELFORM[@name="total_exceptional_call"]', 0)
        self.assert_count_equal('COMPONENTS/LABELFORM[@name="total_exceptional_payoff"]', 0)
        self.assert_count_equal('COMPONENTS/LABELFORM[@name="total_exceptional_owner"]', 0)

    def test_conversion(self):
        add_test_callfunds(False, True)
        add_test_expenses(False, True)
        init_compta()

        self.factory.xfer = CondominiumConvert()
        self.call('/diacamma.condominium/condominiumConvert', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConvert')
        self.assert_count_equal('COMPONENTS/*', 25)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_code_450"]', "{[b]}450{[/b]}")
        self.assert_count_equal('COMPONENTS/SELECT[@name="code_450"]/CASE', 5)

        self.factory.xfer = CondominiumConvert()
        self.call('/diacamma.condominium/condominiumConvert', {'CONVERT': 'YES', 'code_450': '4501'}, False)
        self.assert_observer('core.dialogbox', 'diacamma.condominium', 'condominiumConvert')

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_initial"]', "23.45€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_payoff"]', "100.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_owner"]', "-7.80€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_ventilated"]', "75.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_current_regularization"]', "56.25€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_extra"]', "-5.55€")

        self.assert_count_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="exceptionnal"]/HEADER', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="set"]', "CCC")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="ratio"]', "45.0 %")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="total_callfunds"]', "45.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="ventilated_txt"]', "33.75€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="exceptionnal"]/RECORD[1]/VALUE[@name="total_current_regularization"]', "11.25€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_initial"]', "0.00€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_call"]', "45.00€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_payoff"]', "30.00€")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total_exceptional_owner"]', "-15.00€")

        self.check_account(year_id=1, code='120', value=25.00)
        self.check_account(year_id=1, code='401', value=65.00)
        self.check_account(year_id=1, code='4501', value=151.55)
        self.check_account(year_id=1, code='4502', value=70.00)
        self.check_account(year_id=1, code='512', value=11.11)
        self.check_account(year_id=1, code='531', value=20.00)
        self.check_account(year_id=1, code='701', value=275.00)
        self.check_account(year_id=1, code='702', value=75.00)

    def test_close_classload(self):
        add_test_callfunds(False, True)
        add_test_expenses(False, True)
        init_compta()

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 175.00€ - {[b]}Charge:{[/b]} 187.34€ = {[b]}Résultat:{[/b]} -12.34€ | {[b]}Trésorie:{[/b]} 31.11€ - {[b]}Validé:{[/b]} 11.11€{[/center]}')

        self.factory.xfer = SetShow()
        self.call('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="is_active"]', 'Oui')

        self.factory.xfer = SetClose()
        self.call('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'setClose')

        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = SetClose()
        self.call('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.dialogbox', 'diacamma.condominium', 'setClose')

        self.factory.xfer = SetClose()
        self.call('/diacamma.condominium/setClose', {'set': 3, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setClose')

        self.factory.xfer = SetShow()
        self.call('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="is_active"]', 'Non')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 175.00€ - {[b]}Charge:{[/b]} 187.34€ = {[b]}Résultat:{[/b]} -12.34€ | {[b]}Trésorie:{[/b]} 31.11€ - {[b]}Validé:{[/b]} 31.11€{[/center]}')
