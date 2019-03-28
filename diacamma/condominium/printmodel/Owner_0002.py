# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from diacamma.condominium.models import Owner

name = _("situation")
kind = 2
modelname = Owner.get_long_name()

value = """<model hmargin="10.0" vmargin="10.0" page_width="210.0" page_height="297.0">
<header extent="25.0">
<text height="10.0" width="120.0" top="0.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="20" font_family="sans-serif" font_weight="" font_size="20">
{[b]}#OUR_DETAIL.name{[/b]}
</text>
<text height="10.0" width="120.0" top="10.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="8" font_family="sans-serif" font_weight="" font_size="8">
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
<text height="8.0" width="190.0" top="0.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="15" font_family="sans-serif" font_weight="" font_size="15">
{[b]}%(title)s{[/b]}
</text>
<text height="8.0" width="190.0" top="8.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="13" font_family="sans-serif" font_weight="" font_size="13">
#date_begin - #date_end
</text>
<text height="20.0" width="100.0" top="25.0" left="80.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}#third.contact.str{[/b]}{[br/]}#third.contact.address{[br/]}#third.contact.postal_code #third.contact.city
</text>

<text height="20.0" width="70.0" top="25.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}%(email)s{[/b]}: #third.contact.email{[br/]}
{[b]}%(tel)s{[/b]}: #third.contact.tel1 #third.contact.tel2{[br/]}
#information
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

<text height="10.0" width="180.0" top="70.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[u]}{[b]}%(partition)s{[/b]}{[/u]}
</text>
<text height="10.0" width="170.0" top="75.0" left="10.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[i]}%(current)s{[/i]}
</text>
<table height="20.0" width="180.0" top="85.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2">
    <columns width="60.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(set)s{[/b]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="8">
    {[b]}%(budget)s{[/b]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="8">
    {[b]}%(expense)s{[/b]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="8">
    {[b]}%(ratio)s{[/b]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="8">
    {[b]}%(ventilated)s{[/b]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="8">
    {[b]}%(recover_load)s{[/b]}
    </columns>
    <rows data="partition_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#set
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#set.budget_txt
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#set.sumexpense_txt
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#ratio
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#ventilated_txt
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#recovery_load_txt
        </cell>
    </rows>
</table>

<text height="10.0" width="170.0" top="110.0" left="10.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[i]}%(exceptionnal)s{[/i]}
</text>
<table height="20.0" width="180.0" top="120.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2">
    <columns width="60.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(set)s{[/b]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(ratio)s{[/b]}
    </columns>
    <columns width="30.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(total_callfunds)s{[/b]}
    </columns>
    <columns width="30.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(ventilated)s{[/b]}
    </columns>
    <rows data="exceptionnal_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#set
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#ratio
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#total_callfunds
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#ventilated_txt
        </cell>
    </rows>
</table>

<text height="10.0" width="180.0" top="130.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[u]}{[b]}%(property)s{[/b]}{[/u]}
</text>
<table height="20.0" width="180.0" top="135.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2">
    <columns width="10.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(num)s{[/b]}
    </columns>
    <columns width="15.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(value)s{[/b]}
    </columns>
    <columns width="12.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(ratio)s{[/b]}
    </columns>
    <columns width="33.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
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

<text height="10.0" width="180.0" top="145.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[u]}{[b]}%(account detail)s{[/b]}{[/u]}
</text>
<text height="10.0" width="180.0" top="150.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="10" font_family="sans-serif" font_weight="" font_size="10">
{[u]}{[i]}%(third_initial)s :{[/i]}{[/u]} #thirdinitial
</text>
<table height="20.0" width="180.0" top="155.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2">
    <columns width="40.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(date)s{[/b]}
    </columns>
    <columns width="80.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(designation)s{[/b]}
    </columns>
    <columns width="30.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(debit)s{[/b]}
    </columns>
    <columns width="30.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
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
<text height="10.0" width="180.0" top="155.0" left="0.0" padding="1.0" spacing="0.1" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="10" font_family="sans-serif" font_weight="" font_size="10">
{[u]}{[i]}%(thirdtotal)s :{[/i]}{[/u]} #thirdtotal
</text>

</body>
</model>""" % {'title': _('Owner situation'), 'email': _('emai'), 'tel': _('tel'), 'TO PAY': _('sum to pay'),
               'exceptionnal': _('exceptional'), 'current': _('current'),
               'partition': _('partition'), 'set': _('set'), 'budget': _('budget'), 'expense': _('expense'), 'value': _('tantime'), 'ratio': _('ratio'),
               'ventilated': _('ventilated'), 'recover_load': _('recover. load'), 'total_callfunds': _('total call for funds'), 'rest_to_pay': _('rest to pay'),
               'property': _('property lot'), 'num': _('numeros'), 'description': _('description'),
               'account detail': _('account detail'), 'third_initial': _('total owner initial'), 'thirdtotal': _('total owner'),
               'date': _('date'), 'designation': _('designation'), 'debit': _('debit'), 'credit': _('credit')}
mode = 0
