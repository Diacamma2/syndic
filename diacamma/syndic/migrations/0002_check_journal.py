# -*- coding: utf-8 -*-
'''
Initial django functions

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2019 sd-libre.fr
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

from django.db import migrations
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import set_locale_lang
from diacamma.accounting.models import Journal


def check_values(*args):
    set_locale_lang(settings.LANGUAGE_CODE)
    jnl2 = Journal.objects.get(id=2)
    jnl2.name = _('spending')
    jnl2.save()
    jnl3 = Journal.objects.get(id=3)
    jnl3.name = _('revenue')
    jnl3.save()


class Migration(migrations.Migration):

    dependencies = [
        ('syndic', '0001_initial'),
        ('accounting', '0014_journal_is_default'),
    ]

    operations = [
        migrations.RunPython(check_values),
    ]
