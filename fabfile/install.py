#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# tfutils - installs utilities.
#

from fabric.api import task
from cuisine import select_package, package_ensure, file_update, text_strip_margin,\
        file_append

@task
def pxeserver():
    """Install PXE server"""
    select_package('apt')
    package_ensure("tftpd-hpa syslinux")
    file_update('/etc/default/tftpd-hpa', _update_tftpd_conf)

def _update_tftpd_conf(conf):
    """Update /etc/default/tftpd-hpa"""
    new_conf = text_strip_margin(
            """
            |# Defaults for tftpd-hpa",
            |RUN_DAEMON=\"yes\"",
            |OPTIONS=\"-l -s /tftpboot\"
            |""")
    return new_conf

@task
def nfsserver(allowed_subnet):
    """Install NFS server"""
    select_package('apt')
    package_ensure("nfs-kernel-server")
    file_update(
            '/etc/exports',
            lambda _:text_ensure_line(_,
                "/nfsroot  {0}(rw,no_root_squash,async,insecure)".format(allowed_subnet),
                "# just test"
            ))
