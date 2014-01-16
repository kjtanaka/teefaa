#!/usr/bin/env python

import os
import time

from fabric.api import (
        cd,
        env,
        get,
        hide,
        run,
        sudo,
        task
        )
from fabric.contrib.files import (
        append,
        put
        )
from cuisine import (
        dir_ensure,
        file_append,
        file_exists,
        file_is_link,
        file_write,
        mode_sudo,
        text_strip_margin
        )

from .common import read_config

class InstallSnapshot(object):

    def __init__(self):
        # Set config
        config = read_config()
        env.host_string = config['host_config']['hostname']
        self.snapshot_file = config['snapshot_config']['snapshot_path']
        distro = config['snapshot_config']['os']['distro']
        # Create tmp dir
        self.tmp_dir = "/mnt/tmp/teefaa"
        self.squashfs = self.tmp_dir + "/filesystem.squashfs"
        self.rootimg = self.tmp_dir + "/rootimg"
        if not file_exists(self.rootimg):
            cmd = ['mkdir', '-p', self.rootimg]
            sudo(' '.join(cmd))
        cmd = ['chmod', '700', self.tmp_dir, '&&',
               'chown', '\$USER', self.tmp_dir]
        sudo(' '.join(cmd))

    def _upload_squashfs(self):
        # Download snapshot
        print("Uploading snapshot '{f}'...".format(f=self.snapshot_file))
        if not file_exists(self.squashfs):
            put(self.snapshot_file, self.squashfs)
            sudo("sync && echo 3 > /proc/sys/vm/drop_caches")

    def _mount_squashfs(self):

        print("Mounting snapshot '{f}'...".format(f=self.squashfs))
        output = sudo("df -a")
        if not self.rootimg in output:
            cmd = ['mount', '-o', 'loop', self.squashfs, self.rootimg]
            sudo(' '.join(cmd))

    def _copy_files(self):

        print("Copying system from snapshot to local disk...")
        cmd = ['rsync', '-a', '--stats', '--exclude=\'/tmp/*\'']
        cmd.append(self.rootimg + '/') 
        cmd.append('/mnt')
        sudo(' '.join(cmd))
        sudo("sync && echo 3 > /proc/sys/vm/drop_caches")

    def run(self):

        self._upload_squashfs()
        self._mount_squashfs()
        self._copy_files()


class Condition(object):

    def __init__(self):
        config = read_config()
        env.host_string = config['host_config']['hostname']
        self.distro = config['snapshot_config']['os']['distro']
        self.user = config['user_config']['username']
        self.home_dir = "/home/" + self.user
        self.authorized_keys = config['user_config']['authorized_keys_path']
        self.interfaces = config['network_config']
        self.disk_config = config['disk_config']
        self.rootimg = "/mnt"
        if not file_exists(self.rootimg + '/etc'):
            raise IOError("snapshot isn't installed yet.")

    def condition_common(self):
        
        self._condition_common_rules()
        self._condition_common_user()

    def _condition_common_rules(self):

        time.sleep(1)
        file_path = "/mnt/etc/udev/rules.d/70-persistent-net.rules"
        if file_exists(file_path):
            if not file_is_link(file_path):
                cmd = ['rm', '-rf', file_path]
                sudo(' '.join(cmd))
                cmd = ['ln', '-s', '/dev/null', file_path]
                sudo(' '.join(cmd))

    def _condition_common_user(self):

        cmd = ['chroot', self.rootimg, 'id', self.user, '||',
                'chroot', self.rootimg, 'useradd', self.user, '-m',
                '-s', '/bin/bash', '-d', self.home_dir]
        sudo(' '.join(cmd))
        with mode_sudo():
            ssh_dir = '/mnt/' + self.home_dir + '/.ssh'
            dir_ensure(ssh_dir, mode=700)
        put(self.authorized_keys, ssh_dir + '/authorized_keys',
                use_sudo=True, mode=0644)
        cmd = ['chroot', self.rootimg, 'chown', '-R', self.user,
                self.home_dir + '/.ssh']
        sudo(' '.join(cmd))

        sudo_conf = self.rootimg + '/etc/sudoers'
        append_text = "{u}   ALL=NOPASSWD:ALL".format(u=self.user)
        append(sudo_conf, append_text, use_sudo=True)

    def condition_ubuntu(self):
        print("Updating configuration...")
        self.condition_common()
        self._condition_ubuntu_hostname()
        self._condition_ubuntu_network()
        self._condition_ubuntu_resolv()
        self._condition_ubuntu_fstab()
        self._condition_ubuntu_mtab()

    def _condition_ubuntu_hostname(self):

        time.sleep(1)
        with mode_sudo():
            file_write('/mnt/etc/hostname', env.host_string)

    def _condition_ubuntu_network(self):

        text = text_strip_margin("""
        |# This file describes the network interfaces available on your system
        |# and how to activate them. For more information, see interfaces(5).
        |
        |# The loopback network interface
        |auto lo
        |iface lo inet loopback
        |""")
        file_path = "/mnt/etc/network/interfaces"
        with mode_sudo():
            file_write(file_path, text)

        for iface in self.interfaces['add']:
            print(iface + "...")
            bootp = self.interfaces['add'][iface]['bootp']
            if bootp == 'dhcp':
                text = text_strip_margin("""
                |# {iface}
                |auto {iface}
                |iface {iface} inet dhcp
                |""".format(iface=iface))
                with mode_sudo():
                    file_append(file_path, text)
            elif bootp == 'static':
                address = self.interfaces['add'][iface]['address']
                netmask = self.interfaces['add'][iface]['netmask']
                text = text_strip_margin("""
                |# {iface}
                |auto {iface}
                |iface {iface} inet static
                |  address {addr}
                |  netmask {mask}
                |""".format(iface=iface,
                    addr=address, mask=netmask))
                with mode_sudo(): 
                    file_append(file_path, text)
                try:
                    gateway = self.interfaces['add'][iface]['gateway']
                except:
                    gateway = None
                if gateway:
                    text = "  gateway {g}\n".format(g=gateway)
                    with mode_sudo():
                        file_append(file_path, text)
                try:
                    dnsserver = self.interfaces['add'][iface]['dnsserver']
                except:
                    dnsserver = None
                if dnsserver:
                    text = "  dns-nameservers {d}\n".format(d=dnsserver)
                    with mode_sudo():
                        file_append(file_path, text)
            else:
                raise TypeError("network_config: {0} is not supported.\n".format(iface))

    def _condition_ubuntu_fstab(self):

        time.sleep(1)
        file_path = "/mnt/etc/fstab"
        label_type = self.disk_config['label_type']
        device = self.disk_config['device']
        system_format = self.disk_config['system']['format']
        if label_type == 'mbr':
            num = 0
        elif label_type == 'gpt':
            num = 1
        text = text_strip_margin("""
        |# /etc/fstab: static file system information.
        |#
        |# Use 'blkid' to print the universally unique identifier for a
        |# device; this may be used with UUID= as a more robust way to name devices
        |# that works even if disks are added and removed. See fstab(5).
        |#
        |# <file system> <mount point>   <type>  <options>       <dump>  <pass>
        |proc   /proc           proc    nodev,noexec,nosuid 0       0
        |{device}{swap_num}   none            swap    sw              0       0
        |{device}{system_num}   /               {system_format}    errors=remount-ro 0       1
        |""".format(device=device,
            swap_num=num+1,
            system_num=num+2,
            system_format=system_format))
        with mode_sudo():
            file_write(file_path, text)

    def _condition_ubuntu_mtab(self):

        time.sleep(1)
        file_path = "/mnt/etc/mtab"
        label_type = self.disk_config['label_type']
        device = self.disk_config['device']
        system_format = self.disk_config['system']['format']
        if label_type == 'mbr':
            num = 0
        elif label_type == 'gpt':
            num = 1
        text = text_strip_margin("""
        |{device}{system_num} / {system_format} rw,errors=remount-ro 0 0
        |proc /proc proc rw,noexec,nosuid,nodev 0 0
        |sysfs /sys sysfs rw,noexec,nosuid,nodev 0 0
        |none /sys/fs/fuse/connections fusectl rw 0 0
        |none /sys/kernel/debug debugfs rw 0 0
        |none /sys/kernel/security securityfs rw 0 0
        |udev /dev devtmpfs rw,mode=0755 0 0
        |devpts /dev/pts devpts rw,noexec,nosuid,gid=5,mode=0620 0 0
        |tmpfs /run tmpfs rw,noexec,nosuid,size=10%,mode=0755 0 0
        |none /run/lock tmpfs rw,noexec,nosuid,nodev,size=5242880 0 0
        |none /run/shm tmpfs rw,nosuid,nodev 0 0
        |rpc_pipefs /run/rpc_pipefs rpc_pipefs rw 0 0
        |""".format(device=device,
            system_num=num+2,
            system_format=system_format))
        with mode_sudo():
            file_write(file_path, text)

    def _condition_ubuntu_resolv(self):

        file_path = "/mnt/etc/resolv.conf"
        sudo("rm -f " + file_path)
        sudo("cat /etc/resolv.conf > " + file_path)

    def run(self):
        sub_func = getattr(self, 'condition_' + self.distro)
        sub_func()


class InstallBootloader(object):

    def __init__(self):
        config = read_config()
        env.host_string = config['host_config']['hostname']
        self.device = config['disk_config']['device']
        self.bootloader_type = config['bootloader_config']['type']

    def install_bootloader_grub2(self):
        self._install_bootloader_mount_devices()
        self._install_bootloader_grub2()

    def _install_bootloader_mount_devices(self):

        with hide('stdout', 'running'):
            output = sudo("df -a")
        mpoint = "/mnt/proc"
        if not mpoint in output:
            sudo("mount -t proc proc /mnt/proc")
            time.sleep(2)
        mpoint = "/mnt/sys"
        if not mpoint in output:
            sudo("mount -t sysfs sys /mnt/sys")
            time.sleep(2)
        mpoint = "/mnt/dev"
        if not mpoint in output:
            sudo("mount -o bind /dev /mnt/dev")
            time.sleep(2)
        #mpoint = "/mnt/run"
        #if not mpoint in output:
        #    sudo("mount -o bind /run /mnt/run")
        #    time.sleep(2)

    def _install_bootloader_grub2(self):

        #cmd = ['chroot', '/mnt', 'apt-get', '-o','Dpkg::Options::=\'--force-confdef\'','-o',
        #        'Dpkg::Options::=\'--force-confold\'', '-f','-q', '-y', 'install', 'grub2']
        #sudo(' '.join(cmd))
        cmd = ['chroot', '/mnt', 'update-grub']
        sudo(' '.join(cmd))
        cmd = ['chroot', '/mnt', 'grub-install', '--recheck', self.device]
        sudo(' '.join(cmd))
        sudo("sync")

    def run(self):
        print("Installing Bootloader...")
        sub_func = getattr(self, 'install_bootloader_' + self.bootloader_type)
        sub_func()


@task
def install_snapshot():
    insnap = InstallSnapshot()
    insnap.run()

@task
def condition():
    cond = Condition()
    cond.run()

@task
def install_grub():
    inst_grub = InstallBootloader()
    inst_grub.run()
