#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import time
import yaml

from fabric.api import (
        env,
        hide,
        local,
        run,
        sudo,
        task
        )

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
        print("ssh_config doesn't exist in .teefaa.yml or .teefaa.local.yml", file=sys.stderr)
        exit(1)
   
    return config
