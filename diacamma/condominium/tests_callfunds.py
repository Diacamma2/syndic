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
from diacamma.condominium.views_callfunds import CallFundsList,\
    CallFundsAddModify, CallFundsDel, CallFundsShow, CallDetailAddModify,\
    CallFundsValid, CallFundsClose, CallFundsPrint


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
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 5)

        self.factory.xfer = CallFundsAddModify()
        self.call('/diacamma.condominium/callFundsAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)

        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsList()
        self.call('/diacamma.condominium/callFundsList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 5)

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 5)

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
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/HEADER', 5)

    def test_add(self):
        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsAddModify')

        self.factory.xfer = CallFundsShow()
        self.call(
            '/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal('COMPONENTS/*', 15)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="calldetail"]/RECORD', 0)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="calldetail"]/HEADER', 3)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="calldetail"]/ACTIONS/ACTION', 3)

        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'callfunds': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="set"]', '1')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="price"]', '250.00')

        self.factory.xfer = CallDetailAddModify()
        self.call(
            '/diacamma.condominium/callDetailAddModify', {'callfunds': 1, 'set': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callDetailAddModify')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="set"]', '2')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="price"]', '25.00')

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

        self.factory.xfer = CallFundsShow()
        self.call(
            '/diacamma.condominium/callFundsShow', {'callfunds': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsShow')
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="calldetail"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="total"]', '275.00€')

    def test_valid(self):
        self.factory.xfer = CallFundsAddModify()
        self.call(
            '/diacamma.condominium/callFundsAddModify', {'SAVE': 'YES', "date": '2015-06-10', "comment": 'abc 123'}, False)
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

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)
        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)

        self.factory.xfer = CallFundsValid()
        self.call(
            '/diacamma.condominium/callFundsValid', {'CONFIRME': 'YES', 'callfunds': 1}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsValid')

        self.factory.xfer = CallFundsDel()
        self.call(
            '/diacamma.condominium/callFundsAddDel', {'CONFIRME': 'YES', "callfunds": 3}, False)
        self.assert_observer(
            'core.exception', 'diacamma.condominium', 'callFundsAddDel')

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 3)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="owner"]', "Minimum")  # 250*45%+25*75%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[1]/VALUE[@name="total"]', "131.25€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="owner"]', "Dalton William")  # 250*35%+25*0%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[2]/VALUE[@name="total"]', "87.50€")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="owner"]', "Dalton Joe")  # 250*20%+25*25%
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="callfunds"]/RECORD[3]/VALUE[@name="total"]', "56.25€")

        self.factory.xfer = CallFundsPrint()
        self.call(
            '/diacamma.condominium/callFundsPrint', {'callfunds': 3}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsPrint')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="MODEL"]', '8')

        self.factory.xfer = CallFundsPrint()
        self.call(
            '/diacamma.condominium/callFundsPrint', {'callfunds': 3, 'PRINT_MODE': 0, 'MODEL': 8}, False)
        self.assert_observer(
            'core.print', 'diacamma.condominium', 'callFundsPrint')

        self.factory.xfer = CallFundsClose()
        self.call(
            '/diacamma.condominium/callFundsClose', {'CONFIRME': 'YES', 'callfunds': 3}, False)
        self.assert_observer(
            'core.acknowledge', 'diacamma.condominium', 'callFundsClose')

        self.factory.xfer = CallFundsDel()
        self.call(
            '/diacamma.condominium/callFundsAddDel', {'CONFIRME': 'YES', "callfunds": 3}, False)
        self.assert_observer(
            'core.exception', 'diacamma.condominium', 'callFundsAddDel')

        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 0}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 0)
        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 2}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 1)
        self.factory.xfer = CallFundsList()
        self.call(
            '/diacamma.condominium/callFundsList', {'status_filter': 1}, False)
        self.assert_observer(
            'core.custom', 'diacamma.condominium', 'callFundsList')
        self.assert_count_equal('COMPONENTS/GRID[@name="callfunds"]/RECORD', 2)
