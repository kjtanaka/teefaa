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
sub command make-*, mk*
"""

import os
import argparse
from fabric.api import execute, hide

from .libexec.common import print_logo
from .libexec.make import (
        make_snapshot,
        make_installer,
        make_swap,
        make_fs
        )

class TeefaaMake(object):

    def setup(self, parser):

        make_snapshot = parser.add_parser('make-snapshot', help='Make a snapshot')
        make_snapshot.set_defaults(func=self.do_make_snapshot)
        make_installer = parser.add_parser('make-installer', help='Make a iso image')
        make_installer.set_defaults(func=self.do_make_installer)
        make_swap = parser.add_parser('make-swap', help='Make swap')
        make_swap.set_defaults(func=self.do_make_swap)
        make_fs = parser.add_parser('make-fs', help='Make filesystem')
        make_fs.set_defaults(func=self.do_mkfs)

    def do_make_snapshot(self, args):

        print_logo()
        if args.debug:
            execute(make_snapshot)
        else:
            with hide('everything'):
                execute(make_snapshot)

    def do_make_installer(self, args):

        print_logo()
        if args.debug:
            execute(make_installer)
        else:
            with hide('everything'):
                execute(make_installer)

    def do_make_swap(self, args):

        execute(make_swap)

    def do_mkfs(self, args):

        execute(make_fs)

