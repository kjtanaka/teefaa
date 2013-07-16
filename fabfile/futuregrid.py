#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# futuregrid.py - collection of maintenance work scripts in FugureGrid.
#

from fabric.api import *
from fabric.contrib import *
from cuisine import *
import yaml
from hostlist import expand_hostlist

@task
def check_state(noderegex):

    # tricks from gregor
    
    filename = 'private/futuregrid/nodes.yml'
    names = expand_hostlist(noderegex)

    state = dict.fromkeys(names, {})

    print state
    #execute(_check_each_state, state, hosts=nodes)
    #ymlfile = fil(filename, 'w')
    #yaml.dump(state, ymlfile, default_flow_style=False)

def _check_each_state(state):

    env.disable_known_hosts = True
    env.warn_only = True
    if local("ping -c 1 -W 1 %s" % env.host).failed:
        state[env.host]['state'] = 'Down'
        state[env.host]['partition'] = 'Unknown'
    else:
        state[env.host]['state'] = 'Up'
        if file_exists('/etc/init.d/eucalyptus-nc'):
            state[env.host]['partition'] = 'euca-nc'
        elif file_exists('/etc/init.d/pbs_mom'):
            state[env.host]['partition'] = 'hpc-compute'
        elif file_exists('/etc/init.d/nova-compute'):
            state[env.host]['partition'] = 'nova-compute'
        else:
            state[env.host]['partition'] = 'Unknown'
