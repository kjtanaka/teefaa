#!/usr/bin/env python

import os
import time
import subprocess
import fabric.exceptions

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

        sub_func = getattr(self, '_shutdown_'+ self.power_driver)
        sub_func()

    def _shutdown_virtualbox(self):
        print("Shutting down '{h}'...".format(h=self.hostname))
        with hide('running', 'stdout'):
            try:
                sudo("shutdown -h now")
            except fabric.exceptions.NetworkError:
                print("machine is offline.")
                exit(1)
            self._ensure_power_off_virtualbox()

    def _shutdown_ipmi(self):
        print("Shutting down '{h}'...".format(h=self.hostname))
        with hide('running', 'stdout'):
            try:
                sudo("shutdown -h now")
            except fabric.exceptions.NetworkError:
                print("machine is offline.")
                exit(1)
            self._ensure_power_off_ipmi()

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
        #FNULL = open(os.devnull, 'w')
        cmd = ['ipmitool', '-I', 'lanplus', '-U', ipmi_user, '-P', ipmi_password, '-E',
                '-H', bmc_address, 'power', 'off']
        subprocess.check_call(cmd)
        self._ensure_power_off_ipmi()
        #FNULL.close()

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
            self._ensure_power_off_virtualbox()

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

    def setup_installer_boot(self):
        """
        Set ISO Boot
        """
        sub_func = getattr(self, '_setup_installer_boot_'+ self.boot_driver)
        sub_func()

    def _setup_installer_boot_virtualbox(self):
        """
        Set ISO Boot (VirtualBox)
        """

        vbox_name = self.power_driver_config['vbox_name']
        iso_file = self.boot_driver_config['iso_file']
        print("Booting Installer on '{h}'...".format(
            h=self.hostname))
        time.sleep(1)
        self._check_id_controller_virtualbox()

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

    def _check_id_controller_virtualbox(self):

        vbox_name = self.power_driver_config['vbox_name']
        storage_controller_name = "IDE Controller"
        cmd = ['VBoxManage', 'showvminfo', vbox_name]
        output = subprocess.check_output(cmd)
        if not storage_controller_name in output:
            cmd = ['VBoxManage', 'storagectl', vbox_name, 
                    '--name', storage_controller_name, '--add', 'ide']
            subprocess.check_call(cmd)

    def _setup_installer_boot_pxe(self):

        server = self.boot_driver_config['pxe_server']
        user = self.boot_driver_config['pxe_server_user']
        pxe_config = self.boot_driver_config['boot_config_file']
        pxe_config_installer = self.boot_driver_config['installer_boot_config_file']
        env.host_string = server
        env.user = user
        cmd = ['cp', pxe_config_installer, pxe_config]
        #run(' '.join(cmd))

    def setup_diskboot(self):
        """
        Set local disk boot
        """
        sub_func = getattr(self, '_setup_diskboot_'+ self.boot_driver)
        sub_func()

    def _setup_diskboot_pxe(self):

        print("Setting up boot local disk boot...")
        time.sleep(1)

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
        print("Setting up boot local disk boot...")
        time.sleep(1)
        self._check_id_controller_virtualbox()

        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'storageattach', vbox_name, '--storagectl', 'IDE Controller', 
                '--port', '0', '--device', '1', '--type', 'dvddrive', '--medium', 'none']
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            print("Machine is already set with local disk boot...")

    def power_on(self):
        """
        Power on
        """
        sub_func = getattr(self, '_power_on_'+ self.power_driver)
        sub_func()

    def _power_on_ipmi(self):

        print("Power on machine \'{host}\' ...".format(host=self.hostname))
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

    def ensure_power_off(self):
        """Power off"""
        sub_func = getattr(self, '_ensure_power_off_'+ self.power_driver)
        sub_func()

    def _ensure_power_off_virtualbox(self):

        print("Checking power is off...")
        count = 1
        limit = 50
        interval = 10
        #FNULL = open(os.devnull, 'w')
        vbox_name = self.power_driver_config['vbox_name']
        cmd = ['VBoxManage', 'list', 'runningvms']
        while count < limit:
            output = subprocess.check_output(cmd)
            if not vbox_name in output: break
            time.sleep(interval)
        if count == limit:
            raise SystemExit("Power won't be off.")
        else:
            print("Confirmed power is off...")

    def _ensure_power_off_ipmi(self):

        print("Checking power is off...")
        count = 1
        limit = 50
        interval = 10
        #FNULL = open(os.devnull, 'w')
        ipmi_password = self.power_driver_config['ipmi_password']
        ipmi_user = self.power_driver_config['ipmi_user']
        bmc_address = self.power_driver_config['bmc_address']
        cmd = ['ipmitool', '-I', 'lanplus', '-U', ipmi_user, '-P', ipmi_password, '-E',
                '-H', bmc_address, 'power', 'status']
        while count < limit:
            output = subprocess.check_output(cmd)
            if "Power is off" in output: break
            time.sleep(interval)
        if count == limit:
            raise SystemExit("Power won't be off.")
        else:
            print("Confirmed power is off...")
        #FNULL.close()

    def boot_installer(self):
        try:
            self.shutdown()
        except:
            self.power_off()
        time.sleep(1)
        self.setup_installer_boot()
        time.sleep(1)
        self.power_on()
        time.sleep(1)

    def boot_disk(self):
        try:
            self.shutdown()
        except:
            self.power_off()
        time.sleep(1)
        self.setup_diskboot()
        time.sleep(1)
        self.power_on()
        time.sleep(1)


@task
def boot_installer():
    tfboot = Boot()
    tfboot.boot_installer()

@task
def boot_disk():
    tfboot = Boot()
    tfboot.boot_disk()

@task
def power_off():
    tfboot = Boot()
    tfboot.power_off()

@task
def power_on():
    tfboot = Boot()
    tfboot.power_on()

@task
def power_state():
    tfboot = Boot()
    tfboot.power_state()

@task
def shutdown():
    tfboot = Boot()
    tfboot.shutdown()

@task
def reboot():
    tfboot = Boot()
    tfboot.reboot()

@task
def test_boot(func):
    tfboot = Boot()
    test_func = getattr(tfboot, func)
    test_func()
