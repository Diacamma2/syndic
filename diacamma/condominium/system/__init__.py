# -*- coding: utf-8 -*-
'''
diacamma.condominium.system package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2018 sd-libre.fr
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

from django.utils.module_loading import import_module


def condo_system_list():
    res = {}
    res['diacamma.accounting.system.french.FrenchSystemAcounting'] = 'diacamma.condominium.system.french.FrenchSystemCondo'
    res['diacamma.accounting.system.belgium.BelgiumSystemAcounting'] = 'diacamma.condominium.system.belgium.BelgiumSystemCondo'
    return res


def get_condo_system():
    from lucterios.CORE.parameters import Params
    complete_name = Params.getvalue("accounting-system")
    sys_list = condo_system_list()
    if complete_name in sys_list.keys():
        modules_long = sys_list[complete_name].split('.')
        module_name = ".".join(modules_long[:-1])
        class_name = modules_long[-1]
        try:
            module_sys = import_module(module_name)
            class_sys = getattr(module_sys, class_name)
            return class_sys()
        except (ImportError, AttributeError):
            pass
    from diacamma.condominium.system.default import DefaultSystemCondo
    return DefaultSystemCondo()


def current_system_condo():
    import sys
    current_module = sys.modules[__name__]
    if not hasattr(current_module, 'SYSTEM_CONDO_CACHE'):
        setattr(current_module, 'SYSTEM_CONDO_CACHE', get_condo_system())
    return current_module.SYSTEM_CONDO_CACHE


def clear_system_condo():
    import sys
    current_module = sys.modules[__name__]
    if hasattr(current_module, 'SYSTEM_CONDO_CACHE'):
        del current_module.SYSTEM_CONDO_CACHE
