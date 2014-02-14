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
command line API
"""

__author__ = 'Koji Tanaka, Javier Diaz'

import os
import argparse
from . import (
        boot,
        init,
        install,
        make, 
        partition,
        provision,
        ssh
        )

class TeefaaShell(object):

    def setup(self):

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--debug", 
                                 help="Enable debugging",
                                 action="store_true")
        self.parser.add_argument("--config",
                                 metavar='<file>',
                                 help="Configurtion file")
        
        self.subparsers = self.parser.add_subparsers(help='sub-command help')

        commands = [boot.TeefaaBoot(),
                    init.TeefaaInit(),
                    install.TeefaaInstall(),
                    make.TeefaaMake(),
                    partition.TeefaaPartition(),
                    provision.TeefaaProvision(),
                    ssh.TeefaaSsh()]
        for command in commands:
            command.setup(self.subparsers)

    def main(self):

        self.setup()
        args = self.parser.parse_args()
        args.func(args)

def main():

    ts = TeefaaShell()
    ts.main()
