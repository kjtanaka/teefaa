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
sub command provision
"""

import os
import time
import argparse
from fabric.api import execute, hide
from cuisine import text_strip_margin

from .libexec.common import print_logo
from .ssh import check_ssh
from .libexec.make import make_swap, make_fs
from .libexec.boot import boot_installer, boot_disk
from .libexec.partition import make_partition, mount_partition
from .libexec.install import install_snapshot, install_grub, condition

class TeefaaProvision(object):

    def setup(self, parser):

        provision = parser.add_parser('provision', help='Provision OS')
        provision.add_argument('--no-reboot',
                               help="No reboot at beginning/end of provisioning",
                               action="store_true")
        provision.set_defaults(func=self.do_provision)

    def do_provision(self, args):

        print_logo()
        if args.debug:
            self._do_provision()
        else:
            with hide('running', 'stdout'):
                self._do_provision(args)

    def _do_provision(self, args):

        if args.no_reboot:
            print("Starts provisioning without reboot.")
        else:
            execute(boot_installer)
        check_ssh()
        execute(make_partition)
        time.sleep(2)
        execute(make_swap)
        time.sleep(2)
        execute(make_fs)
        time.sleep(2)
        execute(mount_partition)
        time.sleep(2)
        execute(install_snapshot)
        time.sleep(2)
        execute(condition)
        time.sleep(2)
        execute(install_grub)
        time.sleep(2)
        print("Done.")
        if args.no_reboot:
            text = text_strip_margin("""
            |
            |IMPORTANT:
            | Remove Teefaa ISO image, or change PXE config
            | to boot the machine with localdisk, then reboot.
            |""")
            print(text)
        else:
            execute(boot_disk)
