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
from lucterios.framework.xfercomponents import XferCompButton, XferCompLabelForm,\
    XferCompSelect
from lucterios.framework.tools import ActionsManage, FORMTYPE_MODAL, CLOSE_NO,\
    SELECT_SINGLE, FORMTYPE_REFRESH
from diacamma.accounting.models import Third, AccountThird
from diacamma.condominium.models import Set


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

    def before_save(self, xfer):
        accounts = self.item.third.accountthird_set.filter(
            code__regex=current_system_account().get_societary_mask())
        if len(accounts) == 0:
            AccountThird.objects.create(
                third=self.item.third, code=Params.getvalue("condominium-default-owner-account"))
        return SupportingEditor.before_save(self, xfer)

    def edit(self, xfer):
        lbl = XferCompLabelForm('lbl_third')
        lbl.set_location(1, 0)
        lbl.set_value_as_name(_('third'))
        xfer.add_component(lbl)

        sel = XferCompSelect('third')
        sel.needed = True
        sel.set_location(2, 0)
        sel.set_select_query(
            Third.objects.filter(supporting__owner__isnull=True))
        xfer.add_component(sel)

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


class CallDetailEditor(LucteriosEditor):

    def edit(self, xfer):
        set_comp = xfer.get_components('set')
        set_comp.set_action(
            xfer.request, xfer.get_action(), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        freq = Params.getvalue("condominium-frequency")
        xfer.get_components('price').prec = Params.getvalue(
            "accounting-devise-prec")
        set_comp.get_reponse_xml()
        current_set = Set.objects.get(id=set_comp.value)
        if freq == 1:
            xfer.get_components('price').value = current_set.budget / 4
        elif freq == 2:
            xfer.get_components('price').value = current_set.budget / 12
        else:
            xfer.get_components('price').value = current_set.budget


class ExpenseEditor(SupportingEditor):

    def show(self, xfer):
        if self.item.status == 0:
            third = xfer.get_components('third')
            third.colspan -= 2
            btn = XferCompButton('change_third')
            btn.set_location(third.col + third.colspan, third.row)
            modal_name = xfer.item.__class__.__name__
            btn.set_action(xfer.request, ActionsManage.get_act_changed(modal_name, 'third', _('change'), ''),
                           {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO})
            xfer.add_component(btn)

            if self.item.third is not None:
                btn = XferCompButton('show_third')
                btn.set_location(third.col + third.colspan + 1, third.row)
                btn.set_action(xfer.request, ActionsManage.get_act_changed('Third', 'show', _('show'), ''),
                               {'modal': FORMTYPE_MODAL, 'close': CLOSE_NO, 'params': {'third': self.item.third.id}})
                xfer.add_component(btn)
        else:
            details = xfer.get_components('expensedetail')
            details.actions = []
            if self.item.bill_type != 0:
                SupportingEditor.show(self, xfer)
