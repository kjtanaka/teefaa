Baremetal provisioning with ISO boot
====================================

1. Initialize a virtual machine named 'vm1'. ::
    
   $ mkdir teefaa && cd teefaa
   $ teefaa init vm1

2. It will take a while to complete the initial setting, 
and the following files are created. ::

   $ tree -a -L 2
   .
   ├── .teefaa
   │   ├── ssh_config_vm1          --- ssh config
   │   ├── ssh_key                 --- ssh private key
   │   ├── ssh_key.pub             --- ssh public key
   │   └── teefaa-debian-live.iso  --- customized livecd for teefaa
   └── vm1
       ├── Teefaafile.yml          --- teefaa config
       ├── .vagrant                --- vagrant dot directory
       └── Vagrantfile             --- vagrant config

.. note::

   Take a look at ``vm1/Teefaafile.yml``. 
   Teefaa provisions CentOS 6 basic image as default.

3. Move to vm1 directory and provision a base system. ::

   $ cd vm1
   $ teefaa provision

4. Add some software packages and make a snapshot. ::

    $ teefaa ssh
    [teefaa@vm1 ~]$ sudo yum install screen
    [teefaa@vm1 ~]$ echo Hello World! > test.txt
    [teefaa@vm1 ~]$ exit
    $ teefaa make-snapshot

5. Create ``bm1/Teefaafile.yml``. ::

   $ mkdir bm1
   $ cp vm1/Teefaafile.yml bm1/Teefaafile.yml
   $ sed -i -e 's/vm1/bm1/' bm1/Teefaafile.yml

6. Create ``.teefaa/ssh_config_bm1``. ::

    $ cp .teefaa/ssh_config_vm1 .teefaa/ssh_config_bm1
    $ vi .teefaa/ssh_config_bm1

  ::
    
    Host bm1
      HostName <update ip address>
      User teefaa
      Port 22
      UserKnownHostsFile /dev/null
      StrictHostKeyChecking no
      PasswordAuthentication no
      IdentityFile *********/.teefaa/ssh_key
      IdentitiesOnly yes
      LogLevel FATAL

7. Burn the livecd ``.teefaa/teefaa-debian-live.iso`` to CD-R and boot your
baremetal machine(named bm1 in this example) with the livecd.

8. If everything is configured fine, the snapshot will be installed with this. ::

   $ cd bm1
   $ teefaa provision --no-reboot

9. Reboot the machine from localdisk.

10. Should be able to login with this. ::
   
   teefaa ssh
   [teefaa@bm1 ~]$ which screen
   [teefaa@bm1 ~]$ cat text.txt
   Hello World!
