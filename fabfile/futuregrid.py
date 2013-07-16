#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# futuregrid.py - collection of maintenance work scripts in FugureGrid.
#

from fabric.api import *
from fabric.contrib import *
from cuisine import *

@task
def check_state(nodes):

    nodes = nodes.strip().split('/')
    execute(_check_each_state, hosts=nodes)

def _check_each_state():

    run('hostname')
    if file_exists('/etc/fg-release'):
        local('cat /etc/fg-release')
    else:
        local('echo unknown partition')
