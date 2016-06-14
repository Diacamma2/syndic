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

from diacamma.accounting.test_tools import initial_thirds, default_compta,\
    default_costaccounting
from diacamma.accounting.views import ThirdShow

from diacamma.payoff.test_tools import default_bankaccount,\
    default_paymentmethod, PaymentTest
from diacamma.payoff.views import PayableShow, PayableEmail

from diacamma.condominium.views import SetOwnerList, SetAddModify, SetDel,\
    OwnerAdd, OwnerDel, SetShow, PartitionAddModify, OwnerShow
from diacamma.condominium.test_tools import default_setowner,\
    add_simple_callfunds


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


class MethodTest(PaymentTest):

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
            'COMPONENTS/LABELFORM[@name="total_estimate"]', "0.00€")
        self.assert_count_equal('ACTIONS/ACTION', 3)

        self.factory.xfer = PayableShow()
        self.call('/diacamma.payoff/supportingPaymentMethod',
                  {'owner': 1, 'item_name': 'owner'}, False)
        self.assert_observer(
            'core.exception', 'diacamma.payoff', 'supportingPaymentMethod')
        self.assert_xml_equal(
            "EXCEPTION/MESSAGE", "Pas de paiement pour ce document")

    def test_payment_owner_nopayable(self):
        add_simple_callfunds()
        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_estimate"]', "-131.25€")
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
        add_simple_callfunds()
        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_initial"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_payed"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_estimate"]', "-131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_real"]', "0.00€")
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
            'COMPONENTS/LABELFORM[@name="total_estimate"]', "-131.25€")
        self.check_payment(1, "copropriete de Minimum", "131.25")

    def test_payment_paypal_owner(self):
        default_paymentmethod()
        add_simple_callfunds()
        self.check_payment_paypal(1, "copropriete de Minimum")

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_initial"]', "0.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_call"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_payed"]', "100.00€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_estimate"]', "-31.25€")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_real"]', "100.00€")
        self.assert_count_equal('ACTIONS/ACTION', 4)

    def test_send_owner(self):
        from lucterios.mailing.tests import configSMTP, TestReceiver
        default_paymentmethod()
        add_simple_callfunds()
        configSMTP('localhost', 1025)

        self.factory.xfer = OwnerShow()
        self.call('/diacamma.condominium/ownerShow', {'owner': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'ownerShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="total_estimate"]', "-131.25€")
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
                ['Minimum@worldcompany.com'], server.get(0)[2])
            msg, msg_file = server.check_first_message('my bill', 2)
            self.assertEqual('text/html', msg.get_content_type())
            self.assertEqual('base64', msg.get('Content-Transfer-Encoding', ''))
            self.check_email_msg(msg, 1, "copropriete de Minimum", "131.25")

            self.assertTrue(
                'copropriete_de_Minimum.pdf' in msg_file.get('Content-Type', ''), msg_file.get('Content-Type', ''))
            self.assertEqual(
                "%PDF".encode('ascii', 'ignore'), b64decode(msg_file.get_payload())[:4])
        finally:
            server.stop()
