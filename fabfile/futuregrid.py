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
    state = {}
    execute(_check_each_state, state, hosts=nodes)
    for node in nodes:
        print node + ":"
        print "    partition: " + state[node]['partition']

def _check_each_state(state):

    run('hostname')
    if file_exists('/etc/fg-release'):
        state[env.host]['partition'] = run('cat /etc/fg-release')
    else:
        state[env.host]['partition'] = run('echo unknown partition')

    print "fg-release: %s" % fg_release
