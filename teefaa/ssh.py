#!/usr/bin/env python

import os
import time
import argparse
import subprocess
from fabric.api import local, run,execute, hide, settings, env

from .libexec.common import read_config

class TeefaaSsh(object):

    def setup(self, parser):

        ssh = parser.add_parser(
                'ssh', 
                help="ssh to destination host")
        ssh.set_defaults(func=self.do_ssh)

    def do_ssh(self, args):

        self._init_ssh()
        print("\nssh to machine '{0}'...\n".format(self.hostname))
        self._check_ssh()
        cmd = ['ssh', '-o', 'PasswordAuthentication=no', 
                '-F', self.ssh_config, self.hostname]
        if self.ssh_key: cmd.append('-i' + self.ssh_key)
        try:
            subprocess.check_call(cmd)
        except:
            print("SSH is disconnected...")

    def check_ssh(self):

        self._init_ssh()
        with hide('everything'):
            self._check_ssh()

    def _init_ssh(self):

        config = read_config()
        self.ssh_config = config['ssh_config']

        self.hostname = config['host_config']['hostname']
        try:
            self.ssh_key = os.path.abspath(config['ssh_key'])
        except:
            self.ssh_key = None

    def _check_ssh(self):

        count = 1
        limit = 50
        cmd = ['ssh', '-o', 'PasswordAuthentication=no', 
                '-o', 'ConnectTimeout=5', '-F', self.ssh_config]
        if self.ssh_key: cmd.append('-i' + self.ssh_key)
        cmd.append(self.hostname)
        cmd.append('echo Confirmed $HOSTNAME is online.')
        while count < limit:
            try:
                subprocess.check_call(cmd)
                break
            except:
                time.sleep(3)
                print ("Waiting machine '{h}' to be offline. Retrying ssh... ({c}/{l})...".format(
                    h=self.hostname,c=count,l=limit))
                count += 1
                time.sleep(7)


def check_ssh():
    ts = TeefaaSsh()
    ts.check_ssh()
