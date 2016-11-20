# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, TITLE_EDIT, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE,\
    XferTransition
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE, CLOSE_YES, SELECT_MULTI
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect
from lucterios.framework.xfergraphic import XferContainerAcknowledge

from diacamma.condominium.models import Expense, ExpenseDetail
from diacamma.accounting.models import FiscalYear
from diacamma.condominium.views_classload import SetShow


@MenuManage.describ('condominium.change_expense', FORMTYPE_NOMODAL, 'condominium.manage', _('Manage of expenses'))
class ExpenseList(XferListEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Condominium expenses")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', 0)
        self.params['status_filter'] = status_filter
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
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        lbl = XferCompLabelForm('lbl_date_filter')
        lbl.set_value_as_name(_('Filter by date'))
        lbl.set_location(0, 4)
        self.add_component(lbl)
        edt = XferCompSelect("date_filter")
        edt.set_select([(0, _('only current fiscal year')), (1, _('all expenses'))])
        edt.set_value(date_filter)
        edt.set_location(1, 4)
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        self.filter = Q(status=status_filter)
        if date_filter == 0:
            current_year = FiscalYear.get_current()
            self.filter &= Q(date__gte=current_year.begin) & Q(date__lte=current_year.end)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.getparam('status_filter', 0) == 0)
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.status == 0)
@MenuManage.describ('condominium.add_expense')
class ExpenseAddModify(XferAddEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption_add = _("Add expense")
    caption_modify = _("Modify expense")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('condominium.change_expense')
class ExpenseShow(XferShowEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Show expense")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', 0) == 0)
@MenuManage.describ('condominium.delete_expense')
class ExpenseDel(XferDelete):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Delete expense")


@ActionsManage.affect_transition("status", close=CLOSE_NO)
@MenuManage.describ('condominium.add_expense')
class ExpenseTransition(XferTransition):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.item.status == 0)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.item.status == 0)
@MenuManage.describ('condominium.add_expense')
class ExpenseDetailAddModify(XferAddEditor):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption_add = _("Add detail of expense")
    caption_modify = _("Modify detail of call")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.item.status == 0)
@MenuManage.describ('condominium.add_expense')
class ExpenseDetailDel(XferDelete):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption = _("Delete detail of expense")


@ActionsManage.affect_grid(_("Show set"), "diacamma.condominium/images/set.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.item.status == 0)
@MenuManage.describ('condominium.change_set')
class ExpenseDetailShowSet(XferContainerAcknowledge):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption = _("Show class load")

    def fillresponse(self):
        self.redirect_action(SetShow.get_action(), close=CLOSE_NO, params={'set': self.item.set_id})
