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
from cuisine import text_strip_margin


from .libexec.make import (
        make_snapshot,
        make_iso,
        make_swap,
        make_fs
        )

class TeefaaMake(object):

    def setup(self, parser):

        make_snapshot = parser.add_parser('make-snapshot', help='Make a snapshot')
        make_snapshot.add_argument(
                '--host',
                metavar='<host_name>',
                help='Set hostname')
        make_snapshot.add_argument(
                '--ssh-config',
                metavar='</path/to/ssh-config>',
                help='Set the path to ssh-config if you have')
        make_snapshot.set_defaults(func=self.do_make_snapshot)
        make_iso = parser.add_parser('make-iso', help='Make a iso image')
        make_iso.set_defaults(func=self.do_make_iso)
        make_swap = parser.add_parser('make-swap', help='Make swap')
        make_swap.set_defaults(func=self.do_make_swap)
        make_fs = parser.add_parser('make-fs', help='Make filesystem')
        make_fs.set_defaults(func=self.do_mkfs)

    def do_make_snapshot(self, args):

        text = text_strip_margin("""
        | 
        | _|_|_|_|_|                        _|_|                      
        |    |_|      _|_|      _|_|      _|        _|_|_|    _|_|_|  
        |    |_|    _|_|_|_|  _|_|_|_|  _|_|_|_|  _|    _|  _|    _|  
        |    |_|    _|        _|          _|      _|    _|  _|    _|  
        |    |_|      _|_|_|    _|_|_|    _|        _|_|_|    _|_|_|
        |""")
        print(text)
        with hide('running', 'stdout'):
            execute(make_snapshot)

    def do_make_iso(self, args):

        execute(make_iso)

    def do_make_swap(self, args):

        execute(make_swap)

    def do_mkfs(self, args):

        execute(make_fs)

