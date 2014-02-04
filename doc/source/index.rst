Welcome to Cloudmesh Teefaa!
============================

Your system on baremetal machine should be as easily and reproducibly provisioned 
as virtual machine.

What is Cloudmesh Teefaa?
-------------------------
Cloudmesh Teefaa is a simplified baremetal provisioner of Linux based Operating
System. It allows you to make a snapshot of a running OS and provision it on 
another baremetal machine. 

Cloudmesh Teefaa also supports VirtualBox so that you can build a custom OS on 
a VM, and then provision the snapshot on another baremetal/virtual machine. 
Means you can easily try it with two VMs to see what it actually does.

Here's example. Provision a base system on a virtual machine and make a snapshot. ::

    $ mkdir try_teefaa
    $ cd try_teefaa
    $ teefaa init sputnik1
    $ cd sputnik1
    $ teefaa provision
    $ teefaa ssh
    [teefaa@sputnik1 ~]$ echo Hello World! > test.txt
    [teefaa@sputnik1 ~]$ exit
    $ teefaa make-snapshot

And then, provision the snapshot on another virtual machine. ::
   
    $ cd ..
    $ teefaa init sputnik2
    $ cd sputnik2
    $ teefaa provision
    $ teefaa ssh
    [teefaa@sputnik2 ~]$ cat test.txt
    Hello World!

.. note::
   * It takes a while at the step "teefaa init" and "teefaa provision".
   * Prerequisites and installation are written below.

Characteristics
---------------
* Simple to use.
* Written in Python and Fabric.
* Inspired by Vagrant and Test Kitchen.
* Able to provision Ubuntu and CentOS right now. Will cover 
  Debian and Fedora soon. And more distros later.

Prerequisites
-------------
* Python 2.7 ~ 2.7.6
* VirtualBox
* Vagrant

Installation
------------
::

    git clone https://github.com/kjtanaka/teefaa.git
    cd teefaa
    python setup.py install

Provisioning on baremetal machine
---------------------------------

There are two ways to do baremetal provisioning, and it all depends 
on what you have on your environment. If you have a CD/DVD drive on 
your server, the simple way is to go with ISO boot. If you also have 
a PXE boot server and a NFS server, PXE boot is more efficient.
If you also have IPMI access to the BMC of your server, you can 
provision a system and make a snapshot, easily and reproducibly.

.. toctree::
 :maxdepth: 1

 how_to_iso_boot
 how_to_pxe_boot
 how_to_scale
 license

