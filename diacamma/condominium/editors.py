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
from django.utils import six

from lucterios.framework.editors import LucteriosEditor
from lucterios.CORE.parameters import Params
from lucterios.framework.xfercomponents import XferCompButton, XferCompLabelForm,\
    XferCompSelect
from lucterios.framework.tools import ActionsManage, FORMTYPE_MODAL, CLOSE_NO,\
    SELECT_SINGLE, FORMTYPE_REFRESH

from diacamma.accounting.tools import current_system_account
from diacamma.accounting.models import Third, AccountThird, FiscalYear
from diacamma.payoff.editors import SupportingEditor
from diacamma.condominium.models import Set, CallFunds


class SetEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('budget').prec = currency_decimal
        xfer.get_components(
            'revenue_account').mask = current_system_account().get_revenue_mask()

    def show(self, xfer):
        partition = xfer.get_components('partition')
        partition.delete_header('set')
        partition.delete_header('set.budget')
        partition.delete_header('set.sumexpense_txt')


class OwnerEditor(SupportingEditor):

    def before_save(self, xfer):
        accounts = self.item.third.accountthird_set.filter(
            code__regex=current_system_account().get_societary_mask())
        if len(accounts) == 0:
            AccountThird.objects.create(
                third=self.item.third, code=Params.getvalue("condominium-default-owner-account"))
        return SupportingEditor.before_save(self, xfer)

    def edit(self, xfer):
        if xfer.item.id is None:
            third = xfer.get_components('third')
            xfer.remove_component('third')
            xfer.remove_component('lbl_third')
            lbl = XferCompLabelForm('lbl_third')
            lbl.set_location(third.col - 1, third.row)
            lbl.set_value_as_name(_('third'))
            xfer.add_component(lbl)

            sel = XferCompSelect('third')
            sel.needed = True
            sel.set_location(third.col, third.row)
            items = Third.objects.filter(
                supporting__owner__isnull=True).distinct()
            items = sorted(items, key=lambda t: six.text_type(t))
            sel.set_select_query(items)
            xfer.add_component(sel)
            btn = XferCompButton('add_third')
            btn.set_location(3, 0)
            btn.set_is_mini(True)
            btn.set_action(xfer.request, ActionsManage.get_act_changed(
                'Third', 'add', '', "images/add.png"), {"close": CLOSE_NO, "modal": FORMTYPE_MODAL})
            xfer.add_component(btn)
        else:
            xfer.change_to_readonly('third')

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
        callfunds.add_actions(xfer, model=CallFunds,
                              action_list=[('show', _("Edit"), "images/show.png", SELECT_SINGLE)])
        lbl = XferCompLabelForm('sep')
        lbl.set_location(1, xfer.get_max_row() + 1)
        lbl.set_value("{[br/]}")
        xfer.add_component(lbl)
        SupportingEditor.show(self, xfer)
        xfer.remove_component('lbl_total_rest_topay')
        xfer.remove_component('total_rest_topay')
        xfer.move_components('lbl_total_payed', 0, 1)
        xfer.move_components('total_payed', 0, 1)
        xfer.move_components('lbl_total_real', 2, 4)
        xfer.move_components('total_real', 2, 4)


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

    def edit(self, xfer):
        xfer.change_to_readonly('status')

    def show(self, xfer):
        if self.item.status == 0:
            SupportingEditor.show_third(self, xfer)
        else:
            details = xfer.get_components('expensedetail')
            details.actions = []
            SupportingEditor.show(self, xfer)


class ExpenseDetailEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.get_components('price').prec = Params.getvalue(
            "accounting-devise-prec")
        old_account = xfer.get_components("expense_account")
        xfer.remove_component("expense_account")
        sel_account = XferCompSelect("expense_account")
        sel_account.set_location(
            old_account.col, old_account.row, old_account.colspan, old_account.rowspan)
        for item in FiscalYear.get_current().chartsaccount_set.all().filter(code__regex=current_system_account().get_expence_mask()).order_by('code'):
            sel_account.select_list.append(
                (item.code, six.text_type(item)))
        sel_account.set_value(self.item.expense_account)
        xfer.add_component(sel_account)
