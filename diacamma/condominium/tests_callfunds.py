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
from diacamma.condominium.test_tools import default_setowner, old_accounting
from diacamma.condominium.views_callfunds import CallFundsList,\
    CallFundsAddModify, CallFundsDel, CallFundsShow, CallDetailAddModify,\
    CallFundsTransition, CallFundsPrint, CallFundsAddCurrent
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.payoff.views import PayoffAddModify
from diacamma.accounting.models import ChartsAccount


class CallFundsTest(LucteriosTest):

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
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 6)

        self.factory.xfer = CallFundsAddModify()
        self.call('/diacamma.condominium/callFundsAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsAddModify')
        self.assert_count_equal('COMPONENTS/*', 9)

        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 7)

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 6)

        self.factory.xfer = CallFundsDel()
        self.call(
            '/diacamma.condominium/callFundsAddDel', {'CONFIRME': 'YES', "callfunds": 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddDel')

        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 6)

    def test_add(self):
        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsShow()
        self.call('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('COMPONENTS/*', 17)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="calldetail"]/HEADER', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="calldetail"]/ACTIONS/ACTION', 3)

        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="set"]', '1')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="price"]', '250.00')

        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'callfunds': 1, 'set': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="set"]', '2')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="price"]', '25.00')

        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.call('/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_call"]', 'charge courante')
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '275.00€')

    def test_add_default_current(self):
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)

        self.factory.xfer = CallFundsAddCurrent()
        self.call('/diacamma.condominium/callFundsAddCurrent', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddCurrent')

        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="date"]', "1 janvier 2015")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="date"]', "1 avril 2015")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="date"]', "1 juillet 2015")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[4]/VALUE[@name="date"]', "1 octobre 2015")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="total"]', "275.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="total"]', "275.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="total"]', "275.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[4]/VALUE[@name="total"]', "275.00€")

    def test_valid_current(self):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.call('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "type_call": 0, "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 1, 'price': '250.00', 'designation': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 2, 'price': '25.00', 'designation': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)

        self.factory.xfer = CallFundsTransition()
        self.call('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsShow()
        self.call('/diacamma.condominium/callFundsShow', {'callfunds': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('COMPONENTS/*', 23)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="calldetail"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="calldetail"]/ACTIONS/ACTION', 0)
        self.assert_xml_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD[1]/VALUE[@name="set"]', "AAA")
        self.assert_xml_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD[1]/VALUE[@name="designation"]', "set 1")
        self.assert_xml_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD[1]/VALUE[@name="total_amount"]', "250.00€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD[1]/VALUE[@name="set.total_part"]', "100.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD[1]/VALUE[@name="owner_part"]', "35.00")
        self.assert_xml_equal('COMPONENTS/GRID[@name="calldetail"]/RECORD[1]/VALUE[@name="price_txt"]', "87.50€")
        self.assert_count_equal('COMPONENTS/GRID[@name="payoff"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="payoff"]/HEADER', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="payoff"]/ACTIONS/ACTION', 3)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="status"]', 'validé')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_call"]', 'charge courante')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '87.50€')

        self.factory.xfer = CallFundsDel()
        self.call('/diacamma.condominium/callFundsAddDel', {'CONFIRME': 'YES', "callfunds": 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'callFundsAddDel')

        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="type_call"]', "charge courante")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="owner"]', "Minimum")  # 250*45%+25*75%
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="total"]', "131.25€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="type_call"]', "charge courante")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="owner"]', "Dalton William")  # 250*35%+25*0%
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="total"]', "87.50€")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="type_call"]', "charge courante")
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="owner"]', "Dalton Joe")  # 250*20%+25*25%
        self.assert_xml_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="total"]', "56.25€")

        self.factory.xfer = CallFundsPrint()
        self.call('/diacamma.condominium/callFundsPrint', {'callfunds': 3}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsPrint')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="MODEL"]', '8')

        self.factory.xfer = CallFundsPrint()
        self.call('/diacamma.condominium/callFundsPrint', {'callfunds': 3, 'PRINT_MODE': 0, 'MODEL': 8}, False)
        self.assert_observer('core.print', 'diacamma.condominium', 'callFundsPrint')

        self.factory.xfer = CallFundsTransition()
        self.call('/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 3, 'TRANSITION': 'close'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsDel()
        self.call('/diacamma.condominium/callFundsAddDel', {'CONFIRME': 'YES', "callfunds": 3}, False)
        self.assert_observer('core.exception', 'diacamma.condominium', 'callFundsAddDel')

        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)
        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer('core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 2)

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="costaccounting"]', 'AAA 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[4501 Minimum]' in description, description)
        self.assertTrue('[701] 701' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="costaccounting"]', 'BBB 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[4501 Minimum]' in description, description)
        self.assertTrue('[701] 701' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="costaccounting"]', 'AAA 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="description"]').text
        self.assertTrue('[4501 Dalton William]' in description, description)
        self.assertTrue('[701] 701' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[4]/VALUE[@name="costaccounting"]', 'AAA 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[4]/VALUE[@name="description"]').text
        self.assertTrue('[4501 Dalton Joe]' in description, description)
        self.assertTrue('[701] 701' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[5]/VALUE[@name="costaccounting"]', 'BBB 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[5]/VALUE[@name="description"]').text
        self.assertTrue('[4501 Dalton Joe]' in description, description)
        self.assertTrue('[701] 701' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 275.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 275.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 5)

        self.factory.xfer = PayoffAddModify()
        self.call('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 6)
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[6]/VALUE[@name="description"]').text
        self.assertTrue('[4501 Minimum]' in description, description)
        self.assertTrue('[531] 531' in description, description)

    def test_valid_exceptional(self):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "type_call": 1, "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 3, 'price': '250.00', 'comment': 'set 3'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.call(
            '/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_call"]', 'charge exceptionnelle')

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)

        self.factory.xfer = CallFundsTransition()
        self.call(
            '/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="type_call"]', "charge exceptionnelle")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="owner"]', "Minimum")  # 250*45%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="total"]', "112.50€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="type_call"]', "charge exceptionnelle")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="owner"]', "Dalton William")  # 250*35%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="total"]', "87.50€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="type_call"]', "charge exceptionnelle")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="owner"]', "Dalton Joe")  # 250*20%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="total"]', "50.00€")

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="costaccounting"]', 'CCC')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[4502 Minimum]' in description, description)
        self.assertTrue('[120] 120' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="costaccounting"]', 'CCC')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[4502 Dalton William]' in description, description)
        self.assertTrue('[120] 120' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="costaccounting"]', 'CCC')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="description"]').text
        self.assertTrue('[4502 Dalton Joe]' in description, description)
        self.assertTrue('[120] 120' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)

        self.factory.xfer = PayoffAddModify()
        self.call(
            '/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 4)
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[4]/VALUE[@name="description"]').text
        self.assertTrue('[4502 Minimum]' in description, description)
        self.assertTrue('[531] 531' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 100.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

    def test_valid_advance(self):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "type_call": 2, "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 1, 'price': '100.00', 'comment': 'set 1'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsShow()
        self.call(
            '/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="type_call"]', 'avance de fond')

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)

        self.factory.xfer = CallFundsTransition()
        self.call(
            '/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="type_call"]', "avance de fond")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="owner"]', "Minimum")  # 100*45%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="total"]', "45.00€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="type_call"]', "avance de fond")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="owner"]', "Dalton William")  # 100*35%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="total"]', "35.00€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="type_call"]', "avance de fond")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="owner"]', "Dalton Joe")  # 100*20%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="total"]', "20.00€")

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="costaccounting"]', 'AAA 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[4503 Minimum]' in description, description)
        self.assertTrue('[103] 103' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="costaccounting"]', 'AAA 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[2]/VALUE[@name="description"]').text
        self.assertTrue('[4503 Dalton William]' in description, description)
        self.assertTrue('[103] 103' in description, description)
        self.assert_xml_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="costaccounting"]', 'AAA 2015')
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[3]/VALUE[@name="description"]').text
        self.assertTrue('[4503 Dalton Joe]' in description, description)
        self.assertTrue('[103] 103' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '3', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 3)

        self.factory.xfer = PayoffAddModify()
        self.call(
            '/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 4)
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[4]/VALUE[@name="description"]').text
        self.assertTrue('[531] 531' in description, description)
        self.assertTrue('[4503 Minimum]' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 100.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

    def test_payoff(self):
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=17).current_total, '4501')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=2).current_total, '512')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=3).current_total, '531')
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.call('/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "type_call": 0, "comment": 'abc 123'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call('/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.call(
            '/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.assertEqual('{[font color="blue"]}Débit: 275.00€{[/font]}',
                         ChartsAccount.objects.get(id=17).current_total, '4501')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=2).current_total, '512')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=3).current_total, '531')

        self.factory.xfer = PayoffAddModify()
        self.call('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0',
                                                       'payer': "Nous", 'date': '2015-04-03', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.assertEqual('{[font color="blue"]}Débit: 175.00€{[/font]}',
                         ChartsAccount.objects.get(id=17).current_total, '4501')
        self.assertEqual('{[font color="green"]}Crédit: 0.00€{[/font]}',
                         ChartsAccount.objects.get(id=2).current_total, '512')
        self.assertEqual('{[font color="blue"]}Débit: 100.00€{[/font]}',
                         ChartsAccount.objects.get(id=3).current_total, '531')


class CallFundsTestOldAccounting(LucteriosTest):

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

    def test_valid_current(self):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "type_call": 0, "comment": 'abc 123'}, False)

        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.call(
            '/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.call(
            '/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[450 Minimum]' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 100.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

    def test_valid_exceptional(self):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "type_call": 1, "comment": 'abc 123'}, False)

        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.call(
            '/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.call(
            '/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[450 Minimum]' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 100.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

    def test_valid_advance(self):
        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "type_call": 2, "comment": 'abc 123'}, False)

        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 1, 'price': '250.00', 'comment': 'set 1'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')
        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'SAVE': 'YES', 'callfunds': 1, 'set': 2, 'price': '25.00', 'comment': 'set 2'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callDetailAddModify')

        self.factory.xfer = CallFundsTransition()
        self.call(
            '/diacamma.condominium/callFundsTransition', {'CONFIRME': 'YES', 'callfunds': 1, 'TRANSITION': 'valid'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsTransition')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 0)
        self.assert_xml_equal(
            "COMPONENTS/LABELFORM[@name='result']", '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 0.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')

        self.factory.xfer = PayoffAddModify()
        self.call(
            '/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 4, 'amount': '100.0', 'payer': "Minimum", 'date': '2015-06-12', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = EntryAccountList()
        self.call('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('COMPONENTS/GRID[@name="entryaccount"]/RECORD', 1)
        description = self.get_first_xpath('COMPONENTS/GRID[@name="entryaccount"]/RECORD[1]/VALUE[@name="description"]').text
        self.assertTrue('[450 Minimum]' in description, description)
        self.assert_xml_equal("COMPONENTS/LABELFORM[@name='result']",
                              '{[center]}{[b]}Produit:{[/b]} 0.00€ - {[b]}Charge:{[/b]} 0.00€ = {[b]}Résultat:{[/b]} 0.00€ | {[b]}Trésorie:{[/b]} 100.00€ - {[b]}Validé:{[/b]} 0.00€{[/center]}')
