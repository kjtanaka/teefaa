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
sub command boot
"""


import os
import argparse
from fabric.api import execute

from .libexec.boot import (
        boot_installer,
        boot_disk,
        power_on,
        power_off,
        power_state,
        reboot,
        shutdown
        )

class TeefaaBoot(object):

    def setup(self, parser):

        boot_installer = parser.add_parser('boot-installer', help='Boot installer on machine')
        boot_installer.set_defaults(func=self.do_boot_installer)
        boot_disk = parser.add_parser('boot-disk', help='boot system on machine')
        boot_disk.set_defaults(func=self.do_boot_disk)
        power_on = parser.add_parser('power-on', help='Power on machine')
        power_on.set_defaults(func=self.do_power_on)
        power_off = parser.add_parser('power-off', help='Power off machine')
        power_off.set_defaults(func=self.do_power_off)
        power_state = parser.add_parser('power-state', help='Check power state of machine')
        power_state.set_defaults(func=self.do_power_state)
        power_shutdown = parser.add_parser('shutdown', help='Shutdown machine')
        power_shutdown.set_defaults(func=self.do_shutdown)
        power_reboot = parser.add_parser('reboot', help='Reboot machine')
        power_reboot.set_defaults(func=self.do_reboot)

    def do_boot_installer(self, args):

        execute(boot_installer)

    def do_boot_disk(self, args):

        execute(boot_disk)

    def do_power_off(self, args):

        execute(power_off)

    def do_power_on(self, args):

        execute(power_on)

    def do_power_state(self, args):

        execute(power_state)

    def do_shutdown(self, args):

        execute(shutdown)

    def do_reboot(self, args):

        execute(reboot)
