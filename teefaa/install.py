#!/usr/bin/env python
#
# Copyright 2013-2014, Indiana University
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
sub command install-*
"""

import os
import argparse
from fabric.api import execute

from .libexec.install import install_snapshot, condition, install_grub

class TeefaaInstall(object):

    def setup(self, parser):

        install_snapshot = parser.add_parser('install-snapshot', help='Install snapshot')
        install_snapshot.set_defaults(func=self.do_install_snapshot)
        condition = parser.add_parser('condition', help='Condition')
        condition.set_defaults(func=self.do_condition)
        install_grub = parser.add_parser('install-grub', help='Install grub')
        install_grub.set_defaults(func=self.do_install_grub)

    def do_install_snapshot(self, args):

        execute(install_snapshot)

    def do_condition(self, args):

        execute(condition)

    def do_install_grub(self, args):

        execute(install_grub)
