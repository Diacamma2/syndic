# -*- coding: utf-8 -*-
'''
setup module to pip integration of Diacamma syndic

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


from setuptools import setup
from diacamma.syndic import __version__

setup(
    name="diacamma-syndic",
    version=__version__,
    author="Lucterios",
    author_email="info@lucterios.org",
    url="http://www.sd-libre.fr",
    description="Condominium application.",
    long_description="""
    Condominium application with Lucterios framework.
    """,
    include_package_data=True,
    platforms=('Any',),
    license="GNU General Public License v3",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
    ],
    # Packages
    packages=["diacamma", "diacamma.syndic"],
    package_data={
        "diacamma.syndic": ['build', 'logo.gif', 'locale/*/*/*', 'help/*'],
    },
    install_requires=["lucterios ==2.0.*", "lucterios-contacts ==2.0.*",
                      "diacamma-financial >=2.0b0,<=2.0b999999999999999"],
)
