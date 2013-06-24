#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# tfutils - installs utilities.
#

import os
import sys
import time
from fabric.api import *
from fabric.contrib import *
from cuisine import *

@task
def node_ensure(nodename,np,properties,note):
    ''':nodename,np,properties,note,gpus=0
    --- ensure node exists'''
    env.host_string = 'i136'
    with settings(warn_only = True):
        output = run('pbsnodes %s' % nodename)
    if output.return_code != 0:
        run('echo create node %s|qmgr' % nodename)
        time.sleep(1)
        run('echo set node %s np = %s|qmgr' % (nodename, np))
        time.sleep(1)
        run('echo set node %s properties = %s|qmgr' % (nodename, properties))
        time.sleep(1)
        run('echo set node %s note = %s|qmgr' % (nodename, note))
