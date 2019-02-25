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
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params

from diacamma.accounting.models import ChartsAccount, FiscalYear, Budget
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, default_costaccounting, initial_thirds_be,\
    default_compta_be
from diacamma.payoff.views import PayoffAddModify
from diacamma.payoff.test_tools import default_bankaccount_fr, default_bankaccount_be
from diacamma.condominium.views_callfunds import CallFundsList, CallFundsAddModify, CallFundsDel, \
    CallFundsShow, CallDetailAddModify, CallFundsTransition, CallFundsPrint, CallFundsAddCurrent
from diacamma.condominium.test_tools import default_setowner_fr, old_accounting, default_setowner_be
from diacamma.condominium.models import Set


class CallFundsTest(LucteriosTest):

    def setUp(self):
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_costaccounting()
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)

    def test_create(self):
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_grid_equal('callfunds', {"num": "N°", "date": "date", "owner": "propriétaire", "comment": "commentaire", "total": "total"}, 0)

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsAddModify')
        self.assert_count_equal('', 4)

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_grid_equal('callfunds', {"num": "N°", "date": "date", "owner": "propriétaire", "comment": "commentaire", "total": "total", "supporting.total_rest_topay": "reste à payer"}, 0)

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_grid_equal('callfunds', {"num": "N°", "date": "date", "owner": "propriétaire", "comment": "commentaire", "total": "total"}, 1)

        self.factory.xfer = CallFundsDel()
        self.calljson('/diacamma.condominium/callFundsDel', {'CONFIRME': 'YES', "callfunds": 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsDel')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)

    def test_add(self):
        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('', 8)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_grid_equal('calldetail', {"type_call_ex": "type d'appel", "set": "catégorie de charges", "designation": "désignation", "set.total_part": "somme des tantièmes", "price_txt": "montant", }, 0)
        self.assert_count_equal('#calldetail/actions', 3)

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('SELECT', 'set', '1')
        self.assert_json_equal('FLOAT', 'price', '250.00')
        self.assert_select_equal('type_call', {0: 'charge courante', 1: 'charge exceptionnelle', 2: 'avance de fond', 4: 'fond travaux'})

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'callfunds': 1, 'type_call': 0, 'set': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_json_equal('SELECT', 'set', '2')
        self.assert_json_equal('FLOAT', 'price', '25.00')

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'type_call': 0, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'type_call': 0, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assertEqual(len(self.json_actions), 3)
        self.assert_count_equal('calldetail', 2)
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge courante')
        self.assert_json_equal('', 'calldetail/@0/set', '[1] AAA')
        self.assert_json_equal('', 'calldetail/@0/price_txt', '250.00€')
        self.assert_json_equal('', 'calldetail/@1/type_call_ex', 'charge courante')
        self.assert_json_equal('', 'calldetail/@1/set', '[2] BBB')
        self.assert_json_equal('', 'calldetail/@1/price_txt', '25.00€')
        self.assert_json_equal('LABELFORM', 'total', '275.00€')

    def test_add_default_current(self):
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 4)
        self.assert_json_equal('', 'callfunds/@0/date', "2015-01-01")
        self.assert_json_equal('', 'callfunds/@1/date', "2015-04-01")
        self.assert_json_equal('', 'callfunds/@2/date', "2015-07-01")
        self.assert_json_equal('', 'callfunds/@3/date', "2015-10-01")
        self.assert_json_equal('', 'callfunds/@0/total', "275.00€")
        self.assert_json_equal('', 'callfunds/@1/total', "275.00€")
        self.assert_json_equal('', 'callfunds/@2/total', "275.00€")
        self.assert_json_equal('', 'callfunds/@3/total', "275.00€")
        self.assertEqual(len(self.json_actions), 1)

    def test_add_default_current_monthly(self):
        Parameter.change_value('condominium-mode-current-callfunds', 1)
        Params.clear()

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 12)
        self.assert_json_equal('', 'callfunds/@0/date', "2015-01-01")
        self.assert_json_equal('', 'callfunds/@1/date', "2015-02-01")
        self.assert_json_equal('', 'callfunds/@2/date', "2015-03-01")
        self.assert_json_equal('', 'callfunds/@3/date', "2015-04-01")
        self.assert_json_equal('', 'callfunds/@4/date', "2015-05-01")
        self.assert_json_equal('', 'callfunds/@5/date', "2015-06-01")
        self.assert_json_equal('', 'callfunds/@6/date', "2015-07-01")
        self.assert_json_equal('', 'callfunds/@7/date', "2015-08-01")
        self.assert_json_equal('', 'callfunds/@8/date', "2015-09-01")
        self.assert_json_equal('', 'callfunds/@9/date', "2015-10-01")
        self.assert_json_equal('', 'callfunds/@10/date', "2015-11-01")
        self.assert_json_equal('', 'callfunds/@11/date', "2015-12-01")
        self.assert_json_equal('', 'callfunds/@0/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@1/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@2/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@3/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@4/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@5/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@6/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@7/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@8/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@9/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@10/total', "91.66€")
        self.assert_json_equal('', 'callfunds/@11/total', "91.66€")
        self.assertEqual(len(self.json_actions), 1)

    def test_valid_current(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 0, 'set': 1, 'price': '250.00', 'designation': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 0, 'set': 2, 'price': '25.00', 'designation': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('', 11)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_count_equal('calldetail', 1)  # nb=6
        self.assert_count_equal('#calldetail/actions', 0)
        self.assert_json_equal('', 'calldetail/@0/set', "[1] AAA")
        self.assert_json_equal('', 'calldetail/@0/designation', "set 1")
        self.assert_json_equal('', 'calldetail/@0/total_amount', "250.00€")
        self.assert_json_equal('', 'calldetail/@0/set.total_part', "100")
        self.assert_json_equal('', 'calldetail/@0/owner_part', "35.00")
        self.assert_json_equal('', 'calldetail/@0/price_txt', "87.50€")
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge courante')
        self.assert_count_equal('payoff', 0)
        self.assert_count_equal('#payoff/actions', 3)
        self.assert_json_equal('LABELFORM', 'status', 'validé')
        self.assert_json_equal('LABELFORM', 'total', '87.50€')

        self.factory.xfer = CallFundsDel()
        self.calljson('/diacamma.condominium/callFundsDel', {'CONFIRME': 'YES', "callfunds": 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'callFundsDel')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 250*45%+25*75%
        self.assert_json_equal('', 'callfunds/@0/total', "131.25€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 250*35%+25*0%
        self.assert_json_equal('', 'callfunds/@1/total', "87.50€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 250*20%+25*25%
        self.assert_json_equal('', 'callfunds/@2/total', "56.25€")

        self.factory.xfer = CallFundsPrint()
        self.calljson('/diacamma.condominium/callFundsPrint', {'callfunds': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsPrint')
        self.assert_json_equal('SELECT', 'MODEL', '8')

        self.factory.xfer = CallFundsPrint()
        self.calljson('/diacamma.condominium/callFundsPrint', {'callfunds': 3, 'PRINT_MODE': 0, 'MODEL': 8}, False)
        self.assert_observer('core.print', 'diacamma.condominium', 'callFundsPrint')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 3, 'TRANSITION': 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsDel()
        self.calljson('/diacamma.condominium/callFundsDel', {'CONFIRME': 'YES', "callfunds": 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'callFundsDel')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[4501 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[701] 701')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[701] 701')

        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[4501 Dalton William]')
        self.assert_json_equal('', 'entryline/@4/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[701] 701')

        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[4501 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@6/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@6/entry_account', '[701] 701')
        self.assert_json_equal('', 'entryline/@7/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[701] 701')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 275.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 275.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 10)
        self.assert_json_equal('', 'entryline/@8/entry_account', '[4501 Minimum]')
        self.assert_json_equal('', 'entryline/@8/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@9/entry_account', '[531] 531')
        self.assert_json_equal('', 'entryline/@9/costaccounting', '---')

    def test_valid_exceptional(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 1, 'set': 3, 'price': '250.00', 'comment': 'set 3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge exceptionnelle')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 250*45%
        self.assert_json_equal('', 'callfunds/@0/total', "112.50€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 250*35%
        self.assert_json_equal('', 'callfunds/@1/total', "87.50€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 250*20%
        self.assert_json_equal('', 'callfunds/@2/total', "50.00€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[4502 Minimum]')

        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[4502 Dalton William]')

        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[4502 Dalton Joe]')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@6/entry_account', '[4502 Minimum]')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[531] 531')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_advance(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 2, 'set': 1, 'price': '100.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'avance de fond')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 100*45%
        self.assert_json_equal('', 'callfunds/@0/total', "45.00€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 100*35%
        self.assert_json_equal('', 'callfunds/@1/total', "35.00€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 100*20%
        self.assert_json_equal('', 'callfunds/@2/total', "20.00€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[103] 103')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[4503 Minimum]')

        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[103] 103')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[4503 Dalton William]')

        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[103] 103')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[4503 Dalton Joe]')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@6/entry_account', '[4503 Minimum]')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[531] 531')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_fundforworks(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 4, 'set': 1, 'price': '100.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'fond travaux')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 100*45%
        self.assert_json_equal('', 'callfunds/@0/total', "45.00€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 100*35%
        self.assert_json_equal('', 'callfunds/@1/total', "35.00€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 100*20%
        self.assert_json_equal('', 'callfunds/@2/total', "20.00€")
        self.factory.xfer = EntryAccountList()

        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[105] 105')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[4505 Minimum]')

        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[105] 105')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[4505 Dalton William]')

        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[105] 105')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[4505 Dalton Joe]')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@6/entry_account', '[4505 Minimum]')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[531] 531')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_multi(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'Multi'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 0, 'set': 1, 'price': '250.00', 'designation': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 1, 'set': 3, 'price': '100.00', 'designation': 'set 3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 4, 'set': 1, 'price': '150.00', 'designation': 'font'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('', 11)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_count_equal('calldetail', 3)
        self.assert_count_equal('#calldetail/actions', 0)
        self.assert_json_equal('', 'calldetail/@0/set', "[1] AAA")
        self.assert_json_equal('', 'calldetail/@0/designation', "set 1")
        self.assert_json_equal('', 'calldetail/@0/total_amount', "250.00€")
        self.assert_json_equal('', 'calldetail/@0/set.total_part', "100")
        self.assert_json_equal('', 'calldetail/@0/owner_part', "35.00")
        self.assert_json_equal('', 'calldetail/@0/price_txt', "87.50€")
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge courante')

        self.assert_json_equal('', 'calldetail/@1/set', "[3] CCC")
        self.assert_json_equal('', 'calldetail/@1/designation', "set 3")
        self.assert_json_equal('', 'calldetail/@1/total_amount', "100.00€")
        self.assert_json_equal('', 'calldetail/@1/set.total_part', "100")
        self.assert_json_equal('', 'calldetail/@1/owner_part', "35.00")
        self.assert_json_equal('', 'calldetail/@1/price_txt', "35.00€")
        self.assert_json_equal('', 'calldetail/@1/type_call_ex', 'charge exceptionnelle')

        self.assert_json_equal('', 'calldetail/@2/set', "[1] AAA")
        self.assert_json_equal('', 'calldetail/@2/designation', "font")
        self.assert_json_equal('', 'calldetail/@2/total_amount', "150.00€")
        self.assert_json_equal('', 'calldetail/@2/set.total_part', "100")
        self.assert_json_equal('', 'calldetail/@2/owner_part', "35.00")
        self.assert_json_equal('', 'calldetail/@2/price_txt', "52.50€")
        self.assert_json_equal('', 'calldetail/@2/type_call_ex', 'fond travaux')

        self.assert_count_equal('payoff', 0)
        self.assert_count_equal('#payoff/actions', 3)
        self.assert_json_equal('LABELFORM', 'status', 'validé')
        self.assert_json_equal('LABELFORM', 'total', '175.00€')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 250*45% + 100*45% + 150*45%
        self.assert_json_equal('', 'callfunds/@0/total', "225.00€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 250*35% + 100*35%+ 150*35%
        self.assert_json_equal('', 'callfunds/@1/total', "175.00€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 250*20% + 100*20% + 150*20%
        self.assert_json_equal('', 'callfunds/@2/total', "100.00€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 18)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[4501 Minimum]')
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}112.50€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[701] 701')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[4502 Minimum]')
        self.assert_json_equal('', 'entryline/@3/debit', '{[font color="blue"]}45.00€{[/font]}')
        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[105] 105')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[4505 Minimum]')
        self.assert_json_equal('', 'entryline/@5/debit', '{[font color="blue"]}67.50€{[/font]}')

        self.assert_json_equal('', 'entryline/@6/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@6/entry_account', '[4501 Dalton William]')
        self.assert_json_equal('', 'entryline/@7/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[701] 701')
        self.assert_json_equal('', 'entryline/@8/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@8/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@9/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@9/entry_account', '[4502 Dalton William]')
        self.assert_json_equal('', 'entryline/@10/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@10/entry_account', '[105] 105')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[4505 Dalton William]')

        self.assert_json_equal('', 'entryline/@12/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[4501 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@13/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@13/entry_account', '[701] 701')
        self.assert_json_equal('', 'entryline/@14/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@14/entry_account', '[120] 120')
        self.assert_json_equal('', 'entryline/@15/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@15/entry_account', '[4502 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@16/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@16/entry_account', '[105] 105')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[4505 Dalton Joe]')

        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 250.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 250.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 18)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 22)
        self.assert_json_equal('', 'entryline/@18/entry_account', '[4501 Minimum]')  # 112.5 + 45 + 67.5 =  225 => 100 = 44.444444%
        self.assert_json_equal('', 'entryline/@18/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/credit', '{[font color="green"]}50.00€{[/font]}')
        self.assert_json_equal('', 'entryline/@19/entry_account', '[4502 Minimum]')
        self.assert_json_equal('', 'entryline/@19/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@19/credit', '{[font color="green"]}20.00€{[/font]}')
        self.assert_json_equal('', 'entryline/@20/entry_account', '[4505 Minimum]')
        self.assert_json_equal('', 'entryline/@20/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@20/credit', '{[font color="green"]}30.00€{[/font]}')
        self.assert_json_equal('', 'entryline/@21/entry_account', '[531] 531')
        self.assert_json_equal('', 'entryline/@21/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@21/debit', '{[font color="blue"]}100.00€{[/font]}')

    def test_payoff(self):
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=17).current_total, '4501')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=2).current_total, '512')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=3).current_total, '531')
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 0, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 0, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.assertEqual('{[font color="blue"]}Débit: 275.00€{[/font]}',
                         ChartsAccount.objects.get(id=17).current_total, '4501')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=2).current_total, '512')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=3).current_total, '531')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0',
                                                           'payer': "Nous", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.assertEqual('{[font color="blue"]}Débit: 175.00€{[/font]}',
                         ChartsAccount.objects.get(id=17).current_total, '4501')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=2).current_total, '512')
        self.assertEqual('{[font color="blue"]}Débit: 100.00€{[/font]}',
                         ChartsAccount.objects.get(id=3).current_total, '531')


class CallFundsBelgiumTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        default_compta_be(with12=False)
        initial_thirds_be()
        default_bankaccount_be()
        default_setowner_be()
        rmtree(get_user_dir(), True)

    def test_create(self):
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_grid_equal('callfunds', {"num": "N°", "date": "date", "owner": "propriétaire", "comment": "commentaire", "total": "total"}, 0)

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsAddModify')
        self.assert_count_equal('', 4)

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_grid_equal('callfunds', {"num": "N°", "date": "date", "owner": "propriétaire", "comment": "commentaire", "total": "total", "supporting.total_rest_topay": "reste à payer"}, 0)

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_grid_equal('callfunds', {"num": "N°", "date": "date", "owner": "propriétaire", "comment": "commentaire", "total": "total"}, 1)

        self.factory.xfer = CallFundsDel()
        self.calljson('/diacamma.condominium/callFundsDel', {'CONFIRME': 'YES', "callfunds": 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsDel')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)

    def test_add(self):
        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('', 8)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_grid_equal('calldetail', {"type_call_ex": "type d'appel", "set": "catégorie de charges", "designation": "désignation", "set.total_part": "somme des tantièmes", "price_txt": "montant", }, 0)
        self.assert_count_equal('#calldetail/actions', 3)

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('SELECT', 'set', '1')
        self.assert_json_equal('FLOAT', 'price', '100.00')
        self.assert_select_equal('type_call', {0: 'charge courante', 1: 'charge de travaux', 2: 'roulement', 4: 'réserve'})

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'callfunds': 1, 'type_call': 0, 'set': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_json_equal('SELECT', 'set', '2')
        self.assert_json_equal('FLOAT', 'price', '10.00')

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'type_call': 0, 'set': 1, 'price': '100.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'type_call': 0, 'set': 2, 'price': '10.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assertEqual(len(self.json_actions), 3)
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge courante')
        self.assert_json_equal('', 'calldetail/@0/set', '[1] AAA')
        self.assert_json_equal('', 'calldetail/@0/price_txt', '100.00€')
        self.assert_json_equal('', 'calldetail/@1/type_call_ex', 'charge courante')
        self.assert_json_equal('', 'calldetail/@1/set', '[2] BBB')
        self.assert_json_equal('', 'calldetail/@1/price_txt', '10.00€')
        self.assert_json_equal('LABELFORM', 'total', '110.00€')

    def test_add_default_current(self):
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)
        self.assert_json_equal('', 'callfunds/@0/date', "2015-01-01")
        self.assert_json_equal('', 'callfunds/@0/total', "110.00€")
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 2)
        self.assert_json_equal('', 'callfunds/@0/date', "2015-01-01")
        self.assert_json_equal('', 'callfunds/@0/total', "110.00€")
        self.assert_json_equal('', 'callfunds/@1/date', "2015-02-01")
        self.assert_json_equal('', 'callfunds/@1/total', "110.00€")
        self.assertEqual(len(self.json_actions), 2)

        setitem = Set.objects.get(id=1)
        year = FiscalYear.get_current()
        cost = setitem.current_cost_accounting
        Budget.objects.create(cost_accounting=cost, year=year, code='610', amount=1200)
        setitem.change_budget_product(cost, year.id)

        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 12)
        self.assert_json_equal('', 'callfunds/@0/date', "2015-01-01")
        self.assert_json_equal('', 'callfunds/@0/total', "110.00€")
        self.assert_json_equal('', 'callfunds/@1/date', "2015-02-01")
        self.assert_json_equal('', 'callfunds/@1/total', "110.00€")
        self.assert_json_equal('', 'callfunds/@2/date', "2015-03-01")
        self.assert_json_equal('', 'callfunds/@2/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@3/date', "2015-04-01")
        self.assert_json_equal('', 'callfunds/@3/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@4/date', "2015-05-01")
        self.assert_json_equal('', 'callfunds/@4/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@5/date', "2015-06-01")
        self.assert_json_equal('', 'callfunds/@5/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@6/date', "2015-07-01")
        self.assert_json_equal('', 'callfunds/@6/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@7/date', "2015-08-01")
        self.assert_json_equal('', 'callfunds/@7/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@8/date', "2015-09-01")
        self.assert_json_equal('', 'callfunds/@8/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@9/date', "2015-10-01")
        self.assert_json_equal('', 'callfunds/@9/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@10/date', "2015-11-01")
        self.assert_json_equal('', 'callfunds/@10/total', "230.00€")
        self.assert_json_equal('', 'callfunds/@11/date', "2015-12-01")
        self.assert_json_equal('', 'callfunds/@11/total', "230.00€")
        self.assertEqual(len(self.json_actions), 1)

    def test_add_default_current_quartly(self):
        Parameter.change_value('condominium-mode-current-callfunds', 0)
        Params.clear()

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 0)
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')
        self.factory.xfer = CallFundsAddCurrent()
        self.calljson('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 4)
        self.assert_json_equal('', 'callfunds/@0/date', "2015-01-01")
        self.assert_json_equal('', 'callfunds/@0/total', "330.00€")
        self.assert_json_equal('', 'callfunds/@1/date', "2015-04-01")
        self.assert_json_equal('', 'callfunds/@1/total', "330.00€")
        self.assert_json_equal('', 'callfunds/@2/date', "2015-07-01")
        self.assert_json_equal('', 'callfunds/@2/total', "330.00€")
        self.assert_json_equal('', 'callfunds/@3/date', "2015-10-01")
        self.assert_json_equal('', 'callfunds/@3/total', "330.00€")
        self.assertEqual(len(self.json_actions), 1)

    def test_valid_current(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'type_call': 0, 'set': 1, 'price': '250.00', 'designation': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'type_call': 0, 'set': 2, 'price': '25.00', 'designation': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('', 11)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_count_equal('calldetail', 1)  # nb=6
        self.assert_count_equal('#calldetail/actions', 0)
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge courante')
        self.assert_count_equal('payoff', 0)
        self.assert_count_equal('#payoff/actions', 3)
        self.assert_json_equal('LABELFORM', 'status', 'validé')
        self.assert_json_equal('LABELFORM', 'total', '87.50€')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 250*45%+25*75%
        self.assert_json_equal('', 'callfunds/@0/total', "131.25€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 250*35%+25*0%
        self.assert_json_equal('', 'callfunds/@1/total', "87.50€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 250*20%+25*25%
        self.assert_json_equal('', 'callfunds/@2/total', "56.25€")

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 3, 'TRANSITION': 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[410100 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[701100] 701100')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[701100] 701100')

        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[410100 Dalton William]')
        self.assert_json_equal('', 'entryline/@4/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[701100] 701100')

        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[410100 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@6/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@6/entry_account', '[701100] 701100')
        self.assert_json_equal('', 'entryline/@7/costaccounting', '[2] BBB 2015')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[701100] 701100')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 275.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 275.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 2, 'reference': 'abc', 'bank_account': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 10)
        self.assert_json_equal('', 'entryline/@8/entry_account', '[410100 Minimum]')
        self.assert_json_equal('', 'entryline/@8/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@9/entry_account', '[550000] 550000')
        self.assert_json_equal('', 'entryline/@9/costaccounting', '---')

    def test_valid_working(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 1, 'set': 3, 'price': '250.00', 'comment': 'set 3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'charge de travaux')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 250*45%
        self.assert_json_equal('', 'callfunds/@0/total', "112.50€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 250*35%
        self.assert_json_equal('', 'callfunds/@1/total', "87.50€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 250*20%
        self.assert_json_equal('', 'callfunds/@2/total', "50.00€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[410000 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[700100] 700100')

        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[410000 Dalton William]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[700100] 700100')

        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[410000 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '[3] CCC')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[700100] 700100')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 250.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 250.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 2, 'reference': 'abc', 'bank_account': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@6/entry_account', '[410000 Minimum]')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[550000] 550000')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 250.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 250.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_rolling(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 2, 'set': 1, 'price': '100.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'roulement')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 100*45%
        self.assert_json_equal('', 'callfunds/@0/total', "45.00€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 100*35%
        self.assert_json_equal('', 'callfunds/@1/total', "35.00€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 100*20%
        self.assert_json_equal('', 'callfunds/@2/total', "20.00€")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[410100 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[701200] 701200')

        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[410100 Dalton William]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[701200] 701200')

        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[410100 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[701200] 701200')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 100.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 100.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 2, 'reference': 'abc', 'bank_account': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@6/entry_account', '[410100 Minimum]')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[550000] 550000')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 100.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 100.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_reserved(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 4, 'set': 1, 'price': '100.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.calljson('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_json_equal('', 'calldetail/@0/type_call_ex', 'réserve')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 1)

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.calljson('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('callfunds', 3)
        self.assert_json_equal('', 'callfunds/@0/owner', "Minimum")  # 100*45%
        self.assert_json_equal('', 'callfunds/@0/total', "45.00€")
        self.assert_json_equal('', 'callfunds/@1/owner', "Dalton William")  # 100*35%
        self.assert_json_equal('', 'callfunds/@1/total', "35.00€")
        self.assert_json_equal('', 'callfunds/@2/owner', "Dalton Joe")  # 100*20%
        self.assert_json_equal('', 'callfunds/@2/total', "20.00€")
        self.factory.xfer = EntryAccountList()

        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[410000 Minimum]')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[700000] 700000')

        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[410000 Dalton William]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[700000] 700000')

        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[410000 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '[1] AAA 2015')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[700000] 700000')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 100.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 100.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 6)

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 2, 'reference': 'abc', 'bank_account': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('', 'entryline/@6/entry_account', '[410000 Minimum]')
        self.assert_json_equal('', 'entryline/@7/entry_account', '[550000] 550000')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 100.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 100.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')


class CallFundsTestOldAccounting(LucteriosTest):

    def setUp(self):
        initial_thirds_fr()
        old_accounting()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_costaccounting()
        default_bankaccount_fr()
        default_setowner_fr()
        rmtree(get_user_dir(), True)

    def test_valid_current(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)

        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 0, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 0, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[450 Minimum]')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_exceptional(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)

        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 1, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 1, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[450 Minimum]')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_advance(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.calljson('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)

        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 2, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.calljson('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, "type_call": 2, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.calljson('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/entry_account', '[450 Minimum]')
        self.assert_json_equal('LABELFORM', 'result',
                               '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 100.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')
