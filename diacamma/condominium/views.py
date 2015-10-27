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

from lucterios.framework.xferadvance import XferListEditor
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.xferadvance import XferShowEditor
from lucterios.framework.xferadvance import XferDelete
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage,\
    FORMTYPE_MODAL

from diacamma.condominium.models import Set, Partition, Owner
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage,\
    XferCompButton
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit


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
@MenuManage.describ('condominium.change_set', FORMTYPE_NOMODAL, 'condominium', _('Manage of set'))
class SetOwnerList(XferListEditor):
    icon = "set.png"
    model = Set
    field_id = 'set'
    caption = _("set")

    def fillownerlist(self):
        row = self.get_max_row()
        img = XferCompImage('imgowner')
        img.set_value("diacamma.condominium/images/owner.png")
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
@MenuManage.describ('condominium.add_set')
class OwnerAddModify(XferAddEditor):
    icon = "set.png"
    model = Owner
    field_id = 'owner'
    caption_add = _("Add owner")
    redirect_to_show = False


@ActionsManage.affect('Owner', 'delete')
@MenuManage.describ('condominium.delete_set')
class OwnerDel(XferDelete):
    icon = "set.png"
    model = Owner
    field_id = 'owner'
    caption = _("Delete owner")


@ActionsManage.affect('Owner', 'show')
@MenuManage.describ('condominium.change_set')
class OwneShow(XferShowEditor):
    icon = "set.png"
    model = Owner
    field_id = 'owner'
    caption = _("Show owner")
