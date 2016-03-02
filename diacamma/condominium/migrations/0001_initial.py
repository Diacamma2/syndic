# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.utils.translation import ugettext_lazy as _

from lucterios.CORE.models import Parameter, PrintModel
from diacamma.condominium.models import CallFunds


def initial_values(*args):
    param = Parameter.objects.create(
        name='condominium-frequency', typeparam=4)
    param.title = _("condominium-frequency")
    param.param_titles = (_("condominium-frequency.0"),
                          _("condominium-frequency.1"), _("condominium-frequency.2"))
    param.args = "{'Enum':3}"
    param.value = '0'
    param.save()

    param = Parameter.objects.create(
        name='condominium-default-owner-account', typeparam=0)
    param.title = _("condominium-default-owner-account")
    param.args = "{'Multi':False}"
    param.value = '455'
    param.save()

    prtmdl = PrintModel.objects.create(
        name=_("call of funds"), kind=2, modelname=CallFunds.get_long_name())
    prtmdl.value = """
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
<table height="100.0" width="150.0" top="70.0" left="20.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2">
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(set)s{[/b]}
    </columns>
    <columns width="100.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
    {[b]}%(designation)s{[/b]}
    </columns>
    <columns width="25.0" display_align="center" border_color="black" border_style="solid" border_width="0.2" text_align="center" line_height="10" font_family="sans-serif" font_weight="" font_size="9">
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
<text height="5.0" width="60.0" top="215.0" left="20.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="center" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[u]}{[i]}%(situation)s{[/i]}{[/u]}
</text>
<text height="15.0" width="50.0" top="220.0" left="00.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
{[i]}%(total_initial)s{[/i]}{[br/]}
{[i]}%(total_call)s{[/i]}{[br/]}
{[i]}%(total_payed)s{[/i]}{[br/]}
{[i]}%(total_estimate)s{[/i]}{[br/]}
</text>
<text height="15.0" width="15.0" top="220.0" left="50.0" padding="1.0" spacing="0.0" border_color="black" border_style="" border_width="0.2" text_align="right" line_height="9" font_family="sans-serif" font_weight="" font_size="9">
#owner.total_initial{[br/]}
#owner.total_call{[br/]}
#owner.total_payed{[br/]}
#owner.total_estimate{[br/]}
</text>
</body>
</model>
""" % {
        'callfunds': _('call of funds'),
        'set': _('set'),
        'designation': _('designation'),
        'price': _('price'),
        'situation': _('situation at #owner.date_current'),
        'total_initial': _('initial state'),
        'total_call': _('total call for funds'),
        'total_payed': _('total payed'),
        'total_estimate': _('total estimate'),
        'total': _('total'),
    }
    prtmdl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('payoff', '0001_initial'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('supporting_ptr', models.OneToOneField(primary_key=True, serialize=False, on_delete=models.CASCADE,
                                                        to='payoff.Supporting', auto_created=True, parent_link=True)),
            ],
            options={'verbose_name_plural': 'owners', 'verbose_name': 'owner'},
            bases=('payoff.supporting',),
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(
                    verbose_name='name', max_length=100)),
                ('budget', models.DecimalField(decimal_places=3, verbose_name='budget', max_digits=10, default=0.0, validators=[
                 django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(9999999.999)])),
                ('revenue_account', models.CharField(
                    verbose_name='revenue account', max_length=50)),
                ('cost_accounting', models.ForeignKey(to='accounting.CostAccounting', default=None,
                                                      null=True, on_delete=models.PROTECT, verbose_name='cost accounting')),
            ],
            options={
                'verbose_name': 'set',
                'verbose_name_plural': 'sets',
            },
        ),
        migrations.CreateModel(
            name='Partition',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('value', models.DecimalField(decimal_places=2, verbose_name='value', max_digits=7, default=0.0, validators=[
                 django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1000.0)])),
                ('owner', models.ForeignKey(to='condominium.Owner',
                                            on_delete=models.PROTECT, verbose_name='owner')),
                ('set', models.ForeignKey(to='condominium.Set',
                                          on_delete=models.PROTECT, verbose_name='set')),
            ],
            options={'verbose_name_plural': 'partitions',
                     'verbose_name': 'partition',
                     'default_permissions': [], },
        ),
        migrations.CreateModel(
            name='CallFunds',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(
                    null=True, verbose_name='numeros')),
                ('date', models.DateField(verbose_name='date')),
                ('comment', models.TextField(
                    null=True, verbose_name='comment', default='')),
                ('status', models.IntegerField(db_index=True, choices=[
                 (0, 'building'), (1, 'valid'), (2, 'ended')], verbose_name='status', default=0)),
                ('owner', models.ForeignKey(on_delete=models.CASCADE,
                                            verbose_name='owner', null=True, to='condominium.Owner')),
            ],
            options={
                'verbose_name': 'call of funds',
                'verbose_name_plural': 'calls of funds',
            },
        ),
        migrations.CreateModel(
            name='CallDetail',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('designation', models.TextField(verbose_name='designation')),
                ('price', models.DecimalField(max_digits=10, validators=[django.core.validators.MinValueValidator(
                    0.0), django.core.validators.MaxValueValidator(9999999.999)], verbose_name='price', default=0.0, decimal_places=3)),
                ('callfunds', models.ForeignKey(null=True, default=None, verbose_name='call of funds',
                                                to='condominium.CallFunds', on_delete=models.PROTECT)),
                ('set', models.ForeignKey(on_delete=models.CASCADE,
                                          verbose_name='set', to='condominium.Set')),
            ],
            options={
                'verbose_name': 'detail of call',
                'verbose_name_plural': 'details of call',
                'default_permissions': [],
            },
        ),
        migrations.AlterField(
            model_name='partition',
            name='owner',
            field=models.ForeignKey(on_delete=models.CASCADE,
                                    to='condominium.Owner', verbose_name='owner'),
        ),
        migrations.AlterField(
            model_name='partition',
            name='set',
            field=models.ForeignKey(
                on_delete=models.CASCADE, to='condominium.Set', verbose_name='set'),
        ),
        migrations.AlterField(
            model_name='calldetail',
            name='callfunds',
            field=models.ForeignKey(on_delete=models.CASCADE,
                                    verbose_name='call of funds', null=True, default=None, to='condominium.CallFunds'),
        ),
        migrations.AlterField(
            model_name='calldetail',
            name='set',
            field=models.ForeignKey(
                verbose_name='set', on_delete=models.PROTECT, to='condominium.Set'),
        ),
        migrations.AlterField(
            model_name='callfunds',
            name='owner',
            field=models.ForeignKey(
                verbose_name='owner', on_delete=models.PROTECT, null=True, to='condominium.Owner'),
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('supporting_ptr', models.OneToOneField(serialize=False, primary_key=True, on_delete=models.CASCADE,
                                                        parent_link=True, auto_created=True, to='payoff.Supporting')),
                ('num', models.IntegerField(
                    verbose_name='numeros', null=True)),
                ('date', models.DateField(verbose_name='date')),
                ('comment', models.TextField(
                    verbose_name='comment', default='', null=True)),
                ('expensetype', models.IntegerField(verbose_name='expense type', default=0,
                                                    db_index=True, choices=[(0, 'expense'), (1, 'asset of expense')])),
                ('status', models.IntegerField(verbose_name='status', default=0,
                                               db_index=True, choices=[(0, 'building'), (1, 'valid'), (2, 'ended')])),
                ('entries', models.ManyToManyField(
                    to='accounting.EntryAccount', verbose_name='entries')),
            ],
            options={
                'verbose_name': 'expense',
                'verbose_name_plural': 'expenses',
            },
            bases=('payoff.supporting',),
        ),
        migrations.CreateModel(
            name='ExpenseDetail',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('designation', models.TextField(verbose_name='designation')),
                ('expense_account', models.CharField(
                    verbose_name='account', max_length=50)),
                ('price', models.DecimalField(verbose_name='price', default=0.0, max_digits=10, validators=[
                 django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(9999999.999)], decimal_places=3)),
                ('expense', models.ForeignKey(on_delete=models.CASCADE,
                                              verbose_name='expense', null=True, default=None, to='condominium.Expense')),
                ('set', models.ForeignKey(verbose_name='set',
                                          on_delete=models.PROTECT, to='condominium.Set')),
            ],
            options={
                'verbose_name': 'detail of expense',
                'verbose_name_plural': 'details of expense',
                'default_permissions': [],
            },
        ),
        migrations.RunPython(initial_values),
    ]
