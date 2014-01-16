#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
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
        boot_diskless,
        boot_disk,
        power_on,
        power_off,
        power_state
        )

class TeefaaBoot(object):

    def setup(self, parser):

        boot_diskless = parser.add_parser('boot-diskless', help='Boot without local disk')
        boot_diskless.set_defaults(func=self.do_boot_diskless)
        boot_disk = parser.add_parser('boot-disk', help='boot with local disk')
        boot_disk.set_defaults(func=self.do_boot_disk)
        power_on = parser.add_parser('power-on', help='Power on your dest-machine')
        power_on.set_defaults(func=self.do_power_on)
        power_off = parser.add_parser('power-off', help='Power off your dest-machine')
        power_off.set_defaults(func=self.do_power_off)
        power_state = parser.add_parser('power-state', help='Check power state of your dest-machine')
        power_state.set_defaults(func=self.do_power_state)

    def do_boot_diskless(self, args):

        execute(boot_diskless)

    def do_boot_disk(self, args):

        execute(boot_disk)

    def do_power_off(self, args):

        execute(power_off)

    def do_power_on(self, args):

        execute(power_on)

    def do_power_state(self, args):

        execute(power_state)
