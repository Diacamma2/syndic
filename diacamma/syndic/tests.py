# -*- coding: utf-8 -*-
'''
diacamma.syndic tests package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2018 sd-libre.fr
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
from shutil import rmtree

from lucterios.framework.test import LucteriosTest, add_user
from lucterios.framework.filetools import get_user_dir
from lucterios.contacts.models import Individual
from lucterios.CORE.views import get_wizard_step_list, Configuration
from lucterios.documents.views import DocumentShow

from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr
from diacamma.payoff.test_tools import default_bankaccount_fr
from diacamma.condominium.test_tools import default_setowner_fr, add_test_callfunds, add_test_expenses_fr, init_compta, add_years


class SyndicTest(LucteriosTest):

    def setUp(self):
        DocumentShow.url_text
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with12=False)
        default_bankaccount_fr()
        default_setowner_fr()
        contact = Individual.objects.get(id=5)
        contact.user = add_user('joe')
        contact.save()
        rmtree(get_user_dir(), True)
        add_years()
        init_compta()
        add_test_callfunds(False, True)
        add_test_expenses_fr(False, True)

    def test_status(self):
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/statusMenu', {}, 'get')
        self.assert_observer('core.custom', 'CORE', 'statusMenu')
        self.assert_count_equal('', 15)

    def test_wizard(self):
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        steplist = get_wizard_step_list()
        self.assertEqual(18, len(steplist.split(';')), steplist)

        self.calljson('/CORE/configurationWizard', {'steplist': steplist})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 1/18')
        self.assert_json_equal('LABELFORM', 'title', 'Diacamma Syndic')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 1})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 18)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 2/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Nos coordonnées')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 2})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 14)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 3/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Paramètres')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 3})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 9)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 4/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Liste des exercices')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 4})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 5/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Journaux')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 5})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 11)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 6/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Paramètres')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 6})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 7/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Comptes bancaires')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 7})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 8/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Moyens de paiement')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 8})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 21)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 9/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Configuration de la copropriété')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 9})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 19)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 10/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Configuration des contacts')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 10})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 11/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'associés')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 11})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 12/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Clefs secondaires')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 12})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 13/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Les propriétaires')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 13})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 11)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 14/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Les lots')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 14})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 9)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 15/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Les catégories de charges')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 15})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 9)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 16/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Paramètres de courrier')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 16})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 10)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 17/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Paramètres')

        self.calljson('/CORE/configurationWizard', {'steplist': steplist, 'step': 17})
        self.assert_observer('core.custom', 'CORE', 'configurationWizard')
        self.assert_count_equal('', 13)
        self.assert_json_equal('LABELFORM', 'progress', 'étape de progression: 18/18')
        self.assert_json_equal('LABELFORM', 'subtitle', 'Groupes et utilisateurs')

    def test_situation(self):
        self.calljson('/CORE/authentification', {'username': 'joe', 'password': 'joe'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/situationMenu', {}, 'get')
        self.assert_observer('core.custom', 'CORE', 'situationMenu')
        self.assert_count_equal('', 8)

    def test_config(self):
        self.factory.xfer = Configuration()
        self.calljson('/CORE/configuration', {}, False)
        self.assert_observer('core.custom', 'CORE', 'configuration')
        self.assert_count_equal('', 7 + 6 + 3)
        self.assert_action_equal('POST', self.json_comp["05@Adresses et Contacts_btn"]['action'],
                                 ("Modifier", 'images/edit.png', 'CORE', 'paramEdit', 0, 1, 1, {'params': ['contacts-mailtoconfig', 'contacts-createaccount', 'contacts-defaultgroup', 'contacts-size-page']}))
        self.assert_action_equal('POST', self.json_comp["60@Gestion documentaire_btn"]['action'],
                                 ("Modifier", 'images/edit.png', 'CORE', 'paramEdit', 0, 1, 1, {'params': ["documents-signature"]}))
