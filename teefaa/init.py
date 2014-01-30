#!/usr/bin/env python

import os
import time
import argparse
import subprocess

from fabric.api import execute, hide

from .libexec.init import init
from .libexec.common import print_logo

class TeefaaInit(object):

    def setup(self, parser):

        init = parser.add_parser(
                'init', 
                help="Initialize Teefaa environment")
        init.add_argument(
                'hostname',
                metavar='<hostname>',
                help="Hostname")
        init.set_defaults(func=self.do_init)

    def do_init(self, args):

        print_logo()
        if args.debug:
            execute(init, args)
        else:
            with hide('running', 'stdout'):
                execute(init, args)

