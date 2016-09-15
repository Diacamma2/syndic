# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.utils import six

from lucterios.framework.xferadvance import TITLE_MODIFY, TITLE_ADD, TITLE_EDIT, TITLE_DELETE, TITLE_PRINT,\
    TITLE_CANCEL, TITLE_OK
from lucterios.framework.xferadvance import XferListEditor, XferShowEditor, XferAddEditor, XferDelete
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompDate, XferCompGrid, XferCompButton,\
    XferCompImage, XferCompSelect
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, WrapAction
from lucterios.framework.tools import SELECT_SINGLE, CLOSE_NO, FORMTYPE_REFRESH, FORMTYPE_MODAL, CLOSE_YES, SELECT_MULTI
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock
from lucterios.CORE.xferprint import XferPrintAction, XferPrintReporting

from lucterios.contacts.models import Individual, LegalEntity

from diacamma.condominium.models import PropertyLot, Owner, Set, CallFunds,\
    Expense
from lucterios.framework.xfergraphic import XferContainerCustom,\
    XferContainerAcknowledge
from lucterios.CORE.parameters import Params
from diacamma.condominium.views_classload import fill_params
from diacamma.accounting.models import ChartsAccount, AccountThird, FiscalYear
from diacamma.payoff.models import Payoff
from lucterios.CORE.models import Parameter
from diacamma.accounting.tools import correct_accounting_code


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


@MenuManage.describ('CORE.change_parameter')
class CondominiumConvert(XferContainerAcknowledge):
    icon = "condominium.png"
    caption = _("Condominium conversion")

    def fill_third_convert(self, dlg):
        lbl = XferCompLabelForm('tle_third')
        lbl.set_value(_('How do want to convert owner third account?'))
        lbl.set_location(0, 0, 2)
        dlg.add_component(lbl)
        select_account = [('', None)]
        for num_account in range(1, 5):
            owner_account = correct_accounting_code(Params.getvalue('condominium-default-owner-account%d' % num_account))
            select_account.append((owner_account, owner_account))
        row = 1
        for code_item in AccountThird.objects.filter(code__regex=r"^45[0-9a-zA-Z]*$", third__status=0).values_list('code').distinct():
            lbl = XferCompLabelForm('lbl_code_' + code_item[0])
            lbl.set_value_as_name(code_item[0])
            lbl.set_location(0, row)
            dlg.add_component(lbl)
            sel = XferCompSelect('code_' + code_item[0])
            sel.set_location(1, row)
            sel.set_value(dlg.getparam('code_' + code_item[0], ""))
            sel.set_select(select_account)
            dlg.add_component(sel)
            row += 1

    def get_thirds_convert(self):
        thirds_convert = {}
        for param_name, param_val in self.params.items():
            if param_name.startswith('code_') and (param_val != ''):
                thirds_convert[param_name[5:]] = param_val
        return thirds_convert

    def fillresponse(self):
        if self.getparam("CONVERT") is None:
            dlg = self.create_custom()
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0)
            dlg.add_component(lbl)
            year_list = ["{[i]} - %s{[/i]}" % year for year in FiscalYear.objects.filter(status__lt=2)]
            lab = XferCompLabelForm('info')
            lab.set_value(
                _("This conversion tool will change your account to respect French law about condominium.{[br/]}For the no-closed fiscal years:{[newline]}%s{[newline]}It will do:{[newline]} - To change accounting code for each owners.{[newline]} - To de-validate all your entity.{[br/]} - To delete all entity link to call of funds or expenses.{[br/]} - To de-archive call of funds or expenses.{[br/]} - To generate correct account for call of funds or expenses.{[br/]}{[center]}{[u]}{[b]}Warning: This action is  definitive.{[/b]}{[/u]}{[center]}") % '{[br/]}'.join(year_list))
            lab.set_location(0, 1, 4)
            dlg.add_component(lab)
            dlg.new_tab(_("Third accounts"))
            self.fill_third_convert(dlg)
            dlg.new_tab(_("Parameters"))
            fill_params(dlg, True, True)
            dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), modal=FORMTYPE_MODAL, close=CLOSE_YES, params={'CONVERT': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            Parameter.change_value('condominium-old-accounting', False)
            Params.clear()
            thirds_convert = self.get_thirds_convert()
            for owner in Owner.objects.all():
                for num_account in range(1, 5):
                    AccountThird.objects.create(third=owner.third,
                                                code=correct_accounting_code(Params.getvalue("condominium-default-owner-account%d" % num_account)))
            for year in FiscalYear.objects.filter(status__lt=2):
                year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account1')),
                                              'Copropriétaire - budget prévisionnel')
                year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account2')),
                                              'Copropriétaire - travaux et opération exceptionnelles')
                year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account3')),
                                              'Copropriétaire - avances')
                year.getorcreate_chartaccount(correct_accounting_code(Params.getvalue('condominium-default-owner-account4')),
                                              'Copropriétaire - emprunts')
                for code_init, code_target in thirds_convert.items():
                    try:
                        account_init = ChartsAccount.objects.get(year=year, code=code_init)
                        account_target = ChartsAccount.objects.get(year=year, code=code_target)
                        account_target.merge_objects(account_init)
                    except:
                        pass
                for entry in year.entryaccount_set.exclude(journal_id=1):
                    entry.num = None
                    entry.close = False
                    entry.date_entry = None
                    entry.save()
                for call_funds in CallFunds.objects.filter(status__gte=1, date__gte=year.begin, date__lte=year.end):
                    if (call_funds.status == 2):
                        call_funds.status = 1
                        call_funds.save()
                    call_funds.generate_accounting()
                for expense in Expense.objects.filter(status__gte=1, date__gte=year.begin, date__lte=year.end):
                    if (expense.status == 2):
                        expense.status = 1
                        expense.save()
                    expense.reedit()
                    expense.valid()
                for pay_off in Payoff.objects.filter(date__gte=year.begin, date__lte=year.end):
                    pay_off.save()
            self.message(_("Data converted"))


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
        if Params.getvalue("condominium-old-accounting"):
            lab = XferCompLabelForm('condoconvinfo')
            lab.set_value_as_header(_("Your condominium account is not in respect of French law{[newline]}An conversion is necessary."))
            lab.set_color('red')
            lab.set_location(0, row + 2, 4)
            xfer.add_component(lab)
            btn = XferCompButton('condoconv')
            btn.set_location(0, row + 3, 4)
            btn.set_action(xfer.request, CondominiumConvert.get_action(_('Convertion ...'), ""), close=CLOSE_NO)
            xfer.add_component(btn)
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
            xfer.filltab_from_model(0, 1, True, Owner.get_show_fields_in_third())
            xfer.item = old_item
            btn = XferCompButton('condobtn')
            btn.set_location(0, 5, 2)
            btn.set_action(xfer.request, OwnerShow.get_action(TITLE_EDIT, 'images/edit.png'),
                           close=CLOSE_NO, modal=FORMTYPE_MODAL, params={'owner': owner.id})
            xfer.add_component(btn)
        except ObjectDoesNotExist:
            pass


@signal_and_lock.Signal.decorate('finalize_year')
def finalizeyear_condo(year):
    pass
