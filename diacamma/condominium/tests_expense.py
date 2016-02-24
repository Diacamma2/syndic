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
from diacamma.condominium.test_tools import default_setowner
from diacamma.condominium.views_expense import ExpenseList,\
    ExpenseAddModify, ExpenseDel, ExpenseShow, ExpenseDetailAddModify,\
    ExpenseValid, ExpenseClose
from diacamma.payoff.views import SupportingThirdValid, PayoffAddModify
from diacamma.accounting.views_entries import EntryLineAccountList
from diacamma.accounting.views import ThirdShow


class ExpenseTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        initial_thirds()
        LucteriosTest.setUp(self)
        default_compta()
        default_costaccounting()
        default_bankaccount()
        default_setowner()
        rmtree(get_user_dir(), True)

    def test_create(self):
        self.factory.xfer = ExpenseList()
        self.call('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/HEADER', 5)

        self.factory.xfer = ExpenseAddModify()
        self.call('/diacamma.condominium/expenseAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)

        self.factory.xfer = ExpenseAddModify()
        self.call(
            '/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseAddModify')

        self.factory.xfer = ExpenseList()
        self.call('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/HEADER', 5)

        self.factory.xfer = ExpenseShow()
        self.call(
            '/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('COMPONENTS/*', 19)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="third"]', "---")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}aucun tiers sélectionné{[/font]}")
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="expensedetail"]/RECORD', 0)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="expensedetail"]/HEADER', 4)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="expensedetail"]/ACTIONS/ACTION', 3)

        self.factory.xfer = SupportingThirdValid()
        self.call('/diacamma.payoff/supportingThirdValid',
                  {'supporting': 4, 'third': 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = ExpenseShow()
        self.call(
            '/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('COMPONENTS/*', 20)
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="third"]', "Minimum")
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="info"]', "{[font color=\"red\"]}{[/font]}")
        self.assert_count_equal('ACTIONS/ACTION', 3)

        self.factory.xfer = ExpenseDel()
        self.call(
            '/diacamma.condominium/expenseAddDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseAddDel')

        self.factory.xfer = ExpenseList()
        self.call('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/HEADER', 5)

    def test_add(self):
        self.factory.xfer = ExpenseAddModify()
        self.call(
            '/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.call('/diacamma.payoff/supportingThirdValid',
                  {'supporting': 4, 'third': 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = ExpenseDetailAddModify()
        self.call(
            '/diacamma.condominium/expenseDetailAddModify', {'expense': 4}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseDetailAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="set"]', '1')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="price"]', '0.00')
        self.assert_count_equal(
            'COMPONENTS/SELECT[@name="expense_account"]/CASE', 5)
        self.assert_attrib_equal(
            'COMPONENTS/SELECT[@name="expense_account"]/CASE[1]', 'id', '601')
        self.assert_attrib_equal(
            'COMPONENTS/SELECT[@name="expense_account"]/CASE[2]', 'id', '602')
        self.assert_attrib_equal(
            'COMPONENTS/SELECT[@name="expense_account"]/CASE[3]', 'id', '604')
        self.assert_attrib_equal(
            'COMPONENTS/SELECT[@name="expense_account"]/CASE[4]', 'id', '607')
        self.assert_attrib_equal(
            'COMPONENTS/SELECT[@name="expense_account"]/CASE[5]', 'id', '627')

        self.factory.xfer = ExpenseDetailAddModify()
        self.call(
            '/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseDetailAddModify()
        self.call(
            '/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseShow()
        self.call(
            '/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="expensedetail"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '180.00€')

    def test_valid(self):
        self.factory.xfer = ExpenseAddModify()
        self.call(
            '/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.call('/diacamma.payoff/supportingThirdValid',
                  {'supporting': 4, 'third': 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.call(
            '/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.call(
            '/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 1)
        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)
        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = ExpenseValid()
        self.call(
            '/diacamma.condominium/expenseValid', {'CONFIRME': 'YES', 'expense': 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseValid')

        self.factory.xfer = EntryLineAccountList()
        self.call('/diacamma.accounting/entryLineAccountList',
                  {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryLineAccountList')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="entrylineaccount"]/RECORD', 4 + 4 + 3)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 180.00€ - {[b]}Charge:{[/b]} 180.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = ExpenseDel()
        self.call(
            '/diacamma.condominium/expenseAddDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer(
            'core.exception', 'diacamma.condominium', 'expenseAddDel')

        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)
        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)
        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="expense"]/RECORD[1]/VALUE[@name="third"]', "Minimum")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="expense"]/RECORD[1]/VALUE[@name="total"]', "180.00€")

        self.factory.xfer = ExpenseClose()
        self.call(
            '/diacamma.condominium/expenseClose', {'CONFIRME': 'YES', 'expense': 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseClose')

        self.factory.xfer = ExpenseDel()
        self.call(
            '/diacamma.condominium/expenseAddDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer(
            'core.exception', 'diacamma.condominium', 'expenseAddDel')

        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)
        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 1)
        self.factory.xfer = ExpenseList()
        self.call(
            '/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('COMPONENTS/GRID[@name="expense"]/RECORD', 0)

    def test_payoff(self):
        self.factory.xfer = ExpenseAddModify()
        self.call(
            '/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.call('/diacamma.payoff/supportingThirdValid',
                  {'supporting': 4, 'third': 3}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.call(
            '/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.call(
            '/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseShow()
        self.call(
            '/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="expensedetail"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '180.00€')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="contact"]', 'Luke Lucky')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD', 2)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="code"]', '411')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[1]/VALUE[@name="total_txt"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[2]/VALUE[@name="code"]', '401')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[2]/VALUE[@name="total_txt"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '0.00€')

        self.factory.xfer = ExpenseValid()
        self.call(
            '/diacamma.condominium/expenseValid', {'CONFIRME': 'YES', 'expense': 4}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'expenseValid')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[2]/VALUE[@name="total_txt"]', '{[font color="green"]}Crédit: 180.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '180.00€')

        self.factory.xfer = PayoffAddModify()
        self.call(
            '/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '180.0', 'payer': "Nous", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = ThirdShow()
        self.call('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="accountthird"]/RECORD[2]/VALUE[@name="total_txt"]', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '0.00€')
