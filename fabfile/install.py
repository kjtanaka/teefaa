#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# tfutils - installs utilities.
#

from fabric.api import \
        task
from cuisine import \
        select_package, \
        package_ensure, \
        file_update

@task
def pxeserver():

    select_package('apt')
    package_ensure('tftpd-hpa syslinux')
    file_update('/etc/default/tftpd-hpa', _update_tftpd_conf)

def _update_tftpd_conf(conf):

    new_conf = [
            "# Defaults for tftpd-hpa",
            "RUN_DAEMON=\"yes\"",
            "OPTIONS=\"-l -s /tftpboot\"",
            ""
            ]
    return '\n'.join(new_conf)
