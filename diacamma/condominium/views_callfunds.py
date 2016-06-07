# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage,\
    FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE, CLOSE_YES, SELECT_MULTI
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.error import LucteriosException, IMPORTANT

from lucterios.CORE.xferprint import XferPrintReporting

from diacamma.condominium.models import CallFunds, CallDetail


@ActionsManage.affect('CallFunds', 'list')
@MenuManage.describ('condominium.change_callfunds', FORMTYPE_NOMODAL, 'condominium', _('Manage of calls of funds'))
class CallFundsList(XferListEditor):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("calls of funds")

    def fillresponse_header(self):
        status_filter = self.getparam('status_filter', 1)
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
        edt.set_action(self.request, self.get_action(),
                       {'modal': FORMTYPE_REFRESH, 'close': CLOSE_NO})
        self.add_component(edt)
        self.filter = Q(status=status_filter)
        if status_filter > 0:
            self.action_grid = [
                ('show', _("Edit"), "images/show.png", SELECT_SINGLE)]
            self.action_grid.append(
                ('printcall', _("Print"), "images/print.png", SELECT_MULTI))
        if status_filter == 1:
            self.action_grid.append(
                ('close', _("Closed"), "images/ok.png", SELECT_SINGLE))


@ActionsManage.affect('CallFunds', 'modify', 'add')
@MenuManage.describ('condominium.add_callfunds')
class CallFundsAddModify(XferAddEditor):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption_add = _("Add call of funds")
    caption_modify = _("Modify call of funds")


@ActionsManage.affect('CallFunds', 'show')
@MenuManage.describ('condominium.change_callfunds')
class CallFundsShow(XferShowEditor):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Show call of funds")

    def fillresponse(self):
        if (self.item.status == 0):
            self.action_list.insert(
                0, ('valid', _("Valid"), "images/ok.png", CLOSE_YES))
        elif self.item.status == 1:
            self.action_list.insert(
                0, ('close', _("Closed"), "images/ok.png", CLOSE_NO))
        if self.item.status in (1, 2):
            self.action_list.insert(0,
                                    ('printcall', _("Print"), "images/print.png", CLOSE_NO))
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('CallFunds', 'printcall')
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
            raise LucteriosException(
                IMPORTANT, _("No call of funds to print!"))


@ActionsManage.affect('CallFunds', 'delete')
@MenuManage.describ('condominium.delete_callfunds')
class CallFundsDel(XferDelete):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Delete call of funds")


@ActionsManage.affect('CallFunds', 'valid')
@MenuManage.describ('condominium.add_callfunds')
class CallFundsValid(XferContainerAcknowledge):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Valid call of funds")

    def fillresponse(self):
        if (self.item.status == 0) and self.confirme(_("Do you want validate this call of funds?")):
            self.item.valid()


@ActionsManage.affect('CallFunds', 'close')
@MenuManage.describ('condominium.add_callfunds')
class CallFundsClose(XferContainerAcknowledge):
    icon = "callfunds.png"
    model = CallFunds
    field_id = 'callfunds'
    caption = _("Close call of funds")

    def fillresponse(self):
        if (self.item.status == 1) and self.confirme(_("Do you want close '%s'?") % self.item):
            self.item.close()


@ActionsManage.affect('CallDetail', 'edit', 'add')
@MenuManage.describ('condominium.add_callfunds')
class CallDetailAddModify(XferAddEditor):
    icon = "callfunds.png"
    model = CallDetail
    field_id = 'calldetail'
    caption_add = _("Add detail of call")
    caption_modify = _("Modify detail of call")


@ActionsManage.affect('CallDetail', 'delete')
@MenuManage.describ('condominium.add_callfunds')
class CallDetailDel(XferDelete):
    icon = "callfunds.png"
    model = CallDetail
    field_id = 'calldetail'
    caption = _("Delete detail of call")
