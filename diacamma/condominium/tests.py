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

from django.utils import six

from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir
from lucterios.framework.models import LucteriosScheduler

from lucterios.mailing.models import Message
from lucterios.mailing.test_tools import decode_b64

from diacamma.accounting.models import EntryAccount, FiscalYear
from diacamma.accounting.views import ThirdShow
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.accounting.views_accounts import FiscalYearClose, FiscalYearBegin, FiscalYearReportLastYear
from diacamma.accounting.views_other import CostAccountingList
from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting, default_compta_be, initial_thirds_be

from diacamma.payoff.models import Payoff
from diacamma.payoff.views import PayableShow, PayableEmail, PayoffAddModify
from diacamma.payoff.test_tools import default_bankaccount_fr, default_paymentmethod, PaymentTest, default_bankaccount_be

from diacamma.condominium.views_classload import SetList, SetAddModify, SetDel, SetShow, PartitionAddModify, CondominiumConf, SetClose,\
    OwnerLinkAddModify, OwnerLinkDel, RecoverableLoadRatioAddModify,\
    RecoverableLoadRatioDel
from diacamma.condominium.views import OwnerAndPropertyLotList, OwnerAdd, OwnerDel, OwnerShow, PropertyLotAddModify, CondominiumConvert, OwnerVentilatePay,\
    OwnerLoadCount, OwnerMultiPay, OwnerPayableEmail
from diacamma.condominium.views_report import FinancialStatus, GeneralManageAccounting, CurrentManageAccounting, ExceptionalManageAccounting
from diacamma.condominium.test_tools import default_setowner_fr, add_test_callfunds, old_accounting, add_test_expenses_fr, init_compta, add_years, default_setowner_be, add_test_expenses_be


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
        self.assert_count_equal('', 2 + 15 + 2 + 2)
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

    def test_config_old_accounting(self):
        old_accounting()
        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('', 2 + 4 + 2 + 2)
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account', '450')

    def test_config_owner_link(self):
        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('ownerlink', 4)

        self.factory.xfer = OwnerLinkAddModify()
        self.calljson('/diacamma.condominium/ownerLinkAddModify', {'SAVE': 'YES', 'name': 'ami'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerLinkAddModify')

        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('ownerlink', 5)
        self.assert_json_equal('', 'ownerlink/@4/id', '5')
        self.assert_json_equal('', 'ownerlink/@4/name', 'ami')

        self.factory.xfer = OwnerLinkDel()
        self.calljson('/diacamma.condominium/ownerLinkDel', {'CONFIRME': 'YES', 'ownerlink': '5'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerLinkDel')

        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('ownerlink', 4)

        self.factory.xfer = OwnerLinkDel()
        self.calljson('/diacamma.condominium/ownerLinkDel', {'ownerlink': '1'}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'ownerLinkDel')
        self.assert_json_equal('', 'message', "Cet nature de relation n'est pas supprimable !")

        self.factory.xfer = OwnerLinkDel()
        self.calljson('/diacamma.condominium/ownerLinkDel', {'ownerlink': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'ownerLinkDel')
        self.assert_json_equal('', 'message', "Cet nature de relation n'est pas supprimable !")

        self.factory.xfer = OwnerLinkDel()
        self.calljson('/diacamma.condominium/ownerLinkDel', {'CONFIRME': 'YES', 'ownerlink': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerLinkDel')

        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('ownerlink', 3)

    def test_config_recoverableloadratio(self):
        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('recoverableloadratio', 0)

        self.factory.xfer = RecoverableLoadRatioAddModify()
        self.calljson('/diacamma.condominium/recoverableLoadRatioAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'recoverableLoadRatioAddModify')
        self.assert_count_equal('', 3)
        self.assert_select_equal('code', {'601': '[601] 601', '602': '[602] 602', '604': '[604] 604', '607': '[607] 607', '627': '[627] 627'})
        self.assert_json_equal('FLOAT', 'ratio', '100')

        self.factory.xfer = RecoverableLoadRatioAddModify()
        self.calljson('/diacamma.condominium/recoverableLoadRatioAddModify', {'SAVE': 'YES', 'code': '602', 'ratio': 40}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'recoverableLoadRatioAddModify')

        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('recoverableloadratio', 1)
        self.assert_json_equal('', 'recoverableloadratio/@0/code_txt', '[602] 602')
        self.assert_json_equal('', 'recoverableloadratio/@0/ratio', '40')

        self.factory.xfer = RecoverableLoadRatioAddModify()
        self.calljson('/diacamma.condominium/recoverableLoadRatioAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'recoverableLoadRatioAddModify')
        self.assert_count_equal('', 3)
        self.assert_select_equal('code', {'601': '[601] 601', '604': '[604] 604', '607': '[607] 607', '627': '[627] 627'})
        self.assert_json_equal('FLOAT', 'ratio', '100')

        self.factory.xfer = RecoverableLoadRatioDel()
        self.calljson('/diacamma.condominium/recoverableLoadRatioDel', {'CONFIRME': 'YES', 'recoverableloadratio': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'recoverableLoadRatioDel')

        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('recoverableloadratio', 0)

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
        self.assert_json_equal('', 'set/@0/budget_txt', 0.00)
        self.assert_json_equal('', 'set/@0/type_load', 1)
        self.assert_json_equal('', 'set/@0/partitionfill_set', [])
        self.assert_json_equal('', 'set/@0/sumexpense', 0.00)
        self.assert_json_equal('', 'set/@1/identify', '[2] xyz987')
        self.assert_json_equal('', 'set/@1/budget_txt', 0.00)
        self.assert_json_equal('', 'set/@1/type_load', 0)
        self.assert_json_equal('', 'set/@1/partitionfill_set', [])
        self.assert_json_equal('', 'set/@1/sumexpense', 0.00)

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
        self.assert_json_equal('', 'owner/@0/thirdinitial', 0.00)
        self.assert_json_equal('', 'owner/@0/total_all_call', 0.00)
        self.assert_json_equal('', 'owner/@0/total_payoff', 0.00)
        self.assert_json_equal('', 'owner/@0/thirdtotal', 0.00)
        self.assert_json_equal('', 'owner/@0/sumtopay', 0.00)

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
        self.assert_json_equal('', 'propertylot/@0/value', 100.0)
        self.assert_json_equal('', 'propertylot/@0/ratio', 100.0)
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
        self.assert_json_equal('', 'propertylot/@0/ratio', 24.69)
        self.assert_json_equal('', 'propertylot/@0/owner', 'Minimum')
        self.assert_json_equal('', 'propertylot/@1/num', '2')
        self.assert_json_equal('', 'propertylot/@1/value', '150')
        self.assert_json_equal('', 'propertylot/@1/ratio', 37.04)
        self.assert_json_equal('', 'propertylot/@1/owner', 'Dalton William')
        self.assert_json_equal('', 'propertylot/@2/num', '3')
        self.assert_json_equal('', 'propertylot/@2/value', '125')
        self.assert_json_equal('', 'propertylot/@2/ratio', 30.86)
        self.assert_json_equal('', 'propertylot/@2/owner', 'Dalton Joe')
        self.assert_json_equal('', 'propertylot/@3/num', '4')
        self.assert_json_equal('', 'propertylot/@3/value', '15')
        self.assert_json_equal('', 'propertylot/@3/ratio', 3.70)
        self.assert_json_equal('', 'propertylot/@3/owner', 'Minimum')
        self.assert_json_equal('', 'propertylot/@4/num', '5')
        self.assert_json_equal('', 'propertylot/@4/value', '15')
        self.assert_json_equal('', 'propertylot/@4/ratio', 3.70)
        self.assert_json_equal('', 'propertylot/@4/owner', 'Dalton William')

        self.assert_json_equal('', 'owner/@2/third', 'Minimum')
        self.assert_json_equal('', 'owner/@2/property_part', [115, 405, 28.40])
        self.assert_json_equal('', 'owner/@1/third', 'Dalton William')
        self.assert_json_equal('', 'owner/@1/property_part', [165, 405, 40.74])
        self.assert_json_equal('', 'owner/@0/third', 'Dalton Joe')
        self.assert_json_equal('', 'owner/@0/property_part', [125, 405, 30.86])
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
        self.assert_json_equal('', 'set/@0/budget_txt', 0.00)
        self.assert_json_equal('', 'set/@0/type_load', 0)
        self.assert_json_equal('', 'set/@0/partitionfill_set', [])
        self.assert_json_equal('', 'set/@0/sumexpense', 0.00)
        self.assert_json_equal('', 'set/@1/identify', '[2] BBB')
        self.assert_json_equal('', 'set/@1/budget_txt', 0.00)
        self.assert_json_equal('', 'set/@1/type_load', 0)
        self.assert_json_equal('', 'set/@1/partitionfill_set', [])
        self.assert_json_equal('', 'set/@1/sumexpense', 0.00)

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
        self.assert_grid_equal('partition', {"owner": "propriétaire", "value": "tantième", "ratio": "ratio", "ventilated": "ventilé"}, 3)  # nb=4
        self.assert_json_equal('', 'partition/@0/value', '0.00')
        self.assert_json_equal('', 'partition/@0/owner', 'Minimum')
        self.assert_json_equal('', 'partition/@1/value', '0.00')
        self.assert_json_equal('', 'partition/@1/owner', 'Dalton William')
        self.assert_json_equal('', 'partition/@2/value', '0.00')
        self.assert_json_equal('', 'partition/@2/owner', 'Dalton Joe')
        self.assert_count_equal('#partition/actions', 1)
        self.assert_json_equal('LABELFORM', 'total_part', 0.0)
        self.assert_json_equal('LABELFORM', 'sumexpense', 0.0)
        self.assert_json_equal('', '#total_part/formatnum', "N2")
        self.assert_json_equal('', '#sumexpense/formatnum', "C2EUR")
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
        self.assert_json_equal('', 'partition/@0/ratio', 16.67)
        self.assert_json_equal('', 'partition/@1/value', '20.00')
        self.assert_json_equal('', 'partition/@1/ratio', 33.33)
        self.assert_json_equal('', 'partition/@2/value', '30.00')
        self.assert_json_equal('', 'partition/@2/ratio', 50.0)
        self.assert_json_equal('LABELFORM', 'total_part', 60.0)

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 3)

        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 1)
        self.assert_json_equal('', 'set/@0/partitionfill_set', ["Minimum : 16,7 %", "Dalton William : 33,3 %", "Dalton Joe : 50,0 %"])


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
        self.assert_json_equal('', 'report_1/@1/left_n', 4.34)
        self.assert_json_equal('', 'report_1/@2/left', '[531] 531')
        self.assert_json_equal('', 'report_1/@2/left_n', 20.00)

        self.assert_json_equal('', 'report_1/@7/left', '[4501 Minimum]')
        self.assert_json_equal('', 'report_1/@7/left_n', 7.80)
        self.assert_json_equal('', 'report_1/@8/left', '[4501 Dalton William]')
        self.assert_json_equal('', 'report_1/@8/left_n', 100.00)
        self.assert_json_equal('', 'report_1/@9/left', '[4501 Dalton Joe]')
        self.assert_json_equal('', 'report_1/@9/left_n', 56.25)
        self.assert_json_equal('', 'report_1/@10/left', '[4502 Minimum]')
        self.assert_json_equal('', 'report_1/@10/left_n', 9.27)
        self.assert_json_equal('', 'report_1/@11/left', '[4502 Dalton William]')
        self.assert_json_equal('', 'report_1/@11/left_n', 35.00)
        self.assert_json_equal('', 'report_1/@12/left', '[4502 Dalton Joe]')
        self.assert_json_equal('', 'report_1/@12/left_n', 20.00)

        self.assert_json_equal('', 'report_1/@1/right', '[120] 120')
        self.assert_json_equal('', 'report_1/@1/right_n', 25.00)

        self.assert_json_equal('', 'report_1/@7/right', '[401 Maximum]')
        self.assert_json_equal('', 'report_1/@7/right_n', 65.00)

    def test_general(self):
        self.factory.xfer = GeneralManageAccounting()
        self.calljson('/diacamma.condominium/generalManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'generalManageAccounting')
        self.assert_count_equal('', 6)
        self.assert_count_equal('report_1', 21)
        self.assert_json_equal('', 'report_1/@1/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@1/budget_n', 1100.00)
        self.assert_json_equal('', 'report_1/@1/year_n', 100.00)

        self.assert_json_equal('', 'report_1/@6/design', '[701] 701')
        self.assert_json_equal('', 'report_1/@6/budget_n', 1100.00)
        self.assert_json_equal('', 'report_1/@6/year_n', 275.00)

        self.assert_json_equal('', 'report_1/@11/design', '[602] 602')
        self.assert_json_equal('', 'report_1/@11/budget_n', "")
        self.assert_json_equal('', 'report_1/@11/year_n', 75.00)
        self.assert_json_equal('', 'report_1/@12/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@12/budget_n', 500.00)
        self.assert_json_equal('', 'report_1/@12/year_n', "")

        self.assert_json_equal('', 'report_1/@17/design', '[702] 702')
        self.assert_json_equal('', 'report_1/@17/budget_n', 500.00)
        self.assert_json_equal('', 'report_1/@17/year_n', 75.00)

    def test_current(self):
        self.factory.xfer = CurrentManageAccounting()
        self.calljson('/diacamma.condominium/currentManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'currentManageAccounting')
        self.assert_count_equal('', 6)
        self.assert_count_equal('report_1', 11)
        self.assert_json_equal('', 'report_1/@0/design', '&#160;&#160;&#160;&#160;&#160;{[u]}[1] AAA{[/u]}')
        self.assert_json_equal('', 'report_1/@1/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@1/budget_n', 1000.00)
        self.assert_json_equal('', 'report_1/@1/year_n', "")
        self.assert_json_equal('', 'report_1/@3/design', '&#160;&#160;&#160;&#160;&#160;{[u]}total{[/u]}')

        self.assert_json_equal('', 'report_1/@5/design', '&#160;&#160;&#160;&#160;&#160;{[u]}[2] BBB{[/u]}')
        self.assert_json_equal('', 'report_1/@6/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@6/budget_n', 100.00)
        self.assert_json_equal('', 'report_1/@6/year_n', 100.00)
        self.assert_json_equal('', 'report_1/@8/design', '&#160;&#160;&#160;&#160;&#160;{[u]}total{[/u]}')
        self.assert_json_equal('', 'report_1/@10/design', '&#160;&#160;&#160;&#160;&#160;{[b]}total{[/b]}')
        self.assert_json_equal('', 'report_1/@10/budget_n', {'value': 1100.0, 'format': '{[b]}{0}{[/b]}'})
        self.assert_json_equal('', 'report_1/@10/year_n', {'value': 100.0, 'format': '{[b]}{0}{[/b]}'})

    def test_exceptionnal(self):
        self.factory.xfer = ExceptionalManageAccounting()
        self.calljson('/diacamma.condominium/exceptionalManageAccounting', {'year': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'exceptionalManageAccounting')
        self.assert_count_equal('', 3)
        self.assert_count_equal('report_1', 7)
        self.assert_json_equal('', 'report_1/@0/design', '&#160;&#160;&#160;&#160;&#160;{[u]}[3] CCC{[/u]}')
        self.assert_json_equal('', 'report_1/@1/design', '[602] 602')
        self.assert_json_equal('', 'report_1/@1/budget_n', '')
        self.assert_json_equal('', 'report_1/@1/year_n', 75.00)
        self.assert_json_equal('', 'report_1/@2/design', '[604] 604')
        self.assert_json_equal('', 'report_1/@2/budget_n', 500.00)
        self.assert_json_equal('', 'report_1/@2/year_n', '')
        self.assert_json_equal('', 'report_1/@4/design', '&#160;&#160;&#160;&#160;&#160;{[u]}total{[/u]}')
        self.assert_json_equal('', 'report_1/@4/budget_n', {'value': 500.0, 'format': '{[u]}{0}{[/u]}'})
        self.assert_json_equal('', 'report_1/@4/year_n', {'value': 75.0, 'format': '{[u]}{0}{[/u]}'})
        self.assert_json_equal('', 'report_1/@4/calloffund', {'value': 100.0, 'format': '{[u]}{0}{[/u]}'})
        self.assert_json_equal('', 'report_1/@4/result', {'value': 25.0, 'format': '{[u]}{0}{[/u]}'})


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
        self.assert_json_equal('LABELFORM', 'total_current_owner', 0.00)
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
        self.assert_json_equal('LABELFORM', 'total_current_owner', -131.25)
        self.assert_json_equal('LABELFORM', 'thirdtotal', -131.25)
        self.assert_json_equal('LABELFORM', 'sumtopay', 131.25)
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
        self.assert_json_equal('LABELFORM', 'total_current_initial', 0.00)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 0.00)
        self.assert_json_equal('LABELFORM', 'total_current_owner', -131.25)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_action_equal(self.json_actions[2], (six.text_type('Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.condominium', 'ownerPayableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow',
                      {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.assert_count_equal('', 13)
        self.assert_json_equal('LABELFORM', 'total_current_owner', -131.25)
        self.check_payment(1, "copropriete de Minimum", "131.25")

    def test_payment_paypal_owner(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(1, "copropriete de Minimum")

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', 0.00)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 100.00)
        self.assert_json_equal('LABELFORM', 'total_current_owner', -31.25)
        self.assert_json_equal('LABELFORM', 'thirdtotal', -31.25)
        self.assert_json_equal('LABELFORM', 'sumtopay', 31.25)
        self.assertEqual(len(self.json_actions), 4)

    def test_payment_paypal_callfund(self):
        default_paymentmethod()
        add_test_callfunds()
        self.check_payment_paypal(4, "appel de fonds pour Minimum")

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', 0.00)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 100.00)
        self.assert_json_equal('LABELFORM', 'total_current_owner', -31.25)
        self.assertEqual(len(self.json_actions), 4)

    def test_send_owner(self):
        from lucterios.mailing.tests import configSMTP, TestReceiver
        add_test_callfunds()
        configSMTP('localhost', 2025)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_owner', -131.25)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_action_equal(self.json_actions[2], (six.text_type('Envoyer'), 'lucterios.mailing/images/email.png', 'diacamma.condominium', 'ownerPayableEmail', 0, 1, 1))

        self.factory.xfer = OwnerPayableEmail()
        self.calljson('/diacamma.condominium/ownerPayableEmail', {'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerPayableEmail')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payableEmail")
        self.assertEqual(self.response_json['action']['params'], {'item_name': 'owner'})

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
                          {'owner': 1, 'OK': 'YES', 'item_name': 'owner', 'subject': 'my owner', 'message': 'this is a owner.', 'model': 9}, False)
            self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payableEmail')
            self.assertEqual(1, server.count())
            self.assertEqual('mr-sylvestre@worldcompany.com', server.get(0)[1])
            self.assertEqual(['Minimum@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(0)[2])
            msg, msg_txt, msg_file = server.check_first_message('my owner', 3, {'To': 'Minimum@worldcompany.com'})
            self.assertEqual('text/plain', msg_txt.get_content_type())
            self.assertEqual('text/html', msg.get_content_type())
            self.assertEqual('base64', msg.get('Content-Transfer-Encoding', ''))
            self.assertEqual('<html>this is a owner.</html>', decode_b64(msg.get_payload()))

            self.assertTrue('copropriete_de_Minimum.pdf' in msg_file.get('Content-Type', ''), msg_file.get('Content-Type', ''))
            self.save_pdf(base64_content=msg_file.get_payload())
        finally:
            server.stop()

    def test_send_multi_owner(self):
        from lucterios.mailing.tests import configSMTP, TestReceiver
        default_paymentmethod()
        add_test_callfunds()
        configSMTP('localhost', 2025)
        server = TestReceiver()
        server.start(2025)
        try:
            self.assertEqual(0, server.count())
            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail',
                          {'item_name': 'owner', 'owner': '1;2;3'}, False)
            self.assert_observer('core.custom', 'diacamma.payoff', 'payableEmail')
            self.assert_count_equal('', 5)
            self.assert_json_equal('LABELFORM', "nb_item", '3')

            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail',
                          {'owner': '1;2;3', 'OK': 'YES', 'item_name': 'owner', 'subject': '#reference', 'message': 'this is a owner.', 'model': 9}, False)
            self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payableEmail')

            email_msg = Message.objects.get(id=1)
            self.assertEqual(email_msg.subject, '#reference')
            self.assertEqual(email_msg.body, 'this is a owner.')
            self.assertEqual(email_msg.status, 2)
            self.assertEqual(email_msg.recipients, "condominium.Owner id||8||1;2;3\n")
            self.assertEqual(email_msg.email_to_send, "condominium.Owner:1:9\ncondominium.Owner:2:9\ncondominium.Owner:3:9")

            self.assertEqual(1, len(LucteriosScheduler.get_list()))
            LucteriosScheduler.stop_scheduler()
            email_msg.sendemail(10, "http://testserver")
            self.assertEqual(3, server.count())
            self.assertEqual(['Minimum@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(0)[2])
            server.get_msg_index(0, "Situation de 'Minimum'")
            self.assertEqual(['William.Dalton@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(1)[2])
            server.get_msg_index(1, "Situation de 'Dalton William'")
            self.assertEqual(['Joe.Dalton@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(2)[2])
            server.get_msg_index(2, "Situation de 'Dalton Joe'")

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
        self.check_account(year_id=1, code='4501', value=164.05)
        self.check_account(year_id=1, code='4502', value=64.27)
        self.check_account(year_id=1, code='512', value=4.34)
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
        self.assert_count_equal('', 52)
        self.assert_json_equal('LABELFORM', 'total_current_initial', 23.45)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 100.00)
        self.assert_json_equal('LABELFORM', 'total_current_owner', -7.80)
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', 75.00)
        self.assert_json_equal('LABELFORM', 'total_recoverable_load', 30.00)
        self.assert_json_equal('LABELFORM', 'total_current_regularization', 56.25)
        self.assert_json_equal('LABELFORM', 'total_extra', -5.55)

        self.assert_grid_equal('exceptionnal', {"set": "catégorie de charges", "ratio": "ratio", "total_callfunds": "total des appels de fonds", "ventilated": "ventilé", "total_current_regularization": "régularisation estimée"}, 1)  # nb=5
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', 45.0)
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', 45.0)
        self.assert_json_equal('', 'exceptionnal/@0/ventilated', 33.75)
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', 11.25)
        self.assert_json_equal('LABELFORM', 'total_exceptional_initial', 5.73)
        self.assert_json_equal('LABELFORM', 'total_exceptional_call', 45.00)
        self.assert_json_equal('LABELFORM', 'total_exceptional_payoff', 30.00)
        self.assert_json_equal('LABELFORM', 'total_exceptional_owner', -9.27)

    def test_close_classload(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.check_account(year_id=1, code='120', value=25.0)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', [350.00, 187.34, 162.66, 24.34, 4.34])

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_json_equal('LABELFORM', 'is_active', True)

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
        self.assert_json_equal('LABELFORM', 'is_active', False)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('LABELFORM', 'result', [350.00, 187.34, 162.66, 24.34, 24.34])

        self.assert_json_equal('', 'entryline/@2/costaccounting', None)
        self.assert_json_equal('', 'entryline/@2/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@3/costaccounting', None)
        self.assert_json_equal('', 'entryline/@3/entry_account', '[4502 Minimum]')
        self.assert_json_equal('', 'entryline/@4/costaccounting', None)
        self.assert_json_equal('', 'entryline/@4/entry_account', '[4502 Dalton William]')
        self.assert_json_equal('', 'entryline/@5/costaccounting', None)
        self.assert_json_equal('', 'entryline/@5/entry_account', '[4502 Dalton Joe]')

        self.check_account(year_id=1, code='120', value=0.00)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=164.05)
        self.check_account(year_id=1, code='4502', value=39.27)
        self.check_account(year_id=1, code='512', value=4.34)
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
        self.assert_json_equal('LABELFORM', 'title_condo', 'Cet exercice a un résultat non nul égal à 162,66 €')
        self.assert_select_equal('ventilate', 7)  # nb=7

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose',
                      {'year': '1', 'type_of_account': '-1', 'CONFIRME': 'YES', 'ventilate': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.check_account(year_id=1, code='103', value=0.0)
        self.check_account(year_id=1, code='105', value=0.0)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=1.39)
        self.check_account(year_id=1, code='4502', value=64.27)
        self.check_account(year_id=1, code='512', value=4.34)
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
        self.check_account(year_id=2, code='4501', value=1.39)
        self.check_account(year_id=2, code='4502', value=64.27)
        self.check_account(year_id=2, code='512', value=4.34)
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
        self.assert_json_equal('LABELFORM', 'title_condo', 'Cet exercice a un résultat non nul égal à 162,66 €')
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
        self.check_account(year_id=1, code='4501', value=164.05)
        self.check_account(year_id=1, code='4502', value=64.27)
        self.check_account(year_id=1, code='512', value=4.34)
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
        self.check_account(year_id=2, code='4501', value=164.05)
        self.check_account(year_id=2, code='4502', value=64.27)
        self.check_account(year_id=2, code='512', value=4.34)
        self.check_account(year_id=2, code='531', value=20.0)
        self.check_account(year_id=2, code='602', value=None)
        self.check_account(year_id=2, code='604', value=None)
        self.check_account(year_id=2, code='627', value=None)
        self.check_account(year_id=2, code='701', value=None)
        self.check_account(year_id=2, code='702', value=None)

    def test_ventilation_credit(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', 29.18)
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -131.25)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-06-15")
        self.assert_json_equal('', 'entryline/@1/credit', 100.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@2/debit', -45.00)
        self.assert_json_equal('', 'entryline/@3/entry.date_value', "2015-07-21")
        self.assert_json_equal('', 'entryline/@3/credit', 30.00)
        self.assert_json_equal('LABELFORM', 'thirdtotal', -17.07)
        self.assert_json_equal('LABELFORM', 'sumtopay', 17.07)
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/num', '1')
        self.assert_json_equal('', 'callfunds/@0/date', '2015-06-10')
        self.assert_json_equal('', 'callfunds/@0/total', 131.25)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 31.25)
        self.assert_json_equal('', 'callfunds/@1/num', '2')
        self.assert_json_equal('', 'callfunds/@1/date', '2015-07-14')
        self.assert_json_equal('', 'callfunds/@1/total', 45.00)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 15.00)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerVentilatePay()
        self.calljson('/diacamma.condominium/ownerVentilatePay', {'CONFIRME': 'YES', 'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerVentilatePay')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', 29.18)
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -131.25)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-06-15")
        self.assert_json_equal('', 'entryline/@1/credit', 100.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@2/debit', -45.00)
        self.assert_json_equal('', 'entryline/@3/entry.date_value', "2015-07-21")
        self.assert_json_equal('', 'entryline/@3/credit', 30.00)
        self.assert_json_equal('LABELFORM', 'thirdtotal', -17.07)
        self.assert_json_equal('LABELFORM', 'sumtopay', 17.07)
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/num', '1')
        self.assert_json_equal('', 'callfunds/@0/date', '2015-06-10')
        self.assert_json_equal('', 'callfunds/@0/total', 131.25)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 0.00)
        self.assert_json_equal('', 'callfunds/@1/num', '2')
        self.assert_json_equal('', 'callfunds/@1/date', '2015-07-14')
        self.assert_json_equal('', 'callfunds/@1/total', 45.00)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 17.07)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerMultiPay()
        self.calljson('/diacamma.condominium/ownerMultiPay', {'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerMultiPay')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payoffAddModify")
        self.assertEqual(len(self.response_json['action']['params']), 3)
        self.assertEqual(self.response_json['action']['params']['supportings'], '1;7')
        self.assertEqual(self.response_json['action']['params']['NO_REPARTITION'], 'yes')
        self.assertEqual(self.response_json['action']['params']['repartition'], '1')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supportings': '1;7', 'NO_REPARTITION': 'yes', 'repartition': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "17.07")
        self.assert_json_equal('EDIT', 'payer', "Minimum")
        self.assert_json_equal('LABELFORM', 'supportings', "Minimum{[br/]}appel de fonds N°2 - 14 juillet 2015")

    def test_ventilation_debit(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()
        pay1 = Payoff(supporting_id=2, date='2015-07-31', mode=0, amount=150.0)
        pay1.editor.before_save(None)
        pay1.save()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', -12.50)
        self.assert_count_equal('entryline', 3)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -87.50)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@1/debit', -35.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@2/credit', 150.00)
        self.assert_json_equal('LABELFORM', 'thirdtotal', 15.00)
        self.assert_json_equal('LABELFORM', 'sumtopay', 0.00)
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/num', '1')
        self.assert_json_equal('', 'callfunds/@0/date', '2015-06-10')
        self.assert_json_equal('', 'callfunds/@0/total', 87.50)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 87.50)
        self.assert_json_equal('', 'callfunds/@1/num', '2')
        self.assert_json_equal('', 'callfunds/@1/date', '2015-07-14')
        self.assert_json_equal('', 'callfunds/@1/total', 35.00)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 35.00)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/date', '2015-07-31')
        self.assert_json_equal('', 'payoff/@0/amount', 150.0)

        self.factory.xfer = OwnerVentilatePay()
        self.calljson('/diacamma.condominium/ownerVentilatePay', {'CONFIRME': 'YES', 'owner': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerVentilatePay')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', -12.50)
        self.assert_count_equal('entryline', 3)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -87.50)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@1/debit', -35.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@2/credit', 150.00)
        self.assert_json_equal('LABELFORM', 'thirdtotal', 15.00)
        self.assert_json_equal('LABELFORM', 'sumtopay', 0.00)
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/date', '2015-01-01')
        self.assert_json_equal('', 'callfunds/@0/total', 12.50)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 0.00)
        self.assert_json_equal('', 'callfunds/@1/num', '1')
        self.assert_json_equal('', 'callfunds/@1/date', '2015-06-10')
        self.assert_json_equal('', 'callfunds/@1/total', 87.50)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 0.00)
        self.assert_json_equal('', 'callfunds/@2/num', '2')
        self.assert_json_equal('', 'callfunds/@2/date', '2015-07-14')
        self.assert_json_equal('', 'callfunds/@2/total', 35.00)
        self.assert_json_equal('', 'callfunds/@2/supporting.total_rest_topay', 0.00)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/date', '2015-07-31')
        self.assert_json_equal('', 'payoff/@0/amount', 15.0)

        self.factory.xfer = OwnerMultiPay()
        self.calljson('/diacamma.condominium/ownerMultiPay', {'owner': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerMultiPay')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payoffAddModify")
        self.assertEqual(len(self.response_json['action']['params']), 3)
        self.assertEqual(self.response_json['action']['params']['supportings'], '2')
        self.assertEqual(self.response_json['action']['params']['NO_REPARTITION'], 'yes')
        self.assertEqual(self.response_json['action']['params']['repartition'], '1')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supportings': '2', 'NO_REPARTITION': 'yes', 'repartition': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "0.00")
        self.assert_json_equal('EDIT', 'payer', "Dalton William")
        self.assert_json_equal('LABELFORM', 'supportings', "Dalton William")


class OwnerBelgiumTest(PaymentTest):

    def setUp(self):
        # six.print_('>> %s' % self._testMethodName)
        LucteriosTest.setUp(self)
        default_compta_be(with12=False)
        initial_thirds_be()
        default_costaccounting()
        default_bankaccount_be()
        default_setowner_be()
        rmtree(get_user_dir(), True)

    def tearDown(self):
        LucteriosTest.tearDown(self)
        # six.print_('<< %s' % self._testMethodName)

    def test_owner_situation(self):
        add_test_callfunds(False, True)
        add_test_expenses_be(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_count_equal('', 50)
        self.assert_grid_equal('partition', {"set": "catégorie de charges", 'set.budget_txt': 'budget', 'set.sumexpense': 'dépense',
                                             'value': 'tantième', 'ratio': 'ratio', "ventilated": "ventilé", 'recovery_load': 'charges récupérables'}, 2)
        self.assert_json_equal('', 'partition/@1/set', "[2] BBB")
        self.assert_json_equal('', 'partition/@1/set.budget_txt', 120.00)
        self.assert_json_equal('', 'partition/@1/set.sumexpense', 100.00)
        self.assert_json_equal('', 'partition/@1/value', "75.00")
        self.assert_json_equal('', 'partition/@1/ratio', 75.0)
        self.assert_json_equal('', 'partition/@1/ventilated', 75.00)
        self.assert_json_equal('', 'partition/@1/recovery_load', 30.00)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 100.00)
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', 75.00)
        self.assert_json_equal('LABELFORM', 'total_recoverable_load', 30.00)
        self.assert_json_equal('LABELFORM', 'total_current_regularization', 56.25)
        self.assert_json_equal('LABELFORM', 'total_extra', 5.70)

        self.assert_grid_equal('exceptionnal', {"set": "catégorie de charges", "ratio": "ratio", "total_callfunds": "total des appels de fonds", "ventilated": "ventilé", "total_current_regularization": "régularisation estimée"}, 1)  # nb=5
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', 45.0)
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', 45.00)
        self.assert_json_equal('', 'exceptionnal/@0/ventilated', 33.75)
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', 11.25)
        self.assert_json_equal('LABELFORM', 'total_exceptional_call', 45.00)
        self.assert_json_equal('LABELFORM', 'total_exceptional_payoff', 30.00)

    def test_owner_load_count(self):
        add_test_callfunds(False, True)
        add_test_expenses_be(False, True)
        init_compta()

        self.factory.xfer = OwnerLoadCount()
        self.calljson('/diacamma.condominium/ownerLoadCount', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerLoadCount')
        self.assert_count_equal('', 5)
        self.assert_count_equal('loadcount', 9)
        self.assert_json_equal('', '#loadcount/headers/@0/@0', "designation")
        self.assert_json_equal('', '#loadcount/headers/@0/@2', None)
        self.assert_json_equal('', '#loadcount/headers/@1/@0', "total")
        self.assert_json_equal('', '#loadcount/headers/@1/@2', "C2EUR")
        self.assert_json_equal('', '#loadcount/headers/@2/@0', "ratio")
        self.assert_json_equal('', '#loadcount/headers/@2/@2', None)
        self.assert_json_equal('', '#loadcount/headers/@3/@0', "ventilated")
        self.assert_json_equal('', '#loadcount/headers/@3/@2', "C2EUR")
        self.assert_json_equal('', '#loadcount/headers/@4/@0', "recoverable_load")
        self.assert_json_equal('', '#loadcount/headers/@4/@2', "C2EUR")

        self.assert_json_equal('', 'loadcount/@0/designation', "{[i]}[2] BBB{[/i]}")
        self.assert_json_equal('', 'loadcount/@0/total', {'value': 100.0, 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@0/ratio', {'value': "75/100", 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@0/ventilated', {'value': 75.0, 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@0/recoverable_load', {'value': 30.0, 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@1/designation', "&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;{[b]}[602000] 602000{[/b]}")
        self.assert_json_equal('', 'loadcount/@1/total', {'value': 100.0, 'format': '{[b]}{0}[/b]}'})
        self.assert_json_equal('', 'loadcount/@1/ratio', {'value': "75/100", 'format': '{[b]}{0}[/b]}'})
        self.assert_json_equal('', 'loadcount/@1/ventilated', {'value': 75.0, 'format': '{[b]}{0}[/b]}'})
        self.assert_json_equal('', 'loadcount/@1/recoverable_load', {'value': 30.0, 'format': '{[b]}{0}[/b]}'})

        self.assert_json_equal('', 'loadcount/@4/designation', "{[i]}[3] CCC{[/i]}")
        self.assert_json_equal('', 'loadcount/@4/total', {'value': 75.0, 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@4/ratio', {'value': "45/100", 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@4/ventilated', {'value': 33.75, 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@4/recoverable_load', {'value': 20.25, 'format': '{[i]}{0}[/i]}'})
        self.assert_json_equal('', 'loadcount/@5/designation', "&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;{[b]}[601000] 601000{[/b]}")
        self.assert_json_equal('', 'loadcount/@5/total', {'value': 75.0, 'format': '{[b]}{0}[/b]}'})
        self.assert_json_equal('', 'loadcount/@5/ratio', {'value': "45/100", 'format': '{[b]}{0}[/b]}'})
        self.assert_json_equal('', 'loadcount/@5/ventilated', {'value': 33.75, 'format': '{[b]}{0}[/b]}'})
        self.assert_json_equal('', 'loadcount/@5/recoverable_load', {'value': 20.25, 'format': '{[b]}{0}[/b]}'})

        self.assert_json_equal('', 'loadcount/@8/designation', "")
        self.assert_json_equal('', 'loadcount/@8/total', {'value': 175.0, 'format': '{[u]}{0}[/u]}'})
        self.assert_json_equal('', 'loadcount/@8/ratio', None)
        self.assert_json_equal('', 'loadcount/@8/ventilated', {'value': 108.75, 'format': '{[u]}{0}[/u]}'})
        self.assert_json_equal('', 'loadcount/@8/recoverable_load', {'value': 50.25, 'format': '{[u]}{0}[/u]}'})


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
        self.assert_json_equal('LABELFORM', 'total_current_initial', 0.00)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 100.00)
        self.assert_json_equal('LABELFORM', 'total_current_owner', 100.00)
        self.assert_json_equal('LABELFORM', 'thirdtotal', 100.00)
        self.assert_json_equal('LABELFORM', 'sumtopay', 0.00)
        self.assertFalse("total_current_regularization" in self.json_data.keys())
        self.assertEqual(len(self.json_actions), 4)

    def test_owner_situation(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_initial', 23.45)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 100.00)
        self.assert_json_equal('LABELFORM', 'total_current_owner', 44.70)
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', 75.00)
        self.assertFalse("total_current_regularization" in self.json_data.keys())
        self.assertFalse("total_extra" in self.json_data.keys())

        self.assert_count_equal('exceptionnal', 1)
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', 45.0)
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', 45.00)
        self.assert_json_equal('', 'exceptionnal/@0/ventilated', 33.75)
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', 11.25)
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
        self.assert_json_equal('LABELFORM', 'total_current_initial', 23.45)
        self.assert_json_equal('LABELFORM', 'total_current_call', 131.25)
        self.assert_json_equal('LABELFORM', 'total_current_payoff', 100.00)
        self.assert_json_equal('LABELFORM', 'total_current_owner', -7.80)
        self.assert_json_equal('LABELFORM', 'total_current_ventilated', 75.00)
        self.assert_json_equal('LABELFORM', 'total_current_regularization', 56.25)
        self.assert_json_equal('LABELFORM', 'total_extra', -5.55)

        self.assert_count_equal('exceptionnal', 1)
        self.assert_json_equal('', 'exceptionnal/@0/set', "[3] CCC")
        self.assert_json_equal('', 'exceptionnal/@0/ratio', 45.0)
        self.assert_json_equal('', 'exceptionnal/@0/total_callfunds', 45.00)
        self.assert_json_equal('', 'exceptionnal/@0/ventilated', 33.75)
        self.assert_json_equal('', 'exceptionnal/@0/total_current_regularization', 11.25)
        self.assert_json_equal('LABELFORM', 'total_exceptional_initial', 0.00)
        self.assert_json_equal('LABELFORM', 'total_exceptional_call', 45.00)
        self.assert_json_equal('LABELFORM', 'total_exceptional_payoff', 30.00)
        self.assert_json_equal('LABELFORM', 'total_exceptional_owner', -15.00)

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
        self.assert_json_equal('LABELFORM', 'result', [175.00, 187.34, -12.34, 31.11, 11.11])

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_json_equal('LABELFORM', 'is_active', True)

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
        self.assert_json_equal('LABELFORM', 'is_active', False)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('LABELFORM', 'result', [175.00, 187.34, -12.34, 31.11, 31.11])
