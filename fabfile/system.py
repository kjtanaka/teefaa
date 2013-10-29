#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
# system.py - is a set of tools for system management.
#

import os
import re
import sys
import yaml
import time
import datetime
from fabric.api import *
from fabric.contrib import *
from fabric.contrib.files import *
from cuisine import *

fabname = 'system'
@task
def print_fabname():
    print fabname


@task
def users_force_resetpass(group):
    ''':group=XXXXX | Force users to reset password'''
    users = read_ymlfile('users.yml')[group]

    for user in users:
        with mode_sudo():
            run('usermod -p \'\' %s' % user)
            run('chage -d 0 %s' % user)

@task
def users_en_sudo(group):
    ''':group | enable sudo'''
    users = read_ymlfile('users.yml')[group]

    file_name = '/etc/sudoers'
    file_ensure(file_name, mode=640)
    for user in users:
        with mode_sudo():
            file_append('/etc/sudoers', '{0}    ALL=(ALL:ALL) ALL\n'.format(user))
    file_ensure(file_name, mode=440)

@task
def users_ensure(group):
    ''':group=XXXXX | Ensure Users exists'''
    users = read_ymlfile('users.yml')[group]

    distro = check_distro()
    if distro == 'fedora':
        select_package('yum')
        package_ensure('openssl')

    for user in users:
        options = users[user]
        passwd,home,uid,gid,shell,fullname = None,None,None,None,None,None
        if options['passwd']:
            passwd = options['passwd']
        if options['home']:
            home = options['home']
        if options['uid']:
            uid = options['uid']
        if options['gid']:
            gid = options['gid']
        if options['shell']:
            shell = options['shell']
        if options['fullname']:
            fullname = options['fullname']
        user_ensure(user, passwd, home, uid, gid, shell, fullname)
        user_home = user_check(user)['home']
        dot_ssh = '%s/.ssh' % user_home
        authorized_keys = '%s/authorized_keys' % dot_ssh
        with mode_sudo():
            dir_ensure(dot_ssh, mode=700, owner=user)
            if not file_exists(authorized_keys):
                run('touch %s' % authorized_keys)
                file_ensure(authorized_keys, mode=600, owner=user)
        for key in options['authorized_keys']:
            with mode_sudo():
                ssh_authorize(user, key)

@task
def backup(hostname):
    ''':item=XXXXX | Backup System'''
    cfg = read_ymlfile('{}.yml'.format(hostname))['backup']

    if not os.getenv('USER') == 'root':
        print 'You have to be root.'
        exit(1)

    _backup_rsync(cfg)
    _backup_squashfs(cfg, item)

def _backup_rsync(cfg):
    '''Execute rsync'''
    cmd = []
    cmd.append('rsync -av')

    if not os.path.isdir(cfg['dest']):
        local('mkdir -p %s' % cfg['dest'])

    if cfg['one-file-system']:
        cmd.append('--one-file-system')

    if cfg['delete']:
        cmd.append('--delete')

    if cfg['exclude']:
        for a in cfg['exclude-list']:
            cmd.append('--exclude=\'%s\'' % a)

    cmd.append(cfg['src'])
    cmd.append(cfg['dest'])

    cmd = ' '.join(cmd)
    local(cmd)

def _backup_squashfs(cfg, item):
    '''Make squashfs'''
    if cfg['mksquashfs']:
        today = datetime.date.today
        save_as = '%s/%s-%s.squashfs' \
                % (cfg['dir_squashfs'],item,today())
        cmd = []
        cmd.append('mksquashfs')
        cmd.append(cfg['dest'])
        cmd.append(save_as)
        cmd.append('-noappend')

        cmd = ' '.join(cmd)
        local(cmd)

@task
def pxeboot(hostname, boottype):
    ''':hostname,[localboot/netboot/show/list] - utility for pxeboot'''
    pxecfg = read_ymlfile('{}.yml'.format(hostname))['pxe']
    env.host_string = pxecfg['ssh_server']
    env.user = pxecfg['ssh_user']

    hostcfg = '%s/%s' % (pxecfg['pxe_prefix'], hostname)

    with hide('running', 'stdout'):
        test = file_exists(hostcfg)
    if not file_exists(hostcfg):
        print ''
        print ' ERROR: %s does not exist.' % hostcfg
        print ''
        exit(1)

    if boottype == 'show':
        with hide('running', 'stdout'):
            output = run('cat %s' % hostcfg)
        print ''
        print '[%s]' % hostname
        print '--------------------------------------------'
        print output
        print '--------------------------------------------'
        exit(0)

    if boottype == 'list':
        with hide('running', 'stdout'):
            output = run('ls -1 %s| grep -v 01-' % pxecfg['pxe_prefix'])
        print ''
        print output
        print ''
        exit(0)

    bootcfg = '%s/%s' % (pxecfg['pxe_prefix'], boottype)
    with hide('running', 'stdout'):
        test = file_exists(bootcfg)
    if not test:
        print ''
        print ' ERROR: %s does not exist.' % bootcfg
        print ''
        exit(1)

    run('cat %s > %s' % (bootcfg, hostcfg))

@task
def power(hostname,action):
    ''':hostname,[on/off/status]'''
    ipmicfg = read_ymlfile('{}.yml'.format(hostname))['ipmi']
    user = ipmicfg['ipmi_user']
    password = ipmicfg['ipmi_pass']
    bmcaddr = ipmicfg['bmc_addr']
    env.host_string = ipmicfg['ssh_server']
    env.user = ipmicfg['ssh_user']

    with hide('running', 'stdout'):
        if action == 'wait_till_on':
            keywords = 'Power is on'
            _power_wait(keywords, user, password, bmcaddr)
        elif action == 'wait_till_off':
            keywords = 'Power is off'
            _power_wait(keywords, user, password, bmcaddr)
        elif action == 'on' or \
                action == 'off' or \
                action == 'status':
            output = run('ipmitool -I lanplus -U %s -P %s -E -H %s power %s' 
                         % (user, password, bmcaddr, action))
            print ''
            print '[%s]' % hostname
            print '-------------------------------------------------'
            print output
        else:
            print 'action \'%s\' is not supported.' % action
            exit(1)

def _power_wait(keywords, user, password, bmcaddr):
    output = ''
    counter = 0
    while output.find(keywords) == -1:
        output = run('ipmitool -I lanplus -U %s -P %s -E -H %s power status'
                     % (user, password, bmcaddr))
        counter += 1
        limit = 10
        print '[%s/%s]\n%s' % (counter, limit, output)
        if counter == limit:
            print 'Give it up'
            exit(1)
        time.sleep(5)
    return True

@task
def wait_till_ping(hostname,limit=10):
    ''':hostname,limit=10'''
    with settings(warn_only = True):
        counter = 0
        loop = True
        while loop:
            output = local('ping -c 3 %s' % hostname)
            counter += 1
            if output.return_code == 0:
                print "Tried ping and succeeded [%s/%s]" % (counter, limit)
                break
            else:
                print "Tried ping and no answer [%s/%s]" % (counter, limit)
            if counter > limit:
                print "Give up"
                exit(1)
                time.sleep(5)

@task
def wait_till_ssh(hostname,limit=10):
    ''':hostname,limit=10'''
    env.host_string = hostname
    env.user = 'root'
    with settings(warn_only = True):
        counter = 0
        loop = True
        while loop:
            counter += 1
            try:
                run('hostname')
                break
            except fabric.exceptions.NetworkError:
                print "Tried ssh and no answer [%s/%s]" % (counter, limit)
                if counter > limit:
                    print "Give up"
                    exit(1)
                time.sleep(5)
                pass
        print "Tried ssh and succeeded [%s/%s]" % (counter, limit)

@task
def temperature(hostname):
    ''':hostname'''
    ipmicfg = read_ymlfile('{}.yml'.format(hostname))['ipmi']
    user = ipmicfg['ipmi_user']
    password = ipmicfg['ipmi_pass']
    bmcaddr = ipmicfg['bmc_addr']
    env.host_string = ipmicfg['ssh_server']
    env.user = ipmicfg['ssh_user']

    with hide('running', 'stdout'):
        output = run('ipmitool -I lanplus -U %s -P %s -E -H %s sdr type temperature'
                         % (user, password, bmcaddr))
    print ''
    print '[%s]' % hostname
    print '-------------------------------------------------'
    print output

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

def check_distro():
    distro = run('python -c "import platform; print platform.dist()[0].lower()"')

    return distro

@task
def make_livecd(livecd_name):
    ''':livecd_name | Make LiveCD'''
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
        append(file, '%s' % livecd['pubkeys'][key])
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

