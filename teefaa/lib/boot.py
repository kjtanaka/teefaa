#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import time
import subprocess

from fabric.api import (
        env,
        local,
        task
        )
from fabric.contrib.files import (
        append
        )
from cuisine import (
        file_write,
        package_ensure_apt,
        package_ensure_yum,
        text_strip_margin
        )

from .common import read_config


class FabricBoot(object):

    def __init__(self):
        # Set config
        config = read_config()
        env.host_string = config['host_config']['hostname']
        self.distro = config['snapshot_config']['os']['distro']
        self.power_driver = config['host_config']['power_driver']
        self.power_driver_config = config['host_config']['power_driver_config']
        self.boot_driver = config['host_config']['boot_driver']
        self.boot_driver_config = config['host_config']['boot_driver_config']

    def power_off(self):
        """Power off"""
        sub_func = getattr(self, '_power_off_'+ self.power_driver)
        sub_func()

    def _power_off_virtualbox(self):
        """
        Power off VM (VirtualBox)
        """
        print(self._power_off_virtualbox.__doc__)
        time.sleep(1)
        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'list', 'runningvms']
        output = subprocess.check_output(cmd)
        if vbox_name in output:
            cmd = ['VBoxManage', 'controlvm', vbox_name, 'poweroff']
            subprocess.check_call(cmd)
            time.sleep(1)

    def setup_diskless_boot(self):
        """
        Set ISO Boot
        """
        sub_func = getattr(self, '_setup_diskless_boot_'+ self.boot_driver)
        sub_func()

    def _setup_diskless_boot_virtualbox(self):
        """
        Set ISO Boot (VirtualBox)
        """
        print(self._setup_diskless_boot_virtualbox.__doc__)
        time.sleep(1)

        vbox_name = self.power_driver_config['vbox_name']
        iso_file = self.boot_driver_config['iso_file']
        cmd = ['VBoxManage', 'storageattach', vbox_name, '--storagectl', 'IDE Controller', 
                '--port', '0', '--device', '1', '--type', 'dvddrive', '--medium', iso_file]
        subprocess.check_call(cmd)
        time.sleep(1)
        cmd = ['VBoxManage', 'modifyvm', vbox_name, '--boot1', 'dvd']
        subprocess.check_call(cmd)
        time.sleep(1)
        cmd = ['VBoxManage', 'modifyvm', vbox_name, '--boot2', 'disk']
        subprocess.check_call(cmd)
        time.sleep(1)

    def setup_diskboot(self):
        """
        Set local disk boot
        """
        sub_func = getattr(self, '_setup_diskboot_'+ self.boot_driver)
        sub_func()

    def _setup_diskboot_virtualbox(self):
        """
        Set local disk boot (VirtualBox)
        """
        print(self._setup_diskboot_virtualbox.__doc__)
        time.sleep(1)

        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'storageattach', vbox_name, '--storagectl', 'IDE Controller', 
                '--port', '0', '--device', '1', '--type', 'dvddrive', '--medium', 'none']
        subprocess.check_call(cmd)

    def power_on(self):
        """
        Power on
        """
        sub_func = getattr(self, '_power_on_'+ self.power_driver)
        sub_func()

    def _power_on_virtualbox(self):
        """
        Power on VM (VirtualBox)
        """
        print(self._power_on_virtualbox.__doc__)
        time.sleep(1)
        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'list', 'runningvms']
        output = subprocess.check_output(cmd)
        if not vbox_name in output:
            cmd = ['VBoxManage', 'startvm', vbox_name, '--type', 'gui']
            subprocess.check_call(cmd)
            time.sleep(1)

    def power_state(self):
        """
        Check power state
        """
        sub_func = getattr(self, '_power_state_'+ self.power_driver)
        sub_func()

    def _power_state_virtualbox(self):
        """
        Check power state (VirtualBox)
        """
        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'showvminfo', vbox_name]
        output = subprocess.check_output(cmd)
        for line in output.split('\n'):
            if line.startswith('State:'):
                print('\n ' + line + '\n')

    def boot_diskless(self):
        self.power_off()
        time.sleep(1)
        self.setup_diskless_boot()
        time.sleep(1)
        self.power_on()
        time.sleep(1)

    def boot_disk(self):
        self.power_off()
        time.sleep(1)
        self.setup_diskboot()
        time.sleep(1)
        self.power_on()
        time.sleep(1)


@task
def boot_diskless():
    fabboot = FabricBoot()
    fabboot.boot_diskless()

@task
def boot_disk():
    fabboot = FabricBoot()
    fabboot.boot_disk()

@task
def power_off():
    fabboot = FabricBoot()
    fabboot.power_off()

@task
def power_on():
    fabboot = FabricBoot()
    fabboot.power_on()

@task
def power_state():
    fabboot = FabricBoot()
    fabboot.power_state()

@task
def test_boot(func):
    fabboot = FabricBoot()
    test_func = getattr(fabboot, func)
    test_func()
