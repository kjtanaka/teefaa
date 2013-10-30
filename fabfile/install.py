#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# tfutils - installs utilities.
#

from fabric.api import task
from fabric.operations import local, run
from cuisine import select_package, package_ensure, file_update, text_strip_margin,\
        file_append, text_ensure_line

@task
def help(function):
    """Show help of function"""
    myfunc = __name__
    local('pydoc {0}.{1}'.format(myfunc, function))

@task
def pxeserver(tftp_addr):
    """Install PXE server.
    
    Command example:
        fab install.pxeserver:tftp_addr=192.168.1.1

    Note:
        tftp_addr will set TFTP_ADDRESS in
        \"/etc/default/tftpd-hpa\"
    """
    select_package('apt')
    package_ensure("tftpd-hpa syslinux")
    tftp_conf = text_strip_margin(
            """
            |# Defaults for tftpd-hpa"
            |RUN_DAEMON=\"yes\"
            |OPTIONS=\"-l -s /tftpboot\"
            |TFTP_ADDRESS=\"{0}:69\"
            |TFTP_OPTIONS=\"--secure\"
            |""".format(tftp_addr))
    file_write('/etc/default/tftpd-hpa', tftp_conf, sudo=True)
    sudo('start tftpd-hpa||restart tftpd-hpa')

def _update_tftpd_conf(conf):
    """Update /etc/default/tftpd-hpa"""
    new_conf = text_strip_margin(
            """
            |# Defaults for tftpd-hpa"
            |RUN_DAEMON=\"yes\"
            |OPTIONS=\"-l -s /tftpboot\"
            |TFTP_OPTIONS="--secure"
            |""")
    return new_conf

@task
def nfsserver(allowed_subnet):
    """Install NFS server.
    
    Necessary valiable:
        allowed_subnet

    Example:
        fab -H localhost install.nfsserver:\'192.168.1.0/24\'
    """
    select_package('apt')
    package_ensure("nfs-kernel-server")
    file_update(
            '/etc/exports',
            lambda _:text_ensure_line(_,
                "/nfsroot  {0}(rw,no_root_squash,async,insecure,no_subtree_check)".format(allowed_subnet)
            ))
    run('exportfs -rv')


