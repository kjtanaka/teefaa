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

defaultconfigfile = "teefaa.conf"

def baremetal_provisioning(hostname, imagename):

def main():
    parser = argparse.ArgumentParser(prog="teefaa", formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description="FutureGrid Teefaa Dynamic Provisioning Help ")
    parser.add_argument('-H', '--host', dest="host", required=True, metavar='hostname', help='Host that will be provisioned with a new OS.')
    parser.add_argument('-C', '--conf', dest="conf", metavar='config_file', default="/opt/teefaa/etc/teefaa.conf", help='Configuration file.')
    parser.add_argument('-O', '--os', dest="os", required=True, metavar='OS', help='Name of the OS image that will be provisioned.')
    parser.add_argument('--site', dest="site", required=True, metavar='site_name', help='Name of the site.')
    
    options = parser.parse_args()    
    
    conf = os.path.expandvars(os.path.expanduser(options.conf))
    if not os.path.isfile(conf):
        print "ERROR: Configutarion file " + conf + " not found."
        sys.exit(1)    
    
    teefaaobj = Teefaa(conf, True)
    status = teefaaobj.provision(options.host, options.os, options.site)
    if status != 'OK':
        print status
    else:
        print "Teefaa provisioned the host " + options.host + " of the site " + options.site + " with the os " + options.os + " successfully"
        
if __name__ == "__main__":
    main()
