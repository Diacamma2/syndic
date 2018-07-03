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

from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting,\
    default_compta_be, initial_thirds_be
from diacamma.accounting.views import ThirdShow
from diacamma.accounting.models import EntryAccount, FiscalYear
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.accounting.views_accounts import FiscalYearClose, FiscalYearBegin, FiscalYearReportLastYear
from diacamma.accounting.views_other import CostAccountingList

from diacamma.payoff.test_tools import default_bankaccount_fr, default_paymentmethod, PaymentTest,\
    default_bankaccount_be
from diacamma.payoff.views import PayableShow, PayableEmail

from diacamma.condominium.views_classload import SetList, SetAddModify, SetDel, SetShow, PartitionAddModify, CondominiumConf, SetClose
from diacamma.condominium.views import OwnerAndPropertyLotList, OwnerAdd, OwnerDel, OwnerShow, PropertyLotAddModify, CondominiumConvert
from diacamma.condominium.test_tools import default_setowner_fr, add_test_callfunds, old_accounting, add_test_expenses_fr, init_compta, add_years,\
    default_setowner_be
from diacamma.condominium.views_report import FinancialStatus, GeneralManageAccounting, CurrentManageAccounting, ExceptionalManageAccounting


class SetOwnerTest(LucteriosTest):

    def setUp(self):
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_bankaccount_fr()
        rmtree(get_user_dir(), True)

    def test_config(self):
        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('', 2 + 15 + 2)
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account1', '4501')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account2', '4502')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account3', '4503')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account4', '4504')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account5', '4505')
        self.assert_json_equal('LABELFORM', 'condominium-current-revenue-account', '701')
        self.assert_json_equal('LABELFORM', 'condominium-exceptional-revenue-account', '702')
        self.assert_json_equal('LABELFORM', 'condominium-fundforworks-revenue-account', '705')
        self.assert_json_equal('LABELFORM', 'condominium-exceptional-reserve-account', '120')
        self.assert_json_equal('LABELFORM', 'condominium-advance-reserve-account', '103')
        self.assert_json_equal('LABELFORM', 'condominium-fundforworks-reserve-account', '105')
        self.assert_json_equal('LABELFORM', 'condominium-mode-current-callfunds', 'trimestrielle')
        self.assert_count_equal('ownerlink', 4)

    def test_config_old_accounting(self):
        old_accounting()
        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('', 2 + 4 + 2)
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account', '450')

    def test_add_set(self):
        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 0)

        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 0)

        self.factory.xfer = SetAddModify()
        self.calljson('/diacamma.condominium/setAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setAddModify')
        self.assert_count_equal('', 4)

        self.factory.xfer = SetAddModify()
        self.calljson('/diacamma.condominium/setAddModify', {'SAVE': 'YES', "name": "abc123", 'type_load': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setAddModify')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {"set": 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_count_equal('', 10)

        self.factory.xfer = SetAddModify()
        self.calljson('/diacamma.condominium/setAddModify', {'SAVE': 'YES', "name": "xyz987", 'type_load': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setAddModify')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {"set": 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')

        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 2)
        self.assert_json_equal('', 'set/@0/identify', '[1] abc123')
        self.assert_json_equal('', 'set/@0/budget_txt', '0.00€')
        self.assert_json_equal('', 'set/@0/type_load', 'charge exceptionnelle')
        self.assert_json_equal('', 'set/@0/partitionfill_set', '')
        self.assert_json_equal('', 'set/@0/sumexpense_txt', "0.00€")
        self.assert_json_equal('', 'set/@1/identify', '[2] xyz987')
        self.assert_json_equal('', 'set/@1/budget_txt', '0.00€')
        self.assert_json_equal('', 'set/@1/type_load', 'charge courante')
        self.assert_json_equal('', 'set/@1/partitionfill_set', '')
        self.assert_json_equal('', 'set/@1/sumexpense_txt', "0.00€")

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 2)
        self.assert_json_equal('', 'costaccounting/@0/name', '[1] abc123')
        self.assert_json_equal('', 'costaccounting/@1/name', '[2] xyz987 2015')

        self.factory.xfer = SetDel()
        self.calljson('/diacamma.condominium/setDel', {'CONFIRME': 'YES', "set": 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setDel')

        self.factory.xfer = SetDel()
        self.calljson('/diacamma.condominium/setDel', {'CONFIRME': 'YES', "set": 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setDel')

        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 0)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 0)

    def test_add_owner(self):
        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 0)

        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAdd')
        self.assert_count_equal('', 4)
        self.assert_select_equal('third', 7)  # nb=7

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Minimum')
        self.assert_count_equal('accountthird', 2)
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@1/code', '401')

        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd',
                      {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 1)
        self.assert_json_equal('', 'owner/@0/third', 'Minimum')
        self.assert_json_equal('', 'owner/@0/thirdinitial', '0.00€')
        self.assert_json_equal('', 'owner/@0/total_all_call', '0.00€')
        self.assert_json_equal('', 'owner/@0/total_payoff', '0.00€')
        self.assert_json_equal('', 'owner/@0/thirdtotal', '0.00€')
        self.assert_json_equal('', 'owner/@0/sumtopay', '0.00€')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Minimum')
        self.assert_count_equal('accountthird', 7)
        self.assert_json_equal('', 'accountthird/@2/code', '4501')
        self.assert_json_equal('', 'accountthird/@3/code', '4502')
        self.assert_json_equal('', 'accountthird/@4/code', '4503')
        self.assert_json_equal('', 'accountthird/@5/code', '4504')
        self.assert_json_equal('', 'accountthird/@6/code', '4505')

        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAdd')
        self.assert_count_equal('', 4)
        self.assert_select_equal('third', 6)  # nb=6

        self.factory.xfer = OwnerDel()
        self.calljson('/diacamma.condominium/ownerDel',
                      {'CONFIRME': 'YES', "owner": 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerDel')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 0)

    def test_add_owner_old_accounting(self):
        old_accounting()
        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Minimum')
        self.assert_count_equal('accountthird', 2)
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@1/code', '401')

        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd',
                      {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Minimum')
        self.assert_count_equal('accountthird', 3)
        self.assert_json_equal('', 'accountthird/@2/code', '450')

    def test_add_propertylot(self):
        default_setowner_fr(with_lots=False)
        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 3)
        self.assert_grid_equal('propertylot', {"num": "N°", "value": "tantième", "ratio": "ratio", "description": "description", "owner": "propriétaire"}, 0)  # nb=5

        self.factory.xfer = PropertyLotAddModify()
        self.calljson('/diacamma.condominium/propertyLotAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'propertyLotAddModify')
        self.assert_count_equal('', 5)
        self.assert_select_equal('owner', 3)  # nb=3

        self.factory.xfer = PropertyLotAddModify()
        self.calljson('/diacamma.condominium/propertyLotAddModify',
                      {'SAVE': 'YES', "num": "1", "value": '100', "description": 'Apart A', 'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'propertyLotAddModify')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 3)
        self.assert_count_equal('propertylot', 1)
        self.assert_json_equal('', 'propertylot/@0/num', '1')
        self.assert_json_equal('', 'propertylot/@0/value', '100')
        self.assert_json_equal('', 'propertylot/@0/ratio', '100.0 %')
        self.assert_json_equal('', 'propertylot/@0/owner', 'Minimum')

        self.factory.xfer = PropertyLotAddModify()
        self.calljson('/diacamma.condominium/propertyLotAddModify',
                      {'SAVE': 'YES', "num": "2", "value": '150', "description": 'Apart B', 'owner': 2}, False)
        self.factory.xfer = PropertyLotAddModify()
        self.calljson('/diacamma.condominium/propertyLotAddModify',
                      {'SAVE': 'YES', "num": "3", "value": '125', "description": 'Apart B', 'owner': 3}, False)
        self.factory.xfer = PropertyLotAddModify()
        self.calljson('/diacamma.condominium/propertyLotAddModify',
                      {'SAVE': 'YES', "num": "4", "value": '15', "description": 'Cave A', 'owner': 1}, False)
        self.factory.xfer = PropertyLotAddModify()
        self.calljson('/diacamma.condominium/propertyLotAddModify',
                      {'SAVE': 'YES', "num": "5", "value": '15', "description": 'Cave A', 'owner': 2}, False)

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 3)
        self.assert_count_equal('propertylot', 5)
        self.assert_json_equal('', 'propertylot/@0/num', '1')
        self.assert_json_equal('', 'propertylot/@0/value', '100')
        self.assert_json_equal('', 'propertylot/@0/ratio', '24.7 %')
        self.assert_json_equal('', 'propertylot/@0/owner', 'Minimum')
        self.assert_json_equal('', 'propertylot/@1/num', '2')
        self.assert_json_equal('', 'propertylot/@1/value', '150')
        self.assert_json_equal('', 'propertylot/@1/ratio', '37.0 %')
        self.assert_json_equal('', 'propertylot/@1/owner', 'Dalton William')
        self.assert_json_equal('', 'propertylot/@2/num', '3')
        self.assert_json_equal('', 'propertylot/@2/value', '125')
        self.assert_json_equal('', 'propertylot/@2/ratio', '30.9 %')
        self.assert_json_equal('', 'propertylot/@2/owner', 'Dalton Joe')
        self.assert_json_equal('', 'propertylot/@3/num', '4')
        self.assert_json_equal('', 'propertylot/@3/value', '15')
        self.assert_json_equal('', 'propertylot/@3/ratio', '3.7 %')
        self.assert_json_equal('', 'propertylot/@3/owner', 'Minimum')
        self.assert_json_equal('', 'propertylot/@4/num', '5')
        self.assert_json_equal('', 'propertylot/@4/value', '15')
        self.assert_json_equal('', 'propertylot/@4/ratio', '3.7 %')
        self.assert_json_equal('', 'propertylot/@4/owner', 'Dalton William')

        self.assert_json_equal('', 'owner/@2/third', 'Minimum')
        self.assert_json_equal('', 'owner/@2/property_part', '115/405{[br/]}28.4 %')
        self.assert_json_equal('', 'owner/@1/third', 'Dalton William')
        self.assert_json_equal('', 'owner/@1/property_part', '165/405{[br/]}40.7 %')
        self.assert_json_equal('', 'owner/@0/third', 'Dalton Joe')
        self.assert_json_equal('', 'owner/@0/property_part', '125/405{[br/]}30.9 %')
        self.assert_json_equal('EDIT', 'filter', '')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {'filter': 'dalT'}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_json_equal('EDIT', 'filter', 'dalT')
        self.assert_count_equal('owner', 2)
        self.assert_json_equal('', 'owner/@1/third', 'Dalton William')
        self.assert_json_equal('', 'owner/@0/third', 'Dalton Joe')

    def test_show_partition(self):
        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 0)

        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 0)

        self.factory.xfer = SetAddModify()
        self.calljson('/diacamma.condominium/setAddModify',
                      {'SAVE': 'YES', "name": "AAA"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setAddModify')
        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd',
                      {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')
        self.factory.xfer = SetAddModify()
        self.calljson('/diacamma.condominium/setAddModify',
                      {'SAVE': 'YES', "name": "BBB"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setAddModify')
        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd',
                      {'SAVE': 'YES', "third": 5}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')
        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd',
                      {'SAVE': 'YES', "third": 7}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 3)

        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 2)
        self.assert_json_equal('', 'set/@0/identify', '[1] AAA')
        self.assert_json_equal('', 'set/@0/budget_txt', '0.00€')
        self.assert_json_equal('', 'set/@0/type_load', 'charge courante')
        self.assert_json_equal('', 'set/@0/partitionfill_set', "")
        self.assert_json_equal('', 'set/@0/sumexpense_txt', "0.00€")
        self.assert_json_equal('', 'set/@1/identify', '[2] BBB')
        self.assert_json_equal('', 'set/@1/budget_txt', '0.00€')
        self.assert_json_equal('', 'set/@1/type_load', 'charge courante')
        self.assert_json_equal('', 'set/@1/partitionfill_set', "")
        self.assert_json_equal('', 'set/@1/sumexpense_txt', "0.00€")

        self.factory.xfer = OwnerDel()
        self.calljson('/diacamma.condominium/ownerDel',
                      {'CONFIRME': 'YES', "owner": 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerDel')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 2)

    def test_modify_partition(self):
        self.factory.xfer = SetAddModify()
        self.calljson('/diacamma.condominium/setAddModify', {'SAVE': 'YES', "name": "AAA", "budget": '1000'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setAddModify')
        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd',
                      {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')
        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd', {'SAVE': 'YES', "third": 5}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')
        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd', {'SAVE': 'YES', "third": 7}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_count_equal('', 10)
        self.assert_grid_equal('partition', {"owner": "propriétaire", "value": "tantième", "ratio": "ratio", "ventilated_txt": "ventilé"}, 3)  # nb=4
        self.assert_json_equal('', 'partition/@0/value', '0.00')
        self.assert_json_equal('', 'partition/@0/owner', 'Minimum')
        self.assert_json_equal('', 'partition/@1/value', '0.00')
        self.assert_json_equal('', 'partition/@1/owner', 'Dalton William')
        self.assert_json_equal('', 'partition/@2/value', '0.00')
        self.assert_json_equal('', 'partition/@2/owner', 'Dalton Joe')
        self.assert_count_equal('#partition/actions', 1)
        self.assert_json_equal('LABELFORM', 'total_part', '0.00')
        self.assert_json_equal('LABELFORM', 'sumexpense_txt', "0.00€")
        self.assert_json_equal('LABELFORM', 'current_cost_accounting', "[1] AAA 2015")

        self.factory.xfer = PartitionAddModify()
        self.calljson('/diacamma.condominium/partitionAddModify', {'partition': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'partitionAddModify')
        self.assert_count_equal('', 4)

        self.factory.xfer = PartitionAddModify()
        self.calljson('/diacamma.condominium/partitionAddModify', {'partition': 1, 'SAVE': 'YES', 'value': 10}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'partitionAddModify')
        self.factory.xfer = PartitionAddModify()
        self.calljson('/diacamma.condominium/partitionAddModify', {'partition': 2, 'SAVE': 'YES', 'value': 20}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'partitionAddModify')
        self.factory.xfer = PartitionAddModify()
        self.calljson('/diacamma.condominium/partitionAddModify', {'partition': 3, 'SAVE': 'YES', 'value': 30}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'partitionAddModify')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_count_equal('partition', 3)
        self.assert_json_equal('', 'partition/@0/value', '10.00')
        self.assert_json_equal('', 'partition/@0/ratio', '16.7 %')
        self.assert_json_equal('', 'partition/@1/value', '20.00')
        self.assert_json_equal('', 'partition/@1/ratio', '33.3 %')
        self.assert_json_equal('', 'partition/@2/value', '30.00')
        self.assert_json_equal('', 'partition/@2/ratio', '50.0 %')
        self.assert_json_equal('LABELFORM', 'total_part', '60.00')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 3)

        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 1)
        self.assert_json_equal('', 'set/@0/partitionfill_set', "Minimum : 16.7 %{[br/]}Dalton William : 33.3 %{[br/]}Dalton Joe : 50.0 %")


class ReportTest(PaymentTest):

    def setUp(self):
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)
        add_years()
        init_compta()
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)

    def test_financial(self):
        self.factory.xfer = FinancialStatus()
        self.calljson('/diacamma.condominium/financialStatus', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'financialStatus')
        self.assert_count_equal('', 4)
        self.assert_count_equal('report_1', 17)
        self.assert_json_equal('', 'report_1/@1/left', '[512] 512')
        self.assert_json_equal('', 'report_1/@1/left_n', '16.84€')
        self.assert_json_equal('', 'report_1/@2/left', '[531] 531')
        self.assert_json_equal('', 'report_1/@2/left_n', '20.00€')

        self.assert_json_equal('', 'report_1/@7/left', '[4501 Minimum]')
        self.assert_json_equal('', 'report_1/@7/left_n', '7.80€')
        self.assert_json_equal('', 'report_1/@8/left', '[4501 Dalton William]')
        self.assert_json_equal('', 'report_1/@8/left_n', '87.50€')
        self.assert_json_equal('', 'report_1/@9/left', '[4501 Dalton Joe]')
        self.assert_json_equal('', 'report_1/@9/left_n', '56.25€')
        self.assert_json_equal('', 'report_1/@10/left', '[4502 Minimum]')
        self.assert_json_equal('', 'report_1/@10/left_n', '9.27€')
        self.assert_json_equal('', 'report_1/@11/left', '[4502 Dalton William]')
        self.assert_json_equal('', 'report_1/@11/left_n', '35.00€')
        self.assert_json_equal('', 'report_1/@12/left', '[4502 Dalton Joe]')
        self.assert_json_equal('', 'report_1/@12/left_n', '20.00€')

        self.assert_json_equal('', 'report_1/@1/right', '[120] 120')
        self.assert_json_equal('', 'report_1/@1/right_n', '25.00€')

        self.assert_json_equal('', 'report_1/@7/right', '[401 Maximum]')
        self.assert_json_equal('', 'report_1/@7/right_n', '65.00€')

    def test_general(self):
        self.factory.xfer = GeneralManageAccounting()
        self.calljson('/diacamma.condominium/generalManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'generalManageAccounting')
        self.assert_count_equal('', 6)
        self.assert_count_equal('report_1', 21)
        self.assert_json_equal('', 'report_1/@1/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@1/budget_n', '1100.00€')
        self.assert_json_equal('', 'report_1/@1/year_n', '100.00€')

        self.assert_json_equal('', 'report_1/@6/design', '[701] 701')
        self.assert_json_equal('', 'report_1/@6/budget_n', '1100.00€')
        self.assert_json_equal('', 'report_1/@6/year_n', '275.00€')

        self.assert_json_equal('', 'report_1/@11/design', '[602] 602')
        self.assert_json_equal('', 'report_1/@11/budget_n', '0.00€')
        self.assert_json_equal('', 'report_1/@11/year_n', '75.00€')
        self.assert_json_equal('', 'report_1/@12/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@12/budget_n', '500.00€')
        self.assert_json_equal('', 'report_1/@12/year_n', '0.00€')

        self.assert_json_equal('', 'report_1/@17/design', '[702] 702')
        self.assert_json_equal('', 'report_1/@17/budget_n', '500.00€')
        self.assert_json_equal('', 'report_1/@17/year_n', '75.00€')

    def test_current(self):
        self.factory.xfer = CurrentManageAccounting()
        self.calljson('/diacamma.condominium/currentManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'currentManageAccounting')
        self.assert_count_equal('', 6)
        self.assert_count_equal('report_1', 11)
        self.assert_json_equal('', 'report_1/@0/design', '&#160;&#160;&#160;&#160;&#160;{[u]}[1] AAA{[/u]}')
        self.assert_json_equal('', 'report_1/@1/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@1/budget_n', '1000.00€')
        self.assert_json_equal('', 'report_1/@1/year_n', '0.00€')
        self.assert_json_equal('', 'report_1/@3/design', '&#160;&#160;&#160;&#160;&#160;{[u]}total{[/u]}')

        self.assert_json_equal('', 'report_1/@5/design', '&#160;&#160;&#160;&#160;&#160;{[u]}[2] BBB{[/u]}')
        self.assert_json_equal('', 'report_1/@6/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@6/budget_n', '100.00€')
        self.assert_json_equal('', 'report_1/@6/year_n', '100.00€')
        self.assert_json_equal('', 'report_1/@8/design', '&#160;&#160;&#160;&#160;&#160;{[u]}total{[/u]}')
        self.assert_json_equal('', 'report_1/@10/design', '&#160;&#160;&#160;&#160;&#160;{[b]}total{[/b]}')
        self.assert_json_equal('', 'report_1/@10/budget_n', '{[b]}1100.00€{[/b]}')
        self.assert_json_equal('', 'report_1/@10/year_n', '{[b]}100.00€{[/b]}')

    def test_exceptionnal(self):
        self.factory.xfer = ExceptionalManageAccounting()
        self.calljson('/diacamma.condominium/exceptionalManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'exceptionalManageAccounting')
        self.assert_count_equal('', 3)
        self.assert_count_equal('report_1', 7)
        self.assert_json_equal('', 'report_1/@0/design', '&#160;&#160;&#160;&#160;&#160;{[u]}[3] CCC{[/u]}')
        self.assert_json_equal('', 'report_1/@1/design', '[602] 602')
        self.assert_json_equal('', 'report_1/@1/budget_n', '0.00€')
        self.assert_json_equal('', 'report_1/@1/year_n', '75.00€')
        self.assert_json_equal('', 'report_1/@2/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@2/budget_n', '500.00€')
        self.assert_json_equal('', 'report_1/@2/year_n', '0.00€')
        self.assert_json_equal('', 'report_1/@4/design', '&#160;&#160;&#160;&#160;&#160;{[u]}total{[/u]}')
        self.assert_json_equal('', 'report_1/@4/budget_n', '{[u]}500.00€{[/u]}')
        self.assert_json_equal('', 'report_1/@4/year_n', '{[u]}75.00€{[/u]}')
        self.assert_json_equal('', 'report_1/@4/calloffund', '{[u]}100.00€{[/u]}')
        self.assert_json_equal('', 'report_1/@4/result', '{[u]}25.00€{[/u]}')


class OwnerTest(PaymentTest):

    def setUp(self):
        # six.print_('>> %s' % self._testMethodName)
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_costaccounting()
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)

    def tearDown(self):
        LucteriosTest.tearDown(self)
        # six.print_('<< %s' % self._testMethodName)

    def test_payment_owner_empty(self):
        default_paymentmethod()
        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_owner', "0.00€")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow',
                      {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer('core.exception', 'diacamma.payoff', 'payableShow')
        self.assert_json_equal('', 'message', "Pas de paiement pour ce document")

    def test_payment_owner_nopayable(self):
        add_test_callfunds()
        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-131.25€")
        self.assert_json_equal('LABELFORM', 'thirdtotal', "-131.25€")
        self.assert_json_equal('LABELFORM', 'sumtopay', "131.25€")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow',
                      {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer('core.exception', 'diacamma.payoff', 'payableShow')
        self.assert_json_equal('', 'message', "Pas de paiement pour ce document")

    def test_payment_owner_topay(self):
        default_paymentmethod()
        add_test_callfunds()
        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', "0.00€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "0.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-131.25€")
        self.assertEqual(len(self.json_actions), 4)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.payoff', 'payableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow',
                      {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.assert_count_equal('', 13)
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-131.25€")
        self.check_payment(1, "copropriete de Minimum", "131.25")

    def __test_payment_paypal_owner(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(1, "copropriete de Minimum")

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', "0.00€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-31.25€")
        self.assert_json_equal('LABELFORM', 'thirdtotal', "31.25€")
        self.assert_json_equal('LABELFORM', 'sumtopay', "31.25€")
        self.assertEqual(len(self.json_actions), 4)

    def __test_payment_paypal_callfund(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(4, "appel de fonds pour Minimum")

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', "0.00€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-31.25€")
        self.assertEqual(len(self.json_actions), 4)

    def __test_send_owner(self):
        from lucterios.mailing.tests import configSMTP, TestReceiver
        default_paymentmethod()
        add_test_callfunds()
        configSMTP('localhost', 2025)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-131.25€")
        self.assertEqual(len(self.json_actions), 5)

        server = TestReceiver()
        server.start(2025)
        try:
            self.assertEqual(0, server.count())
            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail',
                          {'item_name': 'owner', 'owner': 1}, False)
            self.assert_observer('core.custom', 'diacamma.payoff', 'payableEmail')
            self.assert_count_equal('', 4)

            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail',
                          {'owner': 1, 'OK': 'YES', 'item_name': 'owner', 'subject': 'my bill', 'message': 'this is a bill.', 'model': 8}, False)
            self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payableEmail')
            self.assertEqual(1, server.count())
            self.assertEqual('mr-sylvestre@worldcompany.com', server.get(0)[1])
            self.assertEqual(['Minimum@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(0)[2])
            msg, msg_file = server.check_first_message('my bill', 2, {'To': 'Minimum@worldcompany.com'})
            self.assertEqual('text/html', msg.get_content_type())
            self.assertEqual('base64', msg.get('Content-Transfer-Encoding', ''))
            self.check_email_msg(msg, 1, "copropriete de Minimum", "131.25")

            self.assertTrue('copropriete_de_Minimum.pdf' in msg_file.get('Content-Type', ''), msg_file.get('Content-Type', ''))
            self.assertEqual("%PDF".encode('ascii', 'ignore'), b64decode(msg_file.get_payload())[:4])
        finally:
            server.stop()

    def test_check_operation(self):
        self.check_account(year_id=1, code='103', value=0.0)
        self.check_account(year_id=1, code='105', value=0.0)
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

        add_test_expenses_fr(False, True)
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
        self.check_account(year_id=1, code='105', value=0.0)
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
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_count_equal('', 45)
        self.assert_json_equal('LABELFORM', 'total_current_initial', "23.45€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-7.80€")
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', "75.00€")
        self.assert_json_equal('LABELFORM', 'total_current_regularization', "56.25€")
        self.assert_json_equal('LABELFORM', 'total_extra', "-5.55€")

        self.assert_grid_equal('exceptionnal', {"set": "catégorie de charges", "ratio": "ratio", "total_callfunds": "total des appels de fonds", "ventilated_txt": "ventilé", "total_current_regularization": "régularisation estimée"}, 1)  # nb=5
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', "45.0 %")
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', "45.00€")
        self.assert_json_equal('', 'exceptionnal/@0/ventilated_txt', "33.75€")
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', "11.25€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_initial', "5.73€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_call', "45.00€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_payoff', "30.00€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_owner', "-9.27€")

    def test_close_classload(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.check_account(year_id=1, code='120', value=25.0)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 350.00€ - {[b]}Charge :{[/b]} 187.34€ = {[b]}Résultat :{[/b]} 162.66€{[br/]}{[b]}Trésorerie :{[/b]} 36.84€ - {[b]}Validé :{[/b]} 16.84€{[/center]}')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_json_equal('LABELFORM', 'is_active', 'Oui')

        self.factory.xfer = SetClose()
        self.calljson('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'setClose')

        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = SetClose()
        self.calljson('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setClose')
        self.assert_count_equal('', 4)

        self.factory.xfer = SetClose()
        self.calljson('/diacamma.condominium/setClose', {'set': 3, 'ventilate': True, 'CLOSE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setClose')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_json_equal('LABELFORM', 'is_active', 'Non')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 350.00€ - {[b]}Charge :{[/b]} 187.34€ = {[b]}Résultat :{[/b]} 162.66€{[br/]}{[b]}Trésorerie :{[/b]} 36.84€ - {[b]}Validé :{[/b]} 36.84€{[/center]}')

        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[4502 Minimum]')
        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[4502 Dalton William]')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[4502 Dalton Joe]')

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
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin', {'CONFIRME': 'YES', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)
        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearClose')
        self.assert_json_equal('LABELFORM', 'title_condo', 'Cet exercice a un résultat non nul égal à 162.66€')
        self.assert_select_equal('ventilate', 7)  # nb=7

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose',
                      {'year': '1', 'type_of_account': '-1', 'CONFIRME': 'YES', 'ventilate': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.check_account(year_id=1, code='103', value=0.0)
        self.check_account(year_id=1, code='105', value=0.0)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=-11.11)
        self.check_account(year_id=1, code='4502', value=64.27)
        self.check_account(year_id=1, code='512', value=16.84)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='602', value=75.0)
        self.check_account(year_id=1, code='604', value=100.0)
        self.check_account(year_id=1, code='627', value=12.34)
        self.check_account(year_id=1, code='702', value=75.0)
        self.check_account(year_id=1, code='701', value=112.34)

        self.factory.xfer = FiscalYearReportLastYear()
        self.calljson('/diacamma.accounting/fiscalYearReportLastYear',
                      {'CONFIRME': 'YES', 'year': "2", 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearReportLastYear')

        self.check_account(year_id=2, code='103', value=None)
        self.check_account(year_id=1, code='105', value=0.0)
        self.check_account(year_id=2, code='110', value=None)
        self.check_account(year_id=2, code='119', value=None)
        self.check_account(year_id=2, code='120', value=25.0)
        self.check_account(year_id=1, code='129', value=None)
        self.check_account(year_id=2, code='401', value=65.0)
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
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin', {'CONFIRME': 'YES', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)
        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearClose')
        self.assert_json_equal('LABELFORM', 'title_condo', 'Cet exercice a un résultat non nul égal à 162.66€')
        self.assert_select_equal('ventilate', 7)  # nb=7

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose',
                      {'year': '1', 'type_of_account': '-1', 'CONFIRME': 'YES', 'ventilate': '23'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.check_account(year_id=1, code='103', value=162.66)
        self.check_account(year_id=1, code='105', value=0.0)
        self.check_account(year_id=1, code='110', value=0.0)
        self.check_account(year_id=1, code='119', value=0.0)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='129', value=None)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=151.55)
        self.check_account(year_id=1, code='4502', value=64.27)
        self.check_account(year_id=1, code='512', value=16.84)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='602', value=75.0)
        self.check_account(year_id=1, code='604', value=100.0)
        self.check_account(year_id=1, code='627', value=12.34)
        self.check_account(year_id=1, code='702', value=75.0)
        self.check_account(year_id=1, code='701', value=112.34)

        self.factory.xfer = FiscalYearReportLastYear()
        self.calljson('/diacamma.accounting/fiscalYearReportLastYear',
                      {'CONFIRME': 'YES', 'year': "2", 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearReportLastYear')

        self.check_account(year_id=2, code='103', value=162.66)
        self.check_account(year_id=1, code='105', value=0.0)
        self.check_account(year_id=2, code='110', value=None)
        self.check_account(year_id=2, code='119', value=None)
        self.check_account(year_id=2, code='120', value=25.0)
        self.check_account(year_id=1, code='129', value=None)
        self.check_account(year_id=2, code='401', value=65.0)
        self.check_account(year_id=2, code='4501', value=151.55)
        self.check_account(year_id=2, code='4502', value=64.27)
        self.check_account(year_id=2, code='512', value=16.84)
        self.check_account(year_id=2, code='531', value=20.0)
        self.check_account(year_id=2, code='602', value=None)
        self.check_account(year_id=2, code='604', value=None)
        self.check_account(year_id=2, code='627', value=None)
        self.check_account(year_id=2, code='701', value=None)
        self.check_account(year_id=2, code='702', value=None)


class OwnerBelgiumTest(PaymentTest):

    def setUp(self):
        # six.print_('>> %s' % self._testMethodName)
        initial_thirds_be()
        LucteriosTest.setUp(self)
        default_compta_be(with12=False)
        default_costaccounting()
        default_bankaccount_be()
        default_setowner_be()
        rmtree(get_user_dir(), True)

    def tearDown(self):
        LucteriosTest.tearDown(self)
        # six.print_('<< %s' % self._testMethodName)

    def test_owner_situation(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_count_equal('', 45)
        self.assert_json_equal('LABELFORM', 'third.custom_1', '')
        self.assert_json_equal('LABELFORM', 'third.custom_2', '')
        self.assert_json_equal('LABELFORM', 'total_current_initial', "23.45€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-7.80€")
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', "75.00€")
        self.assert_json_equal('LABELFORM', 'total_current_regularization', "56.25€")
        self.assert_json_equal('LABELFORM', 'total_extra', "-5.55€")

        self.assert_grid_equal('exceptionnal', {"set": "catégorie de charges", "ratio": "ratio", "total_callfunds": "total des appels de fonds", "ventilated_txt": "ventilé", "total_current_regularization": "régularisation estimée"}, 1)  # nb=5
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', "45.0 %")
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', "45.00€")
        self.assert_json_equal('', 'exceptionnal/@0/ventilated_txt', "33.75€")
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', "11.25€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_call', "45.00€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_payoff', "30.00€")


class OwnerTestOldAccounting(PaymentTest):

    def setUp(self):
        initial_thirds_fr()
        old_accounting()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_costaccounting()
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)

    def test_payment_paypal_owner(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(1, "copropriete de Minimum")

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', "0.00€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "100.00€")
        self.assert_json_equal('LABELFORM', 'thirdtotal', "100.00€")
        self.assert_json_equal('LABELFORM', 'sumtopay', "0.00€")
        self.assertFalse("total_current_regularization" in self.json_data.keys())
        self.assertEqual(len(self.json_actions), 4)

    def test_owner_situation(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', "23.45€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "44.70€")
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', "75.00€")
        self.assertFalse("total_current_regularization" in self.json_data.keys())
        self.assertFalse("total_extra" in self.json_data.keys())

        self.assert_count_equal('exceptionnal', 1)
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', "45.0 %")
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', "45.00€")
        self.assert_json_equal('', 'exceptionnal/@0/ventilated_txt', "33.75€")
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', "11.25€")
        self.assertFalse("total_exceptional_initial" in self.json_data.keys())
        self.assertFalse("total_exceptional_call" in self.json_data.keys())
        self.assertFalse("total_exceptional_payoff" in self.json_data.keys())
        self.assertFalse("total_exceptional_owner" in self.json_data.keys())

    def test_conversion(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = CondominiumConvert()
        self.calljson('/diacamma.condominium/condominiumConvert', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConvert')
        self.assert_count_equal('', 20)
        self.assert_attrib_equal('code_450', 'description', '450')
        self.assert_select_equal('code_450', 6)  # nb=6

        self.factory.xfer = CondominiumConvert()
        self.calljson('/diacamma.condominium/condominiumConvert', {'CONVERT': 'YES', 'code_450': '4501'}, False)
        self.assert_observer('core.dialogbox', 'diacamma.condominium', 'condominiumConvert')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', "23.45€")
        self.assert_json_equal('LABELFORM', 'total_current_call', "131.25€")
        self.assert_json_equal('LABELFORM', 'total_current_payoff', "100.00€")
        self.assert_json_equal('LABELFORM', 'total_current_owner', "-7.80€")
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', "75.00€")
        self.assert_json_equal('LABELFORM', 'total_current_regularization', "56.25€")
        self.assert_json_equal('LABELFORM', 'total_extra', "-5.55€")

        self.assert_count_equal('exceptionnal', 1)
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', "45.0 %")
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', "45.00€")
        self.assert_json_equal('', 'exceptionnal/@0/ventilated_txt', "33.75€")
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', "11.25€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_initial', "0.00€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_call', "45.00€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_payoff', "30.00€")
        self.assert_json_equal('LABELFORM', 'total_exceptional_owner', "-15.00€")

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
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 175.00€ - {[b]}Charge :{[/b]} 187.34€ = {[b]}Résultat :{[/b]} -12.34€{[br/]}{[b]}Trésorerie :{[/b]} 31.11€ - {[b]}Validé :{[/b]} 11.11€{[/center]}')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_json_equal('LABELFORM', 'is_active', 'Oui')

        self.factory.xfer = SetClose()
        self.calljson('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'setClose')

        for entry in EntryAccount.objects.filter(year_id=1, close=False):
            entry.closed()

        self.factory.xfer = SetClose()
        self.calljson('/diacamma.condominium/setClose', {'set': 3}, False)
        self.assert_observer('core.dialogbox', 'diacamma.condominium', 'setClose')

        self.factory.xfer = SetClose()
        self.calljson('/diacamma.condominium/setClose', {'set': 3, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'setClose')

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_json_equal('LABELFORM', 'is_active', 'Non')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 175.00€ - {[b]}Charge :{[/b]} 187.34€ = {[b]}Résultat :{[/b]} -12.34€{[br/]}{[b]}Trésorerie :{[/b]} 31.11€ - {[b]}Validé :{[/b]} 31.11€{[/center]}')
