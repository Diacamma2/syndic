# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.core.validators
from django.utils.translation import ugettext_lazy as _

from lucterios.CORE.models import Parameter

def initial_values(*args):
    param = Parameter.objects.create(
        name='condominium-frenquency', typeparam=4)
    param.title = _("condominium-frenquency")
    param.param_titles = (_("condominium-frenquency.0"),
                          _("condominium-frenquency.1"), _("condominium-frenquency.2"))    
    param.args = "{'Enum':3}"
    param.value = '0'
    param.save()

    param = Parameter.objects.create(
        name='condominium-default-owner-account', typeparam=0)
    param.title = _("condominium-default-owner-account")
    param.args = "{'Multi':False}"
    param.value = '455'
    param.save()


class Migration(migrations.Migration):

    dependencies = [
        ('payoff', '0001_initial'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('supporting_ptr', models.OneToOneField(primary_key=True, serialize=False, to='payoff.Supporting', auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('payoff.supporting',),
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=100)),
                ('budget', models.DecimalField(decimal_places=3, verbose_name='budget', max_digits=10, default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(9999999.999)])),
                ('revenue_account', models.CharField(verbose_name='revenue account', max_length=50)),
                ('cost_accounting', models.ForeignKey(to='accounting.CostAccounting', default=None, null=True, on_delete=django.db.models.deletion.PROTECT, verbose_name='cost accounting')),
            ],
            options={
                'verbose_name': 'set',
                'verbose_name_plural': 'sets',
            },
        ),
        migrations.CreateModel(
            name='Partition',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('value', models.DecimalField(decimal_places=2, verbose_name='value', max_digits=7, default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1000.0)])),
                ('owner', models.ForeignKey(to='condominium.Owner', on_delete=django.db.models.deletion.PROTECT, verbose_name='owner')),
                ('set', models.ForeignKey(to='condominium.Set', on_delete=django.db.models.deletion.PROTECT, verbose_name='set')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(initial_values),
    ]
