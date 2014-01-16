#!/usr/bin/env python
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
import envoy
from fabric.api import *
from fabric.contrib import *

def baremetal_provisioning(hostname, imagename):
    cfgfile = os.environ['TEEFAA_CONF_DIR']
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(os.path.expanduser(cfgfile))

    fab_path = cfg.get('fabric', 'path_to_fabfile')

    sys.path.append(fab_path)
    import baremetal

    status = execute(baremetal.provisioning, hostname, imagename)
    print status

    return 'OK'

def baremetal_provisioning_dev(hostname, imagename):
    cfgfile = '~/.teefaa/teefaa.yml'
    cfg = ConfigParser.SafeConfigParser()
    cfg.read(os.path.expanduser(cfgfile))

    fab_path = cfg.get('fabric', 'path_to_fabfile')

    sys.path.append(fab_path)
    import baremetal

    status = execute(baremetal.provisioning, hostname, imagename)
    print status

    return 'OK'

def main():
    '''This is just a test for now.'''
    #baremetal_provisioning('i2', 'india_openstack_v1')
    envoy.run('cd {0}'.format(os.environ['TEEFAA_DIR']))
    r = envoy.run('pwd')
    print r.std_out

if __name__ == "__main__":
 main()
