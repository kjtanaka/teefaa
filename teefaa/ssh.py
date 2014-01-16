#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import argparse
import subprocess
from fabric.api import local, execute, task, hide

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
            ssh_key = os.path.abspath(config['ssh_key'])
            cmd.append('-i ' + ssh_key)
        except:
            ssh_key = None
        print("\nssh to machine '{0}'...\n".format(hostname))
        try:
            subprocess.check_call(cmd)
            #execute(fab_ssh, ssh_config, hostname, ssh_key)
        except subprocess.CalledProcessError:
            print("SSH is disconnected...")

@task
def fab_ssh(ssh_config, hostname, ssh_key):
    cmd = ['ssh', '-F', ssh_config, hostname]
    if not ssh_key == None:
        cmd.append("-i " + ssh_key)
    with hide('running'):
        local(' '.join(cmd))
