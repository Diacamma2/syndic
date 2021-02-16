# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, TITLE_EDIT, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE,\
    XferTransition, TITLE_CREATE
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE, CLOSE_YES, SELECT_MULTI,\
    WrapAction
from lucterios.framework.xfercomponents import XferCompSelect, XferCompGrid
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.error import LucteriosException
from lucterios.framework import signal_and_lock

from diacamma.accounting.models import FiscalYear
from diacamma.accounting.tools import current_system_account
from diacamma.payoff.views import PayoffAddModify
from diacamma.condominium.models import Expense, ExpenseDetail
from diacamma.condominium.views_classload import SetShow
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor


@MenuManage.describ('condominium.change_expense', FORMTYPE_NOMODAL, 'condominium.manage', _('Manage of expenses'))
class ExpenseList(XferListEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Condominium expenses")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', Expense.STATUS_BUILDING_WAITING)
        self.params['status_filter'] = status_filter
        date_filter = self.getparam('date_filter', 0)
        self.fieldnames = Expense.get_default_fields(status_filter)
        edt = XferCompSelect("status_filter")
        edt.set_select(Expense.SELECTION_STATUS)
        edt.set_value(status_filter)
        edt.description = _('Filter by type')
        edt.set_location(0, 3)
        edt.set_action(self.request, self.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        edt = XferCompSelect("date_filter")
        edt.set_select([(0, _('only current fiscal year')), (1, _('all expenses'))])
        edt.set_value(date_filter)
        edt.set_location(0, 4)
        edt.description = _('Filter by date')
        edt.set_action(self.request, self.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        if status_filter == Expense.STATUS_BUILDING_WAITING:
            self.filter = Q(status=Expense.STATUS_BUILDING) | Q(status=Expense.STATUS_WAITING)
        elif status_filter != Expense.STATUS_ALL:
            self.filter = Q(status=status_filter)
        else:
            self.filter = Q()
        if date_filter == 0:
            current_year = FiscalYear.get_current()
            self.filter &= Q(date__gte=current_year.begin) & Q(date__lte=current_year.end)


@ActionsManage.affect_list(_("Search"), "diacamma.condominium/images/expense.png")
@MenuManage.describ('condominium.change_expense')
class ExpenseSearch(XferSavedCriteriaSearchEditor):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Search expense")


@ActionsManage.affect_grid(TITLE_CREATE, "images/new.png", condition=lambda xfer, gridname='': xfer.getparam('status_filter', Expense.STATUS_BUILDING) in (Expense.STATUS_BUILDING, Expense.STATUS_WAITING, Expense.STATUS_BUILDING_WAITING))
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.status in (Expense.STATUS_BUILDING, Expense.STATUS_WAITING))
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

    def fillresponse(self):
        XferShowEditor.fillresponse(self)
        if self.item.status == Expense.STATUS_WAITING:
            self.remove_component('total_rest_topay')


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', Expense.STATUS_BUILDING) == Expense.STATUS_BUILDING)
@MenuManage.describ('condominium.delete_expense')
class ExpenseDel(XferDelete):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'
    caption = _("Delete expense")


@ActionsManage.affect_transition("status", close=CLOSE_NO, multi_list=('close',))
@MenuManage.describ('condominium.add_expense')
class ExpenseTransition(XferTransition):
    icon = "expense.png"
    model = Expense
    field_id = 'expense'


@ActionsManage.affect_grid(_('payoff'), '', close=CLOSE_NO, unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', Expense.STATUS_BUILDING_WAITING) == Expense.STATUS_VALID)
@MenuManage.describ('payoff.add_payoff')
class ExpenseMultiPay(XferContainerAcknowledge):
    caption = _("Multi-pay expense")
    icon = "expense.png"
    model = Expense
    field_id = 'expense'

    def fillresponse(self, expense):
        self.redirect_action(PayoffAddModify.get_action("", ""), params={"supportings": expense, 'repartition': "1"})


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.item.status in (Expense.STATUS_BUILDING, Expense.STATUS_WAITING))
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.item.status in (Expense.STATUS_BUILDING, Expense.STATUS_WAITING))
@MenuManage.describ('condominium.add_expense')
class ExpenseDetailAddModify(XferAddEditor):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption_add = _("Add detail of expense")
    caption_modify = _("Modify detail of call")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.item.status in (Expense.STATUS_BUILDING, Expense.STATUS_WAITING))
@MenuManage.describ('condominium.add_expense')
class ExpenseDetailDel(XferDelete):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption = _("Delete detail of expense")


@ActionsManage.affect_grid(_("Show set"), "diacamma.condominium/images/set.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.item.status in (Expense.STATUS_BUILDING, Expense.STATUS_WAITING))
@MenuManage.describ('condominium.change_set')
class ExpenseDetailShowSet(XferContainerAcknowledge):
    icon = "expense.png"
    model = ExpenseDetail
    field_id = 'expensedetail'
    caption = _("Show class load")
    readonly = True
    methods_allowed = ('GET', )

    def fillresponse(self):
        self.redirect_action(SetShow.get_action(), close=CLOSE_NO, params={'set': self.item.set_id})


@signal_and_lock.Signal.decorate('third_addon')
def thirdaddon_expense(item, xfer):
    if WrapAction.is_permission(xfer.request, 'condominium.change_expense'):
        try:
            status_filter = xfer.getparam('status_filter', Expense.STATUS_BUILDING)
            date_filter = xfer.getparam('date_filter', 0)
            current_year = FiscalYear.get_current()
            item.get_account(current_year, current_system_account().get_provider_mask())
            xfer.new_tab(_('Expenses'))
            edt = XferCompSelect("status_filter")
            edt.set_select(list(Expense.get_field_by_name('status').choices))
            edt.set_value(status_filter)
            edt.description = _('Filter by type')
            edt.set_location(0, 1)
            edt.set_action(xfer.request, xfer.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            xfer.add_component(edt)
            edt = XferCompSelect("date_filter")
            edt.set_select([(0, _('only current fiscal year')), (1, _('all expenses'))])
            edt.set_value(date_filter)
            edt.set_location(0, 2)
            edt.description = _('Filter by date')
            edt.set_action(xfer.request, xfer.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            xfer.add_component(edt)
            expense_filter = Q(status=status_filter) & Q(third=item)
            if date_filter == 0:
                expense_filter &= Q(date__gte=current_year.begin) & Q(date__lte=current_year.end)
            expenses = Expense.objects.filter(expense_filter).distinct()
            expense_grid = XferCompGrid('expense')
            expense_grid.set_model(expenses, Expense.get_default_fields(status_filter), xfer)
            expense_grid.add_action_notified(xfer, Expense)
            expense_grid.set_location(0, 3, 2)
            xfer.add_component(expense_grid)
        except LucteriosException:
            pass
