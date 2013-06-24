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
        output = run('pbsnodes |grep ^%s |grep -v ^%s[0-9]' % (nodename, nodename))
    if output.return_code != 0:
        print 'create node'

