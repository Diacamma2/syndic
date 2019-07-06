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
from lucterios.framework.xfercomponents import XferCompButton, XferCompSelect
from lucterios.framework.tools import ActionsManage, FORMTYPE_MODAL, CLOSE_NO, SELECT_SINGLE, FORMTYPE_REFRESH, SELECT_MULTI
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.parameters import Params

from diacamma.accounting.tools import current_system_account
from diacamma.accounting.models import Third, FiscalYear
from diacamma.payoff.editors import SupportingEditor
from diacamma.condominium.models import Set, CallDetail, CallFundsSupporting, Owner,\
    RecoverableLoadRatio
from lucterios.contacts.models import CustomField
from lucterios.framework.xferadvance import XferSave
from diacamma.condominium.system import current_system_condo


class SetEditor(LucteriosEditor):

    def edit(self, xfer):
        revenue_account = xfer.get_components('revenue_account')
        if revenue_account is not None:
            revenue_account.mask = current_system_account().get_revenue_mask()

    def show(self, xfer):
        if xfer.item.is_link_to_lots:
            part_name = 'partitionfill'
            xfer.remove_component('partition')
        else:
            part_name = 'partition'
            xfer.remove_component('partitionfill')
        partition = xfer.get_components(part_name)
        partition.delete_header('set')
        partition.delete_header('set.budget_txt')
        partition.delete_header('set.sumexpense')


class OwnerEditor(SupportingEditor):

    def before_save(self, xfer):
        self.item.check_account()
        return SupportingEditor.before_save(self, xfer)

    def saving(self, xfer):
        contact_save = XferSave()
        contact_save.request = xfer.request
        contact_save.item = xfer.item.third.contact.get_final_child()
        contact_save.model = contact_save.item.__class__
        contact_save.params = xfer.params
        contact_save.fill_simple_fields()
        contact_save.fillresponse()

        third_save = XferSave()
        third_save.request = xfer.request
        third_save.item = xfer.item.third.get_final_child()
        third_save.model = third_save.item.__class__
        third_save.params = xfer.params
        third_save.fill_simple_fields()
        third_save.fillresponse()

    def edit(self, xfer):
        if xfer.item.id is None:
            sel = XferCompSelect('third')
            sel.needed = True
            sel.description = _('third')
            sel.set_location(1, 0)
            owner_third_ids = []
            for owner in Owner.objects.all():
                owner_third_ids.append(owner.third_id)
            items = Third.objects.all().exclude(id__in=owner_third_ids).distinct()
            items = sorted(items, key=lambda t: six.text_type(t))
            sel.set_select_query(items)
            xfer.add_component(sel)
            btn = XferCompButton('add_third')
            btn.set_location(3, 0)
            btn.set_is_mini(True)
            btn.set_action(xfer.request, ActionsManage.get_action_url('accounting.Third', 'Add', xfer), close=CLOSE_NO,
                           modal=FORMTYPE_MODAL, params={'new_account': Params.getvalue('condominium-default-owner-account')})
            xfer.add_component(btn)
            xfer.filltab_from_model(1, xfer.get_max_row() + 1, False, ["information"])
        else:
            old_item = xfer.item
            xfer.item = old_item.third.contact.get_final_child()
            xfer.filltab_from_model(1, 0, False, xfer.item.get_edit_fields())
            CustomField.edit_fields(xfer, 1)

            xfer.item = old_item.third.get_final_child()
            xfer.filltab_from_model(1, xfer.get_max_row() + 1, False, xfer.item.get_edit_fields())
            CustomField.edit_fields(xfer, 1)

            xfer.item = old_item
            xfer.filltab_from_model(1, xfer.get_max_row() + 1, False, ["information"])

    def show(self, xfer):
        xfer.params['supporting'] = self.item.id
        third = xfer.get_components('thirdtotal')
        xfer.tab = third.tab
        btn = XferCompButton('show_third')
        btn.set_location(third.col + third.colspan, third.row)
        act_btn = ActionsManage.get_action_url('accounting.Third', 'Show', xfer)
        if act_btn is not None:
            act_btn.caption = _('third')
        btn.set_action(xfer.request, act_btn, modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'third': self.item.third.id})
        btn.rowspan = 2
        xfer.add_component(btn)

        if hasattr(xfer.item.third.contact.get_final_child(), 'structure_type'):
            contact = xfer.get_components('ownercontact')
            xfer.tab = contact.tab
            old_item = xfer.item
            xfer.item = old_item.third.contact.get_final_child()
            xfer.filltab_from_model(contact.col, contact.row + 1, True, ['responsability_set'])
            xfer.item = old_item

        link_grid_lines = xfer.get_components('entryline')
        link_grid_lines.description = ''
        link_grid_lines.actions = []
        link_grid_lines.colspan = 2
        link_grid_lines.add_action(xfer.request, ActionsManage.get_action_url('accounting.EntryAccount', 'OpenFromLine', xfer),
                                   modal=FORMTYPE_MODAL, unique=SELECT_SINGLE, close=CLOSE_NO)
        link_grid_lines.add_action(xfer.request, ActionsManage.get_action_url('accounting.EntryAccount', 'Close', xfer),
                                   modal=FORMTYPE_MODAL, unique=SELECT_MULTI, close=CLOSE_NO)
        link_grid_lines.add_action(xfer.request, ActionsManage.get_action_url('accounting.EntryAccount', 'Link', xfer),
                                   modal=FORMTYPE_MODAL, unique=SELECT_MULTI, close=CLOSE_NO)

        partition = xfer.get_components('partition')
        partition.actions = []
        partition.description = _("current class loads")
        partition.delete_header('owner')
        lots = xfer.get_components('propertylot')
        lots.actions = []
        lots.delete_header('owner')
        xfer.get_components('payoff').colspan = 2

        xfer.tab = partition.tab
        row = xfer.get_max_row() + 1
        btn = XferCompButton('show_load_count')
        btn.set_location(partition.col, row)
        btn.set_action(xfer.request, ActionsManage.get_action_url('condominium.Owner', 'LoadCount', xfer), modal=FORMTYPE_MODAL, close=CLOSE_NO)
        xfer.add_component(btn)

        callfunds = xfer.get_components('callfunds')
        callfunds.actions = []
        callfunds.colspan = 2
        callfunds.add_action(xfer.request, ActionsManage.get_action_url('condominium.CallFunds', 'Show', xfer), close=CLOSE_NO, unique=SELECT_SINGLE)

        xfer.tab = callfunds.tab
        row = xfer.get_max_row() + 1
        btn = XferCompButton('add_multipayoff')
        btn.set_location(callfunds.col, row)
        btn.set_action(xfer.request, ActionsManage.get_action_url('condominium.Owner', 'MultiPay', xfer), modal=FORMTYPE_MODAL, close=CLOSE_NO)
        xfer.add_component(btn)
        btn = XferCompButton('add_ventilatePayoff')
        btn.set_location(callfunds.col + 1, row)
        btn.set_action(xfer.request, ActionsManage.get_action_url('condominium.Owner', 'VentilatePay', xfer), modal=FORMTYPE_MODAL, close=CLOSE_NO)
        xfer.add_component(btn)


class RecoverableLoadRatioEditor(LucteriosEditor):

    def edit(self, xfer):
        old_account = xfer.get_components("code")
        xfer.remove_component("code")
        sel_code = XferCompSelect("code")
        sel_code.set_location(old_account.col, old_account.row, old_account.colspan + 1, old_account.rowspan)
        existed_codes = []
        for acc_ratio in RecoverableLoadRatio.objects.all():
            existed_codes.append(acc_ratio.code)
        for item in FiscalYear.get_current().chartsaccount_set.all().filter(code__regex=current_system_account().get_expence_mask()).exclude(code__in=existed_codes).order_by('code'):
            sel_code.select_list.append((item.code, six.text_type(item)))
        sel_code.set_value(self.item.code)
        xfer.add_component(sel_code)


class PartitionEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('set')
        xfer.change_to_readonly('owner')


class OwnerContactEditor(LucteriosEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('contact')


class CallFundsSupportingEditor(SupportingEditor):
    pass


class CallFundsEditor(LucteriosEditor):

    def before_save(self, xfer):
        if self.item.supporting is not None:
            self.item.supporting.edit.before_save(xfer)

    def edit(self, xfer):
        xfer.change_to_readonly('status')

    def show(self, xfer):
        self.item.check_supporting()
        if (self.item.supporting is not None) and (self.item.status > 0):
            old_item = xfer.item
            old_model = xfer.model
            try:
                xfer.item = self.item.supporting
                xfer.model = CallFundsSupporting
                self.item.supporting.editor.show(xfer)
            finally:
                xfer.item = old_item
                xfer.model = old_model
        if self.item.status == 0:
            grid = xfer.get_components("calldetail")
            grid.delete_header('total_amount')
            grid.delete_header('owner_part')


class CallDetailEditor(LucteriosEditor):

    def edit(self, xfer):
        type_call = xfer.get_components('type_call')
        type_call.set_select(current_system_condo().get_callfunds_list())
        type_call.set_action(xfer.request, xfer.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        set_comp = xfer.get_components('set')
        if int(self.item.type_call) == 1:
            type_load = 1
        else:
            type_load = 0
        set_list = Set.objects.filter(is_active=True, type_load=type_load)
        if len(set_list) == 0:
            raise LucteriosException(IMPORTANT, _('No category of charge defined!'))
        set_comp.set_needed(True)
        set_comp.set_select_query(set_list)
        set_comp.set_action(xfer.request, xfer.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        xfer.get_components('price').prec = Params.getvalue("accounting-devise-prec")
        set_comp.get_json()
        current_set = Set.objects.get(id=set_comp.value)
        if current_set.type_load == 0:
            if int(self.item.type_call) == 0:
                xfer.get_components('price').value = current_set.get_new_current_callfunds()
            elif int(self.item.type_call) == 4:
                xfer.get_components('price').value = current_set.get_current_budget() * 0.05
            else:
                xfer.get_components('price').value = 0.0
        elif current_set.type_load == 1:
            already_called = 0
            call_details = CallDetail.objects.filter(set_id=set_comp.value)
            if self.item.id is not None:
                call_details = call_details.exclude(id=self.item.id)
            for detail in call_details:
                already_called += detail.price
            xfer.get_components('price').value = max(0, float(current_set.get_current_budget()) - float(already_called))


class ExpenseEditor(SupportingEditor):

    def edit(self, xfer):
        xfer.change_to_readonly('status')

    def show(self, xfer):
        if self.item.status == 0:
            SupportingEditor.show_third(self, xfer)
            xfer.get_components('date').colspan += 1
            xfer.get_components('expensedetail').colspan += 1
        else:
            SupportingEditor.show(self, xfer)


class ExpenseDetailEditor(LucteriosEditor):

    def edit(self, xfer):
        set_comp = xfer.get_components('set')
        set_comp.set_select_query(Set.objects.filter(is_active=True))
        xfer.get_components('price').prec = Params.getvalue("accounting-devise-prec")
        old_account = xfer.get_components("expense_account")
        xfer.remove_component("expense_account")
        sel_account = XferCompSelect("expense_account")
        sel_account.description = old_account.description
        sel_account.set_location(old_account.col, old_account.row, old_account.colspan, old_account.rowspan)
        for item in FiscalYear.get_current().chartsaccount_set.all().filter(code__regex=current_system_account().get_expence_mask()).order_by('code'):
            sel_account.select_list.append((item.code, six.text_type(item)))
        sel_account.set_value(self.item.expense_account)
        xfer.add_component(sel_account)

        self.item.year = FiscalYear.get_current()
        btn = XferCompButton('add_account')
        btn.set_location(old_account.col + 1, old_account.row)
        btn.set_is_mini(True)
        btn.set_action(xfer.request, ActionsManage.get_action_url('accounting.ChartsAccount', 'AddModify', xfer),
                       close=CLOSE_NO, modal=FORMTYPE_MODAL, params={'year': self.item.year.id})
        xfer.add_component(btn)
        xfer.get_components("set").colspan = old_account.colspan + 1
        xfer.get_components("designation").colspan = old_account.colspan + 1
        xfer.get_components("price").colspan = old_account.colspan + 1
