#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# -------------------------------------------------------------------------- #
# Copyright 2012-2013, Indiana University                                    #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #
"""
Description: Simplified Dynamic Provisioning tool in Teefaa. Installs customized images of Operating System on Bare Metal machine.  
"""
__author__ = 'Koji Tanaka, Javier Diaz'

import os
import sys
import time
import ConfigParser
import argparse
import string
from fabric.api import *
from fabric.contrib import *

def baremetal_provisioning(hostname, imagename):
    cfgfile = '~/.teefaa/teefaa.conf'
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(os.path.expanduser(cfgfile))

    sys.path.append(cfg.get('fabric', 'path_to_fabfile'))
    import baremetal

    execute(baremetal.provisioning, hostname, imagename)
    print imagename

def main():
    baremetal_provisioning('i2', 'india_openstack_v1')

if __name__ == "__main__":
    main()
