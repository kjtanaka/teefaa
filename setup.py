#!/usr/bin/env python
# -------------------------------------------------------------------------- #
# Copyright 2012-2014, Indiana University                                    #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #
from setuptools import setup, find_packages
import sys, os

version = '0.4.0'

setup(name='teefaa',
      version=version,
      description="FutureGrid: Baremetal Provisioning Toolkit",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Cloudmesh Teefaa',
      author = ['Koji Tanaka','Javier Diaz'],
      author_email = 'kj.tanaka@gmail.com',
      maintainer = ['Koji Tanaka', 'Javier Diaz', 'Gregor von Laszewski'],
      url='https://github.com/cloudmesh/teefaa',
      license='Apache Software License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "Fabric>=1.6",
	  "cuisine>=0.6",
	  "PyYAML>=3.10"
      ],
      entry_points="""
      [console_scripts]
      teefaa = teefaa.shell:main
      """,
      )

