# -*- coding: utf-8 -*-
'''
diacamma.syndic package

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
from os.path import dirname, join, isfile


def get_build():
    file_name = join(dirname(__file__), 'build')
    if isfile(file_name):
        with open(file_name) as flb:
            return flb.read()
    return "0"

__version__ = "2.1.6." + get_build()


def __title__():
    from django.utils.translation import ugettext_lazy as _
    return _("Diacamma syndic")


def link():
    return ["lucterios.contacts", "lucterios.mailing", "lucterios.documents", "diacamma.accounting", "diacamma.payoff", "diacamma.condominium"]
