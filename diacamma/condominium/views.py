# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.utils import six

from lucterios.framework.xferadvance import TITLE_MODIFY, TITLE_ADD, TITLE_EDIT, TITLE_DELETE, TITLE_PRINT
from lucterios.framework.xferadvance import XferListEditor, XferShowEditor, XferAddEditor, XferDelete
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompDate, XferCompGrid, XferCompButton
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, WrapAction
from lucterios.framework.tools import SELECT_SINGLE, CLOSE_NO, FORMTYPE_REFRESH, FORMTYPE_MODAL, CLOSE_YES, SELECT_MULTI
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock
from lucterios.CORE.xferprint import XferPrintAction, XferPrintReporting

from lucterios.contacts.models import Individual, LegalEntity

from diacamma.condominium.models import PropertyLot, Owner, Set


@MenuManage.describ('condominium.change_set', FORMTYPE_NOMODAL, 'condominium', _('Manage of owners and property lots'))
class OwnerAndPropertyLotList(XferListEditor):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption = _("Owners and property lots")

    def fillresponse_header(self):
        self.new_tab(_("Owners"))

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.new_tab(_("Property lots"))
        self.fill_grid(self.get_max_row(), PropertyLot, 'propertylot', PropertyLot.objects.all())
        lbl_nb = self.get_components('nb_propertylot')
        lbl_nb.colspan = 1
        lbl = XferCompLabelForm("total_lot")
        lbl.set_location(lbl_nb.col + 1, lbl_nb.row)
        lbl.set_value(_("Total of lot parts: %d") % PropertyLot.get_total_part())
        self.add_component(lbl)


@ActionsManage.affect_list(TITLE_PRINT, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('condominium.change_set')
class OwnerAndPropertyLotPrint(XferPrintAction):
    caption = _("Print owners and property lots")
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    action_class = OwnerAndPropertyLotList
    with_text_export = True


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@MenuManage.describ('condominium.add_owner')
class OwnerAdd(XferAddEditor):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption_add = _("Add owner")
    redirect_to_show = False


@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES)
@MenuManage.describ('condominium.add_owner')
class OwnerModify(XferAddEditor):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption_modify = _("Modify owner")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('condominium.delete_owner')
class OwnerDel(XferDelete):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption = _("Delete owner")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('condominium.change_owner')
class OwnerShow(XferShowEditor):
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
        date_init.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_init)
        lbl = XferCompLabelForm('lbl_end_date')
        lbl.set_value_as_name(_('current date'))
        lbl.set_location(3, 0)
        self.add_component(lbl)
        date_end = XferCompDate("end_date")
        date_end.set_needed(True)
        date_end.set_value(self.item.date_end)
        date_end.set_location(4, 0)
        date_end.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_end)

        XferShowEditor.fillresponse(self)
        self.add_action(ActionsManage.get_action_url('payoff.Supporting', 'Show', self),
                        close=CLOSE_NO, params={'item_name': self.field_id}, pos_act=0)
        self.add_action(ActionsManage.get_action_url('payoff.Supporting', 'Email', self),
                        close=CLOSE_NO, params={'item_name': self.field_id}, pos_act=0)


@ActionsManage.affect_show(TITLE_PRINT, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('condominium.change_owner')
class OwnerReport(XferPrintReporting):
    with_text_export = True
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption = _("Print owner")

    def get_print_name(self):
        if len(self.items) == 1:
            current_owner = self.items[0]
            return current_owner.get_document_filename()
        else:
            return six.text_type(self.caption)


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@MenuManage.describ('condominium.add_owner')
class PropertyLotAddModify(XferAddEditor):
    icon = "owner.png"
    model = PropertyLot
    field_id = 'propertylot'
    caption_add = _("Add property lot")
    caption_modify = _("Modify property lot")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('condominium.delete_owner')
class PropertyLotDel(XferDelete):
    icon = "owner.png"
    model = PropertyLot
    field_id = 'propertylot'
    caption = _("Delete property lot")


def get_owners(request):
    contacts = []
    if not request.user.is_anonymous():
        for contact in Individual.objects.filter(user=request.user):
            contacts.append(contact.id)
        for contact in LegalEntity.objects.filter(responsability__individual__user=request.user):
            contacts.append(contact.id)
    return Owner.objects.filter(third__contact_id__in=contacts)


def current_owner(request):
    right = False
    if not request.user.is_anonymous():
        right = len(get_owners(request)) == 1
    return right


@MenuManage.describ(current_owner, FORMTYPE_MODAL, 'core.general', _('View situation of your condominium.'))
class CurrentOwneShow(OwnerShow):
    caption = _("Your condominium")

    def fillresponse(self, begin_date, end_date):
        owners = get_owners(self.request)
        if len(owners) != 1:
            raise LucteriosException(IMPORTANT, _('Bad access!'))
        self.item = owners[0]
        self.params['owner'] = self.item.id
        OwnerShow.fillresponse(self, begin_date, end_date)
        self.add_action(CurrentOwnePrint.get_action(TITLE_PRINT, "images/print.png"), close=CLOSE_NO, pos_act=0)


@MenuManage.describ(None)
class CurrentOwnePrint(OwnerReport):
    pass


@signal_and_lock.Signal.decorate('summary')
def summary_condo(xfer):
    is_right = WrapAction.is_permission(xfer.request, 'condominium.change_set')
    owners = get_owners(xfer.request)
    if is_right or (len(owners) == 1):
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('condotitle')
        lab.set_value_as_infocenter(_('Condominium'))
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
    if len(owners) == 1:
        lab = XferCompLabelForm('condoowner')
        lab.set_value(_('You are a owner'))
        lab.set_location(0, row + 1, 2)
        xfer.add_component(lab)
        grid = XferCompGrid("part")
        grid.set_model(owners[0].partition_set.all(), ["set", "value", (_("ratio"), 'ratio')])
        grid.set_location(0, row + 2, 4)
        grid.set_size(200, 500)
        xfer.add_component(grid)
    if is_right:
        row = xfer.get_max_row() + 1
        nb_set = len(Set.objects.filter(is_active=True))
        nb_owner = len(Owner.objects.all())
        lab = XferCompLabelForm('condoinfo')
        lab.set_value_as_header(_("There are %(set)d classes of loads for %(owner)d owners") % {'set': nb_set, 'owner': nb_owner})
        lab.set_location(0, row + 1, 4)
        xfer.add_component(lab)
    if is_right or (len(owners) == 1):
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('condosep')
        lab.set_value_as_infocenter("{[hr/]}")
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
        return True
    else:
        return False


@signal_and_lock.Signal.decorate('third_addon')
def thirdaddon_condo(item, xfer):
    if WrapAction.is_permission(xfer.request, 'condominium.change_set'):
        try:
            owner = Owner.objects.get(third=item)
            xfer.new_tab(_('Condominium'))
            old_item = xfer.item
            xfer.item = owner
            fields = [((_('initial state'), 'total_initial'),), ((_('total call for funds'), 'total_call'),),
                      ((_('total estimate'), 'total_estimate'),)]
            xfer.filltab_from_model(0, 1, True, fields)
            xfer.item = old_item
            btn = XferCompButton('condobtn')
            btn.set_location(0, 5, 2)
            btn.set_action(xfer.request, OwnerShow.get_action(TITLE_EDIT, 'images/edit.png'),
                           close=CLOSE_NO, modal=FORMTYPE_MODAL, params={'owner': owner.id})
            xfer.add_component(btn)
        except ObjectDoesNotExist:
            pass
