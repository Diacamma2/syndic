# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from diacamma.condominium.models import Owner

name = _("Load count")
kind = 2
modelname = Owner.get_long_name()

value = """<model hmargin="10.0" vmargin="10.0" page_width="210.0" page_height="297.0">
<header extent="25.0">
<text height="20.0" width="120.0" top="0.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="20" font_family="sans-serif" font_weight="" font_size="20">
{[b]}#OUR_DETAIL.name{[/b]}
</text>
<text height="5.0" width="120.0" top="10.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="8" font_family="sans-serif" font_weight="" font_size="8">
{[italic]}
#OUR_DETAIL.address - #OUR_DETAIL.postal_code #OUR_DETAIL.city - #OUR_DETAIL.tel1 #OUR_DETAIL.tel2 #OUR_DETAIL.email{[br/]}#OUR_DETAIL.identify_number
{[/italic]}
</text>
<image height="25.0" width="30.0" top="0.0" left="10.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
#OUR_DETAIL.image
</image>
</header>
<bottom extent="10.0">
</bottom>
<body>
<text height="8.0" width="120.0" top="10.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="15" font_family="sans-serif" font_weight="" font_size="15">
{[b]}%(title)s{[/b]}
</text>
<text height="20.0" width="70.0" top="20.0" left="120.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}#third.contact.str{[/b]}{[br/]}#third.contact.address{[br/]}#third.contact.postal_code #third.contact.city{[br/]}
#third.contact.email{[br/]}
#information
</text>

<text height="20.0" width="120.0" top="25.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}%(FiscalYear)s{[/b]}: du #date_begin au #date_end
</text>

<table height="16.0" width="60.0" top="50.0" left="70.0" padding="1.0" spacing="0.0" border_color="red" border_style="solid" border_width="0.0">
    <columns width="60.0" display_align="center" border_color="green" border_style="solid" border_width="0.0" text_align="center" line_height="0" font_family="sans-serif" font_weight="" font_size="0">
    </columns>
    <rows>
    <cell display_align="center" border_color="green" border_style="solid" border_width="0.0" text_align="center" line_height="16" font_family="sans-serif" font_weight="" font_size="15">
    {[b]}%(TO PAY)s : #sumtopay{[/b]}
    </cell>
    </rows>
    <rows><cell line_height="0" font_family="sans-serif" font_weight="" font_size="0"> </cell></rows>
</table>

<text height="10.0" width="190.0" top="70.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}Lots concernés{[/b]}
</text>
<table height="10.0" width="190.0" top="80.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
    <columns width="10.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(num)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(value)s{[/b]}
    </columns>
    <columns width="15.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(ratio)s{[/b]}
    </columns>
    <columns width="50.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(description)s{[/b]}
    </columns>
    <rows data="propertylot_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#num
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#value
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#ratio
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#description
        </cell>
    </rows>
</table>

<text height="10.0" width="190.0" top="105.0" left="0.0" padding="1.0" spacing="3.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}%(Distribution of common and individual expenses)s{[/b]}
</text>
<table height="10.0" width="190.0" top="115.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2">
    <columns width="100.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(designation)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(total)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(ratio)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(ventilated)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(recov. load)s{[/b]}
    </columns>

    <rows data="loadcount_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#designation
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#total
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#ratio
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#ventilated
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#recoverable_load
        </cell>
    </rows>
</table>

<text height="10.0" width="190.0" top="115.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="10">
{[i]}%(warning about recoverable load)s{[/i]}
</text>

<text height="10.0" width="190.0" top="120.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}%(total_current_call)s{[/b]} : #total_current_call{[br/]}
{[b]}%(total_current_ventilated)s{[/b]} : #total_current_ventilated{[br/]}
{[b]}%(total_current_regularization)s{[/b]} : #total_current_regularization{[br/]}
{[b]}%(total_current_payoff)s{[/b]} : #total_current_payoff{[br/]}
{[b]}%(total_current_estimated_total)s{[/b]} : #total_current_estimated_total{[br/]}
</text>

<text height="10.0" width="190.0" top="130.0" left="0.0" padding="1.0" spacing="3.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}%(account detail)s{[/b]}
</text>
<text height="10.0" width="190.0" top="135.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="10">
{[u]}{[i]}%(third_initial)s :{[/i]}{[/u]} #thirdinitial
</text>
<table height="10.0" width="190.0" top="145.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2">
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(date)s{[/b]}
    </columns>
    <columns width="100.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(designation)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(debit)s{[/b]}
    </columns>
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(credit)s{[/b]}
    </columns>
    <rows data="entryline_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#entry.date_value
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#entry.designation
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#debit
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#credit
        </cell>
    </rows>
</table>
<text height="10.0" width="190.0" top="155.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="10" font_family="sans-serif" font_weight="" font_size="10">
{[u]}{[i]}%(thirdtotal)s :{[/i]}{[/u]} #thirdtotal
</text>

</body>
</model>""" % {'title': _('OWNER INDIVIDUAL COUNT'), 'FiscalYear': _('Fiscal year'), 'TO PAY': _('sum to pay'),
               'num': _('numeros'), 'value': _('tantime'), 'ratio': _('ratio'), 'description': _('description'),
               'Distribution of common and individual expenses': _('Distribution of common and individual expenses'),
               'designation': _('designation'), 'total': _('total'), 'ventilated': _('ventilated'), 'recov. load': _('recov. load'),
               'account detail': _('Account detail'), 'third_initial': _('total owner initial'), 'thirdtotal': _('total owner'),
               'date': _('date'), 'debit': _('debit'), 'credit': _('credit'),
               'warning about recoverable load': _('warning about recoverable load'),
               'total_current_call': _('current total call for funds'),
               'total_current_ventilated': _('current total ventilated'),
               'total_current_regularization': _('estimated regularization'),
               'total_current_payoff': _('current total payoff'),
               'total_current_estimated_total': _('estimated total'),
               }

mode = 0
