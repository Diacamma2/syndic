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
from lucterios.framework.filetools import get_user_dir
from lucterios.framework.model_fields import LucteriosScheduler
from lucterios.contacts.tests_contacts import change_ourdetail
from lucterios.CORE.models import Parameter
from lucterios.CORE.views import ObjectMerge

from lucterios.mailing.models import Message
from lucterios.mailing.test_tools import decode_b64
from lucterios.contacts.views_contacts import IndividualList

from diacamma.accounting.models import EntryAccount, FiscalYear, Third, AccountThird
from diacamma.accounting.views import ThirdShow, ThirdList, AccountThirdAddModify
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.accounting.views_accounts import FiscalYearClose, FiscalYearBegin, FiscalYearReportLastYear
from diacamma.accounting.views_other import CostAccountingList
from diacamma.accounting.views_reports import FiscalYearTrialBalance,\
    FiscalYearReportPrint
from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting, default_compta_be, initial_thirds_be,\
    check_pdfreport, create_account, set_accounting_system, add_entry, change_legal

from diacamma.payoff.models import Payoff, BankAccount
from diacamma.payoff.views import PayableShow, PayableEmail, PayoffAddModify
from diacamma.payoff.views_conf import paramchange_payoff
from diacamma.payoff.test_tools import default_bankaccount_fr, default_paymentmethod, PaymentTest, default_bankaccount_be

from diacamma.condominium.models import PropertyLot, Set, Owner, CallFunds
from diacamma.condominium.views import OwnerAndPropertyLotList, OwnerAdd, OwnerDel, OwnerShow, PropertyLotAddModify, CondominiumConvert, OwnerVentilatePay,\
    OwnerLoadCount, OwnerMultiPay, OwnerPayableEmail, OwnerModify, OwnerRefund,\
    OwnerReport, OwnerAndPropertyLotPrint
from diacamma.condominium.views_classload import SetList, SetAddModify, SetDel, SetShow, PartitionAddModify, CondominiumConf, SetClose,\
    OwnerLinkAddModify, OwnerLinkDel, RecoverableLoadRatioAddModify, RecoverableLoadRatioDel
from diacamma.condominium.views_callfunds import CallFundsList, CallFundsAddCurrent, CallFundsTransition, CallFundsShow
from diacamma.condominium.views_report import FinancialStatus, GeneralManageAccounting, CurrentManageAccounting, ExceptionalManageAccounting
from diacamma.condominium.test_tools import default_setowner_fr, add_test_callfunds, old_accounting, add_test_expenses_fr, init_compta, add_years, default_setowner_be, add_test_expenses_be,\
    create_owner_fr, _set_partition, _set_budget
from diacamma.condominium.views_expense import ExpenseList


class SetOwnerTest(LucteriosTest):

    def setUp(self):
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_bankaccount_fr()
        rmtree(get_user_dir(), True)

    def test_config(self):
        default_setowner_fr()
        self.factory.xfer = CondominiumConf()
        self.calljson('/diacamma.condominium/condominiumConf', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'condominiumConf')
        self.assert_count_equal('', 2 + 15 + 2 + 2)
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account1', '[4501] 4501')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account2', '[4502] 4502')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account3', '[4503] 4503')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account4', '[4504] 4504')
        self.assert_json_equal('LABELFORM', 'condominium-default-owner-account5', '[4505] 4505')
        self.assert_json_equal('LABELFORM', 'condominium-current-revenue-account', '[701] 701')
        self.assert_json_equal('LABELFORM', 'condominium-exceptional-revenue-account', '[702] 702')
        self.assert_json_equal('LABELFORM', 'condominium-fundforworks-revenue-account', '[705] 705')
        self.assert_json_equal('LABELFORM', 'condominium-exceptional-reserve-account', '[120] 120')
        self.assert_json_equal('LABELFORM', 'condominium-advance-reserve-account', '[103] 103')
        self.assert_json_equal('LABELFORM', 'condominium-fundforworks-reserve-account', '[105] 105')
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
        self.assert_select_equal('third', 0)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Minimum')
        self.assert_count_equal('accountthird', 2)
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@1/code', '401')

        self.factory.xfer = AccountThirdAddModify()
        self.calljson('/diacamma.accounting/accountThirdAddModify', {'SAVE': 'YES', "third": 4, 'code': '4501'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'accountThirdAddModify')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 4}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_count_equal('accountthird', 3)

        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAdd')
        self.assert_select_equal('third', 1)

        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd',
                      {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 1)
        self.assert_json_equal('', 'owner/@0/id', '1')
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
        self.assert_select_equal('third', 0)

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

    def test_modify_owner(self):
        self.factory.xfer = OwnerAdd()
        self.calljson('/diacamma.condominium/ownerAdd', {'SAVE': 'YES', "third": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerAdd')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')

        self.factory.xfer = OwnerModify()
        self.calljson('/diacamma.condominium/ownerModify', {'owner': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerModify')

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

    def test_merge_contacts(self):
        default_setowner_fr(with_lots=False)
        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 3)

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_count_equal('partition', 3)
        self.assert_json_equal('', 'partition/@0/value', '45.00')
        self.assert_json_equal('', 'partition/@0/owner', 'Minimum')
        self.assert_json_equal('', 'partition/@1/value', '35.00')
        self.assert_json_equal('', 'partition/@1/owner', 'Dalton William')
        self.assert_json_equal('', 'partition/@2/value', '20.00')
        self.assert_json_equal('', 'partition/@2/owner', 'Dalton Joe')

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 7)

        self.factory.xfer = IndividualList()
        self.calljson('/lucterios.contacts/individualList', {}, False)
        self.assert_observer('core.custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('individual', 5)

        self.factory.xfer = ObjectMerge()
        self.calljson('/CORE/objectMerge', {'modelname': 'contacts.Individual', 'field_id': 'individual',
                                            'individual': '2;3;4;5', 'CONFIRME': 'YES', 'mrg_object': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'objectMerge')

        self.factory.xfer = IndividualList()
        self.calljson('/lucterios.contacts/individualList', {}, False)
        self.assert_observer('core.custom', 'lucterios.contacts', 'individualList')
        self.assert_count_equal('individual', 2)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_count_equal('third', 4)

        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 2)

        self.factory.xfer = SetShow()
        self.calljson('/diacamma.condominium/setShow', {'set': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setShow')
        self.assert_count_equal('partition', 2)
        partitions_value = [(partition['value'], partition['owner']) for partition in self.get_json_path('partition')]
        partitions_value.sort(key=lambda part: part[0])
        self.assertEqual(partitions_value, [(45.00, 'Minimum'), (55.00, 'Dalton William')])


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
        self.assert_count_equal('report_1', 20)
        self.assert_json_equal('', 'report_1/@1/left', '[512] 512')
        self.assert_json_equal('', 'report_1/@1/left_n', 4.34)
        self.assert_json_equal('', 'report_1/@2/left', '[531] 531')
        self.assert_json_equal('', 'report_1/@2/left_n', 20.00)

        self.assert_json_equal('', 'report_1/@7/left', '[4501 Minimum]')
        self.assert_json_equal('', 'report_1/@7/left_n', 7.80)
        self.assert_json_equal('', 'report_1/@8/left', '[4501 Dalton William]')
        self.assert_json_equal('', 'report_1/@8/left_n', 98.00)
        self.assert_json_equal('', 'report_1/@9/left', '[4501 Dalton Joe]')
        self.assert_json_equal('', 'report_1/@9/left_n', 56.25)
        self.assert_json_equal('', 'report_1/@10/left', '[4502 Minimum]')
        self.assert_json_equal('', 'report_1/@10/left_n', 9.27)
        self.assert_json_equal('', 'report_1/@11/left', '[4502 Dalton William]')
        self.assert_json_equal('', 'report_1/@11/left_n', 35.75)
        self.assert_json_equal('', 'report_1/@12/left', '[4502 Dalton Joe]')
        self.assert_json_equal('', 'report_1/@12/left_n', 20.00)
        self.assert_json_equal('', 'report_1/@13/left', '[4503 Dalton William]')
        self.assert_json_equal('', 'report_1/@13/left_n', 0.6)
        self.assert_json_equal('', 'report_1/@14/left', '[4504 Dalton William]')
        self.assert_json_equal('', 'report_1/@14/left_n', 0.25)
        self.assert_json_equal('', 'report_1/@15/left', '[4505 Dalton William]')
        self.assert_json_equal('', 'report_1/@15/left_n', 0.4)

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

    def test_financial_pdf(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'FinancialStatus', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_pdf()

    def test_general_pdf(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'GeneralManageAccounting', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_pdf()

    def test_current_pdf(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'CurrentManageAccounting', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_pdf()

    def test_exceptionnal_pdf(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'ExceptionalManageAccounting', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_pdf()

    def test_financial_ods(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'FinancialStatus', "PRINT_MODE": 2}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_ods()

    def test_general_ods(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'GeneralManageAccounting', "PRINT_MODE": 2}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_ods()

    def test_current_ods(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'CurrentManageAccounting', "PRINT_MODE": 2}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_ods()

    def test_exceptionnal_ods(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'modulename': 'diacamma.condominium.views_report', 'classname': 'ExceptionalManageAccounting', "PRINT_MODE": 2}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_ods()


class OwnerTest(PaymentTest):

    def setUp(self):
        # print('>> %s' % self._testMethodName)
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_costaccounting()
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)

    def tearDown(self):
        LucteriosTest.tearDown(self)
        # print('<< %s' % self._testMethodName)

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
        self.assert_action_equal('GET', self.json_actions[2], ('Règlements', 'diacamma.payoff/images/payments.png', 'diacamma.condominium', 'ownerShowPayable', 0, 1, 0))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow',
                      {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.assert_count_equal('', 17)
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
        configSMTP('localhost', 4225)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'total_current_owner', -131.25)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_action_equal('POST', self.json_actions[2], ('Envoyer', 'lucterios.mailing/images/email.png', 'diacamma.condominium', 'ownerPayableEmail', 0, 1, 0))

        self.factory.xfer = OwnerPayableEmail()
        self.calljson('/diacamma.condominium/ownerPayableEmail', {'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerPayableEmail')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payableEmail")
        self.assertEqual(self.response_json['action']['params'], {'item_name': 'owner'})

        server = TestReceiver()
        server.start(4225)
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
        configSMTP('localhost', 4325)
        server = TestReceiver()
        server.start(4325)
        try:
            self.assertEqual(0, server.count())
            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail',
                          {'item_name': 'owner', 'owner': '1;2;3'}, False)
            self.assert_observer('core.custom', 'diacamma.payoff', 'payableEmail')
            self.assert_count_equal('', 6)
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
            server.get_msg_index(0, "Minimum")
            self.assertEqual(['William.Dalton@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(1)[2])
            server.get_msg_index(1, "Dalton William")
            self.assertEqual(['Joe.Dalton@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(2)[2])
            server.get_msg_index(2, "Dalton Joe")

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
        self.check_account(year_id=1, code='4501', value=162.05)
        self.check_account(year_id=1, code='4502', value=65.02)
        self.check_account(year_id=1, code='4503', value=0.60)
        self.check_account(year_id=1, code='4504', value=0.25)
        self.check_account(year_id=1, code='4505', value=0.40)
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
        self.assert_count_equal('', 54)
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

        self.assert_grid_equal('payment', {'date': 'date', 'assignment': 'affectation', 'amount': 'montant', 'mode': 'mode', 'bank_account': 'compte bancaire', 'reference': 'référence'}, 2)
        self.assert_json_equal('', 'payment/@0/date', "2015-06-15")
        self.assert_json_equal('', 'payment/@0/assignment', "appel de fonds N°1 Minimum")
        self.assert_json_equal('', 'payment/@0/amount', 100.0)
        self.assert_json_equal('', 'payment/@0/mode', 0)
        self.assert_json_equal('', 'payment/@1/date', "2015-07-21")
        self.assert_json_equal('', 'payment/@1/assignment', "appel de fonds N°2 Minimum")
        self.assert_json_equal('', 'payment/@1/amount', 30.0)
        self.assert_json_equal('', 'payment/@1/mode', 0)

    def test_owner_list_print_pdf(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerAndPropertyLotPrint()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotPrint', {"PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.condominium', 'ownerAndPropertyLotPrint')
        self.save_pdf()

    def test_owner_list_print_ods(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerAndPropertyLotPrint()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotPrint', {"PRINT_MODE": 2}, False)
        self.assert_observer('core.print', 'diacamma.condominium', 'ownerAndPropertyLotPrint')
        self.save_ods()

    def test_owner_situation_print_pdf(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)
        init_compta()

        self.factory.xfer = OwnerReport()
        self.calljson('/diacamma.condominium/ownerReport', {'owner': 1, "PRINT_MODE": 3, 'model': 9}, False)
        self.assert_observer('core.print', 'diacamma.condominium', 'ownerReport')
        self.save_pdf()

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
        self.check_account(year_id=1, code='4501', value=162.05)
        self.check_account(year_id=1, code='4502', value=40.02)
        self.check_account(year_id=1, code='4503', value=0.60)
        self.check_account(year_id=1, code='4504', value=0.25)
        self.check_account(year_id=1, code='4505', value=0.40)
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
        self.assert_json_equal('LABELFORM', 'title_condo', 'Cet exercice a un résultat non nul égal à 162,66 €.')
        self.assert_select_equal('ventilate', 7)  # nb=7

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose',
                      {'year': '1', 'type_of_account': '-1', 'CONFIRME': 'YES', 'ventilate': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.check_account(year_id=1, code='103', value=0.0)
        self.check_account(year_id=1, code='105', value=0.0)
        self.check_account(year_id=1, code='120', value=25.0)
        self.check_account(year_id=1, code='401', value=65.0)
        self.check_account(year_id=1, code='4501', value=-0.61)
        self.check_account(year_id=1, code='4502', value=65.02)
        self.check_account(year_id=1, code='4503', value=0.60)
        self.check_account(year_id=1, code='4504', value=0.25)
        self.check_account(year_id=1, code='4505', value=0.40)
        self.check_account(year_id=1, code='512', value=4.34)
        self.check_account(year_id=1, code='531', value=20.0)
        self.check_account(year_id=1, code='602', value=75.0)
        self.check_account(year_id=1, code='604', value=100.0)
        self.check_account(year_id=1, code='627', value=12.34)
        self.check_account(year_id=1, code='702', value=75.0)
        self.check_account(year_id=1, code='701', value=112.34)

        check_pdfreport(self, '1', 'Etat financier.pdf', "FinancialStatus", "diacamma.condominium.views_report")
        check_pdfreport(self, '1', 'Compte de gestion generale.pdf', "GeneralManageAccounting", "diacamma.condominium.views_report")
        check_pdfreport(self, '1', 'Compte de gestion pour operations courantes.pdf', "CurrentManageAccounting", "diacamma.condominium.views_report")
        check_pdfreport(self, '1', 'Compte de gestion pour operations exceptionnelles.pdf', "ExceptionalManageAccounting", "diacamma.condominium.views_report")

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
        self.check_account(year_id=2, code='4501', value=-0.61)
        self.check_account(year_id=2, code='4502', value=65.02)
        self.check_account(year_id=1, code='4503', value=0.60)
        self.check_account(year_id=1, code='4504', value=0.25)
        self.check_account(year_id=1, code='4505', value=0.40)
        self.check_account(year_id=2, code='512', value=4.34)
        self.check_account(year_id=2, code='531', value=20.0)
        self.check_account(year_id=2, code='602', value=None)
        self.check_account(year_id=2, code='604', value=None)
        self.check_account(year_id=2, code='627', value=None)
        self.check_account(year_id=2, code='701', value=None)
        self.check_account(year_id=2, code='702', value=None)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '2', 'GRID_SIZE%entryline': 100}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 30)
        self.assert_json_equal('', 'entryline/@2/entry.num', 16)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@2/designation_ref', "Ventilation pour [1] AAA")
        self.assert_json_equal('', 'entryline/@2/entry_account', "[4501 Minimum]")
        self.assert_json_equal('', 'entryline/@2/credit', 112.50)
        self.assert_json_equal('', 'entryline/@3/entry.num', 16)
        self.assert_json_equal('', 'entryline/@3/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@3/designation_ref', "Ventilation pour [1] AAA")
        self.assert_json_equal('', 'entryline/@3/entry_account', "[4501 Dalton William]")
        self.assert_json_equal('', 'entryline/@3/credit', 87.50)
        self.assert_json_equal('', 'entryline/@4/entry.num', 16)
        self.assert_json_equal('', 'entryline/@4/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@4/designation_ref', "Ventilation pour [1] AAA")
        self.assert_json_equal('', 'entryline/@4/entry_account', "[4501 Dalton Joe]")
        self.assert_json_equal('', 'entryline/@4/credit', 50.00)
        self.assert_json_equal('', 'entryline/@5/entry.num', 16)
        self.assert_json_equal('', 'entryline/@5/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@5/designation_ref', "Ventilation pour [1] AAA")
        self.assert_json_equal('', 'entryline/@5/entry_account', "[701] 701")
        self.assert_json_equal('', 'entryline/@5/debit', -250.0)

        self.assert_json_equal('', 'entryline/@6/entry.num', 17)
        self.assert_json_equal('', 'entryline/@6/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@6/designation_ref', "Ventilation pour [2] BBB")
        self.assert_json_equal('', 'entryline/@6/entry_account', "[4501 Minimum]")
        self.assert_json_equal('', 'entryline/@6/debit', -56.25)
        self.assert_json_equal('', 'entryline/@7/entry.num', 17)
        self.assert_json_equal('', 'entryline/@7/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@7/designation_ref', "Ventilation pour [2] BBB")
        self.assert_json_equal('', 'entryline/@7/entry_account', "[4501 Dalton Joe]")
        self.assert_json_equal('', 'entryline/@7/debit', -18.75)
        self.assert_json_equal('', 'entryline/@8/entry.num', 17)
        self.assert_json_equal('', 'entryline/@8/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@8/designation_ref', "Ventilation pour [2] BBB")
        self.assert_json_equal('', 'entryline/@8/entry_account', "[701] 701")
        self.assert_json_equal('', 'entryline/@8/credit', 75.0)

        self.assert_json_equal('', 'entryline/@9/entry.num', 18)
        self.assert_json_equal('', 'entryline/@9/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@9/designation_ref', "Ventilation pour Exercice du 1 janvier 2015 au 31 décembre 2015")
        self.assert_json_equal('', 'entryline/@9/entry_account', "[4501 Minimum]")
        self.assert_json_equal('', 'entryline/@9/debit', -5.55)
        self.assert_json_equal('', 'entryline/@10/entry.num', 18)
        self.assert_json_equal('', 'entryline/@10/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@10/designation_ref', "Ventilation pour Exercice du 1 janvier 2015 au 31 décembre 2015")
        self.assert_json_equal('', 'entryline/@10/entry_account', "[4501 Dalton William]")
        self.assert_json_equal('', 'entryline/@10/debit', -4.32)
        self.assert_json_equal('', 'entryline/@11/entry.num', 18)
        self.assert_json_equal('', 'entryline/@11/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@11/designation_ref', "Ventilation pour Exercice du 1 janvier 2015 au 31 décembre 2015")
        self.assert_json_equal('', 'entryline/@11/entry_account', "[4501 Dalton Joe]")
        self.assert_json_equal('', 'entryline/@11/debit', -2.47)
        self.assert_json_equal('', 'entryline/@12/entry.num', 18)
        self.assert_json_equal('', 'entryline/@12/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@12/designation_ref', "Ventilation pour Exercice du 1 janvier 2015 au 31 décembre 2015")
        self.assert_json_equal('', 'entryline/@12/entry_account', "[701] 701")
        self.assert_json_equal('', 'entryline/@12/credit', 12.34)

        self.assert_json_equal('', 'entryline/@13/entry.num', 19)
        self.assert_json_equal('', 'entryline/@13/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@13/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@13/entry_account', "[401] 401")
        self.assert_json_equal('', 'entryline/@13/credit', 65.0)
        self.assert_json_equal('', 'entryline/@14/entry.num', 19)
        self.assert_json_equal('', 'entryline/@14/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@14/designation_ref', "Cloture d'exercice - Tiers{[br/]}dépense 1 - opq 666")
        self.assert_json_equal('', 'entryline/@14/entry_account', "[401 Maximum]")
        self.assert_json_equal('', 'entryline/@14/debit', -100.0)
        self.assert_json_equal('', 'entryline/@15/entry.num', 19)
        self.assert_json_equal('', 'entryline/@15/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@15/designation_ref', "Cloture d'exercice - Tiers{[br/]}règlement de dépense 1 - opq 666")
        self.assert_json_equal('', 'entryline/@15/entry_account', "[401 Maximum]")
        self.assert_json_equal('', 'entryline/@15/credit', 35.0)

        self.assert_json_equal('', 'entryline/@16/entry.num', 19)
        self.assert_json_equal('', 'entryline/@16/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@16/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@16/entry_account', "[4501] 4501")
        self.assert_json_equal('', 'entryline/@16/credit', 0.61)
        self.assert_json_equal('', 'entryline/@17/entry.num', 19)
        self.assert_json_equal('', 'entryline/@17/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@17/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@17/entry_account', "[4501 Minimum]")
        self.assert_json_equal('', 'entryline/@17/debit', -42.90)
        self.assert_json_equal('', 'entryline/@18/entry.num', 19)
        self.assert_json_equal('', 'entryline/@18/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@18/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@18/entry_account', "[4501 Dalton William]")
        self.assert_json_equal('', 'entryline/@18/credit', 14.82)
        self.assert_json_equal('', 'entryline/@19/entry.num', 19)
        self.assert_json_equal('', 'entryline/@19/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@19/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@19/entry_account', "[4501 Dalton Joe]")
        self.assert_json_equal('', 'entryline/@19/credit', 27.47)

        self.assert_json_equal('', 'entryline/@20/entry.num', 19)
        self.assert_json_equal('', 'entryline/@20/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@20/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@20/entry_account', "[4502] 4502")
        self.assert_json_equal('', 'entryline/@20/debit', -65.02)
        self.assert_json_equal('', 'entryline/@21/entry.num', 19)
        self.assert_json_equal('', 'entryline/@21/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@21/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@21/entry_account', "[4502 Minimum]")
        self.assert_json_equal('', 'entryline/@21/credit', 9.27)
        self.assert_json_equal('', 'entryline/@22/entry.num', 19)
        self.assert_json_equal('', 'entryline/@22/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@22/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@22/entry_account', "[4502 Dalton William]")
        self.assert_json_equal('', 'entryline/@22/credit', 35.75)
        self.assert_json_equal('', 'entryline/@23/entry.num', 19)
        self.assert_json_equal('', 'entryline/@23/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@23/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@23/entry_account', "[4502 Dalton Joe]")
        self.assert_json_equal('', 'entryline/@23/credit', 20.00)

        self.assert_json_equal('', 'entryline/@24/entry.num', 19)
        self.assert_json_equal('', 'entryline/@24/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@24/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@24/entry_account', "[4503] 4503")
        self.assert_json_equal('', 'entryline/@24/debit', -0.6)
        self.assert_json_equal('', 'entryline/@25/entry.num', 19)
        self.assert_json_equal('', 'entryline/@25/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@25/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@25/entry_account', "[4503 Dalton William]")
        self.assert_json_equal('', 'entryline/@25/credit', 0.6)

        self.assert_json_equal('', 'entryline/@26/entry.num', 19)
        self.assert_json_equal('', 'entryline/@26/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@26/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@26/entry_account', "[4504] 4504")
        self.assert_json_equal('', 'entryline/@26/debit', -0.25)
        self.assert_json_equal('', 'entryline/@27/entry.num', 19)
        self.assert_json_equal('', 'entryline/@27/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@27/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@27/entry_account', "[4504 Dalton William]")
        self.assert_json_equal('', 'entryline/@27/credit', 0.25)

        self.assert_json_equal('', 'entryline/@28/entry.num', 19)
        self.assert_json_equal('', 'entryline/@28/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@28/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@28/entry_account', "[4505] 4505")
        self.assert_json_equal('', 'entryline/@28/debit', -0.40)
        self.assert_json_equal('', 'entryline/@29/entry.num', 19)
        self.assert_json_equal('', 'entryline/@29/entry.date_value', "2015-12-31")
        self.assert_json_equal('', 'entryline/@29/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@29/entry_account', "[4505 Dalton William]")
        self.assert_json_equal('', 'entryline/@29/credit', 0.40)

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
        self.assert_json_equal('LABELFORM', 'title_condo', 'Cet exercice a un résultat non nul égal à 162,66 €.')
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
        self.check_account(year_id=1, code='4501', value=162.05)
        self.check_account(year_id=1, code='4502', value=65.02)
        self.check_account(year_id=1, code='4503', value=0.60)
        self.check_account(year_id=1, code='4504', value=0.25)
        self.check_account(year_id=1, code='4505', value=0.40)
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
        self.check_account(year_id=2, code='4501', value=162.05)
        self.check_account(year_id=2, code='4502', value=65.02)
        self.check_account(year_id=1, code='4503', value=0.60)
        self.check_account(year_id=1, code='4504', value=0.25)
        self.check_account(year_id=1, code='4505', value=0.40)
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
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
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
        self.assert_count_equal('#entryline/actions', 4)
        self.assert_action_equal('POST', '#entryline/actions/@0', ('Editer', 'images/edit.png', 'diacamma.accounting', 'entryAccountOpenFromLine', 0, 1, 0))
        self.assert_action_equal('DELETE', '#entryline/actions/@1', ('Supprimer', 'images/delete.png', 'diacamma.accounting', 'entryAccountDel', 0, 1, 2))
        self.assert_action_equal('POST', '#entryline/actions/@2', ('Clôturer', 'images/ok.png', 'diacamma.accounting', 'entryAccountClose', 0, 1, 2))
        self.assert_action_equal('POST', '#entryline/actions/@3', ('(dé)lettrage', 'images/left.png', 'diacamma.accounting', 'entryAccountLink', 0, 1, 2))
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
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -131.25)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-06-15")
        self.assert_json_equal('', 'entryline/@1/credit', 100.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@2/debit', -45.00)
        self.assert_json_equal('', 'entryline/@3/entry.date_value', "2015-07-21")
        self.assert_json_equal('', 'entryline/@3/credit', 2.07)
        self.assert_json_equal('', 'entryline/@4/entry.date_value', "2015-07-21")
        self.assert_json_equal('', 'entryline/@4/credit', 27.93)
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
        self.assert_json_equal('LABELFORM', 'supportings', "Minimum{[br/]}appel de fonds N°2 Minimum")

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
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
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
        self.assert_count_equal('entryline', 10)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -87.50)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@1/debit', -35.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@2/credit', 10.50)
        self.assert_json_equal('', 'entryline/@3/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@3/credit', 87.50)
        self.assert_json_equal('', 'entryline/@4/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@4/credit', 15.00)
        self.assert_json_equal('', 'entryline/@5/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@5/credit', 0.75)
        self.assert_json_equal('', 'entryline/@6/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@6/credit', 35.00)
        self.assert_json_equal('', 'entryline/@7/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@7/credit', 0.60)
        self.assert_json_equal('', 'entryline/@8/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@8/credit', 0.25)
        self.assert_json_equal('', 'entryline/@9/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@9/credit', 0.4)
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

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 9}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('LABELFORM', 'status', 2)
        self.assert_json_equal('LABELFORM', 'owner', 'Dalton William')
        self.assert_json_equal('LABELFORM', 'total', 12.50)
        self.assert_count_equal('calldetail', 5)
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge courante')
        self.assert_json_equal('', 'calldetail/@0/set', None)
        self.assert_json_equal('', 'calldetail/@0/total_amount', 10.50)
        self.assert_json_equal('', 'calldetail/@0/set.total_part', None)
        self.assert_json_equal('', 'calldetail/@0/owner_part', 0)
        self.assert_json_equal('', 'calldetail/@0/price', 10.50)

        self.assert_json_equal('', 'calldetail/@1/type_call_ex', 'charge exceptionnelle')
        self.assert_json_equal('', 'calldetail/@1/set', None)
        self.assert_json_equal('', 'calldetail/@1/total_amount', 0.75)
        self.assert_json_equal('', 'calldetail/@1/set.total_part', None)
        self.assert_json_equal('', 'calldetail/@1/owner_part', 0)
        self.assert_json_equal('', 'calldetail/@1/price', 0.75)

        self.assert_json_equal('', 'calldetail/@2/type_call_ex', 'avance de fonds')
        self.assert_json_equal('', 'calldetail/@2/set', None)
        self.assert_json_equal('', 'calldetail/@2/total_amount', 0.60)
        self.assert_json_equal('', 'calldetail/@2/set.total_part', None)
        self.assert_json_equal('', 'calldetail/@2/owner_part', 0)
        self.assert_json_equal('', 'calldetail/@2/price', 0.60)

        self.assert_json_equal('', 'calldetail/@3/type_call_ex', 'emprunt')
        self.assert_json_equal('', 'calldetail/@3/set', None)
        self.assert_json_equal('', 'calldetail/@3/total_amount', 0.25)
        self.assert_json_equal('', 'calldetail/@3/set.total_part', None)
        self.assert_json_equal('', 'calldetail/@3/owner_part', 0)
        self.assert_json_equal('', 'calldetail/@3/price', 0.25)

        self.assert_json_equal('', 'calldetail/@4/type_call_ex', 'fonds travaux')
        self.assert_json_equal('', 'calldetail/@4/set', None)
        self.assert_json_equal('', 'calldetail/@4/total_amount', 0.40)
        self.assert_json_equal('', 'calldetail/@4/set.total_part', None)
        self.assert_json_equal('', 'calldetail/@4/owner_part', 0)
        self.assert_json_equal('', 'calldetail/@4/price', 0.40)

    def test_check_ventilation(self):
        init_compta()
        year = FiscalYear.get_current()
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau', """-2|17|7|-70.000000|0|0|None|
-3|18|7|70.000000|0|0|None|""", True)
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
        self.assert_count_equal('callfunds', 0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 29.18)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 12.5)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 12.5)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)

        add_test_callfunds(True, False)
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', '1')
        self.assert_json_equal('', 'callfunds/@0/total', 131.25)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 102.07)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 12.5)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 12.5)
        self.assert_json_equal('', 'callfunds/@1/num', '1')
        self.assert_json_equal('', 'callfunds/@1/total', 87.50)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 87.50)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_json_equal('', 'callfunds/@1/num', '1')
        self.assert_json_equal('', 'callfunds/@1/total', 56.25)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 0.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 13.75)

        CallFunds.devalid('1')
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
        self.assert_count_equal('callfunds', 0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 29.18)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 12.5)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 12.5)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)

    def test_ventilation_internal_payoff(self):
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, False)
        init_compta()

        self.factory.xfer = OwnerVentilatePay()
        self.calljson('/diacamma.condominium/ownerVentilatePay', {'CONFIRME': 'YES', 'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerVentilatePay')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', 29.18)
        self.assert_count_equal('entryline', 5)
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
        self.assert_json_equal('', '#add_refund/action', None)

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 2)
        self.assert_json_equal('', 'expense/@0/num', '2')
        self.assert_json_equal('', 'expense/@0/total', 75.0)
        self.assert_json_equal('', 'expense/@0/total_payed', 0.0)
        self.assert_json_equal('', 'expense/@1/num', '1')
        self.assert_json_equal('', 'expense/@1/total', 100.0)
        self.assert_json_equal('', 'expense/@1/total_payed', 0.0)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 11, 'amount': '75.0',
                                                           'date': '2015-08-28', 'mode': 6, 'linked_supporting': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 10, 'amount': '10.0',
                                                           'date': '2015-09-07', 'mode': 6, 'linked_supporting': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', 29.18)
        self.assert_count_equal('entryline', 7)
        self.assert_json_equal('LABELFORM', 'thirdtotal', 67.93)
        self.assert_json_equal('LABELFORM', 'sumtopay', 0.0)
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 17.07)
        self.assert_count_equal('payoff', 2)
        self.assert_json_equal('', 'payoff/@0/date', "2015-08-28")
        self.assert_json_equal('', 'payoff/@0/mode', 6)
        self.assert_json_equal('', 'payoff/@0/amount', 75.0)
        self.assert_json_equal('', 'payoff/@0/reference', 'dépense 2 - creation')
        self.assert_json_equal('', 'payoff/@0/bank_account_ex', None)
        self.assert_json_equal('', 'payoff/@1/date', "2015-09-07")
        self.assert_json_equal('', 'payoff/@1/mode', 6)
        self.assert_json_equal('', 'payoff/@1/amount', 10.0)
        self.assert_json_equal('', 'payoff/@1/reference', 'dépense 1 - opq 666')
        self.assert_json_equal('', 'payoff/@1/bank_account_ex', None)

        self.factory.xfer = OwnerVentilatePay()
        self.calljson('/diacamma.condominium/ownerVentilatePay', {'CONFIRME': 'YES', 'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerVentilatePay')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', 29.18)
        self.assert_count_equal('entryline', 7)
        self.assert_json_equal('LABELFORM', 'thirdtotal', 67.93)
        self.assert_json_equal('LABELFORM', 'sumtopay', 0.0)
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 7.07)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/date', "2015-08-28")
        self.assert_json_equal('', 'payoff/@0/mode', 6)
        self.assert_json_equal('', 'payoff/@0/amount', 75.0)
        self.assert_json_equal('', 'payoff/@0/reference', 'dépense 2 - creation')
        self.assert_json_equal('', 'payoff/@0/bank_account_ex', None)

        self.factory.xfer = OwnerVentilatePay()
        self.calljson('/diacamma.condominium/ownerVentilatePay', {'CONFIRME': 'YES', 'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerVentilatePay')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', 29.18)
        self.assert_count_equal('entryline', 7)
        self.assert_json_equal('LABELFORM', 'thirdtotal', 67.93)
        self.assert_json_equal('LABELFORM', 'sumtopay', 0.0)
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 7.07)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/date', "2015-08-28")
        self.assert_json_equal('', 'payoff/@0/mode', 6)
        self.assert_json_equal('', 'payoff/@0/amount', 75.0)
        self.assert_json_equal('', 'payoff/@0/reference', 'dépense 2 - creation')
        self.assert_json_equal('', 'payoff/@0/bank_account_ex', None)

    def test_refund_ventilation(self):
        init_compta()
        year = FiscalYear.get_current()
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau', """-2|17|7|-70.000000|0|0|None|
-3|18|7|70.000000|0|0|None|""", True)
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)
        self.assert_json_equal('BUTTON', 'add_refund', '')
        self.assert_action_equal('POST', '#add_refund/action', ('remboursement', 'images/new.png', 'diacamma.condominium', 'ownerRefund', 0, 1, 1))
        self.assert_count_equal('payment', 1)

        self.factory.xfer = OwnerRefund()
        self.calljson('/diacamma.condominium/ownerRefund', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerRefund')
        self.assert_count_equal('', 6)
        self.assert_json_equal('LABELFORM', 'supportings', 'Dalton Joe')
        self.assert_json_equal('FLOAT', 'amount', 70.0)

        self.factory.xfer = OwnerRefund()
        self.calljson('/diacamma.condominium/ownerRefund', {'SAVE': 'YES', 'owner': 3, 'amount': 50.0, 'mode': 0, 'reference': 'abc123',
                                                            'bank_account': 0, 'date': '2015-02-03', 'fee_bank': 0.0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerRefund')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 2)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)
        self.assert_json_equal('', 'payoff/@1/amount', -50.0)
        self.assert_action_equal('POST', '#add_refund/action', ('remboursement', 'images/new.png', 'diacamma.condominium', 'ownerRefund', 0, 1, 1))
        self.assert_count_equal('payment', 2)
        self.assert_count_equal('entryline', 1)
        self.assert_json_equal('', 'entryline/@0/designation_ref', 'règlement de Dalton Joe')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-02-03")
        self.assert_json_equal('', 'entryline/@0/debit', -50.0)

        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 120.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)
        self.assert_action_equal('POST', '#add_refund/action', ('remboursement', 'images/new.png', 'diacamma.condominium', 'ownerRefund', 0, 1, 1))
        self.assert_count_equal('payment', 2)
        self.assert_count_equal('entryline', 1)
        self.assert_json_equal('', 'entryline/@0/designation_ref', 'règlement de appel de fonds')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-02-03")
        self.assert_json_equal('', 'entryline/@0/debit', -50.0)


class OwnerBelgiumTest(PaymentTest):

    def setUp(self):
        # print('>> %s' % self._testMethodName)
        LucteriosTest.setUp(self)
        default_compta_be(with12=False)
        initial_thirds_be()
        default_costaccounting()
        default_bankaccount_be()
        default_setowner_be()
        rmtree(get_user_dir(), True)

    def tearDown(self):
        LucteriosTest.tearDown(self)
        # print('<< %s' % self._testMethodName)

    def test_owner_situation(self):
        add_test_callfunds(False, True)
        add_test_expenses_be(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_count_equal('', 52)
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
        self.assert_json_equal('', 'loadcount/@0/total', {'value': 100.0, 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@0/ratio', {'value': "75/100", 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@0/ventilated', {'value': 75.0, 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@0/recoverable_load', {'value': 30.0, 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@1/designation', "&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;{[b]}[602000] 602000{[/b]}")
        self.assert_json_equal('', 'loadcount/@1/total', {'value': 100.0, 'format': '{[b]}{0}{[/b]}'})
        self.assert_json_equal('', 'loadcount/@1/ratio', {'value': "75/100", 'format': '{[b]}{0}{[/b]}'})
        self.assert_json_equal('', 'loadcount/@1/ventilated', {'value': 75.0, 'format': '{[b]}{0}{[/b]}'})
        self.assert_json_equal('', 'loadcount/@1/recoverable_load', {'value': 30.0, 'format': '{[b]}{0}{[/b]}'})

        self.assert_json_equal('', 'loadcount/@4/designation', "{[i]}[3] CCC{[/i]}")
        self.assert_json_equal('', 'loadcount/@4/total', {'value': 75.0, 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@4/ratio', {'value': "45/100", 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@4/ventilated', {'value': 33.75, 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@4/recoverable_load', {'value': 20.25, 'format': '{[i]}{0}{[/i]}'})
        self.assert_json_equal('', 'loadcount/@5/designation', "&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;{[b]}[601000] 601000{[/b]}")
        self.assert_json_equal('', 'loadcount/@5/total', {'value': 75.0, 'format': '{[b]}{0}{[/b]}'})
        self.assert_json_equal('', 'loadcount/@5/ratio', {'value': "45/100", 'format': '{[b]}{0}{[/b]}'})
        self.assert_json_equal('', 'loadcount/@5/ventilated', {'value': 33.75, 'format': '{[b]}{0}{[/b]}'})
        self.assert_json_equal('', 'loadcount/@5/recoverable_load', {'value': 20.25, 'format': '{[b]}{0}{[/b]}'})

        self.assert_json_equal('', 'loadcount/@8/designation', "")
        self.assert_json_equal('', 'loadcount/@8/total', {'value': 175.0, 'format': '{[u]}{0}{[/u]}'})
        self.assert_json_equal('', 'loadcount/@8/ratio', None)
        self.assert_json_equal('', 'loadcount/@8/ventilated', {'value': 108.75, 'format': '{[u]}{0}{[/u]}'})
        self.assert_json_equal('', 'loadcount/@8/recoverable_load', {'value': 50.25, 'format': '{[u]}{0}{[/u]}'})

    def test_ventilation_credit(self):
        add_test_callfunds(False, True)
        add_test_expenses_be(False, True)
        init_compta()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
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
        self.assert_count_equal('#entryline/actions', 4)
        self.assert_action_equal('POST', '#entryline/actions/@0', ('Editer', 'images/edit.png', 'diacamma.accounting', 'entryAccountOpenFromLine', 0, 1, 0))
        self.assert_action_equal('DELETE', '#entryline/actions/@1', ('Supprimer', 'images/delete.png', 'diacamma.accounting', 'entryAccountDel', 0, 1, 2))
        self.assert_action_equal('POST', '#entryline/actions/@2', ('Clôturer', 'images/ok.png', 'diacamma.accounting', 'entryAccountClose', 0, 1, 2))
        self.assert_action_equal('POST', '#entryline/actions/@3', ('(dé)lettrage', 'images/left.png', 'diacamma.accounting', 'entryAccountLink', 0, 1, 2))
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
        self.assert_json_equal('', '#add_refund/action', None)

        self.factory.xfer = OwnerVentilatePay()
        self.calljson('/diacamma.condominium/ownerVentilatePay', {'CONFIRME': 'YES', 'owner': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerVentilatePay')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'thirdinitial', 29.18)
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -131.25)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-06-15")
        self.assert_json_equal('', 'entryline/@1/credit', 100.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@2/debit', -45.00)
        self.assert_json_equal('', 'entryline/@3/entry.date_value', "2015-07-21")
        self.assert_json_equal('', 'entryline/@3/credit', 27.93)
        self.assert_json_equal('', 'entryline/@4/entry.date_value', "2015-07-21")
        self.assert_json_equal('', 'entryline/@4/credit', 2.07)
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
        self.assert_json_equal('LABELFORM', 'supportings', "Minimum{[br/]}appel de fonds N°2 Minimum")

    def test_ventilation_debit(self):
        add_test_callfunds(False, True)
        add_test_expenses_be(False, True)
        init_compta()
        pay1 = Payoff(supporting_id=2, date='2015-07-31', mode=0, amount=150.0)
        pay1.editor.before_save(None)
        pay1.save()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
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
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-06-10")
        self.assert_json_equal('', 'entryline/@0/debit', -87.50)
        self.assert_json_equal('', 'entryline/@1/entry.date_value', "2015-07-14")
        self.assert_json_equal('', 'entryline/@1/debit', -35.00)
        self.assert_json_equal('', 'entryline/@2/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@2/credit', 12.50)
        self.assert_json_equal('', 'entryline/@3/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@3/credit', 35.00)
        self.assert_json_equal('', 'entryline/@4/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@4/credit', 87.50)
        self.assert_json_equal('', 'entryline/@5/entry.date_value', "2015-07-31")
        self.assert_json_equal('', 'entryline/@5/credit', 15.00)
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

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 9}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('LABELFORM', 'status', 2)
        self.assert_json_equal('LABELFORM', 'owner', 'Dalton William')
        self.assert_json_equal('LABELFORM', 'total', 12.50)
        self.assert_count_equal('calldetail', 1)
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge de travaux')
        self.assert_json_equal('', 'calldetail/@0/set', None)
        self.assert_json_equal('', 'calldetail/@0/total_amount', 12.50)
        self.assert_json_equal('', 'calldetail/@0/set.total_part', None)
        self.assert_json_equal('', 'calldetail/@0/owner_part', 0)
        self.assert_json_equal('', 'calldetail/@0/price', 12.50)

    def test_check_ventilation(self):
        init_compta()
        year = FiscalYear.get_current()
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau', """-2|17|7|-70.000000|0|0|None|
-3|18|7|70.000000|0|0|None|""", True)
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
        self.assert_count_equal('callfunds', 0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 29.18)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 12.5)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 12.5)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)

        add_test_callfunds(True, False)
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', '1')
        self.assert_json_equal('', 'callfunds/@0/total', 131.25)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 102.07)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 12.5)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 12.5)
        self.assert_json_equal('', 'callfunds/@1/num', '1')
        self.assert_json_equal('', 'callfunds/@1/total', 87.50)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 87.50)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_json_equal('', 'callfunds/@1/num', '1')
        self.assert_json_equal('', 'callfunds/@1/total', 56.25)
        self.assert_json_equal('', 'callfunds/@1/supporting.total_rest_topay', 56.25)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)

        CallFunds.devalid('1')
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Minimum')
        self.assert_count_equal('callfunds', 0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 29.18)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton William')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 12.5)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 12.5)
        self.assert_count_equal('payoff', 0)

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)

    def test_refund_ventilation(self):
        init_compta()
        year = FiscalYear.get_current()
        add_entry(year.id, 1, '2015-01-01', 'Report à nouveau', """-2|17|7|-70.000000|0|0|None|
-3|18|7|70.000000|0|0|None|""", True)
        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)
        self.assert_json_equal('BUTTON', 'add_refund', '')
        self.assert_action_equal('POST', '#add_refund/action', ('remboursement', 'images/new.png', 'diacamma.condominium', 'ownerRefund', 0, 1, 1))
        self.assert_count_equal('payment', 1)

        self.factory.xfer = OwnerRefund()
        self.calljson('/diacamma.condominium/ownerRefund', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerRefund')
        self.assert_count_equal('', 6)
        self.assert_json_equal('LABELFORM', 'supportings', 'Dalton Joe')
        self.assert_json_equal('FLOAT', 'amount', 70.0)

        self.factory.xfer = OwnerRefund()
        self.calljson('/diacamma.condominium/ownerRefund', {'SAVE': 'YES', 'owner': 3, 'amount': 70.0, 'mode': 0, 'reference': 'abc123',
                                                            'bank_account': 0, 'date': '2015-02-03', 'fee_bank': 0.0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'ownerRefund')

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 70.0)
        self.assert_count_equal('payoff', 2)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)
        self.assert_json_equal('', 'payoff/@1/amount', -70.0)
        self.assert_json_equal('', '#add_refund/action', None)
        self.assert_count_equal('payment', 2)
        self.assert_count_equal('entryline', 1)
        self.assert_json_equal('', 'entryline/@0/designation_ref', 'règlement de Dalton Joe')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-02-03")
        self.assert_json_equal('', 'entryline/@0/debit', -70.0)

        Owner.ventilate_pay_all()

        self.factory.xfer = OwnerShow()
        self.calljson('/diacamma.condominium/ownerShow', {'owner': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_json_equal('LABELFORM', 'third', 'Dalton Joe')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/num', None)
        self.assert_json_equal('', 'callfunds/@0/total', 70.0)
        self.assert_json_equal('', 'callfunds/@0/supporting.total_rest_topay', 140.0)
        self.assert_count_equal('payoff', 1)
        self.assert_json_equal('', 'payoff/@0/amount', 70.0)
        self.assert_action_equal('POST', '#add_refund/action', ('remboursement', 'images/new.png', 'diacamma.condominium', 'ownerRefund', 0, 1, 1))
        self.assert_count_equal('payment', 2)
        self.assert_count_equal('entryline', 1)
        self.assert_json_equal('', 'entryline/@0/designation_ref', 'règlement de appel de fonds')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', "2015-02-03")
        self.assert_json_equal('', 'entryline/@0/debit', -70.0)


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


class ExempleArcTest(PaymentTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        self._setup_exemple()

    def _setup_exemple(self):
        Parameter.change_value('CORE-connectmode', '2')
        Parameter.change_value('CORE-Wizard', 'False')
        paramchange_payoff([])
        change_ourdetail()
        set_accounting_system('FR')
        new_year = FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=1)
        new_year.set_has_actif()
        create_account(['502', '512', '581'], 0, None)  # 1 2 3
        create_account(['4501', '4502', '4503', '4504', '4505'], 0, None)  # 4 5 6 7 8
        create_account(['401'], 1, None)  # 9
        create_account(['120', '1031', '1032', '105'], 2, None)  # 10 11 12 13
        create_account(['701', '702', '703', '704', '705'], 3, None)  # 14 15 16 17 18
        create_account(['601', '602', '604', '607', '627'], 4, None)  # 19 20 21 22 23
        BankAccount.objects.create(designation="Compte chèque", reference="0123 456789 321654 12", account_code="512")
        BankAccount.objects.create(designation="chèque en attente", reference="0123 456789 321654 12", account_code="581")
        self._config_comdominum()
        new_third = Third.objects.create(contact=change_legal('Engie'), status=0)
        AccountThird.objects.create(third=new_third, code='401')
        new_third = Third.objects.create(contact=change_legal('Propre & Net'), status=0)
        AccountThird.objects.create(third=new_third, code='401')

        add_entry(new_year.id, 1, '2016-01-01', 'Report à nouveau', """-1|11|0|800.000000|0|0|None|
-2|12|0|2500.000000|0|0|None|
-3|9|6|650.000000|0|0|None|
-3|9|7|200.000000|0|0|None|
-3|4|3|100.000000|0|0|None|
-3|4|1|-250.000000|0|0|None|
-3|4|0|-580.000000|0|0|None|
-3|1|0|3000.000000|0|0|None|
-3|2|0|1880.000000|0|0|None|""", True)

    def _config_comdominum(self):
        owner_dupont = create_owner_fr('M. Dupont')  # lot 1, 10, 11 = 205+30+30 = 265
        owner_durant = create_owner_fr('M. Durant')  # lot 2, 6 = 130+20 = 150
        owner_dernier = create_owner_fr('M. Mme Dernier')  # lot 5, 9 = 185+20 = 205
        owner_dubois = create_owner_fr('M. Mme Dubois')  # lot 3, 7 = 170+20 = 190
        owner_paul_pierre = create_owner_fr('M. Paul Mme Pierre')  # lot 4, 8 = 170+20 = ;;190
        PropertyLot.objects.create(num=1, value=205.0, description="Local commercial RDC gauche", owner=owner_dupont)
        PropertyLot.objects.create(num=2, value=130.0, description="Appartement RDC droite", owner=owner_durant)
        PropertyLot.objects.create(num=3, value=170.0, description="Appartement 1er étage", owner=owner_dubois)
        PropertyLot.objects.create(num=4, value=170.0, description="Appartement 2ème étage", owner=owner_paul_pierre)
        PropertyLot.objects.create(num=5, value=185.0, description="Appartement 3ème étage", owner=owner_dernier)
        PropertyLot.objects.create(num=6, value=20.0, description="Emplacement parking N°1", owner=owner_durant)
        PropertyLot.objects.create(num=7, value=20.0, description="Emplacement parking N°2", owner=owner_dubois)
        PropertyLot.objects.create(num=8, value=20.0, description="Emplacement parking N°3", owner=owner_paul_pierre)
        PropertyLot.objects.create(num=9, value=20.0, description="Emplacement parking N°4", owner=owner_dernier)
        PropertyLot.objects.create(num=10, value=30.0, description="Parking sous-sol N°1", owner=owner_dupont)
        PropertyLot.objects.create(num=11, value=30.0, description="Parking sous-sol N°2", owner=owner_dupont)

        new_set = Set.objects.create(name="Généraux", is_link_to_lots=True, type_load=0)
        new_set.set_of_lots.set(PropertyLot.objects.all())
        new_set.save()
        _set_budget(new_set, '601', 3800.0)

        new_set = Set.objects.create(name="Escalier", is_link_to_lots=False, type_load=0)
        _set_partition(setpart=new_set, owner=owner_dupont, value=289.0)
        _set_partition(setpart=new_set, owner=owner_durant, value=144.0)
        _set_partition(setpart=new_set, owner=owner_dernier, value=199.0)
        _set_partition(setpart=new_set, owner=owner_dubois, value=184.0)
        _set_partition(setpart=new_set, owner=owner_paul_pierre, value=184.0)
        _set_budget(new_set, '601', 120.0)

        new_set = Set.objects.create(name="Chauffage", is_link_to_lots=False, type_load=0)
        _set_partition(setpart=new_set, owner=owner_dupont, value=310.0)
        _set_partition(setpart=new_set, owner=owner_durant, value=110.0)
        _set_partition(setpart=new_set, owner=owner_dernier, value=260.0)
        _set_partition(setpart=new_set, owner=owner_dubois, value=160.0)
        _set_partition(setpart=new_set, owner=owner_paul_pierre, value=160.0)
        _set_budget(new_set, '601', 2030.0)

        new_set = Set.objects.create(name="Sous-sol", is_link_to_lots=False, type_load=0)
        _set_partition(setpart=new_set, owner=owner_dupont, value=1000.0)
        _set_partition(setpart=new_set, owner=owner_durant, value=0.0)
        _set_partition(setpart=new_set, owner=owner_dernier, value=0.0)
        _set_partition(setpart=new_set, owner=owner_dubois, value=0.0)
        _set_partition(setpart=new_set, owner=owner_paul_pierre, value=0.0)
        _set_budget(new_set, '601', 50.0)

        new_set = Set.objects.create(name="Eau privative", is_link_to_lots=False, type_load=0)
        _set_partition(setpart=new_set, owner=owner_dupont, value=1.0)
        _set_partition(setpart=new_set, owner=owner_durant, value=1.0)
        _set_partition(setpart=new_set, owner=owner_dernier, value=1.0)
        _set_partition(setpart=new_set, owner=owner_dubois, value=1.0)
        _set_partition(setpart=new_set, owner=owner_paul_pierre, value=1.0)

    def _check_accounting(self, trial_balance_values, sum_total):
        self.factory.xfer = FiscalYearTrialBalance()
        self.calljson('/diacamma.accounting/fiscalYearTrialBalance', {'filtercode': '', 'with_third': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self.assert_count_equal('report_1', len(trial_balance_values) + 2)
        num = 0
        for accound_code, total_debit, total_credit in trial_balance_values:
            self.assert_json_equal('', 'report_1/@%d/designation' % num, accound_code)
            self.assert_json_equal('', 'report_1/@%d/total_debit' % num, total_debit, delta=1e-3)
            self.assert_json_equal('', 'report_1/@%d/total_credit' % num, total_credit, delta=1e-3)
            num += 1
        self.assert_json_equal('', 'report_1/@%d/designation' % num, "")
        num += 1
        self.assert_json_equal('', 'report_1/@%d/total_debit' % num, {'value': sum_total, 'format': '{[u]}{[b]}{0}{[/b]}{[/u]}'}, delta=1e-3)
        self.assert_json_equal('', 'report_1/@%d/total_credit' % num, {'value': sum_total, 'format': '{[u]}{[b]}{0}{[/b]}{[/u]}'}, delta=1e-3)

    def test_check_owner(self):
        self.factory.xfer = OwnerAndPropertyLotList()
        self.calljson('/diacamma.condominium/ownerAndPropertyLotList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'ownerAndPropertyLotList')
        self.assert_count_equal('owner', 5)
        self.assert_json_equal('', 'owner/@0/id', '1')
        self.assert_json_equal('', 'owner/@0/third', 'M. Dupont')
        self.assert_json_equal('', 'owner/@0/thirdinitial', 250.0)
        self.assert_json_equal('', 'owner/@1/id', '2')
        self.assert_json_equal('', 'owner/@1/third', 'M. Durant')
        self.assert_json_equal('', 'owner/@1/thirdinitial', 0.0)
        self.assert_json_equal('', 'owner/@2/id', '3')
        self.assert_json_equal('', 'owner/@2/third', 'M. Mme Dernier')
        self.assert_json_equal('', 'owner/@2/thirdinitial', -100.0)
        self.assert_json_equal('', 'owner/@3/id', '4')
        self.assert_json_equal('', 'owner/@3/third', 'M. Mme Dubois')
        self.assert_json_equal('', 'owner/@3/thirdinitial', 0.0)
        self.assert_json_equal('', 'owner/@4/id', '5')
        self.assert_json_equal('', 'owner/@4/third', 'M. Paul Mme Pierre')
        self.assert_json_equal('', 'owner/@4/thirdinitial', 0.0)

        self.assert_count_equal('propertylot', 11)
        self.assert_json_equal('', 'propertylot/@0/num', '1')
        self.assert_json_equal('', 'propertylot/@0/ratio', 20.5)
        self.assert_json_equal('', 'propertylot/@0/description', "Local commercial RDC gauche")
        self.assert_json_equal('', 'propertylot/@0/owner', 'M. Dupont')

        self.assert_json_equal('', 'propertylot/@1/num', '2')
        self.assert_json_equal('', 'propertylot/@1/ratio', 13.0)
        self.assert_json_equal('', 'propertylot/@1/description', "Appartement RDC droite")
        self.assert_json_equal('', 'propertylot/@1/owner', 'M. Durant')

        self.assert_json_equal('', 'propertylot/@2/num', '3')
        self.assert_json_equal('', 'propertylot/@2/ratio', 17.0)
        self.assert_json_equal('', 'propertylot/@2/description', "Appartement 1er étage")
        self.assert_json_equal('', 'propertylot/@2/owner', 'M. Mme Dubois')

        self.assert_json_equal('', 'propertylot/@3/num', '4')
        self.assert_json_equal('', 'propertylot/@3/ratio', 17.0)
        self.assert_json_equal('', 'propertylot/@3/description', "Appartement 2ème étage")
        self.assert_json_equal('', 'propertylot/@3/owner', 'M. Paul Mme Pierre')

        self.assert_json_equal('', 'propertylot/@4/num', '5')
        self.assert_json_equal('', 'propertylot/@4/ratio', 18.5)
        self.assert_json_equal('', 'propertylot/@4/description', "Appartement 3ème étage")
        self.assert_json_equal('', 'propertylot/@4/owner', 'M. Mme Dernier')

        self.assert_json_equal('', 'propertylot/@5/num', '6')
        self.assert_json_equal('', 'propertylot/@5/ratio', 2.0)
        self.assert_json_equal('', 'propertylot/@5/description', "Emplacement parking N°1")
        self.assert_json_equal('', 'propertylot/@5/owner', 'M. Durant')

        self.assert_json_equal('', 'propertylot/@6/num', '7')
        self.assert_json_equal('', 'propertylot/@6/ratio', 2.0)
        self.assert_json_equal('', 'propertylot/@6/description', "Emplacement parking N°2")
        self.assert_json_equal('', 'propertylot/@6/owner', 'M. Mme Dubois')

        self.assert_json_equal('', 'propertylot/@7/num', '8')
        self.assert_json_equal('', 'propertylot/@7/ratio', 2.0)
        self.assert_json_equal('', 'propertylot/@7/description', "Emplacement parking N°3")
        self.assert_json_equal('', 'propertylot/@7/owner', 'M. Paul Mme Pierre')

        self.assert_json_equal('', 'propertylot/@8/num', '9')
        self.assert_json_equal('', 'propertylot/@8/ratio', 2.0)
        self.assert_json_equal('', 'propertylot/@8/description', "Emplacement parking N°4")
        self.assert_json_equal('', 'propertylot/@8/owner', 'M. Mme Dernier')

        self.assert_json_equal('', 'propertylot/@9/num', '10')
        self.assert_json_equal('', 'propertylot/@9/ratio', 3.0)
        self.assert_json_equal('', 'propertylot/@9/description', "Parking sous-sol N°1")
        self.assert_json_equal('', 'propertylot/@9/owner', 'M. Dupont')

        self.assert_json_equal('', 'propertylot/@10/num', '11')
        self.assert_json_equal('', 'propertylot/@10/ratio', 3.0)
        self.assert_json_equal('', 'propertylot/@10/description', "Parking sous-sol N°2")
        self.assert_json_equal('', 'propertylot/@10/owner', 'M. Dupont')

    def test_check_setofload(self):
        self.factory.xfer = SetList()
        self.calljson('/diacamma.condominium/setList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'setList')
        self.assert_count_equal('set', 5)
        self.assert_json_equal('', 'set/@0/identify', '[1] Généraux')
        self.assert_json_equal('', 'set/@0/budget_txt', 3800.00)
        self.assert_json_equal('', 'set/@0/type_load', 0)
        self.assert_json_equal('', 'set/@0/partitionfill_set', ['M. Dupont : 26,5 %',
                                                                'M. Durant : 15,0 %',
                                                                'M. Mme Dernier : 20,5 %',
                                                                'M. Mme Dubois : 19,0 %',
                                                                'M. Paul Mme Pierre : 19,0 %'])
        self.assert_json_equal('', 'set/@0/sumexpense', 0.00)
        self.assert_json_equal('', 'set/@1/identify', '[2] Escalier')
        self.assert_json_equal('', 'set/@1/budget_txt', 120.00)
        self.assert_json_equal('', 'set/@1/type_load', 0)
        self.assert_json_equal('', 'set/@1/partitionfill_set', ['M. Dupont : 28,9 %',
                                                                'M. Durant : 14,4 %',
                                                                'M. Mme Dernier : 19,9 %',
                                                                'M. Mme Dubois : 18,4 %',
                                                                'M. Paul Mme Pierre : 18,4 %'])
        self.assert_json_equal('', 'set/@1/sumexpense', 0.00)
        self.assert_json_equal('', 'set/@2/identify', '[3] Chauffage')
        self.assert_json_equal('', 'set/@2/budget_txt', 2030.00)
        self.assert_json_equal('', 'set/@2/type_load', 0)
        self.assert_json_equal('', 'set/@2/partitionfill_set', ['M. Dupont : 31,0 %',
                                                                'M. Durant : 11,0 %',
                                                                'M. Mme Dernier : 26,0 %',
                                                                'M. Mme Dubois : 16,0 %',
                                                                'M. Paul Mme Pierre : 16,0 %'])
        self.assert_json_equal('', 'set/@3/sumexpense', 0.00)
        self.assert_json_equal('', 'set/@3/identify', '[4] Sous-sol')
        self.assert_json_equal('', 'set/@3/budget_txt', 50.00)
        self.assert_json_equal('', 'set/@3/type_load', 0)
        self.assert_json_equal('', 'set/@3/partitionfill_set', ['M. Dupont : 100,0 %'])
        self.assert_json_equal('', 'set/@3/sumexpense', 0.00)
        self.assert_json_equal('', 'set/@4/identify', '[5] Eau privative')
        self.assert_json_equal('', 'set/@4/budget_txt', 0.00)
        self.assert_json_equal('', 'set/@4/type_load', 0)
        self.assert_json_equal('', 'set/@4/partitionfill_set', ['M. Dupont : 20,0 %',
                                                                'M. Durant : 20,0 %',
                                                                'M. Mme Dernier : 20,0 %',
                                                                'M. Mme Dubois : 20,0 %',
                                                                'M. Paul Mme Pierre : 20,0 %'])
        self.assert_json_equal('', 'set/@4/sumexpense', 0.00)

    def test_account(self):
        self._check_accounting([("[1031] 1031", 0, 800.0),
                                ("[1032] 1032", 0, 2500.0),
                                ("[401 Engie]", 0, 650.0),
                                ("[401 Propre & Net]", 0, 200.0),
                                ("[4501] 4501", 0, 580.0),
                                ("[4501 M. Dupont]", 0, 250.0),
                                ("[4501 M. Mme Dernier]", 100.0, 0),
                                ("[502] 502", 3000.0, 0),
                                ("[512] 512", 1880.0, 0)],
                               4980.0)

    def test_add_first_current_calloffunds(self):
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': -1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)

        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 4)
        self.assert_json_equal('', 'callfunds/@0/date', "2016-01-01")
        self.assert_json_equal('', 'callfunds/@1/date', "2016-04-01")
        self.assert_json_equal('', 'callfunds/@2/date', "2016-07-01")
        self.assert_json_equal('', 'callfunds/@3/date', "2016-10-01")
        self.assert_json_equal('', 'callfunds/@0/total', 1500.00)
        self.assert_json_equal('', 'callfunds/@1/total', 1500.00)
        self.assert_json_equal('', 'callfunds/@2/total', 1500.00)
        self.assert_json_equal('', 'callfunds/@3/total', 1500.00)
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 5)
        self.assert_json_equal('', 'callfunds/@0/owner', 'M. Dupont')
        self.assert_json_equal('', 'callfunds/@0/total', 430.24, delta=1e-3)  # Book = 430.25
        self.assert_json_equal('', 'callfunds/@1/owner', 'M. Durant')
        self.assert_json_equal('', 'callfunds/@1/total', 202.65, delta=1e-3)
        self.assert_json_equal('', 'callfunds/@2/owner', 'M. Mme Dernier')
        self.assert_json_equal('', 'callfunds/@2/total', 332.67, delta=1e-3)
        self.assert_json_equal('', 'callfunds/@3/owner', 'M. Mme Dubois')
        self.assert_json_equal('', 'callfunds/@3/total', 267.22, delta=1e-3)
        self.assert_json_equal('', 'callfunds/@4/owner', 'M. Paul Mme Pierre')
        self.assert_json_equal('', 'callfunds/@4/total', 267.22, delta=1e-3)

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 5}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('LABELFORM', 'status', 1)
        self.assert_json_equal('LABELFORM', 'owner', 'M. Dupont')
        self.assert_json_equal('LABELFORM', 'total', 430.24, delta=1e-3)
        self.assert_count_equal('calldetail', 5)
        self.assert_json_equal('', 'calldetail/@0/set', "[1] Généraux")
        self.assert_json_equal('', 'calldetail/@0/total_amount', 950.00)
        self.assert_json_equal('', 'calldetail/@0/set.total_part', 1000)
        self.assert_json_equal('', 'calldetail/@0/owner_part', 265.0)
        self.assert_json_equal('', 'calldetail/@0/price', 251.75, delta=1e-3)

        self.assert_json_equal('', 'calldetail/@1/set', "[2] Escalier")
        self.assert_json_equal('', 'calldetail/@1/total_amount', 30.00)
        self.assert_json_equal('', 'calldetail/@1/set.total_part', 1000)
        self.assert_json_equal('', 'calldetail/@1/owner_part', 289.00)
        self.assert_json_equal('', 'calldetail/@1/price', 8.67, delta=1e-3)

        self.assert_json_equal('', 'calldetail/@2/set', "[3] Chauffage")
        self.assert_json_equal('', 'calldetail/@2/total_amount', 507.50)
        self.assert_json_equal('', 'calldetail/@2/set.total_part', 1000)
        self.assert_json_equal('', 'calldetail/@2/owner_part', 310.0)
        self.assert_json_equal('', 'calldetail/@2/price', 157.32, delta=1e-3)  # Book = 157.32

        self.assert_json_equal('', 'calldetail/@3/set', "[4] Sous-sol")
        self.assert_json_equal('', 'calldetail/@3/total_amount', 12.50)
        self.assert_json_equal('', 'calldetail/@3/set.total_part', 1000)
        self.assert_json_equal('', 'calldetail/@3/owner_part', 1000.0)
        self.assert_json_equal('', 'calldetail/@3/price', 12.50, delta=1e-3)

        self.assert_json_equal('', 'calldetail/@4/set', "[5] Eau privative")
        self.assert_json_equal('', 'calldetail/@4/price', 0.0, delta=1e-3)

        self._check_accounting([("[1031] 1031", 0, 800.0),
                                ("[1032] 1032", 0, 2500.0),
                                ("[401 Engie]", 0, 650.0),
                                ("[401 Propre & Net]", 0, 200.0),
                                ("[4501] 4501", 0, 580.0),
                                ("[4501 M. Dupont]", 430.24, 250.0),
                                ("[4501 M. Durant]", 202.65, 0),
                                ("[4501 M. Mme Dernier]", 432.67, 0),
                                ("[4501 M. Mme Dubois]", 267.22, 0),
                                ("[4501 M. Paul Mme Pierre]", 267.22, 0),
                                ("[502] 502", 3000.0, 0),
                                ("[512] 512", 1880.0, 0),
                                ("[701] 701", 0.0, 1500.0)],
                               6480.0)

    def test_add_payoff(self):
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = PayoffAddModify()  # M. Dupont
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 1, 'amount': '180.24', 'date': '2016-04-01', 'mode': 1, 'bank_account': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = PayoffAddModify()  # M. Durant
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 2, 'amount': '202.65', 'date': '2016-01-06', 'mode': 1, 'bank_account': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = PayoffAddModify()  # M. Mme Dernier
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 3, 'amount': '432.67', 'date': '2016-01-01', 'mode': 2, 'bank_account': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = PayoffAddModify()  # M. Mme Dubois
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '267.22', 'date': '2016-01-04', 'mode': 1, 'bank_account': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = PayoffAddModify()  # M. Paul Mme Pierre
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 5, 'amount': '150.0', 'date': '2016-01-08', 'mode': 1, 'bank_account': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        add_entry(1, 5, '2016-01-09', 'Remise bancaire', """-1|3|0|-800.110000|0|0|None|\n-2|2|0|800.110000|0|0|None|""", False)

        self._check_accounting([("[1031] 1031", 0, 800.0),
                                ("[1032] 1032", 0, 2500.0),
                                ("[401 Engie]", 0, 650.0),
                                ("[401 Propre & Net]", 0, 200.0),
                                ("[4501] 4501", 0, 580.0),
                                ("[4501 M. Dupont]", 430.24, 430.24),
                                ("[4501 M. Durant]", 202.65, 202.65),
                                ("[4501 M. Mme Dernier]", 432.67, 432.67),
                                ("[4501 M. Mme Dubois]", 267.22, 267.22),
                                ("[4501 M. Paul Mme Pierre]", 267.22, 150.0),
                                ("[502] 502", 3000.0, 0),
                                ("[512] 512", 3112.78, 0),
                                ("[581] 581", 800.11, 800.11),
                                ("[701] 701", 0.0, 1500.0)],
                               8512.89)
