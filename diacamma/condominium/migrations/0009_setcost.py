# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-06 13:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payoff', '0006_depositslip_status'),
        ('accounting', '0004_modelentry_costaccounting'),
        ('condominium', '0008_callfunds_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='SetCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost_accounting', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.CostAccounting', verbose_name='cost accounting')),
                ('set', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='condominium.Set', verbose_name='class load')),
                ('year', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.FiscalYear', verbose_name='fiscal year')),
            ],
            options={
                'verbose_name': 'cost of class load',
                'default_permissions': [],
                'verbose_name_plural': 'costs of class load',
                'ordering': ['year_id', 'set_id'],
            },
        ),
    ]