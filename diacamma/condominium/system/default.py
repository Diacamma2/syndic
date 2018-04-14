# -*- coding: utf-8 -*-
"""
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
"""
from lucterios.framework.error import LucteriosException, IMPORTANT


class DefaultSystemCondo(object):

    def __init__(self):
        pass

    def initialize_system(self):
        pass

    def owner_account_changed(self, account_item):
        pass

    def generate_account_callfunds(self, call_funds, fiscal_year):
        raise LucteriosException(IMPORTANT, _('This system condomium is not implemented'))

    def generate_revenue_for_expense(self, expense, is_asset, fiscal_year):
        raise LucteriosException(IMPORTANT, _('This system condomium is not implemented'))

    def generate_expense_for_expense(self, expense, is_asset, fiscal_year):
        raise LucteriosException(IMPORTANT, _('This system condomium is not implemented'))

    def ventilate_result(self, fiscal_year, ventilate):
        raise LucteriosException(IMPORTANT, _('This system condomium is not implemented'))
