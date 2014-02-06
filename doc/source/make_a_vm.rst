Make a VM and build your custom OS
==================================

1. Initialize a virtual machine ``virtual1``. ::
    
   $ mkdir Teefaa && cd Teefaa
   $ teefaa init virtual1

2. It will take a while to complete the initial setting, 
and the following files are created. 
   ::

     $ tree -a -L 2
     .
     ├── .teefaa
     │   ├── ssh_config_virtual1          --- ssh config
     │   ├── ssh_key                 --- ssh private key
     │   ├── ssh_key.pub             --- ssh public key
     │   └── teefaa-debian-live.iso  --- Teefaa LiveCD image
     └── virtual1
         ├── Teefaafile.yml          --- teefaa config
         ├── .vagrant                --- vagrant dot directory
         └── Vagrantfile             --- vagrant config

   .. note::

      * What ``teefaa init`` actually does is;
         * Make configuration files and ssh key pair.
         * Make a VM with using Vagrant and VirtualBox.
         * Download Debian LiveCD to the VM and build Teefaa LiveCD.
      * Take a look at ``virtual1/Teefaafile.yml``. 
        You can find that Teefaa provisions CentOS 6 basic image as default.

3. Change directory to ``virtual1`` and provision the basic CentOS 6 image. ::

      $ cd virtual1
      $ teefaa provision

   .. note::

      * What ``teefaa provision`` does is;
         * Download CentOS 6 image if it doesn't exist on local.
         * Boot ``virtual1`` with the Teefaa LiveCD.
         * Install CentOS 6 on ``virtual1`` over ssh.
         * Reboot ``virtual1`` with local disk.

4. Make some changes and make a snapshot of the system. ::

      $ teefaa ssh
      [teefaa@virtual1 ~]$ sudo yum install screen
      [teefaa@virtual1 ~]$ echo Hello World! > test.txt
      [teefaa@virtual1 ~]$ exit
      $ teefaa make-snapshot

   .. note::
   
      * What ``make-snapshot`` does is;
         * Copy all files into a temporal directory.
         * Compress it with SquashFS.
         * Download and save it in ``.teefaa`` directory.
