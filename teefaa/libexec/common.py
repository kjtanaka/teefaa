#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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


@task
def check_ssh_access(limit=30):
    """
    Check ssh access...
    """
    config = read_config()
    ssh_config = config['ssh_config']
    hostname = config['host_config']['hostname']
    print(check_ssh_access.__doc__)
    time.sleep(1)
    count = 0
    result = True
    while result:
        try:
            cmd = ['ssh', '-o ConnectTimeout=5', '-F', ssh_config, hostname, 'hostname']
            local(' '.join(cmd))
            result = False
        except BaseException as e:
            count+=1
            print(str(count) + '/' + str(limit))
            if count >= limit:
                result == False
            time.sleep(10)
