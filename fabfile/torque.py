#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# tfutils - installs utilities.
#

import os
import sys
from fabric.api import *
from fabric.contrib import *
from cuisine import *

@task
def node_ensure(nodename,np,properties,note,gpus=0):
    ''':nodename,np,properties,note,gpus=0
    --- ensure node exists'''
    env.host_string = 'i136'
    with settings(warn_only = True):
        output = run('pbsnodes %s' % nodename)
    if output.return_code != 0:
        with prefix('LANG=en_US.UTF-8'):
            run('qmgr -c \"create node %s\"' % nodename)
            run('qmgr -c \"set node %s np = %s\"' % (nodename, np))
            run('qmgr -c \"set node %s properties = %s\"' % (nodename, properties))
            run('qmgr -c \"set node %s note = %s\"' % (nodename, note))
            run('qmgr -c \"set node %s gpus = %s\"' % (nodename, gpus))
