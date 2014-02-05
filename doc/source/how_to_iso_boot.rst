Baremetal provisioning with ISO boot
====================================

1. Create ``bm1/Teefaafile.yml``. ::

   $ mkdir bm1
   $ cp vm1/Teefaafile.yml bm1/Teefaafile.yml
   $ sed -i -e 's/vm1/bm1/' bm1/Teefaafile.yml

2. Create ``.teefaa/ssh_config_bm1``. ::

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

3. Burn the livecd ``.teefaa/teefaa-debian-live.iso`` to CD-R and boot your
baremetal machine(named bm1 in this example) with the livecd.

4. If everything is configured fine, the snapshot will be installed with this. ::

   $ cd bm1
   $ teefaa provision --no-reboot

5. Reboot the machine from localdisk.

6. Should be able to login to the node with this. 
    ::
      $ teefaa ssh
      [teefaa@bm1 ~]$ which screen
      [teefaa@bm1 ~]$ cat text.txt
      Hello World!
