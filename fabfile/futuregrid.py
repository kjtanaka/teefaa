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
    '''
    call this with 
    fab -f futuregrid.py check_state:i[0-10]
    
    and it creates a whole bunch of checks for each of the specified machines
    :param noderegex:
    '''

    # tricks from gregor
    
    #todo: in general inventory is better as it maintains the inventory in
    #mongodb and contains a gui, commandline and API
    
    filename = 'private/futuregrid/nodes.yml'
    names = expand_hostlist(noderegex)

    # end tricks from gregor
    
    state = dict.fromkeys(names, {})
    execute(_check_each_state, state, hosts=nodes)
    ymlfile = fil(filename, 'w')
    yaml.dump(state, ymlfile, default_flow_style=False)
    # this could eb better managed with the cloudmesh.inventory
    

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
