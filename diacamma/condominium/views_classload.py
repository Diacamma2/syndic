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

from lucterios.framework.xferadvance import XferListEditor, TITLE_MODIFY, TITLE_PRINT, TITLE_ADD, TITLE_DELETE, TITLE_EDIT
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import ActionsManage, MenuManage
from lucterios.framework.tools import FORMTYPE_NOMODAL, FORMTYPE_MODAL, CLOSE_NO, CLOSE_YES, SELECT_SINGLE, SELECT_MULTI
from lucterios.framework.xfercomponents import XferCompButton
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework import signal_and_lock
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.CORE.xferprint import XferPrintAction

from diacamma.accounting.tools import correct_accounting_code
from diacamma.condominium.models import Set, Partition, ExpenseDetail


def fill_params(self, is_mini):
    param_lists = ['condominium-frequency', 'condominium-default-owner-account']
    Params.fill(self, param_lists, 1, self.get_max_row() + 1)
    btn = XferCompButton('editparam')
    btn.set_location(1, self.get_max_row() + 1, 2, 1)
    btn.set_is_mini(is_mini)
    btn.set_action(self.request, ParamEdit.get_action(TITLE_MODIFY, 'images/edit.png'), close=CLOSE_NO,
                   params={'params': param_lists})
    self.add_component(btn)


@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'contact.conf', _('Management of parameters of condominium'))
class CondominiumConf(XferContainerCustom):
    icon = "condominium.png"
    caption = _("Condominium configuration")

    def fillresponse(self):
        fill_params(self)


MenuManage.add_sub("condominium", "core.general", "diacamma.condominium/images/condominium.png",
                   _("condominium"), _("Manage of condominium"), 30)


@MenuManage.describ('condominium.change_set', FORMTYPE_NOMODAL, 'condominium', _('Manage of class loads'))
class SetList(XferListEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Class loads")


@ActionsManage.affect_list(TITLE_PRINT, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('condominium.change_set')
class SetPrint(XferPrintAction):
    caption = _("Print class loads")
    icon = "set.png"
    model = Set
    field_id = 'set'
    action_class = SetList
    with_text_export = True


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES)
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


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('condominium.delete_set')
class SetDel(XferDelete):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("Delete class load")


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('condominium.add_set')
class PartitionAddModify(XferAddEditor):
    icon = "set.png"
    model = Partition
    field_id = 'partition'
    caption_modify = _("Modify partition")


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_condo(known_codes, accompt_returned):
    set_unknown = Set.objects.exclude(revenue_account__in=known_codes).values_list('revenue_account', flat=True).distinct()
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


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_condominium(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("condominium_params", 35))
    elif (xfer is not None) and (wizard_ident == "condominium_params"):
        xfer.add_title(_("Diacamma condominium"), _("Condominium configuration"))
        fill_params(xfer, True)
