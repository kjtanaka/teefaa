#!/usr/bin/env python

import os
import time

from fabric.api import (
        cd,
        env,
        get,
        hide,
        local,
        put,
        run,
        sudo,
        task
        )
from fabric.contrib.files import append

from cuisine import (
        dir_ensure,
        dir_exists,
        file_ensure,
        file_exists,
        file_write,
        mode_sudo,
        package_ensure_apt,
        package_ensure_yum,
        text_strip_margin
        )

from .common import read_config, do_sudo

class MakeSnapshot(object):

    def __init__(self):
        # Set config
        config = read_config()
        env.host_string = config['snapshot_config']['hostname']
        self.distro = config['snapshot_config']['os']['distro']
        try:
            self.overwrite = config['snapshot_config']['overwrite']
        except:
            self.overwrite = True
        self.save_as = config['snapshot_config']['snapshot_path']
        try:
            self.exclude_list = config['snapshot_config']['exclude']
        except:
            self.exclude_list = None
        self.tmp_dir = "/tmp/teefaa"
        self.user = run("echo $USER")
        self.squashfs = "{tmp_dir}/filesystem.squashfs".format(tmp_dir=self.tmp_dir)
        self.rootimg = "{tmp_dir}/rootimg".format(tmp_dir=self.tmp_dir)

    def _install_required_packages(self):
        """
        Install required packages
        """
        print("Ensuring required packages are installed...")
        pkgs = ['squashfs-tools',
                'rsync']
        if self.distro in ['ubuntu', 'debian']:
            for pkg in pkgs: package_ensure_apt(pkg)
        elif self.distro in ['centos', 'fedora']:
            for pkg in pkgs: package_ensure_yum(pkg)
        else:
            raise TypeError("Teefaa only supports ubuntu, debian, centos and fedora")
        # Create temp directory
        with mode_sudo():
            dir_ensure(self.tmp_dir, owner=self.user, mode=700)

    def _copy_system_to_tmp(self):
        """
        Copy system to temp directory
        """
        print("Copying system to temp directory...")
        if not dir_exists(self.rootimg + '/etc') or self.overwrite==True:
            cmd = ['rsync', '-a', '--stats', '--delete', 
                    '--one-file-system', '--exclude=\'/tmp/*\'']
            try:
                for exclude in self.exclude_list:
                    cmd.append('--exclude=\'{exclude}\''.format(exclude=exclude))
            except:
                pass
            cmd.append('/')
            cmd.append(self.rootimg)
            do_sudo(cmd)
            # Make sure /boot is copied.
            cmd = ['rsync', '-a', '--stats', '--delete',
                    '--one-file-system', '/boot/', 
                    self.rootimg + '/boot']
            do_sudo(cmd)

    def _make_squashfs(self):
        """
        Make SquashFS of system
        """
        print("Making squashFS of system...")
        with mode_sudo():
            if not file_exists(self.squashfs) \
                    or self.overwrite==True:
                cmd = ['mksquashfs', self.rootimg, self.squashfs, '-noappend']
                run(' '.join(cmd))
                user = run("echo \$USER")
                file_ensure(self.squashfs, owner=user, mode=600)
            
    def _download_squashfs(self):
        """
        Download snapshot
        """
        print("Downloading snapshot...")
        try:
            os.path.exists(self.save_as)
            assert(self.overwrite==False)
        except:
            get(self.squashfs, self.save_as)

    def _clean_tmp(self):

        text = text_strip_margin("""
        |The system copy is still stored on /tmp/teefaa on {h}.
        |Right now, Teefaa doesn't delete it for security reason. 
        |So please go check and delete it as needed.
        |""".format(h=env.host_string))
        print(text)

    def run(self):
        """
        Make a snapshot of the system
        """
        print("Starts making a snapshot of machine '{0}'...".format(env.host_string))
        self._install_required_packages()
        self._copy_system_to_tmp()
        self._make_squashfs()
        self._download_squashfs()
        self._clean_tmp()
        text = text_strip_margin("""
        |Done...
        |
        |Snapshot is downloaded and saved as {f}.
        |""".format(f=self.save_as))
        print(text)


class MakeInstaller(object):

    def __init__(self):
        """Make ISO image"""
        # Set variables
        config = read_config()
        env.host_string = config['iso_config']['builder']['hostname']
        self.user = 'teefaa'
        self.ssh_key = config['ssh_key']
        self.distro = config['iso_config']['builder']['distro']
        self.base_iso = '/tmp/' + config['iso_config']['base_iso']
        self.base_iso_url = config['iso_config']['base_iso_url']
        self.save_as = config['iso_config']['iso_path']
        self.base_iso_dir = "/tmp/teefaa/base_iso_dir"
        self.new_iso_dir = "/tmp/teefaa/new_iso_dir"
        self.base_squashfs = self.base_iso_dir + '/live/filesystem.squashfs'
        self.base_squashfs_dir = "/tmp/teefaa/base_squashfs_dir"
        self.new_squashfs = self.new_iso_dir + '/live/filesystem.squashfs'
        self.new_squashfs_dir = "/tmp/teefaa/new_squashfs_dir"

    def _install_required_pkgs(self):
        """ 
        Ensure reuqired packages are installed...
        """
        print("Ensuring reuqired packages are installed...")
        time.sleep(1)
        # Install squashfs-tools
        pkgs = ['squashfs-tools',
                'wget',
                'genisoimage']
        if self.distro in ['ubuntu', 'debian']:
            for pkg in pkgs: package_ensure_apt(pkg)
        elif self.distro in ['centos', 'fedora']:
            for pkg in pkgs: package_ensure_yum(pkg)
        else:
            print("ERROR: Teefaa only support ubuntu, debian, centos and fedora.")
            exit(1)

    def _download_iso(self):
        """
        Download base image...
        """
        print("Downloading base image...")
        time.sleep(1)
        if not file_exists(self.base_iso):
            cmd = ['wget', self.base_iso_url, '-O', self.base_iso]
            sudo(' '.join(cmd))

    def _mount_iso(self):
        """
        Mout base image...
        """
        print("Mounting base image...")
        time.sleep(1)
        with mode_sudo():
            dir_ensure(self.base_iso_dir, recursive=True)
        output = sudo("df -a")
        if not self.base_iso_dir in output:
            cmd = ['mount', '-o','loop', self.base_iso, self.base_iso_dir]
            sudo(' '.join(cmd))

    def _copy_base_iso_to_new_iso(self):
        """
        Copy files from base image to new image...
        """
        print("Copying files from base image to new image...")
        time.sleep(1)
        # Make sure new_iso_dir exists
        with mode_sudo():
            dir_ensure(self.new_iso_dir)
        # Copy files to new dir
        cmd = ['rsync', '-a', '--stats', '--delete',
                '--exclude=\"/live/filesystem.squashfs\"', 
                self.base_iso_dir+'/', self.new_iso_dir.rstrip('/')]
        sudo(' '.join(cmd))

    def _mount_base_squashfs(self):
        """
        Mount base base root file system...
        """
        print("Mounting root filesystem of base image...")
        time.sleep(1)
        _dir = self.base_squashfs_dir
        _squashfs = self.base_squashfs
        # Make sure base_squash_dir exists
        with mode_sudo(): dir_ensure(_dir)
        _output = sudo("df -ha")
        if not _dir in _output:
            cmd = ['mount', '-o','loop', _squashfs, _dir]
            sudo(' '.join(cmd))

    def _copy_base_squashfs_to_new_squashfs(self):
        """
        Copy files from base system to new system...
        """
        print("Copying files from base system to new system...")
        _base_dir = self.base_squashfs_dir
        _new_dir = self.new_squashfs_dir
        time.sleep(1)
        cmd = ['rsync', '-a', '--stats', '--delete',
                _base_dir+'/', _new_dir.rstrip('/')]
        sudo(' '.join(cmd))

    def _mount_proc_sys_dev(self):
        """
        Mount /proc /sys /dev...
        """
        print("Mounting proc, sys, dev...")
        time.sleep(1)
        # Mount /proc
        output = sudo("df -ha")
        if not '/proc' in output:
            cmd = ['mount', '-t', 'proc', 'proc', self.new_squashfs_dir + '/proc']
            do_sudo(cmd)
        # Mount /sys
        if not '/sys' in output:
            cmd = ['mount', '-t', 'sysfs', 'sys', self.new_squashfs_dir + '/sys']
            do_sudo(cmd)
        # Mount /dev
        if not '/dev' in output:
            cmd = ['mount', '-o', 'bind', '/dev', self.new_squashfs_dir + '/dev']
            do_sudo(cmd)

    def _install_packages_in_new_image(self):
        """
        Install required packages to new image...
        """
        print("Installing required packages in new image...")
        time.sleep(1)
        #TODO: /etc/resolve.conf should be recovered after this.
        # Copy /etc/resolv.conf to new image's dir
        cmd = ['cp', '/etc/resolv.conf', self.new_squashfs_dir + '/etc/resolv.conf']
        do_sudo(cmd)
        # Install packages
        cmd = ['chroot', self.new_squashfs_dir, 'aptitude', 'update']
        do_sudo(cmd)
        cmd = ['chroot', self.new_squashfs_dir, 'aptitude', '-y', 'install',
                'openssh-server', 'vim', 'squashfs-tools', 'xfsprogs', 'parted']
        do_sudo(cmd)

    def _create_user(self):
        """
        Create admin user...
        """
        print("Creating admin user...")
        time.sleep(1)
        root_dir = self.new_squashfs_dir
        user = self.user
        home_dir = '/home/' + user
        # Create admin user
        cmd = ['grep', user, self.new_squashfs_dir + '/etc/passwd']
        output = do_sudo(cmd, warn_only=True)
        if not user in output:
            cmd = ['chroot', root_dir, 'useradd', user, '-m',
                    '-s', '/bin/bash', '-d', home_dir]
            do_sudo(cmd)
        # Copy ~/.ssh
        ssh_dir = root_dir + home_dir + '/.ssh'
        ssh_authorize = ssh_dir + '/authorized_keys'
        with mode_sudo(): 
            dir_ensure(ssh_dir, recursive=True, mode=700)
        put(self.ssh_key + '.pub', ssh_authorize, mode=0644, use_sudo=True)
        cmd = ['chroot', root_dir, 'chown', '-R', self.user, home_dir + '/.ssh']
        do_sudo(cmd)
        # Copy /etc/ssh
        text1 = do_sudo(['cat', '/etc/ssh/ssh_host_dsa_key'])
        text2 = do_sudo(['cat', root_dir+'/etc/ssh/ssh_host_dsa_key'], warn_only=True)
        if not text1 == text2:
            cmd = ['cp', '-rp', '/etc/ssh/*', root_dir + '/etc/ssh']
            do_sudo(cmd)
        # Enable sudo
        config = root_dir + '/etc/sudoers'
        text = user + "   ALL=NOPASSWD:ALL"
        cmd = ['grep', '\"'+text+'\"', config]
        output = do_sudo(cmd, warn_only=True)
        if not text in output:
            append(config, text, use_sudo=True)

    def _unmount_all(self):
        """
        Unmount all dir...
        """
        print("Unmounting all dir...")
        # Unmount /dev
        mlist = sudo("df -a")
        for mpoint in [ self.new_squashfs_dir + '/dev', 
                        self.new_squashfs_dir + '/sys', 
                        self.new_squashfs_dir + '/proc',
                        self.base_squashfs_dir ]:
            if mpoint in mlist:
                cmd = ['umount', mpoint]
                do_sudo(cmd)

    def _make_new_squashfs(self):
        """
        Make new squashfs...
        """
        print("Making new squashfs...")
        
        cmd = ['ls', self.new_squashfs]
        output = do_sudo(cmd, warn_only=True)
        if output.startswith(self.new_squashfs):
            print("New SquashFS already exists. Skip...")
        else:
            cmd = ['mksquashfs', self.new_squashfs_dir, 
                    self.new_squashfs, '-noappend']
            do_sudo(cmd)

    def _make_new_iso(self):
        """
        Make new iso image...
        """
        print("Making new iso image...")
        new_iso = '/tmp/teefaa/custom.iso'
        cmd = ['ls', new_iso]
        output = do_sudo(cmd, warn_only=True)
        if output.startswith(new_iso):
            print("New ISO image aready exists. Skip...")
        else:
            with cd(self.new_iso_dir):
                self._update_menu_cfg()
                self._update_md5sum()
                self._mkisofs(new_iso)
        print("Downloading new iso image...")
        get(new_iso, self.save_as)

    def _update_menu_cfg(self):
        """
        Update menu.cfg
        """
        menu_cfg_file = "isolinux/menu.cfg"
        new_menu_cfg = text_strip_margin("""
        |DEFAULT Teefaa
        |TIMEOUT 10
        |TOTALTIMEOUT 20
        |
        |LABEL Teefaa
        |    MENU LABEL Teefaa
        |    KERNEL /live/vmlinuz
        |    APPEND initrd=/live/initrd.img boot=live config quiet noprompt noeject
        |""")
        cmd = ['chmod', 'u+w', menu_cfg_file]
        do_sudo(cmd)
        file_write(menu_cfg_file, new_menu_cfg, sudo=True)

    def _update_md5sum(self):
        """
        Update md5sum.txt
        """
        cmd = ['rm', '-f', 'md5sum.txt']
        do_sudo(cmd)
        cmd = ['find', '-type', 'f', '-print0', '|', 
                'xargs', '-0', 'md5sum', '|',
                'grep', '-v', 'isolinux/boot.cat', '|', 
                'tee md5sum.txt']
        do_sudo(cmd)

    def _mkisofs(self, new_iso):

        cmd = ['mkisofs', '-D', '-r', '-V', 'CustomISO', '-cache-inodes',
                '-J', '-l', '-b', 'isolinux/isolinux.bin', '-c', 
                'isolinux/boot.cat', '-no-emul-boot', '-boot-load-size', 
                '4', '-boot-info-table', '-o', new_iso, '.']
        do_sudo(cmd)

    def setup(self):
        self._install_required_pkgs()
        self._download_iso()
        self._mount_iso()
        self._copy_base_iso_to_new_iso()
        self._mount_base_squashfs()
        self._copy_base_squashfs_to_new_squashfs()
        self._mount_proc_sys_dev()

    def customize(self):
        self._install_packages_in_new_image()
        self._create_user()

    def teardown(self):
        self._unmount_all()

    def epilogue(self):
        self._make_new_squashfs()
        self._make_new_iso()

    def run(self):
        self.setup()
        self.customize()
        self.teardown()
        self.epilogue()


class MakeFilesystem(object):

    def __init__(self):
        config = read_config()
        env.host_string = config['host_config']['hostname']
        self.device = config['disk_config']['device']
        self.system = config['disk_config']['system']
        self.data = config['disk_config']['data']
        label_type = config['disk_config']['label_type']
        self.n = 0
        if label_type == 'gpt': self.n += 1

    def make_swap(self):
    
        print("Making swap partition...")
        p = self.device + str(1 + self.n)
        cmd = ['mkswap', p]
        do_sudo(cmd)

    def make_fs_system(self):

        print("Making system partition...")
        p = self.device + str(2 + self.n)
        mkfs = 'mkfs.' + self.system['format']
        cmd = [mkfs, p]
        do_sudo(cmd)
        time.sleep(1)

    def make_fs_data(self):

        print("Making data partition...")
        p = self.device + str(3 + self.n)
        mkfs = 'mkfs.' + self.data['format']
        cmd = [mkfs, '-f', p]
        do_sudo(cmd)
        time.sleep(1)

    def make_fs(self):

        self.make_fs_system()
        self.make_fs_data()


@task
def make_swap():
    mf = MakeFilesystem()
    mf.make_swap()

@task
def make_fs():
    mf = MakeFilesystem()
    mf.make_fs()

@task
def make_installer():
    mkinst = MakeInstaller()
    mkinst.run()

@task
def make_snapshot():
    mksnap = MakeSnapshot()
    mksnap.run()
