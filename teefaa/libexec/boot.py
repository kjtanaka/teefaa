#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import time
import subprocess

from fabric.api import (
        env,
        hide,
        local,
        task,
        run,
        sudo
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


class Boot(object):

    def __init__(self):
        # Set config
        config = read_config()
        env.host_string = self.hostname = config['host_config']['hostname']
        self.distro = config['snapshot_config']['os']['distro']
        self.power_driver = config['host_config']['power_driver']
        self.power_driver_config = config['host_config']['power_driver_config']
        self.boot_driver = config['host_config']['boot_driver']
        self.boot_driver_config = config['host_config']['boot_driver_config']

    def shutdown(self):

        print("Shutting down '{h}'...".format(h=self.hostname))
        with hide('running', 'stdout'): sudo("shutdown -h now")

    def reboot(self):
        
        print("Rebooting '{h}'...".format(h=self.hostname))
        with hide('running', 'stdout'): sudo("reboot")

    def power_off(self):
        """Power off"""
        sub_func = getattr(self, '_power_off_'+ self.power_driver)
        sub_func()

    def _power_off_ipmi(self):

        print("Power off machine \'{host}\' ...".format(host=env.host_string))
        ipmi_password = self.power_driver_config['ipmi_password']
        ipmi_user = self.power_driver_config['ipmi_user']
        bmc_address = self.power_driver_config['bmc_address']
        cmd = ['ipmitool', '-I', 'lanplus', '-U', ipmi_user, '-P', ipmi_password, '-E',
                '-H', bmc_address, 'power', 'off']
        subprocess.check_call(cmd)
        time.sleep(1)

    def _power_off_virtualbox(self):
        """
        Power off VM (VirtualBox)
        """
        print("Power off machine '{h}'...".format(h=self.hostname))
        time.sleep(1)
        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'list', 'runningvms']
        output = subprocess.check_output(cmd)
        if vbox_name in output:
            cmd = ['VBoxManage', 'controlvm', vbox_name, 'poweroff']
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
        print("Checking power state of '{h}'...".format(h=self.hostname))
        time.sleep(1)
        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'showvminfo', vbox_name]
        output = subprocess.check_output(cmd)
        for line in output.split('\n'):
            if line.startswith('State:'):
                print('\n ' + line + '\n')

    def _power_state_ipmi(self):

        print("Checking power state of machine \'{host}\' ...".format(host=env.host_string))
        ipmi_password = self.power_driver_config['ipmi_password']
        ipmi_user = self.power_driver_config['ipmi_user']
        bmc_address = self.power_driver_config['bmc_address']
        cmd = ['ipmitool', '-I', 'lanplus', '-U', ipmi_user, '-P', ipmi_password, '-E',
                '-H', bmc_address, 'power', 'status']
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

        vbox_name = self.power_driver_config['vbox_name']
        iso_file = self.boot_driver_config['iso_file']
        print("Setting machine '{h}' to boot with file '{f}'...".format(
            h=self.hostname,f=iso_file))
        time.sleep(1)

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

    def _setup_diskless_boot_pxe(self):

        server = self.boot_driver_config['pxe_server']
        user = self.boot_driver_config['pxe_server_user']
        pxe_config = self.boot_driver_config['boot_config_file']
        pxe_config_diskless = self.boot_driver_config['diskless_boot_config_file']
        env.host_string = server
        env.user = user
        cmd = ['cat', pxe_config_diskless, '>', pxe_config]
        run(' '.join(cmd))

    def setup_diskboot(self):
        """
        Set local disk boot
        """
        sub_func = getattr(self, '_setup_diskboot_'+ self.boot_driver)
        sub_func()

    def _setup_diskboot_pxe(self):

        server = self.boot_driver_config['pxe_server']
        user = self.boot_driver_config['pxe_server_user']
        pxe_config = self.boot_driver_config['boot_config_file']
        pxe_config_localdisk = self.boot_driver_config['disk_boot_config_file']
        env.host_string = server
        env.user = user
        cmd = ['cat', pxe_config_localdisk, '>', pxe_config]
        run(' '.join(cmd))

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

    def _power_on_ipmi(self):

        print("Power on machine \'{host}\' ...".format(host=env.host_string))
        ipmi_password = self.power_driver_config['ipmi_password']
        ipmi_user = self.power_driver_config['ipmi_user']
        bmc_address = self.power_driver_config['bmc_address']
        cmd = ['ipmitool', '-I', 'lanplus', '-U', ipmi_user, '-P', ipmi_password, '-E',
                '-H', bmc_address, 'power', 'on']
        subprocess.check_call(cmd)
        time.sleep(1)

    def _power_on_virtualbox(self):
        """
        Power on VM (VirtualBox)
        """
        print("Power on machine '{h}'...".format(h=self.hostname))
        time.sleep(1)
        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'list', 'runningvms']
        output = subprocess.check_output(cmd)
        if not vbox_name in output:
            cmd = ['VBoxManage', 'startvm', vbox_name, '--type', 'gui']
            subprocess.check_call(cmd)
            time.sleep(1)

    def boot_diskless(self):
        try:
            self.shutdown()
        except:
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
    fabboot = Boot()
    fabboot.boot_diskless()

@task
def boot_disk():
    fabboot = Boot()
    fabboot.boot_disk()

@task
def power_off():
    fabboot = Boot()
    fabboot.power_off()

@task
def power_on():
    fabboot = Boot()
    fabboot.power_on()

@task
def power_state():
    fabboot = Boot()
    fabboot.power_state()

@task
def shutdown():
    fabboot = Boot()
    fabboot.shutdown()

@task
def reboot():
    fabboot = Boot()
    fabboot.reboot()

@task
def test_boot(func):
    fabboot = Boot()
    test_func = getattr(fabboot, func)
    test_func()
