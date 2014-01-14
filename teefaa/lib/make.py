#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import time

from fabric.api import (
        cd,
        env,
        get,
        run,
        sudo,
        task
        )
from fabric.contrib.files import (
        append,
        get
        )
from cuisine import (
        dir_ensure,
        dir_exists,
        file_write,
        mode_sudo,
        package_ensure_apt,
        package_ensure_yum,
        text_strip_margin
        )

from .common import read_config

class MakeSnapshot(object):
    """Make snapshot"""
    def __init__(self):
        # Set config
        config = read_config()
        env.host_string = config['snapshot_config']['hostname']
        distro = config['snapshot_config']['os']['distro']
        try:
            self.overwrite = config['snapshot_config']['overwrite']
        except:
            self.overwrite = True
        self.save_as = config['snapshot_config']['save_as']
        self.exclude_list = config['snapshot_config']['exclude']
        self.tmp_dir = "/tmp/teefaa"
        self.user = run("echo $USER")
        self.squashed = "{tmp_dir}/filesystem.squashfs".format(tmp_dir=self.tmp_dir)
        self.rootimg = "{tmp_dir}/rootimg".format(tmp_dir=self.tmp_dir)
        # Install squashfs-tools
        pkgs = ['squashfs-tools',
                'rsync']
        if distro in ['ubuntu', 'debian']:
            for pkg in pkgs: package_ensure_apt(pkg)
        elif distro in ['centos', 'fedora']:
            for pkg in pkgs: package_ensure_yum(pkg)
        else:
            raise TypeError("Teefaa only supports ubuntu, debian, centos and fedora")
        # Create temp directory
        with mode_sudo():
            dir_ensure(self.tmp_dir, owner=self.user, mode=700)

    def _copy_system_to_tmp(self):
        # Copy system image in to temp directory
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
            sudo(' '.join(cmd))

    def _make_squashfs(self):
        # Make SquashFS
        try:
            cmd = ['ls', self.squashed]
            sudo(' '.join(cmd))
            assert(self.overwrite==False)
        except:
            cmd = ['mksquashfs', self.rootimg, self.squashed, '-noappend']
            sudo(' '.join(cmd))
            cmd = ['chown', '\$USER', self.squashed]
            sudo(' '.join(cmd))
            
    def _download_squashfs(self):
        # Download snapshot
        try:
            os.path.exists(self.save_as)
            assert(self.overwrite==False)
        except:
            get(self.squashed, self.save_as)

    def run(self):

        self._copy_system_to_tmp()
        self._make_squashfs()
        self._download_squashfs()


class MakeIso(object):

    def __init__(self):
        """Make ISO image"""
        # Set variables
        config = read_config()
        env.host_string = config['iso_config']['builder']['hostname']
        self.distro = config['iso_config']['builder']['distro']
        self.base_iso = '/tmp/' + config['iso_config']['base_iso']
        self.base_iso_url = config['iso_config']['base_iso_url']
        self.save_as = config['iso_config']['save_as']
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
        print(self._install_required_pkgs.__doc__)
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
        print(self._download_iso.__doc__)
        time.sleep(1)
        try:
            cmd = ['ls', self.base_iso, '1>/dev/null']
            sudo(' '.join(cmd))
        except:
            cmd = ['wget', self.base_iso_url, '-O', self.base_iso]
            sudo(' '.join(cmd))

    def _mount_iso(self):
        """
        Mout base image...
        """
        print(self._mount_iso.__doc__)
        time.sleep(1)
        cmd = ['ls', self.base_iso_dir, '1>/dev/null', '||', 
                'mkdir', '-p', self.base_iso_dir]
        sudo(' '.join(cmd))
        try:
            cmd = ['df', '-ha', '|', 'grep', self.base_iso_dir, '1>/dev/null']
            sudo(' '.join(cmd))
        except:
            cmd = ['mount', '-o','loop', self.base_iso, self.base_iso_dir]
            sudo(' '.join(cmd))

    def _copy_base_iso_to_new_iso(self):
        """
        Copy files from base image to new image...
        """
        print(self._copy_base_iso_to_new_iso.__doc__)
        time.sleep(1)
        # Make sure new_iso_dir exists
        cmd = ['ls', self.new_iso_dir, '||', 
                    'mkdir', '-p', self.new_iso_dir]
        sudo(' '.join(cmd))
        # Copy files to new dir
        cmd = ['rsync', '-a', '--stats', '--delete',
                '--exclude=\"/live/filesystem.squashfs\"', 
                self.base_iso_dir+'/', self.new_iso_dir.rstrip('/')]
        sudo(' '.join(cmd))

    def _mount_base_squashfs(self):
        """
        Mount base base root file system...
        """
        print(self._mount_base_squashfs.__doc__)
        time.sleep(1)
        # Make sure base_squash_dir exists
        cmd = ['ls', self.base_squashfs_dir, '||', 
                    'mkdir', '-p', self.base_squashfs_dir]
        sudo(' '.join(cmd))
        try:
            cmd = ['df', '-ha', '|', 'grep', self.base_squashfs_dir]
            sudo(' '.join(cmd))
        except:
            cmd = ['mount', '-o','loop', self.base_squashfs, self.base_squashfs_dir]
            sudo(' '.join(cmd))

    def _copy_base_squashfs_to_new_squashfs(self):
        """
        Copy files from base system to new system...
        """
        print(self._copy_base_squashfs_to_new_squashfs.__doc__)
        time.sleep(1)
        cmd = ['rsync', '-a', '--stats', '--delete',
                self.base_squashfs_dir+'/', self.new_squashfs_dir.rstrip('/')]
        sudo(' '.join(cmd))

    def _mount_proc_sys_dev(self):
        """
        Mount /proc /sys /dev...
        """
        print(self._mount_proc_sys_dev.__doc__)
        time.sleep(1)
        # Mount /proc
        try:
            cmd = ['df', '-a', '|', 'grep', self.new_squashfs_dir + '/proc']
            sudo(' '.join(cmd))
        except:
            cmd = ['mount', '-t', 'proc', 'proc', self.new_squashfs_dir + '/proc']
            sudo(' '.join(cmd))
        # Mount /sys
        try:
            cmd = ['df', '-a', '|', 'grep', self.new_squashfs_dir + '/sys']
            sudo(' '.join(cmd))
        except:
            cmd = ['mount', '-t', 'sysfs', 'sys', self.new_squashfs_dir + '/sys']
            sudo(' '.join(cmd))
        # Mount /dev
        try:
            cmd = ['df', '-a', '|', 'grep', self.new_squashfs_dir + '/dev']
            sudo(' '.join(cmd))
        except:
            cmd = ['mount', '-o', 'bind', '/dev', self.new_squashfs_dir + '/dev']
            sudo(' '.join(cmd))

    def _install_packages_in_new_image(self):
        """
        Install required packages to new image...
        """
        print(self._install_packages_in_new_image.__doc__)
        time.sleep(1)
        # Copy /etc/resolv.conf to new image's dir
        cmd = ['cp', '/etc/resolv.conf', self.new_squashfs_dir + '/etc/resolv.conf']
        sudo(' '.join(cmd))
        # Install packages
        cmd = ['chroot', self.new_squashfs_dir, 'aptitude', '-y', 'install',
                'openssh-server', 'vim', 'squashfs-tools', 'xfsprogs', 'parted']
        sudo(' '.join(cmd))

    def _create_user(self):
        """
        Create admin user...
        """
        print(self._create_user.__doc__)
        time.sleep(1)
        # Create admin user
        root_dir = self.new_squashfs_dir
        user = run("echo $USER")
        home_dir = run("echo $HOME")
        try:
            cmd = ['chroot', root_dir, 'id', user]
            sudo(' '.join(cmd))
        except:
            cmd = ['chroot', root_dir, 'useradd', user, '-m',
                    '-s', '/bin/bash', '-d', home_dir]
            sudo(' '.join(cmd))
        # Copy ~/.ssh
        try:
            cmd = ['diff', home_dir + '/.ssh/authorized_keys',
                    root_dir + home_dir + '/.ssh/authorized_keys']
            sudo(' '.join(cmd))
        except:
            cmd = ['ls', root_dir + home_dir, '||', 'mkdir', root_dir + home_dir]
            sudo(' '.join(cmd))
            cmd = ['cp', '-rp', home_dir + '/.ssh', root_dir + home_dir + '/.ssh']
            sudo(' '.join(cmd))
            cmd = ['chroot', root_dir, 'chown', '-R', user, home_dir + '/.ssh' ]
            sudo(' '.join(cmd))
        # Copy /etc/ssh
        try:
            cmd = ['diff', '/etc/ssh/ssh_host_dsa_key', 
                    root_dir + '/etc/ssh/ssh_host_dsa_key']
            sudo(' '.join(cmd))
        except:
            cmd = ['cp', '-rp', '/etc/ssh/*', root_dir + '/etc/ssh']
            sudo(' '.join(cmd))
        # Enable sudo
        config = root_dir + '/etc/sudoers'
        text = user + "   ALL=NOPASSWD:ALL"
        try:
            cmd = ['grep', '\"'+text+'\"', config ]
            sudo(' '.join(cmd))
        except:
            append(config, text, use_sudo=True)

    def _unmount_all(self):
        """
        Unmount all dir...
        """
        # Unmount /dev
        for mpoint in [ self.new_squashfs_dir + '/dev', 
                        self.new_squashfs_dir + '/sys', 
                        self.new_squashfs_dir + '/proc',
                        self.base_squashfs_dir ]:
            try:
                cmd = ['df', '-a', '|', 'grep', mpoint ]
                sudo(' '.join(cmd))
                cmd = ['umount', mpoint]
                sudo(' '.join(cmd))
            except:
                pass

    def _make_new_squashfs(self):
        """
        Make new squashfs...
        """
        try:
            cmd = ['ls', self.new_squashfs]
            sudo(' '.join(cmd))
        except:
            cmd = ['mksquashfs', self.new_squashfs_dir, 
                    self.new_squashfs, '-noappend']
            sudo(' '.join(cmd))

    def _make_new_iso(self):
        """
        Make new iso image...
        """
        new_iso = '/tmp/teefaa/custom.iso'
        try:
            cmd = ['ls', new_iso]
            sudo(' '.join(cmd))
        except:
            with cd(self.new_iso_dir):
                self._update_menu_cfg()
                self._update_md5sum()
                self._mkisofs(new_iso)
        try:
            cmd = ['ls', self.save_as]
            sudo(' '.join(cmd))
        except:
            get(new_iso, self.save_as)

    def _update_menu_cfg(self):
        """
        Update menu.cfg
        """
        menu_cfg_file = "isolinux/menu.cfg"
        new_menu_cfg = text_strip_margin("""
        |DEFAULT live
        |TIMEOUT 10
        |TOTALTIMEOUT 20
        |
        |LABEL live
        |    MENU LABEL live
        |    KERNEL /live/vmlinuz
        |    APPEND initrd=/live/initrd.img boot=live config quiet noprompt noeject
        |""")
        cmd = ['chmod', 'u+w', menu_cfg_file]
        sudo(' '.join(cmd))
        file_write(menu_cfg_file, new_menu_cfg, sudo=True)

    def _update_md5sum(self):
        """
        Update md5sum.txt
        """
        cmd = ['rm', '-f', 'md5sum.txt']
        sudo(' '.join(cmd))
        cmd = ['find', '-type', 'f', '-print0', '|', 
                'xargs', '-0', 'md5sum', '|',
                'grep', '-v', 'isolinux/boot.cat', '|', 
                'tee md5sum.txt']
        sudo(' '.join(cmd))

    def _mkisofs(self, new_iso):
        cmd = ['mkisofs', '-D', '-r', '-V', 'CustomISO', '-cache-inodes',
                '-J', '-l', '-b', 'isolinux/isolinux.bin', '-c', 
                'isolinux/boot.cat', '-no-emul-boot', '-boot-load-size', 
                '4', '-boot-info-table', '-o', new_iso, '.']
        sudo(' '.join(cmd))

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
        
        p = self.device + str(1 + self.n)
        cmd = ['mkswap', p]
        sudo(' '.join(cmd))

    def make_fs_system(self):

        p = self.device + str(2 + self.n)
        mkfs = 'mkfs.' + self.system['format']
        cmd = [mkfs, p]
        sudo(' '.join(cmd))
        time.sleep(1)

    def make_fs_data(self):

        p = self.device + str(3 + self.n)
        mkfs = 'mkfs.' + self.data['format']
        cmd = [mkfs, '-f', p]
        sudo(' '.join(cmd))
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
def make_iso():
    mkiso = MakeIso()
    mkiso.run()

@task
def make_snapshot():
    mksnap = MakeSnapshot()
    mksnap.run()

@task
def test(func):
    """
    Test functions.
    param: func - function to test.
    """
    mkiso = MakeIso()
    test_func = getattr(mkiso, func)
    test_func()
