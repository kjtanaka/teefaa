Baremetal provisioning with ISO boot
====================================

Initialize a virtual machine named 'vm1'. ::
    
   $ mkdir teefaa && cd teefaa
   $ teefaa init vm1

It will take a while to complete the initial setting, 
and these files will be created. ::

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
   As default, it provides CentOS 6 basic image.

Move to vm1 directory and provision a base system. ::

   $ cd vm1
   $ teefaa provision

Add some software packages and make a snapshot. ::

   $ teefaa ssh
   [teefaa@vm1 ~]$ sudo yum install screen
   [teefaa@vm1 ~]$ echo Hello World! > test.txt
   [teefaa@vm1 ~]$ exit
   $ teefaa make-snapshot
