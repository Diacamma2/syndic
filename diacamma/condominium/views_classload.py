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
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, TITLE_MODIFY, TITLE_PRINT, TITLE_ADD, TITLE_DELETE, TITLE_EDIT,\
    TITLE_OK, TITLE_CANCEL, TITLE_CLOSE, TITLE_CREATE
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import ActionsManage, MenuManage, WrapAction, FORMTYPE_REFRESH, CLOSE_NO, SELECT_SINGLE
from lucterios.framework.tools import FORMTYPE_NOMODAL, FORMTYPE_MODAL, CLOSE_YES, SELECT_MULTI
from lucterios.framework.xfercomponents import XferCompButton, XferCompImage, XferCompLabelForm, XferCompCheck, XferCompSelect
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.CORE.xferprint import XferPrintAction

from diacamma.accounting.tools import correct_accounting_code,\
    get_amount_from_format_devise
from diacamma.accounting.models import CostAccounting, FiscalYear
from diacamma.accounting.views_budget import BudgetList
from diacamma.accounting.views_reports import CostAccountingIncomeStatement

from diacamma.condominium.models import Set, Partition, ExpenseDetail, Owner, PropertyLot, SetCost, OwnerLink,\
    RecoverableLoadRatio
from diacamma.condominium.system import clear_system_condo, current_system_condo


def fill_params(self, is_mini=False, new_params=False):
    system_condo = current_system_condo()
    param_lists = system_condo.get_config_params(new_params)
    Params.fill(self, param_lists, 1, self.get_max_row() + 1, nb_col=2)
    btn = XferCompButton('editparam')
    btn.set_location(1, self.get_max_row() + 1, 2, 1)
    btn.set_is_mini(is_mini)
    btn.set_action(self.request, ParamEdit.get_action(TITLE_MODIFY, 'images/edit.png'), close=CLOSE_NO,
                   params={'params': param_lists})
    self.add_component(btn)


@MenuManage.describ('CORE.add_parameter')
class CondominiumCheckOwner(XferContainerAcknowledge):
    icon = "owner.png"
    caption = _("Condominium check owner")

    def fillresponse(self):
        if self.confirme(_('Do you want to check account of owners?')):
            Owner.check_all_account()


@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'contact.conf', _('Management of parameters of condominium'))
class CondominiumConf(XferListEditor):
    icon = "condominium.png"
    caption = _("Condominium configuration")
    model = OwnerLink
    field_id = 'ownerlink'

    def fillresponse_header(self):
        self.new_tab(_('Parameters'))
        fill_params(self)
        btn = XferCompButton('checkowner')
        btn.set_location(3, self.get_max_row(), 2, 1)
        btn.set_action(self.request, CondominiumCheckOwner.get_action(_('check owner'), 'diacamma.condominium/images/owner.png'), close=CLOSE_NO)
        self.add_component(btn)
        self.new_tab(_('Links'))

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.new_tab(_('Recoverable loads'))
        self.fill_grid(self.get_max_row() + 1, RecoverableLoadRatio, 'recoverableloadratio', RecoverableLoadRatio.objects.all())


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@MenuManage.describ('CORE.add_parameter')
class OwnerLinkAddModify(XferAddEditor):
    icon = "condominium.png"
    model = OwnerLink
    field_id = 'ownerlink'
    caption_add = _("Add owner link")
    caption_modify = _("Modify owner link")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('CORE.add_parameter')
class OwnerLinkDel(XferDelete):
    caption = _("Delete owner link")
    icon = "condominium.png"
    model = OwnerLink
    field_id = 'ownerlink'

    def fillresponse(self):
        for sub_item in self.items:
            if sub_item.id in (OwnerLink.DEFAULT_LODGER, OwnerLink.DEFAULT_RENTAL_AGENCY):
                raise LucteriosException(IMPORTANT, _('Link not deletable !'))
        XferDelete.fillresponse(self)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@MenuManage.describ('CORE.add_parameter')
class RecoverableLoadRatioAddModify(XferAddEditor):
    icon = "condominium.png"
    model = RecoverableLoadRatio
    field_id = 'recoverableloadratio'
    caption_add = _("Add recoverable load ratio")
    caption_modify = _("Modify recoverable load ratio")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('CORE.add_parameter')
class RecoverableLoadRatioDel(XferDelete):
    caption = _("Delete recoverable load ratio")
    icon = "condominium.png"
    model = RecoverableLoadRatio
    field_id = 'recoverableloadratio'


MenuManage.add_sub("condominium", None, "diacamma.condominium/images/condominium.png",
                   _("Condominium"), _("Condominium tools"), 20)


MenuManage.add_sub("condominium.manage", "condominium", "diacamma.condominium/images/condominium.png",
                   _("Manage"), _("Manage of condominium"), 10)


@MenuManage.describ('condominium.change_set', FORMTYPE_NOMODAL, 'condominium.manage', _('Manage of class loads'))
class SetList(XferListEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Class loads")

    def fillresponse_header(self):
        if not self.getparam('show_inactive', False):
            self.filter = Q(is_active=True)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        chk = XferCompCheck('show_inactive')
        chk.set_value(self.getparam('show_inactive', False))
        chk.description = _('Show all class load')
        chk.set_location(0, self.get_max_row() + 1)
        chk.set_action(self.request, self.return_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(chk)


@ActionsManage.affect_list(TITLE_PRINT, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('condominium.change_set')
class SetPrint(XferPrintAction):
    caption = _("Print class loads")
    icon = "set.png"
    model = Set
    field_id = 'set'
    action_class = SetList
    with_text_export = True


@ActionsManage.affect_grid(TITLE_CREATE, "images/new.png")
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.is_active)
@MenuManage.describ('condominium.add_set')
class SetAddModify(XferAddEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption_add = _("Add class load")
    caption_modify = _("Modify class load")
    redirect_to_show = False


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('condominium.change_set')
class SetShow(XferShowEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Show class load")

    def fillresponse(self):
        XferShowEditor.fillresponse(self)
        grid_set = self.get_components('partition')
        if grid_set is not None:
            grid_set.delete_header('recovery_load')
        grid_set = self.get_components('partitionfill')
        if grid_set is not None:
            grid_set.delete_header('recovery_load')
        self.add_action(ClassCategoryBudget.get_action(), pos_act=0, close=CLOSE_NO)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('condominium.delete_set')
class SetDel(XferDelete):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Delete class load")


@ActionsManage.affect_show(_('Finished'), "images/down.png", condition=lambda xfer: xfer.item.is_active)
@MenuManage.describ('condominium.delete_set')
class SetClose(XferContainerAcknowledge):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Close class load")
    methods_allowed = ('DELETE', )

    def fillresponse(self, ventilate=False):
        msg = self.item.check_close()
        if msg is not None:
            if self.getparam('CLOSE') is None:
                dlg = self.create_custom(self.model)
                img = XferCompImage('img')
                img.set_value(self.icon_path())
                img.set_location(0, 0)
                dlg.add_component(img)
                lbl = XferCompLabelForm('title')
                lbl.set_value_as_title(self.caption)
                lbl.set_location(1, 0, 2)
                dlg.add_component(lbl)
                lbl = XferCompLabelForm('info')
                lbl.set_value(_('This class load has a difference of %s between those call of funds and those expenses.') % get_amount_from_format_devise(msg, 7))
                lbl.set_location(1, 1)
                dlg.add_component(lbl)
                lbl = XferCompCheck('ventilate')
                lbl.set_value(ventilate)
                lbl.set_location(1, 2)
                lbl.description = 'Do you want to ventilate this amount for each owner?'
                dlg.add_component(lbl)
                dlg.add_action(self.return_action(TITLE_OK, 'images/ok.png'), modal=FORMTYPE_MODAL, close=CLOSE_YES, params={'CLOSE': 'YES'})
                dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
            else:
                if self.item.type_load == Set.TYPELOAD_CURRENT:
                    self.item.close_current(ventilate)
                else:
                    self.item.close_exceptional(ventilate)
        elif self.confirme(_('Do you want to close this class load?')):
            if self.item.type_load == Set.TYPELOAD_CURRENT:
                self.item.close_current()
            else:
                self.item.close_exceptional()


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': isinstance(xfer.item, Set) and not xfer.item.is_link_to_lots and xfer.item.is_active)
@MenuManage.describ('condominium.add_set')
class PartitionAddModify(XferAddEditor):
    icon = "set.png"
    model = Partition
    field_id = 'partition'
    caption_modify = _("Modify partition")


@ActionsManage.affect_show(TITLE_EDIT, "images/show.png", condition=lambda xfer: xfer.item.is_link_to_lots and xfer.item.is_active)
@MenuManage.describ('condominium.add_set')
class SetAssociate(XferAddEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    redirect_to_show = False
    caption = _("Associate lots")

    def fillresponse(self):
        self.caption = self.caption
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, 0, True, ['name', 'type_load'])
        self.fill_from_model(1, 2, False, ['set_of_lots'])
        self.add_action(self.return_action(TITLE_OK, 'images/ok.png'), params={"SAVE": "YES"})
        self.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))


@ActionsManage.affect_show(_('Costs'), "images/right.png")
@MenuManage.describ('condominium.change_set')
class SetListCost(XferListEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Costs accounting of a class load")

    def fillresponse(self):
        current_year = FiscalYear.get_current()
        if self.item.type_load == Set.TYPELOAD_CURRENT:
            for year_item in FiscalYear.objects.filter(begin__gte=current_year.begin):
                costs = self.item.setcost_set.filter(year=year_item)
                if len(costs) == 0:
                    self.item.create_new_cost(year=year_item.id)

        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.item.name)
        lbl.set_location(1, 0)
        self.add_component(lbl)
        self.fill_grid(0, CostAccounting, 'costaccounting', CostAccounting.objects.filter(setcost__set=self.item).order_by('-setcost__year__begin'))
        grid = self.get_components('costaccounting')
        grid.delete_header("is_default")
        new_actions = []
        grid = self.get_components('costaccounting')
        for grid_action in grid.actions:
            if grid_action[0].icon_path.endswith('images/print.png'):
                new_actions.append(grid_action)
        grid.actions = new_actions
        grid.add_action(self.request, ClassCategoryBudget.get_action(), close=CLOSE_NO, unique=SELECT_SINGLE)
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@ActionsManage.affect_grid(_("Report"), 'images/print.png', unique=SELECT_SINGLE)
@MenuManage.describ('condominium.change_set')
class ClassCategoryCosts(XferContainerAcknowledge):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Report")
    readonly = True
    methods_allowed = ('GET', )

    def fillresponse(self):
        year_item = FiscalYear.get_current()
        if self.item.type_load == Set.TYPELOAD_CURRENT:
            if len(self.item.setcost_set.filter(year=year_item)) == 0:
                self.item.create_new_cost(year=year_item.id)
        cost_item = self.item.setcost_set.filter(year=year_item)[0]
        params = {'costaccounting': cost_item.cost_accounting.id}
        self.redirect_action(CostAccountingIncomeStatement.get_action(), close=CLOSE_YES, params=params)


@MenuManage.describ('accounting.change_budget')
class ClassCategoryBudget(XferContainerAcknowledge):
    icon = "diacamma.accounting/images/account.png"
    model = CostAccounting
    field_id = 'costaccounting'
    caption = _("Budget")
    readonly = True
    methods_allowed = ('GET', )

    def fillresponse(self):
        if (self.item.id is None) and (self.getparam('set') is not None):
            set_item = Set.objects.get(id=self.getparam('set', 0))
            self.item = set_item.current_cost_accounting
        params = {'cost_accounting': self.item.id, 'readonly': (self.item.status == CostAccounting.STATUS_CLOSED)}
        set_costs = SetCost.objects.filter(cost_accounting=self.item)
        if (len(set_costs) == 1) and (set_costs[0].year_id is not None):
            params['year'] = set_costs[0].year_id
        self.redirect_action(BudgetList.get_action(), close=CLOSE_YES, params=params)


@signal_and_lock.Signal.decorate('editbudget')
def editbudget_condo(xfer):
    if xfer.getparam('set') is not None:
        cost = xfer.getparam('cost_accounting')
        if cost is not None:
            set_item = Set.objects.get(id=xfer.getparam('set', 0))
            title_cost = xfer.get_components('title_cost')
            xfer.remove_component('title_year')
            year = xfer.getparam('year', 0)
            select_year = XferCompSelect('year')
            select_year.set_location(1, title_cost.row - 1)
            select_year.set_select_query(FiscalYear.objects.all())
            select_year.set_value(year)
            select_year.description = _('year')
            select_year.set_needed(set_item.type_load == Set.TYPELOAD_CURRENT)
            select_year.set_action(xfer.request, xfer.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
            xfer.add_component(select_year)
            btn = XferCompButton('confyear')
            btn.set_location(2, title_cost.row - 1)
            btn.set_action(xfer.request, ActionsManage.get_action_url(FiscalYear.get_long_name(), 'configuration', xfer), close=CLOSE_NO)
            btn.set_is_mini(True)
            xfer.add_component(btn)
            if year != 0:
                current_year = FiscalYear.get_current(year)
                xfer.params['readonly'] = str(current_year.status == FiscalYear.STATUS_FINISHED)
                if set_item.type_load == 0:
                    if len(set_item.setcost_set.filter(year=current_year)) == 0:
                        set_item.create_new_cost(year=current_year.id)
                    setcost_item = set_item.setcost_set.filter(year=current_year)[0]
                else:
                    setcost_item = set_item.setcost_set.filter(year=None)[0]
                cost_item = setcost_item.cost_accounting
                xfer.params['cost_accounting'] = cost_item.id
                title_cost.set_value("{[b]}%s{[/b]} : %s" % (_('cost accounting'), cost_item))
            else:
                year = None
                xfer.params['readonly'] = 'True'
                cost_item = CostAccounting.objects.get(id=cost)
            if (cost_item.status == CostAccounting.STATUS_OPENED) and not xfer.getparam('readonly', False):
                set_item.change_budget_product(cost_item, year)
    if xfer.getparam('type_of_account') is not None:
        xfer.params['readonly'] = 'True'
    return


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_condo(known_codes, accompt_returned):
    if Params.getvalue("condominium-old-accounting"):
        account_filter = Q(name='condominium-default-owner-account')
        set_unknown = Set.objects.exclude(revenue_account__in=known_codes).values_list('revenue_account', flat=True)
    else:
        account_filter = Q()
        for param_item in current_system_condo().get_config_params(True):
            account_filter |= Q(name=param_item)
        set_unknown = []
    param_unknown = Parameter.objects.filter(account_filter).exclude(value__in=known_codes).values_list('value', flat=True)
    comptenofound = ""
    if (len(set_unknown) > 0):
        comptenofound = _("set") + ":" + ",".join(set(set_unknown)) + " "
    param_unknown = list(param_unknown)
    if '0' in param_unknown:
        param_unknown.remove('0')
    if (len(param_unknown) > 0):
        comptenofound += _("parameters") + ":" + ",".join(set(param_unknown))
    if comptenofound != "":
        accompt_returned.append("- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Condominium'), comptenofound))
    return True


@signal_and_lock.Signal.decorate('param_change')
def paramchange_condominium(params):
    if 'accounting-sizecode' in params:
        for set_item in Set.objects.all():
            if set_item.revenue_account != correct_accounting_code(set_item.revenue_account):
                set_item.revenue_account = correct_accounting_code(set_item.revenue_account)
                set_item.save()
        for exp_item in ExpenseDetail.objects.filter(expense__status=0):
            if exp_item.expense_account != correct_accounting_code(exp_item.expense_account):
                exp_item.expense_account = correct_accounting_code(exp_item.expense_account)
                exp_item.save()
    accounts = ('condominium-default-owner-account', 'condominium-current-revenue-account',
                'condominium-default-owner-account1', 'condominium-default-owner-account2',
                'condominium-default-owner-account3', 'condominium-default-owner-account4',
                'condominium-default-owner-account5',
                'condominium-exceptional-revenue-account', 'condominium-fundforworks-revenue-account',
                'condominium-exceptional-reserve-account', 'condominium-advance-reserve-account',
                'condominium-fundforworks-reserve-account')
    for account_item in accounts:
        has_changed = False
        if (account_item in params) or ('accounting-sizecode' in params):
            Parameter.change_value(account_item, correct_accounting_code(Params.getvalue(account_item)))
            system_condo = current_system_condo()
            system_condo.owner_account_changed(account_item)
            has_changed = True
        if has_changed:
            Params.clear()
    if 'accounting-system' in params:
        clear_system_condo()
        system_condo = current_system_condo()
        system_condo.initialize_system()


@signal_and_lock.Signal.decorate('get_param_titles')
def paramtitles_condomium(names, titles):
    system_condo = current_system_condo()
    titles.update(system_condo.get_param_titles(names))


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_condominium(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("condominium_params", 35))
        wizard_ident.append(("condominium_owner", 45))
        wizard_ident.append(("condominium_lot", 46))
        wizard_ident.append(("condominium_classload", 47))
    elif (xfer is not None) and (wizard_ident == "condominium_params"):
        xfer.add_title(_("Diacamma condominium"), _("Condominium configuration"))
        fill_params(xfer, True)
    elif (xfer is not None) and (wizard_ident == "condominium_owner"):
        xfer.add_title(_("Diacamma condominium"), _("Owners"), _('Add owners of your condominium.'))
        xfer.fill_grid(xfer.get_max_row(), Owner, 'owner', Owner.objects.all())
    elif (xfer is not None) and (wizard_ident == "condominium_lot"):
        xfer.add_title(_("Diacamma condominium"), _("Property lots"), _('Define the lots for each owners.'))
        xfer.fill_grid(xfer.get_max_row(), PropertyLot, 'propertylot', PropertyLot.objects.all())
        lbl = XferCompLabelForm("total_lot")
        lbl.set_location(0, xfer.get_max_row() + 1)
        lbl.set_value(_("Total of lot parts: %d") % PropertyLot.get_total_part())
        xfer.add_component(lbl)
    elif (xfer is not None) and (wizard_ident == "condominium_classload"):
        xfer.add_title(_("Diacamma condominium"), _("Class loads"), _('Define the class loads of your condominium.'))
        xfer.fill_grid(xfer.get_max_row(), Set, 'set', Set.objects.all())
