#!/usr/bin/env python

import os
import time
import argparse
import subprocess

from .libexec.common import print_logo

class TeefaaInit(object):

    def setup(self, parser):

        init = parser.add_parser(
                'init', 
                help="Initialize Teefaa environment")
        init.set_defaults(func=self.do_init)

    def do_init(self, args):

        print_logo()
        print("Initializing Teefaa environment...")
