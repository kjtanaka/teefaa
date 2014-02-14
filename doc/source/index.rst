Welcome to Cloudmesh Teefaa!
============================

Your system on baremetal machine should be as easily and reproducibly provisioned
and cloned as virtual machine.

What is Cloudmesh Teefaa?
-------------------------
Cloudmesh Teefaa is a simplified baremetal provisioner of Linux based Operating
System. It allows you to make a snapshot of a running OS and provision it on 
another baremetal machine. 

Cloudmesh Teefaa also supports VirtualBox so that you can build a custom OS on 
a VM, and then provision the snapshot on another baremetal/virtual machine. 
Which means that you can easily try it with two VMs to see what it actually does.

.. note::
   Before trying it, please read the sections about "Prerequisites" and "Installation."

Here's an example. Provision a base system on a virtual machine and make a snapshot. ::

    $ mkdir project1
    $ cd project1
    $ teefaa init sputnik1
    $ cd sputnik1
    $ teefaa provision
    $ teefaa ssh
    [teefaa@sputnik1 ~]$ sudo yum install screen
    [teefaa@sputnik1 ~]$ echo Hello World! > test.txt
    [teefaa@sputnik1 ~]$ exit
    $ teefaa make-snapshot

And then, provision the snapshot on another virtual machine. ::
   
    $ cd ..
    $ teefaa init sputnik2
    $ cd sputnik2
    $ teefaa provision
    $ teefaa ssh
    [teefaa@sputnik2 ~]$ which screen
    /usr/bin/screen
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
* Able to provision Ubuntu and CentOS. 
  Will cover Debian and Fedora soon. 
  And more distros later.

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

For baremetal provisioning, it is needed to boot your machine with your
``.teefaa/teefaa-debian-live.iso`` with CD/DVD boot, or configure the
livecd with PXE boot server.

The following chapters explain it with an example as follows.

1. Make a VM ``virtual1``, build a custom OS and make a snapshot.
2. Boot a baremetal machine ``baremetal1`` with Teefaa livecd, and provision 
   the snapshot of ``virtual1`` on ``baremetal1``.
3. Configure DHCP, PXE, NFS and IPMI and make it possible to easily and
   reproducibly provision the snapshot on ``baremetal1``.

.. toctree::
 :maxdepth: 1

 make_a_vm
 how_to_iso_boot
 how_to_pxe_boot
 how_to_scale
 license

