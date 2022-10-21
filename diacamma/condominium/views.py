# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models.functions import Concat
from django.db.models import Q, Value

from lucterios.framework.xferadvance import TITLE_MODIFY, TITLE_ADD, TITLE_EDIT, TITLE_DELETE, TITLE_PRINT, TITLE_CANCEL, TITLE_OK, \
    TITLE_CREATE
from lucterios.framework.xferadvance import XferListEditor, XferShowEditor, XferAddEditor, XferDelete
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompDate, XferCompButton, XferCompImage, XferCompSelect, XferCompEdit, \
    XferCompGrid
from lucterios.framework.xfergraphic import XferContainerAcknowledge, \
    XferContainerCustom
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, WrapAction
from lucterios.framework.tools import SELECT_SINGLE, CLOSE_NO, FORMTYPE_REFRESH, FORMTYPE_MODAL, CLOSE_YES, SELECT_MULTI
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework import signal_and_lock
from lucterios.CORE.parameters import Params
from lucterios.CORE.xferprint import XferPrintAction, XferPrintReporting
from lucterios.CORE.models import Parameter
from lucterios.CORE.views import ObjectImport

from lucterios.contacts.models import Individual, LegalEntity, AbstractContact, CustomField
from lucterios.contacts.tools import ContactSelection

from diacamma.accounting.models import AccountThird, CostAccounting, FiscalYear, Third
from diacamma.accounting.tools import correct_accounting_code, get_amount_from_format_devise
from diacamma.payoff.models import PaymentMethod, Payoff, Supporting
from diacamma.payoff.views import PayoffAddModify, can_send_email

from diacamma.condominium.models import PropertyLot, Owner, Set, SetCost, convert_accounting, OwnerContact, generate_pdfreport, \
    LIST_DEFAULT_ACCOUNTS, DEFAULT_ACCOUNT_CURRENT, Payment, PropertyLotCustomField
from diacamma.condominium.views_classload import fill_params
from diacamma.condominium.system import current_system_condo


@MenuManage.describ('condominium.change_set', FORMTYPE_NOMODAL, 'condominium.manage', _('Manage of owners and property lots'))
class OwnerAndPropertyLotList(XferListEditor):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption = _("Owners and property lots")

    def get_items_from_filter(self):
        items = self.model.objects.annotate(completename=Concat('third__contact__individual__lastname', Value(' '), 'third__contact__individual__firstname')).filter(self.filter)
        sort_owner = self.getparam('GRID_ORDER%owner', '')
        sort_ownerbis = self.getparam('GRID_ORDER%owner+', '')
        self.params['GRID_ORDER%owner'] = ""
        if sort_owner != '':
            if sort_ownerbis.startswith('-'):
                sort_ownerbis = "+"
            else:
                sort_ownerbis = "-"
            self.params['GRID_ORDER%owner+'] = sort_ownerbis
        items = sorted(items, key=lambda t: str(t).lower(), reverse=sort_ownerbis.startswith('-'))
        res = QuerySet(model=Owner)
        res._result_cache = items
        return res

    def fillresponse_header(self):
        self.params['basic_model'] = 'condominium.PropertyLot'
        self.params['custom_editor_title'] = _('Secondary key')
        self.params['custom_type'] = CustomField.KIND_INTEGER
        self.params['args_min'] = 0
        self.params['args_max'] = 1_000_000_000
        self.new_tab(_("Owners"))
        contact_filter = self.getparam('filter', '')
        comp = XferCompEdit('filter')
        comp.set_value(contact_filter)
        comp.set_action(self.request, self.return_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        comp.set_location(0, 0, 2)
        comp.is_default = True
        comp.description = _('Filtrer by owner')
        self.add_component(comp)
        self.filter = Q()
        if contact_filter != "":
            q_legalentity = Q(third__contact__legalentity__name__icontains=contact_filter)
            q_individual = Q(completename__icontains=contact_filter)
            self.filter &= (q_legalentity | q_individual)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        if hasattr(settings, "DIACAMMA_MAXOWNER"):
            grid = self.get_components("owner")
            if getattr(settings, "DIACAMMA_MAXOWNER") <= grid.nb_lines:
                grid.delete_action("diacamma.condominium/ownerAdd")
                lbl = XferCompLabelForm("limit_activity")
                lbl.set_color('red')
                lbl.set_value_as_headername(_("You can't have more than %s owners!") % settings.DIACAMMA_MAXOWNER)
                lbl.set_location(grid.col, self.get_max_row() + 1)
                self.add_component(lbl)
        self.new_tab(_("Property lots"))
        self.fill_grid(0, PropertyLot, 'propertylot', PropertyLot.objects.all())
        grid = self.get_components('propertylot')
        lbl = XferCompLabelForm("total_lot")
        lbl.set_location(0, 5)
        lbl.set_value(_("Total of general lot parts: %d") % PropertyLot.get_total_part())
        self.add_component(lbl)
        for cf_name, cf_model in CustomField.get_fields(PropertyLot):
            lbl = XferCompLabelForm("total_%s" % cf_name)
            lbl.set_location(0, self.get_max_row() + 1)
            lbl.set_value(_("Total of secondary key '%(name)s': %(value)d") % {'name': cf_model.name, 'value': PropertyLotCustomField.get_total_part(cf_model)})
            self.add_component(lbl)
        btn = XferCompButton("btnimport")
        btn.set_location(1, 5, 1, 2)
        btn.set_action(self.request, PropertyLotImport.get_action(), close=CLOSE_NO, params={'step': 0})
        self.add_component(btn)

        self.new_tab(_("Secondary keys"))
        self.fill_grid(0, CustomField, "custom_field", CustomField.get_filter(PropertyLot))
        grid_custom = self.get_components('custom_field')
        grid_custom.delete_header('model_title')
        grid_custom.delete_header('kind_txt')


@ActionsManage.affect_list(TITLE_PRINT, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('condominium.change_set')
class OwnerAndPropertyLotPrint(XferPrintAction):
    caption = _("Print owners and property lots")
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    action_class = OwnerAndPropertyLotList
    with_text_export = True


@ActionsManage.affect_grid(TITLE_CREATE, "images/new.png")
@MenuManage.describ('condominium.add_owner')
class OwnerAdd(XferAddEditor):
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption_add = _("Add owner")
    redirect_to_show = False

    def fillresponse(self):
        if (self.item.id is None) and hasattr(settings, "DIACAMMA_MAXOWNER"):
            nb_owner = len(Owner.objects.all())
            if getattr(settings, "DIACAMMA_MAXOWNER") <= nb_owner:
                raise LucteriosException(IMPORTANT, _("You can't have more than %s owners!") % settings.DIACAMMA_MAXOWNER)
        XferAddEditor.fillresponse(self)


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
        current_year = XferCompLabelForm("current_year")
        current_year.set_italic()
        current_year.set_value_center(self.item.current_year)
        current_year.set_location(1, 0, 4)
        self.add_component(current_year)

        date_init = XferCompDate("begin_date")
        date_init.set_needed(True)
        date_init.set_value(self.item.date_begin)
        date_init.set_location(1, 1)
        date_init.description = _('initial date')
        date_init.set_action(self.request, self.return_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_init)
        date_end = XferCompDate("end_date")
        date_end.set_needed(True)
        date_end.set_value(self.item.date_end)
        date_end.set_location(3, 1)
        date_end.description = _('current date')
        date_end.set_action(self.request, self.return_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_end)
        XferShowEditor.fillresponse(self)


@ActionsManage.affect_other(TITLE_ADD, "images/add.png")
@MenuManage.describ('condominium.add_owner')
class OwnerContactSave(XferAddEditor):
    icon = "condominium.png"
    model = OwnerContact
    field_id = 'ownercontact'
    caption_add = _("Add owner contact")
    caption_modify = _("Modify owner contact")
    redirect_to_show = None

    def fillresponse(self):
        contact_id = self.getparam(self.getparam('pkname'))
        self.params['contact'] = contact_id
        self.item.contact = AbstractContact.objects.get(id=contact_id)
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@MenuManage.describ('accounting.add_owner')
class OwnerContactAdd(ContactSelection):
    icon = "condominium.png"
    caption = _("Add owner contact")
    select_class = OwnerContactSave
    model = OwnerContact
    readonly = False
    methods_allowed = ('POST', 'PUT')

    def fillresponse(self):
        ContactSelection.fillresponse(self)
        grid = self.get_components(self.field_id)
        for action_idx in range(0, len(grid.actions)):
            if grid.actions[action_idx][0].icon_path.endswith('images/add.png'):
                params = grid.actions[action_idx][4]
                if params is None:
                    params = {}
                params['URL_TO_REDIRECT'] = self.select_class.url_text
                params['pkname'] = self.field_id
                grid.actions[action_idx] = (grid.actions[action_idx][0], grid.actions[action_idx][1], CLOSE_YES, grid.actions[action_idx][3], params)


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('condominium.add_owner')
class OwnerContactShow(XferContainerAcknowledge):
    caption = _("Show owner contact")
    icon = "condominium.png"
    model = OwnerContact
    field_id = 'ownercontact'

    def fillresponse(self):
        modal_name = self.item.contact.__class__.get_long_name()
        field_id = self.item.contact.__class__.__name__.lower()
        if field_id == 'legalentity':
            field_id = 'legal_entity'
        self.redirect_action(ActionsManage.get_action_url(modal_name, 'Show', self), close=CLOSE_NO,
                             params={field_id: str(self.item.contact.id)})


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('condominium.add_owner')
class OwnerContactDel(XferDelete):
    caption = _("Delete owner contact")
    icon = "condominium.png"
    model = OwnerContact
    field_id = 'ownercontact'


@ActionsManage.affect_other(_('load count'), 'images/show.png', close=CLOSE_NO)
@MenuManage.describ('payoff.add_owner')
class OwnerLoadCount(XferContainerCustom):
    caption = _("Load count of owner")
    icon = "condominium.png"
    model = Owner
    field_id = 'owner'

    def fillresponse(self, begin_date, end_date):
        self.item.set_dates(begin_date, end_date)
        date_init = XferCompDate("begin_date")
        date_init.set_needed(True)
        date_init.set_value(self.item.date_begin)
        date_init.set_location(1, 0)
        date_init.description = _('initial date')
        date_init.set_action(self.request, self.return_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_init)
        date_end = XferCompDate("end_date")
        date_end.set_needed(True)
        date_end.set_value(self.item.date_end)
        date_end.set_location(2, 0)
        date_end.description = _('current date')
        date_end.set_action(self.request, self.return_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_end)
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, 1, True, [((_('name'), 'third'),)])
        grid = XferCompGrid('loadcount')
        grid.set_model(self.item.loadcount_set.all(), None)
        grid.set_location(1, 2, 2)
        self.add_component(grid)

        self.add_action(WrapAction(_('Close'), 'images/close.png'))


@ActionsManage.affect_grid(TITLE_PRINT, "images/print.png", unique=SELECT_MULTI)
@ActionsManage.affect_show(TITLE_PRINT, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('condominium.change_owner')
class OwnerReport(XferPrintReporting):
    with_text_export = True
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    caption = _("Print owner")

    def items_callback(self):
        return self.items

    def get_print_name(self):
        if len(self.items) == 1:
            current_owner = self.items[0]
            return current_owner.get_document_filename()
        else:
            return str(self.caption)


@ActionsManage.affect_show(_("Payment"), "diacamma.payoff/images/payments.png", close=CLOSE_NO, condition=lambda xfer: xfer.item.payoff_have_payment() and (len(PaymentMethod.objects.all()) > 0))
@MenuManage.describ('condominium.change_owner')
class OwnerShowPayable(XferContainerAcknowledge):
    caption = _("Payment")
    icon = "owner.png"
    model = Owner
    field_id = 'owner'
    readonly = True
    methods_allowed = ('GET',)

    def fillresponse(self):
        self.redirect_action(ActionsManage.get_action_url('payoff.Supporting', 'Show', self),
                             close=CLOSE_NO, params={'item_name': self.field_id})


@ActionsManage.affect_grid(_("Send"), "lucterios.mailing/images/email.png", close=CLOSE_NO, unique=SELECT_MULTI, condition=lambda xfer, gridname='': can_send_email(xfer))
@ActionsManage.affect_show(_("Send"), "lucterios.mailing/images/email.png", close=CLOSE_NO, condition=lambda xfer: can_send_email(xfer))
@MenuManage.describ('condominium.add_owner')
class OwnerPayableEmail(XferContainerAcknowledge):
    caption = _("Send by email")
    icon = "owner.png"
    model = Owner
    field_id = 'owner'

    def fillresponse(self):
        self.redirect_action(ActionsManage.get_action_url('payoff.Supporting', 'Email', self),
                             close=CLOSE_NO, params={'item_name': self.field_id})


@ActionsManage.affect_grid(_('payoff'), 'images/add.png', close=CLOSE_NO)
@MenuManage.describ('payoff.add_payoff')
class PaymentMultiPay(XferContainerAcknowledge):
    caption = _("Multi-pay owner")
    icon = "set.png"
    model = Payment
    field_id = 'payments'

    def fillresponse(self, owner, begin_date, end_date):
        currentowner = Owner.objects.get(id=owner)
        currentowner.set_dates(begin_date, end_date)
        supportings = [str(currentowner.id)]
        for call_fund in currentowner.callfunds_set.filter(date__gte=currentowner.date_begin, date__lte=currentowner.date_end):
            if call_fund.supporting.get_total_rest_topay() > 0.0001:
                supportings.append(str(call_fund.supporting_id))
        self.redirect_action(PayoffAddModify.get_action("", ""), params={"supportings": ";".join(supportings), 'NO_REPARTITION': 'yes', 'repartition': "1"})


@ActionsManage.affect_grid(_('refund'), 'images/new.png', close=CLOSE_NO, condition=lambda xfer, gridname: xfer.item.get_total_payoff_waiting() > 0.001)
@MenuManage.describ('payoff.add_payoff')
class PaymentRefund(XferContainerAcknowledge):
    caption = _("Refund owner")
    icon = "set.png"
    model = Payment
    field_id = 'payments'

    class RefundSupporting(Supporting):

        def __init__(self, owner):
            Supporting.__init__(self, third=owner.third, is_revenu=False)
            self.owner = owner

        def __str__(self):
            return str(self.third)

        def get_total_rest_topay(self, ignore_payoff=-1):
            return max(0, self.owner.get_total_payoff_waiting())

        def get_max_payoff(self, ignore_payoff=-1):
            return 1000000

        class Meta(object):
            proxy = True

    def fillresponse(self, owner, begin_date, end_date):
        currentowner = Owner.objects.get(id=owner)
        currentowner.set_dates(begin_date, end_date)
        if self.getparam('SAVE') is None:
            dlg = self.create_custom(model=Payoff)
            dlg.item.supporting = self.RefundSupporting(currentowner)
            dlg.item.date = currentowner.default_date()
            dlg.params['supportings'] = ''
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0, 1, 6)
            dlg.add_component(img)
            dlg.fill_from_model(1, 0, False)
            dlg.add_action(self.return_action(TITLE_OK, 'images/ok.png'), params={"SAVE": "YES"})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            Payoff.multi_save([currentowner.id], -1 * self.getparam('amount', 0.0), self.getparam('mode', Payoff.MODE_CASH), '',
                              self.getparam('reference', ''), self.getparam('bank_account', None), self.getparam('date', currentowner.default_date()),
                              self.getparam('fee_bank', 0.0), Payoff.REPARTITION_BYDATE)


@ActionsManage.affect_grid(_('ventilate'), 'images/edit.png', close=CLOSE_NO)
@MenuManage.describ('payoff.add_payoff')
class PaymentVentilatePay(XferContainerAcknowledge):
    caption = _("Multi-pay owner")
    icon = "set.png"
    model = Payment
    field_id = 'payments'

    def fillresponse(self, owner, begin_date, end_date):
        currentowner = Owner.objects.get(id=owner)
        if self.confirme(_('Do you want to check ventilate payoff on calls of funds ?')):
            currentowner.ventilatePay(begin_date, end_date)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('condominium.delete_owner')
class PaymentDel(XferDelete):
    icon = "owner.png"
    model = Payment
    field_id = 'payments'
    caption = _("Delete payment")

    def _search_model(self):
        self.model = Payoff
        ids = self.getparam(self.field_id)
        if ids is None:
            raise LucteriosException(GRAVE, _("No selection"))
        ids = ids.split(';')
        self.items = Payoff.objects.filter(entry_id__in=ids).distinct()

    def fillresponse(self, owner, begin_date, end_date):
        XferDelete.fillresponse(self)
        if self.getparam("CONFIRME", "") != "":
            currentowner = Owner.objects.get(id=owner)
            currentowner.ventilatePay(begin_date, end_date)


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@MenuManage.describ('condominium.add_owner')
class PropertyLotAddModify(XferAddEditor):
    icon = "owner.png"
    model = PropertyLot
    field_id = 'propertylot'
    caption_add = _("Add property lot")
    caption_modify = _("Modify property lot")

    def fillresponse(self):
        if self.item.id is None:
            self.item.owner = Owner()
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('condominium.delete_owner')
class PropertyLotDel(XferDelete):
    icon = "owner.png"
    model = PropertyLot
    field_id = 'propertylot'
    caption = _("Delete property lot")


@ActionsManage.affect_other(_('Import'), "images/right.png")
@MenuManage.describ('condominium.add_owner')
class PropertyLotImport(ObjectImport):
    icon = "owner.png"
    model = PropertyLot
    caption = _("Property lot import")

    def get_select_models(self):
        return PropertyLot.get_select_contact_type(True)


def get_owners(request):
    contacts = []
    if not request.user.is_anonymous:
        for contact in Individual.objects.filter(user=request.user).distinct():
            contacts.append(contact.id)
        for contact in LegalEntity.objects.filter(responsability__individual__user=request.user).distinct():
            contacts.append(contact.id)
    return Owner.objects.filter(third__contact_id__in=contacts).distinct()


def current_owner(request):
    right = False
    if not request.user.is_anonymous:
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


@MenuManage.describ(current_owner)
class CurrentOwnePrint(OwnerReport):
    pass


@MenuManage.describ('CORE.add_parameter')
class CondominiumConvert(XferContainerAcknowledge):
    icon = "condominium.png"
    caption = _("Condominium conversion")

    def fill_third_convert(self, dlg):
        lbl = XferCompLabelForm('tle_third')
        lbl.set_value(_('How do want to convert owner third account?'))
        lbl.set_location(0, 0, 2)
        dlg.add_component(lbl)
        select_account = [('', None)]
        for num_account in LIST_DEFAULT_ACCOUNTS:
            owner_account = correct_accounting_code(Params.getvalue('condominium-default-owner-account%d' % num_account))
            select_account.append((owner_account, owner_account))
        row = 1
        for code_item in AccountThird.objects.filter(code__regex=r"^45[0-9a-zA-Z]*$", third__status=0).values_list('code').distinct():
            sel = XferCompSelect('code_' + code_item[0])
            sel.set_location(0, row)
            sel.description = code_item[0]
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
            year_list = ["{[i]} - %s{[/i]}" % year for year in FiscalYear.objects.filter(status__in=(FiscalYear.STATUS_BUILDING, FiscalYear.STATUS_RUNNING))]
            lab = XferCompLabelForm('info')
            lab.set_value(
                _("This conversion tool will change your account to respect French law about condominium.{[br/]}For the no-closed fiscal years:{[newline]}%s{[newline]}It will do:{[newline]} - To change accounting code for each owners.{[newline]} - To de-validate all your entity.{[br/]} - To delete all entity link to call of funds or expenses.{[br/]} - To de-archive call of funds or expenses.{[br/]} - To generate correct account for call of funds or expenses.{[br/]}{[center]}{[u]}{[b]}Warning: This action is  definitive.{[/b]}{[/u]}{[center]}") % 
                '{[br/]}'.join(year_list))
            lab.set_location(0, 1, 4)
            dlg.add_component(lab)
            dlg.new_tab(_("Third accounts"))
            self.fill_third_convert(dlg)
            dlg.new_tab(_("Parameters"))
            fill_params(dlg, True, True)
            dlg.add_action(self.return_action(TITLE_OK, 'images/ok.png'), modal=FORMTYPE_MODAL, close=CLOSE_YES, params={'CONVERT': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            Parameter.change_value('condominium-old-accounting', False)
            Params.clear()
            try:
                thirds_convert = self.get_thirds_convert()
                for set_cost in SetCost.objects.filter(year__status=2, cost_accounting__status=0):
                    set_cost.cost_accounting.is_protected = True
                    set_cost.cost_accounting.save()
                    if (set_cost.year.status == FiscalYear.STATUS_FINISHED) and (set_cost.cost_accounting.status == CostAccounting.STATUS_OPENED):
                        set_cost.cost_accounting.close()
                for owner in Owner.objects.all():
                    owner.check_account()
                for year in FiscalYear.objects.filter(status__in=(FiscalYear.STATUS_BUILDING, FiscalYear.STATUS_RUNNING)):
                    convert_accounting(year, thirds_convert)
            except BaseException:
                Params.clear()
                raise
            self.message(_("Data converted"))


@signal_and_lock.Signal.decorate('situation')
def situation_condo(xfer):
    if not hasattr(xfer, 'add_component'):
        return len(get_owners(xfer)) == 1
    else:
        owners = get_owners(xfer.request)
        if len(owners) == 1:
            row = xfer.get_max_row() + 1
            lab = XferCompLabelForm('condotitle')
            lab.set_value_as_infocenter(_('Condominium'))
            lab.set_location(0, row, 4)
            xfer.add_component(lab)
            lab = XferCompLabelForm('condoowner')
            lab.set_value(_('You are a owner'))
            lab.set_location(0, row + 1, 2)
            xfer.add_component(lab)
            part_description = []
            for part in owners[0].partition_set.filter(set__is_active=True):
                part_description.append("{[b]}%s{[/b]} %d (%s)" % (part.set, part.value, part.ratio))
            lab = XferCompLabelForm('part')
            lab.set_value("{[br/]}".join(part_description))
            lab.set_location(0, row + 2, 4)
            xfer.add_component(lab)

            lab = XferCompLabelForm('balancetitle')
            lab.set_value_as_header(_("Your owner's balance"))
            lab.set_location(0, row + 3)
            xfer.add_component(lab)
            lab = XferCompLabelForm('balance')
            lab.set_value(owners[0].third.total)
            lab.set_location(1, row + 3, 3)
            xfer.add_component(lab)

            lab = XferCompLabelForm('condosep')
            lab.set_value_as_infocenter("{[hr/]}")
            lab.set_location(0, row + 5, 4)
            xfer.add_component(lab)
            return True
        else:
            return False


@signal_and_lock.Signal.decorate('summary')
def summary_condo(xfer):
    if not hasattr(xfer, 'add_component'):
        return WrapAction.is_permission(xfer, 'condominium.change_set')
    else:
        if WrapAction.is_permission(xfer.request, 'condominium.change_set'):
            row = xfer.get_max_row() + 1
            lab = XferCompLabelForm('condotitle')
            lab.set_value_as_infocenter(_('Condominium'))
            lab.set_location(0, row, 4)
            xfer.add_component(lab)
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
            if hasattr(settings, "DIACAMMA_MAXOWNER"):
                lbl = XferCompLabelForm("limit_owner")
                lbl.set_value(_('limitation: %d owners allowed') % getattr(settings, "DIACAMMA_MAXOWNER"))
                lbl.set_italic()
                lbl.set_location(0, row + 4, 4)
                xfer.add_component(lbl)
            row = xfer.get_max_row() + 1
            lab = XferCompLabelForm('condosep')
            lab.set_value_as_infocenter("{[hr/]}")
            lab.set_location(0, row, 4)
            xfer.add_component(lab)
            return True
        else:
            return False


@signal_and_lock.Signal.decorate('post_merge')
def post_merge_condo(item):
    from django.db.models import Count
    if isinstance(item, Third):
        owner_list = Owner.objects.filter(third=item).order_by('id')
        main_owner = owner_list.first()
        if main_owner is not None:
            main_owner.merge_objects(list(owner_list)[1:])
            part_set_list = []
            for ident in main_owner.partition_set.values('set').annotate(Count('id')).values('set').order_by().filter(id__count__gt=1):
                part_set_list.append(ident['set'])
            for set_id in part_set_list:
                part_list = main_owner.partition_set.filter(set_id=set_id).order_by('id')
                main_part = part_list.first()
                if main_part is not None:
                    for part_item in list(part_list)[1:]:
                        main_part.value += part_item.value
                        part_item.delete()
                    main_part.save()


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


@signal_and_lock.Signal.decorate('reportlastyear')
def reportlastyear_condo(xfer):
    xfer.params['import_result'] = 'False'


@signal_and_lock.Signal.decorate('reportlastyear_after')
def reportlastyear_after_condo(xfer):
    Owner.ventilate_pay_all()


@signal_and_lock.Signal.decorate('begin_year')
def beginyear_condo(xfer):
    xfer.params['with_profit'] = 'False'


@signal_and_lock.Signal.decorate('finalize_year')
def finalizeyear_condo(xfer):
    year = FiscalYear.get_current(xfer.getparam('year'))
    if year is not None:
        ventilate = xfer.getparam("ventilate", 0)
        if xfer.observer_name == "core.custom":
            if year.check_to_close() > 0:
                raise LucteriosException(IMPORTANT, _("This fiscal year has entries not closed!"))
            result = year.total_revenue - year.total_expense
            if abs(result) > 0.001:
                row = xfer.get_max_row() + 1
                lbl = XferCompLabelForm('title_condo')
                lbl.set_value(_('This fiscal year has a result no null equals to %s.') % get_amount_from_format_devise(result, 7))
                lbl.set_location(0, row, 2)
                xfer.add_component(lbl)
                lbl = XferCompLabelForm('question_condo')
                lbl.set_value(_('Where do you want to ventilate this amount?'))
                lbl.set_location(0, row + 1)
                xfer.add_component(lbl)
                sel_cmpt = [('0', _("For each owner"))]
                for account in year.chartsaccount_set.filter(type_of_account=2).order_by('code'):
                    sel_cmpt.append((account.id, str(account)))
                sel = XferCompSelect("ventilate")
                sel.set_select(sel_cmpt)
                sel.set_value(ventilate)
                sel.set_location(1, row + 1)
                xfer.add_component(sel)
        elif xfer.observer_name == "core.acknowledge":
            Owner.ventilate_pay_all(year.begin, year.end)
            for set_cost in year.setcost_set.filter(year=year, set__is_active=True, set__type_load=0):
                if ventilate == 0:
                    current_system_condo().ventilate_costaccounting(year, set_cost.set, set_cost.cost_accounting, DEFAULT_ACCOUNT_CURRENT, Params.getvalue("condominium-current-revenue-account"))
                set_cost.cost_accounting.close()
            current_system_condo().ventilate_result(year, ventilate)


@signal_and_lock.Signal.decorate('finalize_year_after')
def finalize_year_after_condo(xfer):
    year = FiscalYear.get_current(xfer.getparam('year'))
    if year is not None:
        year.set_context(xfer)
        generate_pdfreport(year)
