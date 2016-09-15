# -*- coding: utf-8 -*-
'''
from_v1 module for accounting

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
import sys

from django.apps import apps
from django.utils import six

from lucterios.install.lucterios_migration import MigrateAbstract
from lucterios.CORE.models import Parameter
from diacamma.accounting.from_v1 import convert_code
from lucterios.CORE.parameters import Params


class CondominiumMigrate(MigrateAbstract):

    def __init__(self, old_db):
        MigrateAbstract.__init__(self, old_db)
        self.set_list = {}
        self.owner_list = {}
        self.partition_list = {}
        self.payoff_list = {}
        self.bank_list = {}
        self.callfunds_list = {}
        self.calldetail_list = {}
        self.expense_list = {}
        self.expensedetail_list = {}
        self.default_owner_account = ""

    def _setowner(self):
        set_mdl = apps.get_model("condominium", "Set")
        set_mdl.objects.all().delete()
        self.set_list = {}
        owner_mdl = apps.get_model("condominium", "Owner")
        owner_mdl.objects.all().delete()
        self.owner_list = {}
        partition_mdl = apps.get_model("condominium", "Partition")
        partition_mdl.objects.all().delete()
        self.partition_list = {}
        cur_s = self.old_db.open()
        cur_s.execute(
            "SELECT id, nom,budget,imputationProduit,analytique  FROM fr_sdlibre_copropriete_ensemble")
        for setid, nom, budget, imputation_produit, analytique in cur_s.fetchall():
            self.print_debug("=> SET %s", (nom,))
            self.set_list[setid] = set_mdl.objects.create(
                name=nom, budget=budget, revenue_account=convert_code(imputation_produit))
            if analytique in self.old_db.objectlinks['costaccounting'].keys():
                self.set_list[setid].cost_accounting = self.old_db.objectlinks[
                    'costaccounting'][analytique]
                self.set_list[setid].save()
        cur_o = self.old_db.open()
        cur_o.execute(
            "SELECT DISTINCT tiers FROM fr_sdlibre_copropriete_partition")
        for tiers, in cur_o.fetchall():
            if tiers in self.old_db.objectlinks['third'].keys():
                self.print_debug("=> OWNER %s", (tiers,))
                self.owner_list[tiers] = owner_mdl.objects.create(
                    third=self.old_db.objectlinks['third'][tiers])
        cur_p = self.old_db.open()
        cur_p.execute(
            "SELECT id,   tiers,ensemble,part FROM fr_sdlibre_copropriete_partition")
        for partid, tiers, ensemble, part in cur_p.fetchall():
            if (tiers in self.owner_list.keys()) and (ensemble in self.set_list.keys()):
                self.print_debug(
                    "=> PARTITION %s,%s=>%s", (tiers, ensemble, part))
                self.partition_list[partid] = partition_mdl.objects.get(
                    set=self.set_list[ensemble], owner=self.owner_list[tiers])
                self.partition_list[partid].value = part
                self.partition_list[partid].save()
        for current_set in set_mdl.objects.all():
            current_set.convert_cost()

    def _callfunds(self):
        callfunds_mdl = apps.get_model("condominium", "CallFunds")
        callfunds_mdl.objects.all().delete()
        self.callfunds_list = {}
        calldetail_mdl = apps.get_model("condominium", "CallDetail")
        calldetail_mdl.objects.all().delete()
        self.calldetail_list = {}

        cur_f = self.old_db.open()
        cur_f.execute(
            "SELECT id, etat,num,date,tiers,comment  FROM fr_sdlibre_copropriete_justifs WHERE type=0")
        for callid, etat, num, date, tiers, comment in cur_f.fetchall():
            if tiers in self.owner_list.keys():
                self.print_debug(
                    "=> call of funds owner:%s - date=%s", (tiers, date))
                self.callfunds_list[callid] = callfunds_mdl.objects.create(
                    status=etat, num=num, date=date, owner=self.owner_list[tiers], comment=comment)

        cur_d = self.old_db.open()
        cur_d.execute(
            "SELECT id, designation,ensemble,montant,justifs FROM fr_sdlibre_copropriete_details")
        for detailid, designation, ensemble, montant, justifs in cur_d.fetchall():
            if (justifs in self.callfunds_list.keys()) and (ensemble in self.set_list.keys()):
                self.calldetail_list[detailid] = calldetail_mdl.objects.create(callfunds=self.callfunds_list[
                                                                               justifs], set=self.set_list[ensemble], designation=designation, price=montant)

    def _expense(self):
        entryaccount_mdl = apps.get_model("accounting", "EntryAccount")
        expense_mdl = apps.get_model("condominium", "Expense")
        expense_mdl.objects.all().delete()
        self.expense_list = {}
        expensedetail_mdl = apps.get_model("condominium", "ExpenseDetail")
        expensedetail_mdl.objects.all().delete()
        self.expensedetail_list = {}

        cur_e = self.old_db.open()
        cur_e.execute(
            "SELECT id, etat,num,date,tiers,comment,operations  FROM fr_sdlibre_copropriete_justifs WHERE type=1")
        for expenseid, etat, num, date, tiers, comment, operation in cur_e.fetchall():
            if tiers in self.old_db.objectlinks['third'].keys():
                self.print_debug(
                    "=> expense third:%s - date=%s", (tiers, date))
                self.expense_list[expenseid] = expense_mdl.objects.create(
                    status=etat, num=num, date=date, third=self.old_db.objectlinks['third'][tiers], comment=comment, expensetype=0, is_revenu=False)
                entries = []
                if operation is not None:
                    for op_item in operation.split(';'):
                        op_item = int(op_item)
                        if op_item in self.old_db.objectlinks['entryaccount'].keys():
                            entries.append(
                                self.old_db.objectlinks['entryaccount'][op_item].id)
                self.expense_list[expenseid].entries = entryaccount_mdl.objects.filter(
                    id__in=entries)
                self.expense_list[expenseid].save()

        cur_d = self.old_db.open()
        cur_d.execute(
            "SELECT id, designation,ensemble,montant,compteCharge,justifs FROM fr_sdlibre_copropriete_details")
        for detailid, designation, ensemble, montant, compte_charge, justifs in cur_d.fetchall():
            if (justifs in self.expense_list.keys()) and (ensemble in self.set_list.keys()):
                self.expensedetail_list[detailid] = expensedetail_mdl.objects.create(expense=self.expense_list[
                                                                                     justifs], set=self.set_list[ensemble], designation=designation, price=montant, expense_account=compte_charge)

    def _payoff(self):
        payoff_mdl = apps.get_model("payoff", "Payoff")
        payoff_mdl.objects.all().delete()
        bank_mdl = apps.get_model("payoff", "BankAccount")
        bank_mdl.objects.all().delete()

        cur_p = self.old_db.open()
        cur_p.execute(
            "SELECT id,tiers,date,montant,reference,compte,operation,justifs FROM fr_sdlibre_copropriete_payement")
        for payoffid, tiers, date, montant, reference, compte, operation, justifs in cur_p.fetchall():
            supporting = None
            if tiers in self.owner_list.keys():
                supporting = self.owner_list[tiers]
            elif justifs in self.expense_list.keys():
                supporting = self.expense_list[justifs]
            if supporting is not None:
                self.print_debug(
                    "=> payoff owner:%s - date=%s - amount=%.2f", (tiers, date, montant))
                self.payoff_list[payoffid] = payoff_mdl.objects.create(
                    supporting=supporting, date=date, amount=montant, reference=reference)
                if operation in self.old_db.objectlinks['entryaccount'].keys():
                    self.payoff_list[payoffid].entry = self.old_db.objectlinks[
                        'entryaccount'][operation]
                self.payoff_list[payoffid].payer = six.text_type(
                    supporting.third)
                bank_cheque = None
                if compte in self.old_db.objectlinks['chartsaccount'].keys():
                    account = self.old_db.objectlinks[
                        'chartsaccount'][compte]
                    if account.code != self.default_owner_account:
                        banks = bank_mdl.objects.filter(
                            account_code=account.code)
                        if len(banks) > 0:
                            bank_cheque = banks[0]
                        else:
                            bank_cheque = bank_mdl.objects.create(
                                designation=account.name, reference=account.name, account_code=account.code)
                if bank_cheque is not None:
                    self.payoff_list[payoffid].bank_account = bank_cheque
                    self.payoff_list[payoffid].mode = 4
                else:
                    self.payoff_list[payoffid].mode = 0
                self.payoff_list[payoffid].save(
                    do_generate=False, do_linking=False)

    def _params(self):
        cur_p = self.old_db.open()
        cur_p.execute(
            "SELECT paramName,value FROM CORE_extension_params WHERE extensionId LIKE 'fr_sdlibre_copropriete' and paramName in ('frequenceAppel','defautCompteCopro')")
        for param_name, param_value in cur_p.fetchall():
            pname = ''
            if param_name == 'defautCompteCopro':
                pname = 'condominium-default-owner-account'
                param_value = convert_code(param_value)
            if pname != '':
                self.print_debug(
                    "=> parameter of invoice %s - %s", (pname, param_value))
                Parameter.change_value(pname, param_value)
        Parameter.change_value('condominium-old-accounting', True)
        Params.clear()

    def run(self):
        try:
            self._params()
            self._setowner()
            self._callfunds()
            self._expense()
            self._payoff()
        except:
            import traceback
            traceback.print_exc()
            six.print_("*** Unexpected error: %s ****" % sys.exc_info()[0])
        self.print_info("Nb owners:%d", len(self.owner_list))
        self.print_info("Nb sets:%d", len(self.set_list))
        self.print_info("Nb calls of funds:%d", len(self.callfunds_list))
        self.print_info("Nb expenses:%d", len(self.expense_list))
