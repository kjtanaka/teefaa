Welcome to Cloudmesh Teefaa!
============================

Your system on Baremetal Machine should be as easily and reproduciblly installed 
as Virtual Machine.

What is Cloudmesh Teefaa?
-------------------------
The Cloudmesh Teefaa is a simplified baremetal provisioner of Linux based Operating
System. It allows you to make a snapshot of a running OS and provision it on 
another baremetal machine. Here's an example.

First, provision a base system on a Virtual Machine and make a snapshot ::

    $ teefaa init sputnik1
    $ cd sputnik1
    $ teefaa provision
    $ teefaa ssh
    [teefaa@sputnik1 ~]$ echo Hello World! > test.txt
    [teefaa@sputnik1 ~]$ exit
    $ teefaa make-snapshot

And then, provision the snapshot on a Baremetal Machine ::
   
    $ cd ..
    $ cp -r sputnik1 sputnik2
    $ vi sputnik2/Teefaafile.yml .teefaa/ssh_config # Modify two files for Baremetal
    $ cd sputnik2
    ##### Setup iso/pxe boot of sputnik2 #####
    $ teefaa provision
    $ teefaa ssh
    [teefaa@sputnik2 ~]$ cat test.txt
    Hello World!

Characteristics
---------------
* Simple to use.
* Written in Python and Fabric.
* Inspired by Vagrant and Test Kitchen.

Prerequisites
-------------
* Python 2.7 ~ 2.7.6
* VirtualBox
* Vagrant

Install
-------
::

    git clone https://github.com/cloudmesh/teefaa.git
    cd teefaa
    python setup.py install
    teefaa -h

For more information go to the following pages.

  .. toctree::
   :maxdepth: 2

   how_to_iso_boot
   how_to_pxe_boot
   license

