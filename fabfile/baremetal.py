#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# scratch.py - is a collection of scripts for bootstrapping baremetal/virtual machines.
# 

import os
import sys
import yaml
import time
import datetime
from platform import dist
from fabric.api import *
from fabric.contrib import *
from cuisine import *
from system import power, pxeboot, wait_till_ping, wait_till_ssh

@task
def bootstrap(hostname, imagename):
    ''':hostname,imagename  -  Bootstrap OS'''

    env.host_string = hostname
    env.disable_known_hosts = True
    if not env.user == 'root':
        print 'You need to login as root for bootstrap.'
        print 'So add the option \"--user root\"'
        exit(1)

    host = read_ymlfile('hosts/%s.yml' % hostname)
    image = read_ymlfile('images/%s.yml' % imagename)

    if image['os'] == 'centos6' or \
            image['os'] == 'redhat6':
        bp = BaremetalProvisioningRedHat6(host, image)
    elif image['os'] == 'centos5' or \
            image['os'] == 'redhat5':
        bp = BaremetalProvisioningRedHat5(host, image)
    elif image['os'] == 'ubuntu12' or \
            image['os'] == 'ubuntu13':
        bp = BaremetalProvisioningUbuntu(host, image)
    else:
        print "ERROR: %s is not supported yet."
        exit(1)

    bp.partitioning()
    bp.makefs()
    bp.mountfs()
    bp.copyimg()
    bp.condition()
    bp.install_bootloader()

@task
def provisioning(hostname, imagename):
    ''':hostname,imagename | Provisioning'''
    env.disable_known_hosts = True
    pxeboot(hostname, 'netboot')
    power(hostname, 'off')
    power(hostname, 'wait_till_off')
    power(hostname, 'on')
    power(hostname, 'wait_till_on')
    wait_till_ping(hostname, '100')
    wait_till_ssh(hostname, '100')
    bootstrap(hostname, imagename)
    pxeboot(hostname, 'localboot')
    
class BaremetalProvisioning:

    def __init__(self, host, image):
        self.host = host
        self.image = image
        self.device = image['disk']['device']
        self.swap = image['disk']['partitions']['swap']
        self.system = image['disk']['partitions']['system']
        self.data = image['disk']['partitions']['data']
        self.scheme = image['partition_scheme']
        self.bootloader = image['boot']['bootloader']
    
    def partitioning(self):
        '''partitioning'''
        run('aptitude update')
        package_ensure('parted')
        if self.scheme == 'mbr':
            run('parted %s --script -- mklabel msdos' % self.device)
            run('parted %s --script -- unit MB' % self.device)
            a, b = 1, int(self.swap['size']) * 1000
            run('parted %s --script -- mkpart primary linux-swap %s %s' % (self.device, a, b))
            bootid = 2
        elif self.scheme == 'gpt':
            run('parted %s --script -- mklabel gpt' % self.device)
            run('parted %s --script -- unit MB' % self.device)
            run('parted %s --script -- mkpart non-fs 1 3' % self.device)
            a, b = 3, int(self.swap['size']) * 1000
            run('parted %s --script -- mkpart swap linux-swap %s %s' % (self.device, a, b))
            run('parted %s --script -- set 1 bios_grub on' % self.device)
            bootid = 3
        else: 
            print 'ERROR: scheme %s is not supported.' % self.scheme
            exit(1)
        a, b = b, b + int(self.system['size']) * 1000
        run('parted %s --script -- mkpart primary %s %s' % (self.device, a, b))
        if self.data['size'] == '-1':
            a, b = b, -1
        else:
            a, b = b, b + int(self.data['size']) * 1000
        run('parted %s --script -- mkpart primary %s %s' % (self.device, a, b))
        run('parted %s --script -- set %s boot on' % (self.device, bootid))
        run ('parted %s --script -- print' % self.device)

    def makefs(self):
        '''Make Filesytem'''
        pnum = 1
        if self.scheme == 'gpt':
            pnum += 1
        package_ensure('xfsprogs')
        run('mkswap %s%s' % (self.device, pnum))
        pnum += 1
        if self.system['type'] == 'ext3' or \
                self.system['type'] == 'ext4':
            run('mkfs.%s %s%s' % (self.system['type'], self.device, pnum))
        else:
            print "%s is not supported for system partition" % self.system['type']
            exit(1)
        pnum += 1
        if self.data['type'] == 'ext3' or \
                self.data['type'] == 'ext4':
            run('mkfs.%s %s%s' % (self.data['type'], self.device, pnum))
        elif self.data['type'] == 'xfs':
            run('mkfs.%s -f %s%s' % (self.data['type'], self.device, pnum))
        else:
            print "%s is not supported for data partition" % self.data['type']
            exit(1)

    def mountfs(self):
        '''Mount Filesystem'''
        pnum = 1
        if self.scheme == 'gpt':
            pnum += 1
        run('swapon %s%s' % (self.device, pnum))
        pnum += 1
        run('mount %s%s /mnt' % (self.device, pnum))
        if not file_exists('/mnt%s' % self.data['mount']):
            run('mkdir -p /mnt%s' % self.data['mount'])
        pnum += 1
        run('mount %s%s /mnt%s' % (self.device, pnum, self.data['mount']))

    def copyimg(self):
        '''Copy image'''
        remote = self.image['osimage']
        local = "/mnt/osimage.%s" % self.image['extension']
        method = self.image['method']
        mount = "/root/osimage"
    
        if method == "put":
            put(remote, local)
        elif method == "scp":
            run("scp %s %s" % (remote, local))
        elif method == "wget":
            run("wget %s -O %s" % (remote, local))
        elif method == "rsync":
            run("rsync -a --stats --one-file-system %s/ /mnt" % remote)
            run("rsync -a --stats --one-file-system %s/boot/ /mnt/boot" % remote)
        elif method == "btsync":
            run("mkdir -p /mnt/BTsync")
            run("ln -s /mnt/BTsync /BTsync")
            self.make_btsync_seed()
            count = 0
            while not file_exists(self.image['osimage']):
                time.sleep(30)
                print "Waiting for the image to be ready... %s/20" % count
                count += 1
                if count > 41:
                    print "ERROR: give up waiting btsync ready."
                    exit(1)
            local = self.image['osimage']
        else:
            print "Error: method %s is not supported" % method
            exit(1)
    
        if not method == "rsync":
            if not file_exists(mount):
                run('mkdir -p %s' % mount)
            if self.image['extension'] == "tar.gz":
                run('tar zxvf %s -C /mnt' % local)
            elif self.image['extension'] == "squashfs" or \
                    self.image['extension'] == "img" or \
                    self.image['extension'] == "qcow2":
                run('mount %s %s -o loop' % (local, mount))
                run('rsync -a --stats %s/ /mnt' % mount)
                run('umount %s' % mount)
            else:
                print "Extension %s is not supported." % self.image['extension']
                exit(1)
            run('rm -f %s' % local)

    def file_sed(self, filename, old, new):

        file_update(filename, lambda x: text_replace_line(x, old, new)[0])
    
    def make_btsync_seed(self):
        ''':hostname,btcfg,btsync | Make a seed of Bittorrent Sync'''
        btcfg, btsync = self.image['btcfg'], self.image['btbin']
        if not file_is_dir('/BTsync/image'):
            run('mkdir -p /BTsync/image')
        put(btcfg, '/BTsync/btsync.conf')
        put(btsync, '/BTsync/btsync', mode=755)
        #self.file_sed('/BTsync/btsync.conf', 'DEVNAME', self.host)
        run('/BTsync/btsync --config /BTsync/btsync.conf')

class BaremetalProvisioningRedHat6(BaremetalProvisioning):
    
    def __init__(self, host, image):
        BaremetalProvisioning.__init__(self, host, image)

    def condition(self):
        '''Condition config files for Redhat6'''
        # Update fstab, mtab, selinux and udev/rules
        put(share_dir() + '/etc/fstab.' + self.image['os'], '/mnt/etc/fstab')
        put(share_dir() + '/etc/mtab.' + self.image['os'], '/mnt/etc/mtab')
        if self.image['boot']['kernel_type'] == 'kernel':
            put(share_dir() + '/boot/grub/grub.conf.' + self.image['os'], '/mnt/boot/grub/grub.conf')
        elif self.image['boot']['kernel_type'] == 'kernel-xen':
            put(share_dir() + '/boot/grub/grub.conf.' + self.image['os'] + '.xen', '/mnt/boot/grub/grub.conf')
            self.file_sed('/mnt/boot/grub/grub.conf', 'MODULE', self.image['boot']['module'])
        else:
            print "ERROR: kernel_type %s is not supported."
            exit(1)
        data = self.data
        if data['mount']:
            if data['type'] == 'xfs':
                file_append('/mnt/etc/fstab', \
                        'DEVICE3 %s xfs defaults,noatime 0 0' % data['mount'])
            elif data['type'] == 'ext4' or \
                    data['type'] == 'ext3':
                file_append('/mnt/etc/fstab', \
                        'DEVICE3 %s %s defaults 0 0' % (data['mount'], data['type']))
            else:
                print "ERROR: system type %s is not supported." % data['type']
                exit(1)
        if self.scheme == 'gpt':
            for a in 4,3,2:
                b = a - 1
                self.file_sed('/mnt/etc/fstab', 'DEVICE%s' % b, 'DEVICE%s' % a)
                self.file_sed('/mnt/etc/mtab', 'DEVICE%s' % b, 'DEVICE%s' % a)
                self.file_sed('/mnt/boot/grub/grub.conf', 'DEVICE%s' % b, 'DEVICE%s' % a)
        self.file_sed('/mnt/etc/fstab', 'DEVICE', self.device)
        self.file_sed('/mnt/etc/mtab', 'DEVICE', self.device)
        if self.image['fstab_append']:
            for item in self.image['fstab_append_list']:
                file_append('/mnt/etc/fstab', item)
        put(share_dir() + '/etc/selinux/config', '/mnt/etc/selinux/config')
        run('rm -f /mnt/etc/udev/rules.d/70-persistent-net.rules')
        run('rm -f /mnt/etc/sysconfig/network-scripts/ifcfg-eth*')
        run('rm -f /mnt/etc/sysconfig/network-scripts/ifcfg-ib*')
        # Disable ssh password login
        self.file_sed('/mnt/etc/ssh/sshd_config', 'PasswordAuthentication yes', 'PasswordAuthentication no')
        self.file_sed('/mnt/etc/ssh/sshd_config', '#PasswordAuthentication no', 'PasswordAuthentication no')
        # Update Grub Configuration
        self.file_sed('/mnt/boot/grub/grub.conf', 'KERNEL', self.image['boot']['kernel'])
        self.file_sed('/mnt/boot/grub/grub.conf', 'RAMDISK', self.image['boot']['ramdisk'])
        self.file_sed('/mnt/boot/grub/grub.conf', 'OSNAME', self.image['os'])
        self.file_sed('/mnt/boot/grub/grub.conf', 'DEVICE', self.device)
        # Update Hostname
        file = '/mnt/etc/sysconfig/network'
        run('rm -f %s' % file)
        file_append(file, 'HOSTNAME=%s' % self.host['hostname'])
        file_append(file, 'NETWORKING=yes')
        # Update Network Interfaces
        for iface in self.host['network']:
            iface_conf = self.host['network'][iface]
            file = '/mnt/etc/sysconfig/network-scripts/ifcfg-%s' % iface
            #run('rm -f %s' % file)
            file_append(file, 'DEVICE=%s' % iface)
            file_append(file, 'BOOTPROTO=%s' % iface_conf['bootproto'])
            file_append(file, 'ONBOOT=%s' % iface_conf['onboot'])
            if iface_conf['bootproto'] == 'dhcp':
                pass
            elif iface_conf['bootproto'] == 'static' or \
                    iface_conf['bootproto'] == 'none':
                file_append(file, 'IPADDR=%s' % iface_conf['ipaddr'])
                file_append(file, 'NETMASK=%s' % iface_conf['netmask'])
                if iface_conf['gateway']:
                    file_append(file, 'GATEWAY=%s' % iface_conf['gateway'])
            else:
                print "ERROR: bootproto = %s is not supported."
                exit(1)
        # Delete key pair
        #if host['del_keypair']:
    
        # Update Authorized Keys
        if self.host['update_keys']:
            if not file_exists('/mnt/root/.ssh'):
                run('mkdir -p /mnt/root/.ssh')
                run('chmod 700 /mnt/root/.ssh')
            file = '/mnt/root/.ssh/authorized_keys'
            run('rm -f %s' % file)
            for key in self.host['pubkeys']:
                file_append(file, '%s' % self.host['pubkeys'][key])
            run('chmod 640 %s' % file)

    def install_bootloader(self):
        '''Install Grub'''
        run('mount -t proc proc /mnt/proc')
        run('mount -t sysfs sys /mnt/sys')
        run('mount -o bind /dev /mnt/dev')
        if self.image['rootpass'] == "reset":
            run('chroot /mnt usermod -p \'\' root')
            run('chroot /mnt chage -d 0 root')
        elif self.image['rootpass'] == "delete":
            run('chroot /mnt passwd --delete root')
        run('chroot /mnt grub-install %s --recheck' % self.device)
        run('sync')
        run('reboot')

class BaremetalProvisioningRedHat5(BaremetalProvisioningRedHat6):

    def __init__(self, host, image):
        BaremetalProvisioning.__init__(self, host, image)

    def install_bootloader(self):
        '''Install Grub'''
        run('mount -t proc proc /mnt/proc')
        run('mount -t sysfs sys /mnt/sys')
        run('mount -o bind /dev /mnt/dev')
        if self.image['rootpass'] == "reset":
            run('chroot /mnt usermod -p \'\' root')
            run('chroot /mnt chage -d 0 root')
        elif self.image['rootpass'] == "delete":
            run('chroot /mnt passwd --delete root')
        run('grub-install --root-directory=/mnt %s' % self.device)
        run('sync')
        run('reboot')

class BaremetalProvisioningUbuntu(BaremetalProvisioning):

    def __init__(self, host, image):
        BaremetalProvisioning.__init__(self, host, image)

    def condition(self):
        '''Condition config files for Redhat6'''
        # Update fstab, mtab, selinux and udev/rules
        put(share_dir() + '/etc/fstab.' + self.image['os'], '/mnt/etc/fstab')
        put(share_dir() + '/etc/mtab.' + self.image['os'], '/mnt/etc/mtab')
        data = self.data
        if data['mount']:
            if data['type'] == 'xfs':
                file_append('/mnt/etc/fstab', \
                        'DEVICE3 %s xfs defaults,noatime 0 0' % data['mount'])
            elif data['type'] == 'ext4' or \
                    data['type'] == 'ext3':
                file_append('/mnt/etc/fstab', \
                        'DEVICE3 %s %s defaults 0 0' % (data['mount'], data['type']))
            else:
                print "ERROR: system type %s is not supported." % data['type']
                exit(1)
        if self.scheme == 'gpt':
            for a in 4,3,2:
                b = a - 1
                self.file_sed('/mnt/etc/fstab', 'DEVICE%s' % b, 'DEVICE%s' % a)
                self.file_sed('/mnt/etc/mtab', 'DEVICE%s' % b, 'DEVICE%s' % a)
        self.file_sed('/mnt/etc/fstab', 'DEVICE', self.device)
        self.file_sed('/mnt/etc/mtab', 'DEVICE', self.device)
        if self.image['fstab_append']:
            for item in self.image['fstab_append_list']:
                file_append('/mnt/etc/fstab', item)
        run('rm -f /mnt/etc/udev/rules.d/70-persistent-net.rules')
        # Disable ssh password login
        self.file_sed('/mnt/etc/ssh/sshd_config', 'PasswordAuthentication yes', 'PasswordAuthentication no')
        self.file_sed('/mnt/etc/ssh/sshd_config', '#PasswordAuthentication no', 'PasswordAuthentication no')
        # Disable cloud-init
        for file in [
                '/mnt/etc/init/cloud-config.conf',
                '/mnt/etc/init/cloud-final.conf',
                '/mnt/etc/init/cloud-init.conf',
                '/mnt/etc/init/cloud-init-container.conf',
                '/mnt/etc/init/cloud-init-local.conf',
                '/mnt/etc/init/cloud-init-nonet.conf',
                '/mnt/etc/init/cloud-log-shutdown.conf'
                ]:
            if file_is_file(file):
                run('mv %s %s.bak' % (file, file))
        # Update hostname
        file = '/mnt/etc/hostname'
        run('rm -f %s' % file)
        file_append(file, '%s' % self.host['hostname'])
        # Update network interface
        file = '/mnt/etc/network/interfaces'
        run('rm -f %s' % file)
        file_append(file, 'auto lo')
        file_append(file, 'iface lo inet loopback')
        for iface in self.host['network']:
            iface_conf = self.host['network'][iface]
            file_append(file, '# Interface %s' % iface)
            file_append(file, 'auto %s' % iface)
            file_append(file, 'iface %s inet %s' % (iface, iface_conf['bootproto']))
            if iface_conf['bootproto'] == 'dhcp':
                pass
            elif iface_conf['bootproto'] == 'static':
                file_append(file, 'address %s' % iface_conf['ipaddr'])
                file_append(file, 'netmask %s' % iface_conf['netmask'])
                if iface_conf['gateway']:
                    file_append(file, 'gateway %s' % iface_conf['gateway'])
                if iface_conf['nameserver']:
                    file_append(file, 'dns-nameservers %s' % iface_conf['nameserver'])
        # Generate ssh host key if it doesn't exist.
        run('rm -f /mnt/etc/ssh/ssh_host_*')    
        run('ssh-keygen -t rsa -N "" -f /mnt/etc/ssh/ssh_host_rsa_key')
        # Update authorized_keys.
        if self.host['update_keys']:
            if not file_exists('/mnt/root/.ssh'):
                run('mkdir -p /mnt/root/.ssh')
                run('chmod 700 /mnt/root/.ssh')
            file = '/mnt/root/.ssh/authorized_keys'
            run('rm -f %s' % file)
            for key in self.host['pubkeys']:
                file_append(file, '%s' % self.host['pubkeys'][key])
            run('chmod 640 %s' % file)
    
    def install_bootloader(self):
        '''Install Grub'''
        run('mount -t proc proc /mnt/proc')
        run('mount -t sysfs sys /mnt/sys')
        run('mount -o bind /dev /mnt/dev')
        run('chroot /mnt update-grub')
        if self.image['rootpass'] == "reset":
            run('chroot /mnt usermod -p \'\' root')
            run('chroot /mnt chage -d 0 root')
        elif self.image['rootpass'] == "delete":
            run('chroot /mnt passwd --delete root')
        run('chroot /mnt grub-install %s --recheck' % self.device)
        run('sync')
        run('reboot')

@task
def make_btsync_seed(hostname, btcfg, btsync):
    ''':hostname,btcfg,btsync | Make a seed of Bittorrent Sync'''
    env.host_string = hostname
    if not file_is_dir('/BTsync/image'):
        run('mkdir -p /BTsync/image')
    put(btcfg, '/BTsync/btsync.conf')
    put(btsync, '/BTsync/btsync', mode=755)
    self.file_sed('/BTsync/btsync.conf', 'DEVNAME', hostname)
    run('/BTsync/btsync --config /BTsync/btsync.conf')

@task
def make_livecd(livecd_name, livecd_cfg='ymlfile/scratch/livecd.yml'):
    ''':livecd_name,livecd_cfg=ymlfile/scratch/livecd.yml | Make LiveCD'''
    livecd = read_ymlfile('livecd.yml')[livecd_name]

    packages = [
            'wget',
            'genisoimage',
            'squashfs-tools'
            ]
    for package in packages:
        package_ensure(package)
    run('wget %s -O /tmp/livecd.iso' % livecd['isoimage'])
    if not file_is_dir('/mnt/tfmnt'):
        run('mkdir /mnt/tfmnt')
    run('mount /tmp/livecd.iso /mnt/tfmnt -o loop')
    run('rsync -a --stats /mnt/tfmnt/ /tmp/imgdir')
    run('umount /mnt/tfmnt')
    run('mount -o loop /tmp/imgdir/live/filesystem.squashfs /mnt/tfmnt')
    run('rsync -a --stats /mnt/tfmnt/ /tmp/rootimg')
    run('umount /mnt/tfmnt')
    run('cat /etc/resolv.conf > /tmp/rootimg/etc/resolv.conf')
    run('mount -t proc proc /tmp/rootimg/proc')
    run('mount -t sysfs sys /tmp/rootimg/sys')
    run('mount -o bind /dev /tmp/rootimg/dev')
    run('chroot /tmp/rootimg aptitude update')
    run('chroot /tmp/rootimg aptitude -y install openssh-server vim squashfs-tools tree xfsprogs parted')
    run('chroot /tmp/rootimg ssh-keygen -N "" -C "root@teefaa" -f /root/.ssh/id_rsa')
    run('chroot /tmp/rootimg ssh-keygen -t rsa1 -N "" -C "ssh_host_rsa_key" -f /etc/ssh/ssh_host_rsa_key')
    run('chroot /tmp/rootimg ssh-keygen -t dsa -N "" -C "ssh_host_dsa_key" -f /etc/ssh/ssh_host_dsa_key')
    file = '/tmp/rootimg/root/.ssh/authorized_keys'
    for key in livecd['pubkeys']:
        file_append(file, '%s' % livecd['pubkeys'][key])
    run('chmod 640 %s' % file)
    run('umount /tmp/rootimg/proc /tmp/rootimg/sys /tmp/rootimg/dev')
    run('mksquashfs /tmp/rootimg /tmp/imgdir/live/filesystem.squashfs -noappend')
    put('live/menu.cfg', '/tmp/imgdir/isolinux/menu.cfg')
    with cd('/tmp/imgdir'):
        run('rm -f md5sum.txt')
        run('find -type f -print0 | xargs -0 md5sum | \
                grep -v isolinux/boot.cat | tee md5sum.txt')
        run('mkisofs -D -r -V "Teefaa Messenger" -cache-inodes \
                -J -l -b isolinux/isolinux.bin -c isolinux/boot.cat \
                -no-emul-boot -boot-load-size 4 -boot-info-table \
                -o /tmp/%s.iso .' % livecd_name)
    get('/tmp/%s.iso' % livecd_name, livecd['saveto'])

@task
def make_pxeimage(pxename):
    ''':pxename'''
    pxecfg = read_ymlfile('pxe.yml')[pxename]
    prefix = pxecfg['prefix']

    #put(pxecfg['livecd'], '/tmp/livecd.iso')
    if not file_is_dir('/mnt/tfmnt'):
        run('mkdir /mnt/tfmnt')
    run('mount /tmp/livecd.iso /mnt/tfmnt -o loop')
    expdir = prefix['export']
    if not file_is_dir(expdir):
        run('mkdir -p %s' % expdir)
    run('rsync -a --stats /mnt/tfmnt/ %s/%s' % (expdir, pxename))
    run('umount /mnt/tfmnt')
    tftpdir = prefix['tftpdir']
    if not file_is_dir('%s/%s' % (tftpdir, pxename)):
        run('mkdir -p %s/%s' % (tftpdir, pxename))
    run('cp %s/%s/live/initrd.img %s/%s/initrd.img' \
                % (expdir, pxename, tftpdir, pxename))
    run('cp %s/%s/live/vmlinuz %s/%s/vmlinuz' \
                % (expdir, pxename, tftpdir, pxename))
    pxefile = '%s/%s' % (prefix['pxelinux_cfg'], pxename)
    put('live/pxefile', pxefile)
    self.file_sed(pxefile, 'PXENAME', pxename)
    self.file_sed(pxefile, 'EXPDIR', expdir)
    self.file_sed(pxefile, 'PXESERVER', pxecfg['nfs_ip'])

@task
def mksnapshot(name, saveto):
    ''':name,saveto  -  Make Snapshot'''
    today = datetime.date.today
    distro = run('python -c "import platform; print platform.dist()[0].lower()"')
    print distro
    if distro == 'centos' or \
            distro == 'redhat':
        package_ensure_yum('squashfs-tools')
    elif distro == 'ubuntu' or \
            distro == 'debian':
        package_ensure_apt('squashfs-tools')
    else:
        print 'ERROR: distro %s is not supported.' % distro
        exit(1)
    workdir = '/root/TFROOTIMG-%s' % today()
    run('mkdir -p %s' % workdir)
    run('rsync -a --stats --one-file-system --exclude=%s / %s' \
            % (workdir.lstrip('/'), workdir))
    run('rsync -a --stats --one-file-system /var/ %s/var' \
            % workdir)
    run('rsync -a --stats --one-file-system /boot/ %s/boot' \
            % workdir)
    run('mksquashfs %s /tmp/%s-%s.squashfs -noappend' \
            % (workdir, name, today()))
    get('/tmp/%s-%s.squashfs' % (name, today()), \
            '%s/%s-%s.squashfs' % (saveto, name, today()))
    run('rm -rf %s' % workdir)
    run('rm -f /tmp/%s-%s.squashfs' % (name, today()))

@task
def hello(hostname):
    '''-  Check if remote hosts are reachable.'''
    env.host_string = hostname
    run('hostname')
    run('ls -la')

@task
def list(item):
    ''':[hosts/images]| Show Image List'''
    cfg = read_ymlfile(item + '.yml')
    
    no = 1
    for i in cfg:
        print "%s. %s" % (no, i)
        no += 1

@task
def tmp_ifconfig(interface):
    ''':interface  -  Setup IP and GW temporary'''
    cfg = read_ymlfile('hosts.yml')[env.host]
    ipaddr = cfg['network'][interface]['ipaddr']
    netmask = cfg['network'][interface]['netmask']
    gateway = cfg['network'][interface]['gateway']
    run('ifconfig %s %s netmask %s' 
            % (interface, ipaddr, netmask))
    run('route add default gw %s' % gateway)

def read_ymlfile(filename):
    '''Read YAML file'''

    yml_dir = re.sub('fabfile', 'ymlfile', __file__).rstrip(r'\.py$|\.pyc$')
    fullpath_ymlfile = yml_dir + '/' + filename
    if not os.path.exists(fullpath_ymlfile):
        print ''
        print '%s doesn\'t exist.' % fullpath_ymlfile
        print ''
        exit(1)

    f = open(fullpath_ymlfile)
    yml = yaml.safe_load(f)
    f.close()

    return yml

def share_dir():
    '''Return path of share directory'''
    share = re.sub('fabfile', 'share', __file__).rstrip(r'\.py$|\.pyc$')

    return share
