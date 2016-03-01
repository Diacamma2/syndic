# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage,\
    FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE, CLOSE_YES
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect
from lucterios.framework.xfergraphic import XferContainerAcknowledge

from diacamma.condominium.models import Expense, ExpenseDetail
from diacamma.accounting.models import FiscalYear


@ActionsManage.affect('Expense', 'list')
@MenuManage.describ('condominium.change_expense', FORMTYPE_NOMODAL, 'condominium', _('Manage of expenses'))
class ExpenseList(XferListEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("expenses")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', 0)
        date_filter = self.getparam('date_filter', 0)
        self.fieldnames = Expense.get_default_fields(status_filter)
        lbl = XferCompLabelForm('lbl_status_filter')
        lbl.set_value_as_name(_('Filter by type'))
        lbl.set_location(0, 3)
        self.add_component(lbl)
        dep_field = self.item.get_field_by_name('status')
        sel_list = list(dep_field.choices)
        edt = XferCompSelect("status_filter")
        edt.set_select(sel_list)
        edt.set_value(status_filter)
        edt.set_location(1, 3)
        edt.set_action(self.request, self.get_action(),
                       {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        self.add_component(edt)

        lbl = XferCompLabelForm('lbl_date_filter')
        lbl.set_value_as_name(_('Filter by date'))
        lbl.set_location(0, 4)
        self.add_component(lbl)
        edt = XferCompSelect("date_filter")
        edt.set_select(
            [(0, _('only current fiscal year')), (1, _('all expenses'))])
        edt.set_value(date_filter)
        edt.set_location(1, 4)
        edt.set_action(self.request, self.get_action(),
                       {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        self.add_component(edt)

        self.filter = Q(status=status_filter)
        if date_filter == 0:
            current_year = FiscalYear.get_current()
            self.filter &= Q(date__gte=current_year.begin) & Q(
                date__lte=current_year.end)
        if status_filter > 0:
            self.action_grid = [
                ('show', _("Edit"), "images/show.png", SELECT_SINGLE)]


@ActionsManage.affect('Expense', 'modify', 'add')
@MenuManage.describ('condominium.add_expense')
class ExpenseAddModify(XferAddEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption_add = _("Add expense")
    caption_modify = _("Modify expense")


@ActionsManage.affect('Expense', 'show')
@MenuManage.describ('condominium.change_expense')
class ExpenseShow(XferShowEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Show expense")

    def fillresponse(self):
        if (self.item.status == 0) and (self.item.get_info_state() == ''):
            self.action_list.insert(
                0, ('valid', _("Valid"), "images/ok.png", CLOSE_YES))
        elif self.item.status == 1:
            self.action_list = []
            self.action_list.insert(
                0, ('close', _("Closed"), "images/ok.png", CLOSE_NO))
        elif self.item.status == 2:
            self.action_list = []
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('Expense', 'delete')
@MenuManage.describ('condominium.delete_expense')
class ExpenseDel(XferDelete):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Delete expense")


@ActionsManage.affect('Expense', 'valid')
@MenuManage.describ('condominium.add_expense')
class ExpenseValid(XferContainerAcknowledge):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Valid expense")

    def fillresponse(self):
        if (self.item.status == 0) and self.confirme(_("Do you want validate this expense?")):
            self.item.valid()


@ActionsManage.affect('Expense', 'close')
@MenuManage.describ('condominium.add_expense')
class ExpenseClose(XferContainerAcknowledge):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Close expense")

    def fillresponse(self):
        if (self.item.status == 1) and self.confirme(_("Do you want close '%s'?") % self.item):
            self.item.close()


@ActionsManage.affect('ExpenseDetail', 'edit', 'add')
@MenuManage.describ('condominium.add_expense')
class ExpenseDetailAddModify(XferAddEditor):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption_add = _("Add detail of expense")
    caption_modify = _("Modify detail of call")


@ActionsManage.affect('ExpenseDetail', 'delete')
@MenuManage.describ('condominium.add_expense')
class ExpenseDetailDel(XferDelete):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption = _("Delete detail of expense")
