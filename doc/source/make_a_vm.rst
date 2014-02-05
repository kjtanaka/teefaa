Make a VM to build your custom OS
=================================

1. Initialize a virtual machine named 'vm1'. ::
    
   $ mkdir teefaa && cd teefaa
   $ teefaa init vm1

2. It will take a while to complete the initial setting, 
and the following files are created. 
   ::

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

It takes a while to finish making a snapshot. 
When it's done, it's ready to be provisioned on
a baremetal machine.
