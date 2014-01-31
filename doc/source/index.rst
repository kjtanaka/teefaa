Welcome to Cloudmesh Teefaa!
============================

Your systems on baremetal machines should be as easily and reproducibly provisioned 
as virtual machines.

What is Cloudmesh Teefaa?
-------------------------
The Cloudmesh Teefaa is a simplified baremetal provisioner of Linux based Operating
System. It allows you to make a snapshot of a running OS and provision it on 
another baremetal machine. 

Teefaa supports VirtualBox as default, so here's a test with two virtual machines.

First, provision a base system on a virtual machine and make a snapshot. ::

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
   * It takes a while at the steps of "teefaa init" and "teefaa provision".
   * Prerequisites and installation are written below.
   * There are two ways for baremetal provisioning, ISO boot and PXE boot,
     it's explained on the next pages.

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
-------
::

    git clone https://github.com/kjtanaka/teefaa.git
    cd teefaa
    python setup.py install

Provisioning on baremetal machine
---------------------------------

There are two ways to go, and it all depends on 
what you have on your environment.

  .. toctree::
   :maxdepth: 2

   how_to_iso_boot
   how_to_pxe_boot
   how_to_scale
   license

