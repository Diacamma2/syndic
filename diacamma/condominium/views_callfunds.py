# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, TITLE_ADD, TITLE_MODIFY, TITLE_EDIT, TITLE_DELETE, TITLE_PRINT, XferTransition,\
    TITLE_CREATE
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompSelect
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE, CLOSE_YES, SELECT_MULTI
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.xfersearch import get_criteria_list

from diacamma.payoff.views import can_send_email, SupportingPrint
from diacamma.condominium.models import CallFunds, CallDetail
from diacamma.condominium.system import current_system_condo
from diacamma.accounting.models import FiscalYear


@MenuManage.describ('condominium.change_callfunds', FORMTYPE_NOMODAL, 'condominium.manage', _('Manage of calls of funds'))
class CallFundsList(XferListEditor):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Calls of funds")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', CallFunds.STATUS_BUILDING)
        self.params['status_filter'] = status_filter
        dep_field = self.item.get_field_by_name('status')
        sel_list = list(dep_field.choices)
        edt = XferCompSelect("status_filter")
        edt.description = _('Filter by type')
        edt.set_select(sel_list)
        edt.set_value(status_filter)
        edt.set_location(0, 3)
        edt.set_action(self.request, self.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)
        self.filter = Q(status=status_filter)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        if self.getparam('status_filter', CallFunds.STATUS_VALID) == CallFunds.STATUS_BUILDING:
            callfunds_grid = self.get_components('callfunds')
            callfunds_grid.delete_header('supporting.total_rest_topay')


def CallFundsAddCurrent_cond(xfer):
    if xfer.getparam('status_filter', CallFunds.STATUS_VALID) == CallFunds.STATUS_BUILDING:
        return current_system_condo().CurrentCallFundsAdding(False)
    else:
        return False


@ActionsManage.affect_list(_('Add current'), "images/new.png", condition=CallFundsAddCurrent_cond)
@MenuManage.describ('condominium.add_callfunds')
class CallFundsAddCurrent(XferContainerAcknowledge):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Add call of funds")

    def fillresponse(self):
        if self.confirme(_('Do you want create current call of funds of this year?')):
            current_system_condo().CurrentCallFundsAdding(True)


@ActionsManage.affect_grid(TITLE_CREATE, "images/new.png", condition=lambda xfer, gridname='': xfer.getparam('status_filter', CallFunds.STATUS_VALID) == CallFunds.STATUS_BUILDING)
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.status == CallFunds.STATUS_BUILDING)
@MenuManage.describ('condominium.add_callfunds')
class CallFundsAddModify(XferAddEditor):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption_add = _("Add call of funds")
    caption_modify = _("Modify call of funds")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('condominium.change_callfunds')
class CallFundsShow(XferShowEditor):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Show call of funds")

    def fillresponse(self):
        XferShowEditor.fillresponse(self)
        self.add_action(ActionsManage.get_action_url('payoff.Supporting', 'Show', self),
                        close=CLOSE_NO, params={'item_name': 'callfundssupporting', 'callfundssupporting': self.item.supporting_id}, pos_act=0)


def can_printing(xfer, gridname=''):
    if xfer.getparam('CRITERIA') is not None:
        for criteria_item in get_criteria_list(xfer.getparam('CRITERIA')):
            if (criteria_item[0] == 'status') and (criteria_item[2] in ('1', '2', '1;2')):
                return True
        return False
    else:
        return xfer.getparam('status_filter', CallFunds.STATUS_BUILDING) in (CallFunds.STATUS_VALID, CallFunds.STATUS_ENDED)


@ActionsManage.affect_grid(_("Send"), "lucterios.mailing/images/email.png", close=CLOSE_NO, unique=SELECT_MULTI, condition=lambda xfer, gridname='': can_printing(xfer) and can_send_email(xfer))
@ActionsManage.affect_show(_("Send"), "lucterios.mailing/images/email.png", close=CLOSE_NO, condition=lambda xfer: xfer.item.status in (CallFunds.STATUS_VALID, CallFunds.STATUS_ENDED) and can_send_email(xfer))
@MenuManage.describ('condominium.add_callfunds')
class CallFundsPayableEmail(XferContainerAcknowledge):
    caption = _("Send by email")
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'

    def fillresponse(self):
        self.redirect_action(ActionsManage.get_action_url('payoff.Supporting', 'Email', self),
                             close=CLOSE_NO, params={'item_name': self.field_id, "modelname": self.model.get_long_name()})


@ActionsManage.affect_grid(TITLE_PRINT, "images/print.png", unique=SELECT_MULTI, condition=can_printing)
@ActionsManage.affect_show(TITLE_PRINT, "images/print.png", close=CLOSE_NO, condition=lambda xfer: xfer.item.status in (CallFunds.STATUS_VALID, CallFunds.STATUS_ENDED))
@MenuManage.describ('condominium.change_callfunds')
class CallFundsPrint(SupportingPrint):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Print call of funds")

    def get_print_name(self):
        if len(self.items) == 1:
            current_callfund = self.items[0]
            return current_callfund.get_document_filename()
        else:
            return str(self.caption)

    def items_callback(self):
        has_item = False
        for item in self.items:
            if item.status != CallFunds.STATUS_BUILDING:
                year = FiscalYear.get_current(item.date)
                item.owner.set_dates(begin_date=year.begin, end_date=item.date)
                has_item = True
                yield item
        if not has_item:
            raise LucteriosException(IMPORTANT, _("No call of funds to print!"))


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) in (0, 1))
@MenuManage.describ('condominium.delete_callfunds')
class CallFundsDel(XferDelete):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Delete call of funds")

    def fillresponse(self):
        num_list = []
        for item in self.items:
            if item.status == CallFunds.STATUS_VALID:
                num_list.append(str(item.num))
            else:
                num_list = None
                break
        if num_list is None:
            XferDelete.fillresponse(self)
        else:
            num_list = list(set(num_list))
            if self.confirme(_("Do you want delete calls of fonds #%s and the following ones?") % ",".join(num_list)):
                CallFunds.devalid(min(num_list))


@ActionsManage.affect_transition("status", close=CLOSE_YES, multi_list=('close',))
@MenuManage.describ('condominium.add_callfunds')
class CallFundsTransition(XferTransition):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.item.status == CallFunds.STATUS_BUILDING)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.item.status == CallFunds.STATUS_BUILDING)
@MenuManage.describ('condominium.add_callfunds')
class CallDetailAddModify(XferAddEditor):
    icon = "callfunds.png"
    model = CallDetail
    field_id = 'calldetail'
    caption_add = _("Add detail of call")
    caption_modify = _("Modify detail of call")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.item.status == CallFunds.STATUS_BUILDING)
@MenuManage.describ('condominium.add_callfunds')
class CallDetailDel(XferDelete):
    icon = "callfunds.png"
    model = CallDetail
    field_id = 'calldetail'
    caption = _("Delete detail of call")
