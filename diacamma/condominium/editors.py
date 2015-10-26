# -*- coding: utf-8 -*-

'''
Describe database model for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
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

from django.utils.translation import ugettext_lazy as _

from lucterios.framework.editors import LucteriosEditor
from lucterios.CORE.parameters import Params

from diacamma.accounting.tools import current_system_account
from diacamma.payoff.editors import SupportingEditor
from lucterios.framework.xfercomponents import XferCompButton
from lucterios.framework.tools import ActionsManage, FORMTYPE_MODAL, CLOSE_NO,\
    SELECT_SINGLE


class SetEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('budget').prec = currency_decimal
        xfer.get_components(
            'revenue_account').mask = current_system_account().get_revenue_mask()

    def show(self, xfer):
        partition = xfer.get_components('partition')
        partition.delete_header('set')


class OwnerEditor(SupportingEditor):

    def show(self, xfer):
        third = xfer.get_components('third')
        third.colspan -= 1
        btn = XferCompButton('show_third')
        btn.set_location(third.col + third.colspan, third.row)
        btn.set_action(xfer.request, ActionsManage.get_act_changed('Third', 'show', _('show'), ''),
                       {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO, 'params': {'third': self.item.third.id}})
        xfer.add_component(btn)
        partition = xfer.get_components('partition')
        partition.actions = []
        partition.delete_header('owner')
        callfunds = xfer.get_components('callfunds')
        callfunds.actions = []
        callfunds.add_actions(
            xfer, action_list=[('show', _("Edit"), "images/show.png", SELECT_SINGLE)])
        SupportingEditor.show(self, xfer)


class PartitionEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('set')
        xfer.change_to_readonly('owner')


class CallFundsEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('status')

    def show(self, xfer):
        if self.item.status > 0:
            calldetail = xfer.get_components('calldetail')
            calldetail.actions = []
