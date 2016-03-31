# -*- coding: utf-8 -*-
'''
diacamma.condominium views package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
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
from django.core.exceptions import ObjectDoesNotExist

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage,\
    FORMTYPE_MODAL, CLOSE_NO, FORMTYPE_REFRESH, WrapAction, get_icon_path
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage,\
    XferCompButton, XferCompDate
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework import signal_and_lock
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.CORE.xferprint import XferPrintAction, XferPrintReporting

from diacamma.accounting.tools import correct_accounting_code
from diacamma.condominium.models import Set, Partition, Owner, ExpenseDetail


@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'contact.conf', _('Management of parameters of condominium'))
class CondominiumConf(XferContainerCustom):
    icon = "condominium.png"
    caption = _("Condominium configuration")

    def fillresponse(self):
        param_lists = [
            'condominium-frequency', 'condominium-default-owner-account']
        Params.fill(self, param_lists, 1, 1)
        btn = XferCompButton('editparam')
        btn.set_location(1, self.get_max_row() + 1, 2, 1)
        btn.set_action(self.request, ParamEdit.get_action(
            _('Modify'), 'images/edit.png'), {'close': 0, 'params': {'params': param_lists}})
        self.add_component(btn)


MenuManage.add_sub("condominium", "core.general", "diacamma.condominium/images/condominium.png",
                   _("condominium"), _("Manage of condominium"), 30)


@ActionsManage.affect('Set', 'list')
@MenuManage.describ('condominium.change_set', FORMTYPE_NOMODAL, 'condominium', _('Manage of sets and owners'))
class SetOwnerList(XferListEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("sets and owners")

    def fillownerlist(self):
        row = self.get_max_row()
        img = XferCompImage('imgowner')
        img.set_value(
            get_icon_path(icon_path="diacamma.condominium/images/owner.png"))
        img.set_location(0, row + 1)
        self.add_component(img)
        lbl = XferCompLabelForm('titleowner')
        lbl.set_value_as_title(_("owner"))
        lbl.set_location(1, row + 1)
        self.add_component(lbl)
        self.fill_grid(self.get_max_row(), Owner, "owner", Owner.objects.all())

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.fillownerlist()
        self.actions = []
        self.add_action(SetOwnerPrint.get_action(
            _("Print"), "images/print.png"), {'close': CLOSE_NO, 'params': {'classname': self.__class__.__name__}})
        self.add_action(WrapAction(_('Close'), 'images/close.png'), {})


@MenuManage.describ('condominium.change_set')
class SetOwnerPrint(XferPrintAction):
    caption = _("Print sets and owners")
    icon = "set.png"
    model = Set
    field_id = 'set'
    action_class = SetOwnerList
    with_text_export = True


@ActionsManage.affect('Set', 'modify', 'add')
@MenuManage.describ('condominium.add_set')
class SetAddModify(XferAddEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption_add = _("Add set")
    caption_modify = _("Modify set")
    redirect_to_show = False


@ActionsManage.affect('Set', 'show')
@MenuManage.describ('condominium.change_set')
class SetShow(XferShowEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Show set")


@ActionsManage.affect('Set', 'delete')
@MenuManage.describ('condominium.delete_set')
class SetDel(XferDelete):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Delete set")


@ActionsManage.affect('Partition', 'edit')
@MenuManage.describ('condominium.add_set')
class PartitionAddModify(XferAddEditor):
    icon = "set.png"
    model = Partition
    field_id = 'partition'
    caption_modify = _("Modify partition")


@ActionsManage.affect('Owner', 'add')
@MenuManage.describ('condominium.add_owner')
class OwnerAdd(XferAddEditor):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption_add = _("Add owner")
    redirect_to_show = False


@ActionsManage.affect('Owner', 'modify')
@MenuManage.describ('condominium.add_owner')
class OwnerModify(XferAddEditor):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption_modify = _("Modify owner")


@ActionsManage.affect('Owner', 'delete')
@MenuManage.describ('condominium.delete_owner')
class OwnerDel(XferDelete):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption = _("Delete owner")


@ActionsManage.affect('Owner', 'show')
@MenuManage.describ('condominium.change_owner')
class OwneShow(XferShowEditor):
    icon = "set.png"
    model = Owner
    field_id = 'owner'
    caption = _("Show owner")

    def fillresponse(self, begin_date, end_date):
        self.item.set_dates(begin_date, end_date)
        lbl = XferCompLabelForm('lbl_begin_date')
        lbl.set_value_as_name(_('initial date'))
        lbl.set_location(1, 0)
        self.add_component(lbl)
        date_init = XferCompDate("begin_date")
        date_init.set_needed(True)
        date_init.set_value(self.item.date_begin)
        date_init.set_location(2, 0)
        date_init.set_action(
            self.request, self.get_action(), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        self.add_component(date_init)
        lbl = XferCompLabelForm('lbl_end_date')
        lbl.set_value_as_name(_('current date'))
        lbl.set_location(3, 0)
        self.add_component(lbl)
        date_end = XferCompDate("end_date")
        date_end.set_needed(True)
        date_end.set_value(self.item.date_end)
        date_end.set_location(4, 0)
        date_end.set_action(
            self.request, self.get_action(), {'close': CLOSE_NO, 'modal': FORMTYPE_REFRESH})
        self.add_component(date_end)
        XferShowEditor.fillresponse(self)


@ActionsManage.affect('Owner', 'print')
@MenuManage.describ('condominium.change_owner')
class OwnerReport(XferPrintReporting):
    with_text_export = True
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption = _("Print owner")


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_condo(known_codes, accompt_returned):
    set_unknown = Set.objects.exclude(revenue_account__in=known_codes).values_list(
        'revenue_account', flat=True).distinct()
    param_unknown = Parameter.objects.filter(name='condominium-default-owner-account').exclude(
        value__in=known_codes).values_list('value', flat=True).distinct()
    comptenofound = ""
    if (len(set_unknown) > 0):
        comptenofound = _("set") + ":" + ",".join(set_unknown) + " "
    if (len(param_unknown) > 0):
        comptenofound += _("parameters") + ":" + ",".join(param_unknown)
    if comptenofound != "":
        accompt_returned.append(
            "- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Condominium'), comptenofound))
    return True


@signal_and_lock.Signal.decorate('summary')
def summary_condo(xfer):
    if WrapAction.is_permission(xfer.request, 'invoice.change_bill'):
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('condotitle')
        lab.set_value_as_infocenter(_('Condominium'))
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
        nb_set = len(Set.objects.all())
        nb_owner = len(Owner.objects.all())
        lab = XferCompLabelForm('condoinfo')
        lab.set_value_as_header(
            _("There are %(set)d sets for %(owner)d owners") % {'set': nb_set, 'owner': nb_owner})
        lab.set_location(0, row + 1, 4)
        xfer.add_component(lab)
        lab = XferCompLabelForm('condosep')
        lab.set_value_as_infocenter("{[hr/]}")
        lab.set_location(0, row + 2, 4)
        xfer.add_component(lab)


@signal_and_lock.Signal.decorate('third_addon')
def thirdaddon_condo(item, xfer):
    if WrapAction.is_permission(xfer.request, 'condominium.change_set'):
        try:
            owner = Owner.objects.get(third=item)
            xfer.new_tab(_('Condominium'))
            old_item = xfer.item
            xfer.item = owner
            fields = [((_('initial state'), 'total_initial'),), ((
                _('total call for funds'), 'total_call'),), ((_('total estimate'), 'total_estimate'),)]
            xfer.filltab_from_model(0, 1, True, fields)
            xfer.item = old_item
            btn = XferCompButton('condobtn')
            btn.set_location(0, 5, 2)
            btn.set_action(xfer.request, OwneShow.get_action(
                _("show"), 'images/edit.png'), {'close': CLOSE_NO, 'modal': FORMTYPE_MODAL, 'params': {'owner': owner.id}})
            xfer.add_component(btn)
        except ObjectDoesNotExist:
            pass


@signal_and_lock.Signal.decorate('param_change')
def paramchange_condominium(params):
    if 'accounting-sizecode' in params:
        for set_item in Set.objects.all():
            if set_item.revenue_account != correct_accounting_code(set_item.revenue_account):
                set_item.revenue_account = correct_accounting_code(
                    set_item.revenue_account)
                set_item.save()
        for exp_item in ExpenseDetail.objects.filter(expense__status=0):
            if exp_item.expense_account != correct_accounting_code(exp_item.expense_account):
                exp_item.expense_account = correct_accounting_code(
                    exp_item.expense_account)
                exp_item.save()
    if ('condominium-default-owner-account' in params) or ('accounting-sizecode' in params):
        Parameter.change_value('condominium-default-owner-account', correct_accounting_code(
            Params.getvalue('condominium-default-owner-account')))
        Params.clear()
