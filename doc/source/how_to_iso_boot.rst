Baremetal provisioning with ISO boot
====================================

1. Create Teefaa config file ``baremetal1/Teefaafile.yml``. ::

   $ mkdir baremetal1
   $ cp virtual1/Teefaafile.yml baremetal1/Teefaafile.yml
   $ sed -i -e 's/virtual1/baremetal1/' baremetal1/Teefaafile.yml

2. Create SSH config file ``.teefaa/ssh_config_baremetal1``. ::

    $ cp .teefaa/ssh_config_virtual1 .teefaa/ssh_config_baremetal1
    $ vi .teefaa/ssh_config_baremetal1

  ::
    
    Host baremetal1
      HostName <update ip address>
      User teefaa
      Port 22
      UserKnownHostsFile /dev/null
      StrictHostKeyChecking no
      PasswordAuthentication no
      IdentityFile *********/.teefaa/ssh_key
      IdentitiesOnly yes
      LogLevel FATAL

3. Burn the livecd ``.teefaa/teefaa-debian-live.iso`` to CD-R and boot
   ``baremetal1`` with CD boot.

4. If everything is configured fine, the snapshot should be able to install with this. ::

   $ cd baremetal1
   $ teefaa provision --no-reboot

5. Reboot ``baremetal1`` from localdisk.

6. Should be able to login to ``baremetal1`` with this. ::

      $ teefaa ssh

7. Check if it's the same as ``virtual1``. ::

      [teefaa@baremetal1 ~]$ which screen
      [teefaa@baremetal1 ~]$ cat text.txt
      Hello World!
