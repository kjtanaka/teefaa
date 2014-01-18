#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import yaml
import time

from fabric.api import env, sudo, settings, hide
from cuisine import text_strip_margin

def read_config():
    """Make snapshot"""
    try:
        f = open("Teefaafile.yml")
        config = yaml.safe_load(f)
        f.close()
    except IOError:
        print("Teefaafile.yml does not exist.", file=sys.stderr)
        exit(1)

    try:
        env.key_filename = config['ssh_key']
    except KeyError:
        pass

    env.use_ssh_config = True
    env.disable_known_hosts = True
    try:
        env.ssh_config_path = os.path.expanduser(config['ssh_config'])
    except KeyError:
        print("ssh_config doesn't exist in Teefaafile.yml", file=sys.stderr)
        exit(1)

    return config

def do_sudo(cmd, warn_only=False):

    if warn_only:
        with settings(warn_only=True):
            return sudo(' '.join(cmd))
    else:
        return sudo(' '.join(cmd))

def print_logo():

    text = text_strip_margin("""
    |
    | _|_|_|_|_|                        _|_|
    |    |_|      _|_|      _|_|      _|        _|_|_|    _|_|_|
    |    |_|    _|_|_|_|  _|_|_|_|  _|_|_|_|  _|    _|  _|    _|
    |    |_|    _|        _|          _|      _|    _|  _|    _|
    |    |_|      _|_|_|    _|_|_|    _|        _|_|_|    _|_|_|
    |""")
    print(text)
    time.sleep(1)
