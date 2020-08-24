# -*- coding: utf-8 -*-
'''
Describe report accounting viewer for Django

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
from os.path import exists

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.filetools import get_user_path, readimage_to_base64
from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, convert_date, CLOSE_NO, FORMTYPE_REFRESH, WrapAction
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework.xfercomponents import XferCompImage, XferCompSelect, XferCompGrid, XferCompLabelForm
from lucterios.framework.xferadvance import TITLE_CLOSE, TITLE_PRINT
from lucterios.CORE.parameters import Params

from diacamma.accounting.models import FiscalYear, EntryAccount, ChartsAccount, Journal
from diacamma.accounting.views_reports import FiscalYearReportPrint
from diacamma.accounting.tools import current_system_account, format_with_devise
from diacamma.accounting.tools_reports import get_spaces, convert_query_to_account, add_item_in_grid, fill_grid, add_cell_in_grid
from diacamma.condominium.models import Set


MenuManage.add_sub("condominium.print", "condominium", "diacamma.condominium/images/report.png",
                   _("Report"), _("Report of condominium"), 20)


class CondominiumReport(XferContainerCustom):
    model = FiscalYear
    field_id = 'year'
    icon = "report.png"
    saving_pdfreport = True
    readonly = True
    methods_allowed = ('GET', )

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        self.filter = None
        self.lastfilter = None
        hfield = format_with_devise(5).split(';')
        self.format_str = ";".join(hfield[1:])
        self.hfield = hfield[0]

    def current_image(self, icon_path=None):
        img_path = get_user_path("contacts", "Image_1.jpg")
        if exists(img_path):
            return readimage_to_base64(img_path)
        else:
            return self.icon_path(icon_path)

    def fillresponse(self):
        self.fill_header()
        self.define_gridheader()
        self.fill_body()
        self.fill_buttons()

    def fill_header(self):
        self.item = FiscalYear.get_current(self.getparam("year"))
        new_begin = convert_date(self.getparam("begin"), self.item.begin)
        new_end = convert_date(self.getparam("end"), self.item.end)
        if (new_begin >= self.item.begin) and (new_end <= self.item.end):
            self.item.begin = new_begin
            self.item.end = new_end
        img = XferCompImage('img')
        img.set_value(self.current_image())
        if not img.value.startswith('/static/'):
            img.type = 'jpg'
        img.set_location(0, 0, 1, 5)
        self.add_component(img)

        if self.item.last_fiscalyear is not None:
            lbl = XferCompLabelForm('year_1')
            lbl.set_location(1, 0, 3)
            lbl.description = _('year N-1')
            lbl.set_value(str(self.item.last_fiscalyear))
            self.add_component(lbl)
        select_year = XferCompSelect(self.field_id)
        select_year.set_location(1, 1, 3)
        select_year.set_select_query(FiscalYear.objects.all())
        select_year.description = _('year N')
        select_year.set_value(self.item.id)
        select_year.set_needed(True)
        select_year.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(select_year)
        self.filter = Q(entry__year=self.item)
        self.lastfilter = Q(entry__year=self.item.last_fiscalyear)

    def define_gridheader(self):
        pass

    def fill_body(self):
        pass

    def fill_buttons(self):
        self.add_action(FiscalYearReportPrint.get_action(TITLE_PRINT, "images/print.png"),
                        close=CLOSE_NO, params={"modulename": __name__, 'classname': self.__class__.__name__})
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('condominium.change_owner', FORMTYPE_NOMODAL, 'condominium.print', _('Show financial status report'))
class FinancialStatus(CondominiumReport):
    caption = _("Financial status")

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('left', _('Designation'))
        if self.item.last_fiscalyear is not None:
            self.grid.add_header('left_n_1', _('year N-1'), self.hfield, 0, self.format_str)
        self.grid.add_header('left_n', _('year N'), self.hfield, 0, self.format_str)
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Designation'))
        if self.item.last_fiscalyear is not None:
            self.grid.add_header('right_n_1', _('year N-1'), self.hfield, 0, self.format_str)
        self.grid.add_header('right_n', _('year N'), self.hfield, 0, self.format_str)
        self.grid.set_location(0, 10, 6)
        self.grid.no_pager = True
        self.add_component(self.grid)

    def fill_part_of_grid(self, side, current_filter, index_begin, title, sign_value=None, with_third=False):
        data_line, total1, total2, _totalb = convert_query_to_account(self.filter & current_filter, self.lastfilter & current_filter, sign_value=sign_value, with_third=with_third)
        add_cell_in_grid(self.grid, index_begin, side, get_spaces(5) + '{[u]}%s{[/u]}' % title)
        line_idx = index_begin + 1
        line_idx = fill_grid(self.grid, line_idx, side, data_line)
        add_cell_in_grid(self.grid, line_idx, side, '')
        line_idx += 1
        return line_idx, total1, total2

    def fill_body(self):
        line__tresor, total1_tresor, total2_tresor = self.fill_part_of_grid('left', Q(account__code__regex=current_system_account().get_cash_mask()), 0, _('Tresory'))
        line__capital, total1_capital, total2_capital = self.fill_part_of_grid('right', Q(account__type_of_account=2), 0, _('Provision and advance'))
        line_idx = max(line__tresor, line__capital)
        add_item_in_grid(self.grid, line_idx, 'left', (_('total'), total1_tresor, total2_tresor, None), get_spaces(5) + "{[u]}%s{[/u]}")
        add_item_in_grid(self.grid, line_idx, 'right', (_('total'), total1_capital, total2_capital, None), get_spaces(5) + "{[u]}%s{[/u]}")
        add_cell_in_grid(self.grid, line_idx + 1, 'left', '')
        add_cell_in_grid(self.grid, line_idx + 1, 'right', '')

        last_ids = []
        try:
            last_ids.append(EntryAccount.objects.filter(year=self.item).order_by('-id')[0].id)
        except IndexError:
            last_ids.append(0)
        if self.item.last_fiscalyear is not None:
            try:
                last_ids.append(EntryAccount.objects.filter(year=self.item.last_fiscalyear).order_by('-id')[0].id)
            except IndexError:
                last_ids.append(0)
        current_filter = Q(account__type_of_account__in=(ChartsAccount.TYPE_ASSET, ChartsAccount.TYPE_LIABILITY)) & ~Q(account__code__regex=current_system_account().get_cash_mask())
        current_filter &= (~Q(entry__year__status=2) | ~(Q(entry__journal=Journal.DEFAULT_OTHER) & Q(entry__id__in=tuple(last_ids))))
        line__creance, total1_creance, total2_creance = self.fill_part_of_grid('left', current_filter, line_idx + 2, _('Créance'), sign_value=-1, with_third=True)
        line__dette, total1_dette, total2_dette = self.fill_part_of_grid('right', current_filter, line_idx + 2, _('Dettes'), sign_value=1, with_third=True)
        line_idx = max(line__creance, line__dette)
        add_item_in_grid(self.grid, line_idx, 'left', (_('total'), total1_creance, total2_creance, None), get_spaces(5) + "{[u]}%s{[/u]}")
        add_item_in_grid(self.grid, line_idx, 'right', (_('total'), total1_dette, total2_dette, None), get_spaces(5) + "{[u]}%s{[/u]}")
        add_cell_in_grid(self.grid, line_idx + 1, 'left', '')
        add_cell_in_grid(self.grid, line_idx + 1, 'right', '')
        add_item_in_grid(self.grid, line_idx + 2, 'left', (_('total'), total1_tresor + total1_creance, total2_tresor + total2_creance, None), get_spaces(5) + "{[b]}%s{[/b]}")
        add_item_in_grid(self.grid, line_idx + 2, 'right', (_('total'), total1_capital + total1_dette, total2_capital + total2_dette, None), get_spaces(5) + "{[b]}%s{[/b]}")


class ManageAccounting(CondominiumReport):

    def fill_header(self):
        CondominiumReport.fill_header(self)
        self.next_year = self.item.next_fiscalyear.first()
        if self.next_year is not None:
            lbl = XferCompLabelForm('yearn1')
            lbl.set_location(1, 2, 3)
            lbl.set_value(str(self.next_year))
            lbl.description = _('year N+1')
            self.add_component(lbl)
            self.next_year_again = self.next_year.next_fiscalyear.first()
            if self.next_year_again is not None:
                lbl = XferCompLabelForm('yearn2')
                lbl.set_location(1, 3, 3)
                lbl.description = _('year N+2')
                lbl.set_value(str(self.next_year_again))
                self.add_component(lbl)
        else:
            self.next_year_again = None

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('design', _('Designation'))
        if self.item.last_fiscalyear is not None:
            self.grid.add_header('year_n_1', _('year N-1'), self.hfield, 0, self.format_str)
        self.grid.add_header('budget_n', _('budget N'), self.hfield, 0, self.format_str)
        self.grid.add_header('year_n', _('year N'), self.hfield, 0, self.format_str)
        if self.next_year is not None:
            self.grid.add_header('budget_n1', _('budget N+1'), self.hfield, 0, self.format_str)
        if self.next_year_again is not None:
            self.grid.add_header('budget_n2', _('budget N+2'), self.hfield, 0, self.format_str)
        self.grid.set_location(0, 10, 6)
        self.grid.no_pager = True
        self.add_component(self.grid)

    def fill_part_of_grid(self, current_filter, query_budget, index_begin, title, sign_value=None):
        data_line, total1, total2, totalb = convert_query_to_account(self.filter & current_filter, self.lastfilter & current_filter, query_budget=query_budget, sign_value=sign_value)
        add_cell_in_grid(self.grid, index_begin, 'design', get_spaces(5) + '{[u]}%s{[/u]}' % title)
        line_idx = index_begin + 1
        for data_item in data_line:
            add_cell_in_grid(self.grid, line_idx, 'design', data_item[0])
            add_cell_in_grid(self.grid, line_idx, 'year_n', data_item[1])
            add_cell_in_grid(self.grid, line_idx, 'budget_n', data_item[3])
            if self.next_year is not None:
                add_cell_in_grid(self.grid, line_idx, 'budget_n1', data_item[4])
            if self.next_year_again is not None:
                add_cell_in_grid(self.grid, line_idx, 'budget_n2', data_item[5])
            if self.item.last_fiscalyear is not None:
                add_cell_in_grid(self.grid, line_idx, 'year_n_1', data_item[2])
            line_idx += 1
        add_cell_in_grid(self.grid, line_idx, 'design', '')
        line_idx += 1
        add_cell_in_grid(self.grid, line_idx, 'design', get_spaces(5) + "{[u]}%s{[/u]}" % _('total'))
        add_cell_in_grid(self.grid, line_idx, 'year_n', total1, "{[u]}%s{[/u]}")
        add_cell_in_grid(self.grid, line_idx, 'budget_n', totalb[0], "{[u]}%s{[/u]}")
        if self.next_year is not None:
            add_cell_in_grid(self.grid, line_idx, 'budget_n1', totalb[1], "{[u]}%s{[/u]}")
        if self.next_year_again is not None:
            add_cell_in_grid(self.grid, line_idx, 'budget_n2', totalb[2], "{[u]}%s{[/u]}")
        if self.item.last_fiscalyear is not None:
            add_cell_in_grid(self.grid, line_idx, 'year_n_1', total2, "{[u]}%s{[/u]}")
        line_idx += 1
        add_cell_in_grid(self.grid, line_idx, 'design', '')
        return line_idx, total1, total2, totalb


@MenuManage.describ('condominium.change_owner', FORMTYPE_NOMODAL, 'condominium.print', _('Show General manage accounting report'))
class GeneralManageAccounting(ManageAccounting):
    caption = _("General manage accounting")

    def fill_body(self):
        current_query = Q(costaccounting__setcost__set__type_load=Set.TYPELOAD_CURRENT) & Q(costaccounting__setcost__set__is_active=True)
        query_budget = Q(code__regex=current_system_account().get_expence_mask()) & Q(cost_accounting__setcost__set__type_load=Set.TYPELOAD_CURRENT) & Q(cost_accounting__setcost__set__is_active=True)
        budget_query = [Q(year=self.item) & query_budget]
        if self.next_year is not None:
            budget_query.append(Q(year=self.next_year) & query_budget)
        if self.next_year_again is not None:
            budget_query.append(Q(year=self.next_year_again) & query_budget)
        line__current_dep, _total1_current_dep, _total2_current_dep, _totalb_current_dep = self.fill_part_of_grid(Q(account__type_of_account=ChartsAccount.TYPE_EXPENSE) & current_query, budget_query, 0, _('Current depency'))

        query_budget = Q(code__regex=current_system_account().get_revenue_mask()) & Q(cost_accounting__setcost__set__type_load=Set.TYPELOAD_CURRENT) & Q(cost_accounting__setcost__set__is_active=True)
        budget_query = [Q(year=self.item) & query_budget]
        if self.next_year is not None:
            budget_query.append(Q(year=self.next_year) & query_budget)
        if self.next_year_again is not None:
            budget_query.append(Q(year=self.next_year_again) & query_budget)
        line__current_rec, _total1_current_rec, _total2_current_rec, _totalb_current_rec = self.fill_part_of_grid(Q(account__type_of_account=ChartsAccount.TYPE_REVENUE) & current_query, budget_query, line__current_dep + 1, _('Current revenue'))

        self.next_year = None
        self.next_year_again = None
        current_query = Q(costaccounting__setcost__set__type_load=1) & Q(costaccounting__setcost__set__is_active=True)
        query_budget = Q(year=self.item) & Q(code__regex=current_system_account().get_expence_mask()) & Q(cost_accounting__setcost__set__type_load=Set.TYPELOAD_EXCEPTIONAL) & Q(cost_accounting__setcost__set__is_active=True)
        budget_query = [query_budget]
        line__except_dep, _total1_except_dep, _total2_except_dep, _totalb_except_dep = self.fill_part_of_grid(Q(account__type_of_account=ChartsAccount.TYPE_EXPENSE) & current_query, budget_query, line__current_rec + 1, _('Exceptional depency'))

        query_budget = Q(year=self.item) & Q(code__regex=current_system_account().get_revenue_mask()) & Q(cost_accounting__setcost__set__type_load=Set.TYPELOAD_EXCEPTIONAL) & Q(cost_accounting__setcost__set__is_active=True)
        budget_query = [query_budget]
        _line__except_rec, _total1_except_rec, _total2_except_rec, _totalb_except_rec = self.fill_part_of_grid(Q(account__type_of_account=ChartsAccount.TYPE_REVENUE) & current_query, budget_query, line__except_dep + 1, _('Exceptional revenue'))


@MenuManage.describ('condominium.change_owner', FORMTYPE_NOMODAL, 'condominium.print', _('Show Current manage accounting report'))
class CurrentManageAccounting(ManageAccounting):
    caption = _("Current manage accounting")

    def fill_body(self):
        line_idx = 0
        total1 = 0
        total2 = 0
        totalb = [0, 0, 0]
        revenue_account = Params.getvalue("condominium-current-revenue-account")
        initial_filter = self.filter
        initial_lastfilter = self.lastfilter
        for classloaditem in Set.objects.filter(type_load=0, is_active=True):
            first_setcost = classloaditem.setcost_set.filter(year=self.item).first()
            if first_setcost is None:
                continue
            current_costaccounting = first_setcost.cost_accounting
            current_request = Q(account__code__regex=current_system_account().get_expence_mask())
            current_request |= Q(account__code__regex=current_system_account().get_revenue_mask()) & ~Q(account__code=revenue_account)
            if initial_filter is not None:
                self.filter = initial_filter & Q(costaccounting_id=current_costaccounting.id)
            if initial_lastfilter is not None:
                self.lastfilter = initial_lastfilter & Q(costaccounting_id=current_costaccounting.last_costaccounting_id)
            query_budget = [~Q(code=revenue_account) & Q(cost_accounting=current_costaccounting)]
            if self.next_year is not None:
                set_cost = classloaditem.setcost_set.filter(year=self.next_year).first()
                if set_cost is None:
                    set_cost = classloaditem.create_new_cost(year=self.next_year)
                query_budget.append(~Q(code=revenue_account) & Q(cost_accounting=set_cost.cost_accounting))
            if self.next_year_again is not None:
                set_cost = classloaditem.setcost_set.filter(year=self.next_year_again).first()
                if set_cost is None:
                    set_cost = classloaditem.create_new_cost(year=self.next_year_again)
                query_budget.append(~Q(code=revenue_account) & Q(cost_accounting=set_cost.cost_accounting))
            line__current_dep, subtotal1, subtotal2, subtotalb = self.fill_part_of_grid(current_request, query_budget, line_idx, str(classloaditem), sign_value=False)
            line_idx = line__current_dep + 1
            total1 += subtotal1
            total2 += subtotal2
            totalb[0] += subtotalb[0]
            if self.next_year is not None:
                totalb[1] += subtotalb[1]
            if self.next_year_again is not None:
                totalb[2] += subtotalb[2]
        add_cell_in_grid(self.grid, line_idx, 'design', get_spaces(5) + "{[b]}%s{[/b]}" % _('total'))
        add_cell_in_grid(self.grid, line_idx, 'year_n', total1, "{[b]}%s{[/b]}")
        add_cell_in_grid(self.grid, line_idx, 'budget_n', totalb[0], "{[b]}%s{[/b]}")
        if self.item.last_fiscalyear is not None:
            add_cell_in_grid(self.grid, line_idx, 'year_n_1', total2, "{[b]}%s{[/b]}")
        if self.next_year is not None:
            add_cell_in_grid(self.grid, line_idx, 'budget_n1', totalb[1], "{[b]}%s{[/b]}")
        if self.next_year_again is not None:
            add_cell_in_grid(self.grid, line_idx, 'budget_n2', totalb[2], "{[b]}%s{[/b]}")


@MenuManage.describ('condominium.change_owner', FORMTYPE_NOMODAL, 'condominium.print', _('Show Exeptional manage accounting report'))
class ExceptionalManageAccounting(ManageAccounting):
    caption = _("Exceptional manage accounting")

    def fill_header(self):
        CondominiumReport.fill_header(self)
        self.remove_component('lblyear_1')
        self.remove_component('year_1')
        self.next_year = None
        self.next_year_again = None
        self.item.last_fiscalyear = None

    def define_gridheader(self):
        ManageAccounting.define_gridheader(self)
        self.grid.add_header('calloffund', _('call of funds'), self.hfield, 0, self.format_str)
        self.grid.add_header('result', _('result general'), self.hfield, 0, self.format_str)

    def fill_body(self):
        line_idx = 0
        total1 = 0
        total2 = 0
        totalb = [0]
        revenue_account = Params.getvalue("condominium-exceptional-revenue-account")
        for classloaditem in Set.objects.filter(type_load=1, is_active=True):
            current_request = Q(account__code__regex=current_system_account().get_expence_mask())
            current_request |= Q(account__code__regex=current_system_account().get_revenue_mask()) & ~Q(account__code=revenue_account)
            current_request &= Q(costaccounting__setcost__set=classloaditem)
            query_budget = [~Q(code=revenue_account) & Q(cost_accounting=classloaditem.current_cost_accounting) & Q(year=self.item)]
            line__current_dep, subtotal1, subtotal2, subtotalb = self.fill_part_of_grid(current_request, query_budget, line_idx, str(classloaditem), sign_value=False)
            total_call = classloaditem.get_total_calloffund(self.item)
            add_cell_in_grid(self.grid, line__current_dep - 1, 'calloffund', total_call, "{[u]}%s{[/u]}")
            add_cell_in_grid(self.grid, line__current_dep - 1, 'result', total_call - subtotal1, "{[u]}%s{[/u]}")
            line_idx = line__current_dep + 1
            total1 += subtotal1
            total2 += subtotal2
            totalb[0] += subtotalb[0]
        add_cell_in_grid(self.grid, line_idx, 'design', get_spaces(5) + "{[b]}%s{[/b]}" % _('total'))
        add_cell_in_grid(self.grid, line_idx, 'year_n', total1, "{[b]}%s{[/b]}")
        add_cell_in_grid(self.grid, line_idx, 'budget_n', totalb[0], "{[b]}%s{[/b]}")
