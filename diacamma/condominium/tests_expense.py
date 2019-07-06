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

from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting,\
    default_compta_be, initial_thirds_be
from diacamma.accounting.views_entries import EntryAccountList, EntryAccountClose
from diacamma.accounting.views import ThirdShow

from diacamma.payoff.test_tools import default_bankaccount_fr, PaymentTest,\
    default_bankaccount_be
from diacamma.payoff.views import SupportingThirdValid, PayoffAddModify

from diacamma.condominium.test_tools import default_setowner_fr, old_accounting,\
    default_setowner_be
from diacamma.condominium.views_expense import ExpenseList,\
    ExpenseAddModify, ExpenseDel, ExpenseShow, ExpenseDetailAddModify,\
    ExpenseTransition, ExpenseMultiPay


class ExpenseTest(PaymentTest):

    def setUp(self):
        initial_thirds_fr()
        PaymentTest.setUp(self)
        default_compta_fr(with12=False)
        default_costaccounting()
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)

    def test_create(self):
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_grid_equal('expense', {"num": "N°", "date": "date", "third": "tiers", "comment": "commentaire", "total": "total"}, 0)  # nb=5

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseAddModify')
        self.assert_count_equal('', 5)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('', 11)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_json_equal('LABELFORM', 'third', None)
        self.assert_json_equal('LABELFORM', 'info', ["aucun tiers sélectionné"])
        self.assert_grid_equal('expensedetail', {"set": "catégorie de charges", "designation": "désignation", "expense_account": "compte", "price": "prix", "ratio_txt": "ratio"}, 0)  # nb=5
        self.assert_count_equal('#expensedetail/actions', 4)
        self.assert_json_equal('LABELFORM', 'status', 0)
        self.assertEqual(len(self.json_actions), 2)
        self.assertEqual(self.json_actions[0]["action"], 'expenseAddModify')
        self.assertFalse("action" in self.json_actions[1].keys())

        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('', 12)
        self.assert_json_equal('LINK', 'third', "Minimum")
        self.assert_json_equal('LABELFORM', 'info', [])
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

    def test_add(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseDetailAddModify')
        self.assert_count_equal('', 6)
        self.assert_json_equal('SELECT', 'set', '1')
        self.assert_select_equal('set', 3)  # nb=3
        self.assert_json_equal('FLOAT', 'price', '0.00')
        self.assert_select_equal('expense_account', {'601': '[601] 601', '602': '[602] 602', '604': '[604] 604', '607': '[607] 607', '627': '[627] 627'})

        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('', 'expensedetail/@0/set', '[1] AAA')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('', 'expensedetail/@1/set', '[2] BBB')
        self.assert_json_equal('', 'expensedetail/@1/ratio_txt', [{'value': 75.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 25.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'status', 0)
        self.assertEqual(len(self.json_actions), 3)
        self.assertEqual(self.json_actions[0]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[0]['params']['TRANSITION'], 'valid')
        self.assertEqual(self.json_actions[1]["action"], 'expenseAddModify')
        self.assertFalse("action" in self.json_actions[2].keys())

    def test_valid_current(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 0.00, 0.00, 0.00, 0.00])

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 3)
        self.assert_json_equal('', 'entryline/@0/costaccounting', None)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[604] 604')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[627] 627')
        self.assert_json_equal('LABELFORM', 'result', [0.00, 180.00, -180.00, 0.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('', 'expensedetail/@0/set', '[1] AAA')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('', 'expensedetail/@1/set', '[2] BBB')
        self.assert_json_equal('', 'expensedetail/@1/ratio_txt', [{'value': 75.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 25.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'status', 1)
        self.assertEqual(len(self.json_actions), 3)
        self.assertEqual(self.json_actions[0]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[0]['params']['TRANSITION'], 'reedit')
        self.assertEqual(self.json_actions[1]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[1]['params']['TRANSITION'], 'close')
        self.assertFalse("action" in self.json_actions[2].keys())

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.assert_json_equal('', 'expense/@0/third', "Minimum")
        self.assert_json_equal('', 'expense/@0/total', 180.00)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, "TRANSITION": 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'status', 2)
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

    def test_valid_exceptional(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid',
                      {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 3, 'price': '200.00', 'comment': 'set 3', 'expense_account': '602'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@0/costaccounting', None)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entryline/@2/costaccounting', None)
        self.assert_json_equal('', 'entryline/@2/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[702] 702')
        self.assert_json_equal('LABELFORM', 'result', [200.00, 200.00, 0.00, 0.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 1)
        self.assert_json_equal('', 'expensedetail/@0/set', '[3] CCC')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 200.00)
        self.assert_json_equal('LABELFORM', 'status', 1)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, "TRANSITION": 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

    def test_payoff(self):
        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'expensetype', 0)
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Luke Lucky')
        self.assert_count_equal('accountthird', 2)
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@0/total_txt', 0.00)
        self.assert_json_equal('', 'accountthird/@1/code', '401')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 0.00)
        self.assert_json_equal('LABELFORM', 'total', 0.0)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.check_account(year_id=1, code='401', value=180.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 180.00)
        self.assert_json_equal('LABELFORM', 'total', 180.00)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '180.0',
                                                           'payer': "Nous", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=-180.0)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 0.00)
        self.assert_json_equal('LABELFORM', 'total', 0.00)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 180.00, -180.00, -180.00, 0.00])

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', "entryline": "5"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 180.00, -180.00, -180.00, -180.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 2)

    def test_payoff_asset(self):
        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 1, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify', {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'expensetype', 1)
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Luke Lucky')
        self.assert_count_equal('accountthird', 2)
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@0/total_txt', 0.00)
        self.assert_json_equal('', 'accountthird/@1/code', '401')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 0.00)
        self.assert_json_equal('LABELFORM', 'total', 0.00)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.check_account(year_id=1, code='401', value=-180.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('', 'accountthird/@1/total_txt', -180.00)
        self.assert_json_equal('LABELFORM', 'total', -180.00)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '180.0',
                                                           'payer': "Nous", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=180.0)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 0.00)
        self.assert_json_equal('LABELFORM', 'total', 0.00)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('LABELFORM', 'result', [0.00, -180.00, 180.00, 180.00, 0.00])

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', "entryline": "5"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('LABELFORM', 'result', [0.00, -180.00, 180.00, 180.00, 180.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 2)

    def test_payoff_multi(self):
        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-15', "comment": 'def 456'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 5, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 5, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')
        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 5, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.check_account(year_id=1, code='401', value=180.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ExpenseMultiPay()
        self.calljson('/diacamma.condominium/expenseMultiPay', {'expense': '4;5'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseMultiPay')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payoffAddModify")
        self.assertEqual(len(self.response_json['action']['params']), 2)
        self.assertEqual(self.response_json['action']['params']['supportings'], '4;5')
        self.assertEqual(self.response_json['action']['params']['repartition'], '1')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supportings': '4;5', "repartition": "1"}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "180.00")
        self.assert_attrib_equal('amount', 'max', "180.0")
        self.assert_select_equal('repartition', 2)  # nb=2
        self.assert_json_equal('SELECT', 'repartition', "1")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supportings': '4;5', 'amount': '120.0', 'date': '2015-06-23', 'mode': 0, 'reference': '', 'bank_account': 0, "repartition": 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.check_account(year_id=1, code='401', value=60.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=-120.0)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_json_equal('LABELFORM', 'total', 150.00)
        self.assert_json_equal('LABELFORM', 'total_rest_topay', 50.00)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 5}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_json_equal('LABELFORM', 'total', 30.00)
        self.assert_json_equal('LABELFORM', 'total_rest_topay', 10.00)

    def test_payoff_multi_bydate(self):
        self.check_account(year_id=1, code='401', value=0.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-15', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'def 456'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 5, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 5, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')
        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 5, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.check_account(year_id=1, code='401', value=180.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=0.0)

        self.factory.xfer = ExpenseMultiPay()
        self.calljson('/diacamma.condominium/expenseMultiPay', {'expense': '4;5'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseMultiPay')
        self.assertEqual(self.response_json['action']['id'], "diacamma.payoff/payoffAddModify")
        self.assertEqual(len(self.response_json['action']['params']), 2)
        self.assertEqual(self.response_json['action']['params']['supportings'], '4;5')
        self.assertEqual(self.response_json['action']['params']['repartition'], '1')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'supportings': '4;5', "repartition": "1"}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payoffAddModify')
        self.assert_json_equal('FLOAT', 'amount', "180.00")
        self.assert_attrib_equal('amount', 'max', "180.0")
        self.assert_select_equal('repartition', 2)  # nb=2
        self.assert_json_equal('SELECT', 'repartition', "1")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supportings': '4;5', 'amount': '120.0', 'date': '2015-06-23', 'mode': 0, 'reference': '', 'bank_account': 0, "repartition": 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.check_account(year_id=1, code='401', value=60.0)
        self.check_account(year_id=1, code='512', value=0.0)
        self.check_account(year_id=1, code='531', value=-120.0)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_json_equal('LABELFORM', 'total', 150.00)
        self.assert_json_equal('LABELFORM', 'total_rest_topay', 60.00)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 5}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_json_equal('LABELFORM', 'total', 30.00)
        self.assert_json_equal('LABELFORM', 'total_rest_topay', 0.00)

    def test_reedit_fail1(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')
        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', "entryline": "1"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')
        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 2)

    def test_reedit_fail2(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')
        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', "entryline": "3"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')
        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 2)

    def test_reedit(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 0.00, 0.00, 0.00, 0.00])

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')
        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '180.0',
                                                           'payer': "Nous", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 180.00, -180.00, -180.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'reedit'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 0.00, 0.00, 0.00, 0.00])


class ExpenseBelgiumTest(PaymentTest):

    def setUp(self):
        PaymentTest.setUp(self)
        default_compta_be(with12=False)
        initial_thirds_be()
        default_costaccounting()
        default_bankaccount_be()
        default_setowner_be()
        rmtree(get_user_dir(), True)

    def test_create(self):
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_grid_equal('expense', {"num": "N°", "date": "date", "third": "tiers", "comment": "commentaire", "total": "total"}, 0)  # nb=5

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseAddModify')
        self.assert_count_equal('', 5)

        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('', 11)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_json_equal('LABELFORM', 'third', None)
        self.assert_json_equal('LABELFORM', 'info', ["aucun tiers sélectionné"])
        self.assert_grid_equal('expensedetail', {"set": "catégorie de charges", "designation": "désignation", "expense_account": "compte", "price": "prix", "ratio_txt": "ratio"}, 0)  # nb=5
        self.assert_count_equal('#expensedetail/actions', 4)
        self.assert_json_equal('LABELFORM', 'status', 0)
        self.assertEqual(len(self.json_actions), 2)
        self.assertEqual(self.json_actions[0]["action"], 'expenseAddModify')
        self.assertFalse("action" in self.json_actions[1].keys())

        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('', 12)
        self.assert_json_equal('LINK', 'third', "Minimum")
        self.assert_json_equal('LABELFORM', 'info', [])
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

    def test_add(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')

        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseDetailAddModify')
        self.assert_count_equal('', 6)
        self.assert_json_equal('SELECT', 'set', '1')
        self.assert_select_equal('set', 3)  # nb=3
        self.assert_json_equal('FLOAT', 'price', '0.00')
        self.assert_select_equal('expense_account', {'600000': '[600000] 600000', '601000': '[601000] 601000',
                                                     '602000': '[602000] 602000', '603000': '[603000] 603000', '604000': '[604000] 604000'})

        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '602000'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '604000'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('', 'expensedetail/@0/set', '[1] AAA')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('', 'expensedetail/@1/set', '[2] BBB')
        self.assert_json_equal('', 'expensedetail/@1/ratio_txt', [{'value': 75.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 25.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LINK', 'third', 'Minimum')
        self.assert_json_equal('LABELFORM', 'status', 0)
        self.assert_json_equal('LABELFORM', 'info', [])
        self.assertEqual(len(self.json_actions), 3)
        self.assertEqual(self.json_actions[0]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[0]['params']['TRANSITION'], 'valid')
        self.assertEqual(self.json_actions[1]["action"], 'expenseAddModify')
        self.assertFalse("action" in self.json_actions[2].keys())

    def test_valid_current(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '602000'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '604000'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 0.00, 0.00, 0.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_json_equal('LABELFORM', 'info', [])

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 3)
        self.assert_json_equal('', 'entryline/@0/costaccounting', None)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[440000 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[602000] 602000')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[604000] 604000')
        self.assert_json_equal('LABELFORM', 'result', [0.00, 180.00, -180.00, 0.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('', 'expensedetail/@0/set', '[1] AAA')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('', 'expensedetail/@1/set', '[2] BBB')
        self.assert_json_equal('', 'expensedetail/@1/ratio_txt', [{'value': 75.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 25.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'status', 1)
        self.assertEqual(len(self.json_actions), 3)
        self.assertEqual(self.json_actions[0]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[0]['params']['TRANSITION'], 'reedit')
        self.assertEqual(self.json_actions[1]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[1]['params']['TRANSITION'], 'close')
        self.assertFalse("action" in self.json_actions[2].keys())

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.assert_json_equal('', 'expense/@0/third', "Minimum")
        self.assert_json_equal('', 'expense/@0/total', 180.00)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, "TRANSITION": 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'status', 2)
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

    def test_valid_exceptional(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid',
                      {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 3, 'price': '200.00', 'comment': 'set 3', 'expense_account': '601000'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_json_equal('LABELFORM', 'info', [])

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/costaccounting', None)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[440000 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[601000] 601000')
        self.assert_json_equal('LABELFORM', 'result', [0.00, 200.00, -200.00, 0.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 1)
        self.assert_json_equal('', 'expensedetail/@0/set', '[3] CCC')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 200.00)
        self.assert_json_equal('LABELFORM', 'status', 1)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, "TRANSITION": 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)


class ExpenseTestOldAccounting(LucteriosTest):

    def setUp(self):
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        old_accounting()
        default_compta_fr(with12=False)
        default_costaccounting()
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)

    def test_valid_current(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid',
                      {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', [0.00, 0.00, 0.00, 0.00, 0.00])

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 10)
        self.assert_json_equal('', 'entryline/@0/costaccounting', None)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[604] 604')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[627] 627')

        self.assert_json_equal('', 'entryline/@3/costaccounting', None)
        self.assert_json_equal('', 'entryline/@3/entry_account', '[450 Minimum]')
        self.assert_json_equal('', 'entryline/@4/costaccounting', None)
        self.assert_json_equal('', 'entryline/@4/entry_account', '[450 Dalton William]')
        self.assert_json_equal('', 'entryline/@5/costaccounting', None)
        self.assert_json_equal('', 'entryline/@5/entry_account', '[450 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@6/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@6/entry_account', '[701] 701')

        self.assert_json_equal('', 'entryline/@7/costaccounting', None)
        self.assert_json_equal('', 'entryline/@7/entry_account', '[450 Minimum]')
        self.assert_json_equal('', 'entryline/@8/costaccounting', None)
        self.assert_json_equal('', 'entryline/@8/entry_account', '[450 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@9/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@9/entry_account', '[701] 701')

        self.assert_json_equal('LABELFORM', 'result', [180.00, 180.00, 0.00, 0.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('', 'expensedetail/@0/set', '[1] AAA')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('', 'expensedetail/@1/set', '[2] BBB')
        self.assert_json_equal('', 'expensedetail/@1/ratio_txt', [{'value': 75.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 25.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'status', 1)
        self.assertEqual(len(self.json_actions), 3)
        self.assertEqual(self.json_actions[0]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[0]['params']['TRANSITION'], 'reedit')
        self.assertEqual(self.json_actions[1]["action"], 'expenseTransition')
        self.assertEqual(self.json_actions[1]['params']['TRANSITION'], 'close')
        self.assertFalse("action" in self.json_actions[2].keys())

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.assert_json_equal('', 'expense/@0/third', "Minimum")
        self.assert_json_equal('', 'expense/@0/total', 180.00)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, "TRANSITION": 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = ExpenseDel()
        self.calljson('/diacamma.condominium/expenseDel', {'CONFIRME': 'YES', "expense": 4}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'expenseDel')

        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 1)
        self.factory.xfer = ExpenseList()
        self.calljson('/diacamma.condominium/expenseList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseList')
        self.assert_count_equal('expense', 0)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assert_json_equal('LABELFORM', 'status', 2)
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 10)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 7)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

    def test_valid_exceptional(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 4}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 3, 'price': '200.00', 'comment': 'set 3', 'expense_account': '602'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/costaccounting', None)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[602] 602')

        self.assert_json_equal('', 'entryline/@2/costaccounting', None)
        self.assert_json_equal('', 'entryline/@2/entry_account', '[450 Minimum]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', None)
        self.assert_json_equal('', 'entryline/@3/entry_account', '[450 Dalton William]')
        self.assert_json_equal('', 'entryline/@4/costaccounting', None)
        self.assert_json_equal('', 'entryline/@4/entry_account', '[450 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[702] 702')
        self.assert_json_equal('LABELFORM', 'result', [200.00, 200.00, 0.00, 0.00, 0.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 1)
        self.assert_json_equal('', 'expensedetail/@0/set', '[3] CCC')
        self.assert_json_equal('', 'expensedetail/@0/ratio_txt', [{'value': 45.0, 'format': 'Minimum : {0}'},
                                                                  {'value': 35.0, 'format': 'Dalton William : {0}'},
                                                                  {'value': 20.0, 'format': 'Dalton Joe : {0}'}])
        self.assert_json_equal('LABELFORM', 'total', 200.00)
        self.assert_json_equal('LABELFORM', 'status', 1)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 4)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)

    def test_payoff(self):
        self.factory.xfer = ExpenseAddModify()
        self.calljson('/diacamma.condominium/expenseAddModify', {'SAVE': 'YES', 'expensetype': 0, "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseAddModify')
        self.factory.xfer = SupportingThirdValid()
        self.calljson('/diacamma.payoff/supportingThirdValid', {'supporting': 4, 'third': 3}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'supportingThirdValid')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 1, 'price': '150.00', 'comment': 'set 1', 'expense_account': '604'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseDetailAddModify()
        self.calljson('/diacamma.condominium/expenseDetailAddModify',
                      {'SAVE': 'YES', 'expense': 4, 'set': 2, 'price': '30.00', 'comment': 'set 2', 'expense_account': '627'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseDetailAddModify')
        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assert_count_equal('expensedetail', 2)
        self.assert_json_equal('LABELFORM', 'total', 180.00)
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('LABELFORM', 'contact', 'Luke Lucky')
        self.assert_count_equal('accountthird', 2)
        self.assert_json_equal('', 'accountthird/@0/code', '411')
        self.assert_json_equal('', 'accountthird/@0/total_txt', 0.00)
        self.assert_json_equal('', 'accountthird/@1/code', '401')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 0.00)
        self.assert_json_equal('LABELFORM', 'total', 0.00)

        self.factory.xfer = ExpenseTransition()
        self.calljson('/diacamma.condominium/expenseTransition', {'CONFIRME': 'YES', 'expense': 4, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'expenseTransition')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 180.00)
        self.assert_json_equal('LABELFORM', 'total', 180.00)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '180.0',
                                                           'payer': "Nous", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = ThirdShow()
        self.calljson('/diacamma.accounting/thirdShow', {"third": 3}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdShow')
        self.assert_json_equal('', 'accountthird/@1/total_txt', 0.00)
        self.assert_json_equal('LABELFORM', 'total', 0.00)

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 12)
        self.assert_json_equal('LABELFORM', 'result', [180.00, 180.00, 0.00, -180.00, 0.00])

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', "entryline": "12"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 12)
        self.assert_json_equal('LABELFORM', 'result', [180.00, 180.00, 0.00, -180.00, -180.00])

        self.factory.xfer = ExpenseShow()
        self.calljson('/diacamma.condominium/expenseShow', {'expense': 4}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'expenseShow')
        self.assertEqual(len(self.json_actions), 2)
