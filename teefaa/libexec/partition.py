#!/usr/bin/env python

import os
import time

from fabric.api import (
        env,
        sudo,
        task
        )
from fabric.contrib.files import (
        append
        )
from cuisine import (
        file_write,
        dir_ensure,
        mode_sudo,
        text_strip_margin
        )

from .common import read_config

class Partition(object):
    """Make snapshot"""
    def __init__(self):
        # Set config
        config = read_config()
        env.host_string = self.hostname = config['host_config']['hostname']
        self.distro = config['snapshot_config']['os']['distro']
        self.label_type = config['disk_config']['label_type']
        self.device = config['disk_config']['device']
        self.swap = config['disk_config']['swap']
        self.system = config['disk_config']['system']
        self.data = config['disk_config']['data']

    def make_partition(self):
        """
        Partition disk
        """
        sub_func = getattr(self, '_make_partition_'+ self.label_type)
        sub_func()

    def _make_partition_mbr(self):
        """
        Partition Disk with MBR(Master Boot Recorder)
        """
        print("Partition disk with MBR(Master Boot Recorder)...")
        time.sleep(1)

        # Create label
        cmd = ['parted', self.device, '--script', '--', 'mklabel', 'msdos']
        sudo(' '.join(cmd))
        time.sleep(2)

        # Set unit as MB
        cmd = ['parted', self.device, '--script', '--', 'unit', 'MB']
        sudo(' '.join(cmd))
        time.sleep(2)

        # Create swap partition
        a, b = 1, int(self.swap['size']) * 1000
        cmd = ['parted', self.device, '--script', '--', 'mkpart', 
                'primary', 'linux-swap', str(a), str(b)]
        sudo(' '.join(cmd))
        time.sleep(2)

        # Create system partition
        a, b = b, b + int(self.system['size']) * 1000
        cmd = ['parted', self.device, '--script', '--', 'mkpart', 
                'primary', str(a), str(b)]
        sudo(' '.join(cmd))
        time.sleep(2)

        # Create data partition
        if self.data['size'] == -1:
            a, b = b, -1
        else:
            a, b = b, b + int(self.data['size']) * 1000
        cmd = ['parted', self.device, '--script', '--', 'mkpart', 
                'primary', str(a), str(b)]
        sudo(' '.join(cmd))
        time.sleep(2)

        # Set boot partition
        bootid = '2'
        cmd = ['parted', self.device, '--script', '--', 'set', bootid, 'boot', 'on']
        sudo(' '.join(cmd))
        time.sleep(2)

        # Print partition table
        cmd = ['parted', self.device, '--script', '--', 'print']
        sudo(' '.join(cmd))
        time.sleep(2)
            
    def _make_partition_gpt(self):
        """
        Partition Disk with GPT(GUID Partition Table)
        """
        print("Partition disk with GPT(GUID Partition Table)...")
        time.sleep(1)

        # Create label
        cmd = ['parted', self.device, '--script', '--', 'mklabel', 'gpt']
        sudo(' '.join(cmd))
        time.sleep(2)

        # Set unit as MB
        cmd = ['parted', self.device, '--script', '--', 'unit', 'MB']
        sudo(' '.join(cmd))
        time.sleep(2)

        # Make BIOS-GRUB partiton
        cmd = ['parted', self.device, '--script', '--', 'mkpart', 
                'non-fs', '1', '3']
        sudo(' '.join(cmd))
        time.sleep(2)
        cmd = ['parted', self.device, '--script', '--', 'set', '1', 'bios_grub', 'on']
        sudo(' '.join(cmd))
        time.sleep(2)

        # Create swap partition
        a, b = 3, int(self.swap['size']) * 1000
        cmd = ['parted', self.device, '--script', '--', 'mkpart', 
                'primary', 'linux-swap', str(a), str(b)]
        sudo(' '.join(cmd))
        time.sleep(2)

        # Create system partition
        a, b = b, b + int(self.system['size']) * 1000
        cmd = ['parted', self.device, '--script', '--', 'mkpart', 
                'primary', str(a), str(b)]
        sudo(' '.join(cmd))
        time.sleep(2)

        # Create data partition
        if self.data['size'] == -1:
            a, b = b, -1
        else:
            a, b = b, b + int(self.data['size']) * 1000
        cmd = ['parted', self.device, '--script', '--', 'mkpart', 
                'primary', str(a), str(b)]
        sudo(' '.join(cmd))
        time.sleep(2)

        # Set boot partition
        bootid = '2'
        cmd = ['parted', self.device, '--script', '--', 'set', bootid, 'boot', 'on']
        sudo(' '.join(cmd))
        time.sleep(2)

        # Print partition table
        cmd = ['parted', self.device, '--script', '--', 'print']
        sudo(' '.join(cmd))
        time.sleep(2)

    def mount_partition(self):
        """
        Mount partitions
        """
        print("Mounting partitions...")
        time.sleep(1)

        if self.label_type == 'mbr':
            num = 0
        elif self.label_type == 'gpt':
            num = 1
        else:
            raise TypeError(self.label_type + " is not supprted.")
        output = sudo("df -a")
        cmd = ['swapon', self.device+str(num+1)]
        sudo(' '.join(cmd))
        cmd = ['mount', self.device+str(num+2), '/mnt']
        sudo(' '.join(cmd))
        with mode_sudo():
            dir_ensure('/mnt'+self.data['dir'], recursive=True)
        cmd = ['mount', self.device+str(num+3), '/mnt'+self.data['dir']]
        sudo(' '.join(cmd))


@task
def make_partition():
    fabpart = Partition()
    fabpart.make_partition()

@task
def mount_partition():
    fabpart = Partition()
    fabpart.mount_partition()

@task
def test_partition(func):
    fabpart = Partition()
    test_func = getattr(fabpart, func)
    test_func()
