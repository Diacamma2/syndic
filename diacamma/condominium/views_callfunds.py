# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, TITLE_ADD, TITLE_MODIFY, TITLE_EDIT, TITLE_DELETE, TITLE_PRINT,\
    XferTransition
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE, CLOSE_YES, SELECT_MULTI,\
    same_day_months_after
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect
from lucterios.framework.error import LucteriosException, IMPORTANT

from lucterios.CORE.xferprint import XferPrintReporting

from diacamma.condominium.models import CallFunds, CallDetail, Set
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from diacamma.accounting.models import FiscalYear
from lucterios.framework.models import get_value_converted


@MenuManage.describ('condominium.change_callfunds', FORMTYPE_NOMODAL, 'condominium.manage', _('Manage of calls of funds'))
class CallFundsList(XferListEditor):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Calls of funds")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', 0)
        self.params['status_filter'] = status_filter
        lbl = XferCompLabelForm('lbl_filter')
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
        self.filter = Q(status=status_filter)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        if self.getparam('status_filter', 1) == 0:
            callfunds_grid = self.get_components('callfunds')
            callfunds_grid.delete_header('supporting.total_rest_topay')


def CallFundsAddCurrent_cond(xfer):
    if xfer.getparam('status_filter', 1) == 0:
        year = FiscalYear.get_current()
        calls = CallFunds.objects.filter(date__gte=year.begin, date__lte=year.end, type_call=0)
        return len(calls) == 0
    else:
        return False


@ActionsManage.affect_list(_('Add current'), "images/add.png", condition=CallFundsAddCurrent_cond)
@MenuManage.describ('condominium.add_callfunds')
class CallFundsAddCurrent(XferContainerAcknowledge):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Add call of funds")

    def fillresponse(self):
        if self.confirme(_('Do you want create current call of funds of this year?')):
            year = FiscalYear.get_current()
            for num in range(4):
                date = same_day_months_after(year.begin, 3 * num)
                new_call = CallFunds.objects.create(date=date, comment=_("Call of funds #%(num)d of year from %(begin)s to %(end)s") % {'num': num + 1, 'begin': get_value_converted(year.begin), 'end': get_value_converted(year.end)}, type_call=0, status=0)
                for category in Set.objects.filter(type_load=0, is_active=True):
                    CallDetail.objects.create(set=category, callfunds=new_call, price=category.get_current_budget() / 4, designation=_("%(type)s - #%(num)d") % {'type': _('current'), 'num': num + 1})


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.getparam('status_filter', 1) == 0)
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.status == 0)
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


@ActionsManage.affect_grid(TITLE_PRINT, "images/print.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', 1) > 0)
@ActionsManage.affect_show(TITLE_PRINT, "images/print.png", close=CLOSE_NO, condition=lambda xfer: xfer.item.status in (1, 2))
@MenuManage.describ('condominium.change_callfunds')
class CallFundsPrint(XferPrintReporting):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Print call of funds")

    def items_callback(self):
        has_item = False
        for item in self.items:
            if item.status > 0:
                has_item = True
                yield item
        if not has_item:
            raise LucteriosException(IMPORTANT, _("No call of funds to print!"))


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', 1) == 0)
@MenuManage.describ('condominium.delete_callfunds')
class CallFundsDel(XferDelete):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Delete call of funds")


@ActionsManage.affect_transition("status", close=CLOSE_YES)
@MenuManage.describ('condominium.add_callfunds')
class CallFundsTransition(XferTransition):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.item.status == 0)
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.item.status == 0)
@MenuManage.describ('condominium.add_callfunds')
class CallDetailAddModify(XferAddEditor):
    icon = "callfunds.png"
    model = CallDetail
    field_id = 'calldetail'
    caption_add = _("Add detail of call")
    caption_modify = _("Modify detail of call")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.item.status == 0)
@MenuManage.describ('condominium.add_callfunds')
class CallDetailDel(XferDelete):
    icon = "callfunds.png"
    model = CallDetail
    field_id = 'calldetail'
    caption = _("Delete detail of call")
