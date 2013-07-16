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
    execute(run, 'hostname', hosts=nodes)
