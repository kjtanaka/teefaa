#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# futuregrid.py - collection of maintenance work scripts in FugureGrid.
#

from fabric.api import *
from fabric.contrib import *
from cuisine import *

@task
def check_state(node_prefix, start, end):

    nodes = []
    for a in range(int(start), int(end)+1 ):
        nodes.append(node_prefix + str(a))
    print nodes
    state = {}
    for node in nodes:
        state[node] = {}
    execute(_check_each_state, state, hosts=nodes)
    print state
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
        if file_exists('/etc/init.d/eucalyptus-nc'):
            state[env.host]['partition'] = 'Eucalyptus'
        else:
            state[env.host]['partition'] = 'Unknown'
