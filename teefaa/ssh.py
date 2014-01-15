#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import argparse
import subprocess
from fabric.api import local, env

from .lib.common import read_config

class TeefaaSsh(object):

    def setup(self, parser):

        ssh = parser.add_parser(
                'ssh', 
                help="ssh to destination host")
        ssh.set_defaults(func=self.ssh)

    def ssh(self, args):

        config = read_config()
        ssh_config = config['ssh_config']
        hostname = config['host_config']['hostname']
        cmd = ['ssh', '-F', ssh_config, hostname]
        try:
            ssh_key = os.path.expanduser(config['ssh_key'])
            cmd.append('-i ' + ssh_key)
        except:
            pass
        subprocess.call(cmd)
