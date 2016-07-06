# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.utils import translation
from django.conf import settings

from lucterios.CORE.models import PrintModel


def initial_values(*args):
    translation.activate(settings.LANGUAGE_CODE)
    PrintModel().load_model("diacamma.condominium", "CallFunds_0001", is_default=True)


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
