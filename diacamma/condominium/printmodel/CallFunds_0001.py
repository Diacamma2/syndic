# -*- coding: utf-8 -*-
'''
Printmodel django module for condominium

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2016 sd-libre.fr
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

from diacamma.condominium.models import CallFunds

name = _("call of funds")
kind = 2
modelname = CallFunds.get_long_name()
value = """
<model hmargin="10.0" vmargin="10.0" page_width="210.0" page_height="297.0">
<header extent="25.0">
<text height="20.0" width="120.0" top="5.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="20" font_family="sans-serif" font_weight="" font_size="20">
{[b]}#OUR_DETAIL.name{[/b]}
</text>
<image height="25.0" width="30.0" top="0.0" left="10.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
#OUR_DETAIL.image
</image>
</header>
<bottom extent="10.0">
<text height="10.0" width="190.0" top="00.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="8" font_family="sans-serif" font_weight="" font_size="8">
{[italic]}
#OUR_DETAIL.address - #OUR_DETAIL.postal_code #OUR_DETAIL.city - #OUR_DETAIL.tel1 #OUR_DETAIL.tel2 #OUR_DETAIL.email{[br/]}#OUR_DETAIL.identify_number
{[/italic]}
</text>
</bottom>
<body>
<text height="8.0" width="190.0" top="0.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="15" font_family="sans-serif" font_weight="" font_size="15">
{[b]}%(callfunds)s #num{[/b]}
</text>
<text height="8.0" width="190.0" top="8.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="13" font_family="sans-serif" font_weight="" font_size="13">
#date
</text>
<text height="20.0" width="100.0" top="25.0" left="80.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="11" font_family="sans-serif" font_weight="" font_size="11">
{[b]}#owner.third.contact.str{[/b]}{[br/]}#owner.third.contact.address{[br/]}#owner.third.contact.postal_code #owner.third.contact.city
</text>
<table height="100.0" width="170.0" top="70.0" left="10.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
    <columns width="20.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(set)s{[/b]}
    </columns>
    <columns width="82.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(designation)s{[/b]}
    </columns>
    <columns width="17.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(totalamount)s{[/b]}
    </columns>
    <columns width="17.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(partsum)s{[/b]}
    </columns>
    <columns width="17.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(partition)s{[/b]}
    </columns>
    <columns width="17.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(price)s{[/b]}
    </columns>
    <rows data="calldetail_set">
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#set
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="start" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#designation
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#total_amount
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#set.total_part
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#owner_part
        </cell>
        <cell display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="end" line_height="7" font_family="sans-serif" font_weight="" font_size="7">
#price_txt
        </cell>
    </rows>
</table>
<text height="15.0" width="30.0" top="190.0" left="140.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[u]}{[b]}%(total)s{[/b]}{[/u]}{[br/]}
</text>
<text height="15.0" width="20.0" top="190.0" left="170.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[u]}#total{[/u]}{[br/]}
</text>
<text height="20.0" width="100.0" top="190.0" left="0.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="left" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
#comment
</text>
<text height="5.0" width="130.0" top="215.0" left="00.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[u]}{[i]}%(situation)s{[/i]}{[/u]}
</text>
<text height="15.0" width="50.0" top="220.0" left="00.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[i]}%(total_initial)s{[/i]}{[br/]}
{[i]}%(total_call)s{[/i]}{[br/]}
{[i]}%(total_payed)s{[/i]}{[br/]}
{[i]}%(total_estimate)s{[/i]}{[br/]}
</text>
<text height="15.0" width="15.0" top="220.0" left="50.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
#owner.total_current_initial{[br/]}
#owner.total_current_call{[br/]}
#owner.total_current_payoff{[br/]}
#owner.total_current_owner{[br/]}
</text>

<text height="15.0" width="60.0" top="220.0" left="70.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[i]}%(total_excep_initial)s{[/i]}{[br/]}
{[i]}%(total_excep_call)s{[/i]}{[br/]}
{[i]}%(total_excep_payed)s{[/i]}{[br/]}
{[i]}%(total_excep_estimate)s{[/i]}{[br/]}
</text>
<text height="15.0" width="15.0" top="220.0" left="130.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
#owner.total_exceptional_initial{[br/]}
#owner.total_exceptional_call{[br/]}
#owner.total_exceptional_payoff{[br/]}
#owner.total_exceptional_owner{[br/]}
</text>

</body>
</model>
""" % {
        'callfunds': _('call of funds'),
        'set': _('set'),
        'designation': _('designation'),
        'totalamount': _('total'),
        'partsum': _('tantime sum'),
        'partition': _('tantime'),
        'price': _('amount'),
        'situation': _('situation at #owner.date_current'),
        'total_initial': _('current initial state'),
        'total_call': _('current total call for funds'),
        'total_payed': _('current total payoff'),
        'total_estimate': _('current total owner'),
        'total_excep_initial': _('exceptional initial state'),
        'total_excep_call': _('exceptional total call for funds'),
        'total_excep_payed': _('exceptional total payoff'),
        'total_excep_estimate': _('exceptional total owner'),
        'total': _('total'),
}
