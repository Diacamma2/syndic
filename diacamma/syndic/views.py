# -*- coding: utf-8 -*-7
'''
Syndic module to declare a new Diacamma appli

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
from os.path import join, dirname
import os

from lucterios.framework import signal_and_lock
from lucterios.CORE.parameters import Params


@signal_and_lock.Signal.decorate('initial_account')
def initial_account_syndic(account_list):
    from diacamma.accounting.system import accounting_system_ident
    ret = False
    for file_name in os.listdir(dirname(__file__)):
        if file_name.startswith('init_%s' % accounting_system_ident(Params.getvalue("accounting-system"))) and file_name[-4:] == '.csv':
            ret = True
            if isinstance(account_list, list):
                account_list.append(join(dirname(__file__), file_name))
    return ret
