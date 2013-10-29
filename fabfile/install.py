#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# tfutils - installs utilities.
#

from cuisine import select_package, \
        package_ensure

@task
def pxeserver():

    select_package('apt')
    package_ensure('tftpd-hpa syslinux')
