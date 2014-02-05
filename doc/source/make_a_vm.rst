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

      * What the initial setting does is;
         * Make configuration files and keys.
         * Make a VM with Vagrant.
         * Make Teefaa Livecd image from Debian livecd.
      * Take a look at ``virtual1/Teefaafile.yml``. 
      * Teefaa provisions CentOS 6 basic image as default.

3. Change directory to ``virtual1`` and provision the basic CentOS 6 image. ::

      $ cd virtual1
      $ teefaa provision

   .. note::

      * What the provisioning process actually does is;
        * Download CentOS 6 image if needed.
        * Boot virtual1 with the Teefaa LiveCD.
        * Install CentOS 6 on virtual1 over ssh.
        * Reboot virtual1 with local disk.

4. Add some software packages and make a snapshot. ::

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
