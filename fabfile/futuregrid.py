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
    for node in nodes:
        state[node] = {}
    execute(_check_each_state, state, hosts=nodes)
    for node in nodes:
        print node + ":"
        print "    state: " + state[node]['state']
        print "    partition: " + state[node]['partition']

def _check_each_state(state):

    env.warn_only = True
    if local("ping -c 1 -W 1 %s" % env.host).failed:
        state[env.host]['state'] = 'Down'
        state[env.host]['partition'] = 'Unknown'
    else:
        state[env.host]['state'] = 'Up'
        if file_exists('/etc/fg-release'):
            state[env.host]['partition'] = run('cat /etc/fg-release')
        else:
            state[env.host]['partition'] = run('echo UNKNOWN')
