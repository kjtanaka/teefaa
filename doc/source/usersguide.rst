Users Guide
=====================================

What Teefaa actually does is to make a snapshot of a Operating System and provision it
on another Baremetal/Virtual Machine, and it uses ISO/PXE Boot image in the provisioning
process. So there are three major steps as listed below.

1. Make a Teefaa ISO/PXE boot image.
2. Make a snapshot of your system.
3. Provision your system snapshot on another machine.

An easy way to try Teefaa is to use VirtualBox. So it would be great if you have a
baremetal machine which you want to backup. Teefaa can make a snapshot of your system
and provision it on a VM of your VirtualBox.

I use Vagrant to simplify the procesedure, so please install VirtualBox and Vagrant
before starting this tutorial.


Make a Teefaa ISO/PXE boot image
--------------------------------

ISO image of Teefaa is based on Debian7 and you can create the image with Ubuntu or Debian.
Here I'll use Ubuntu VM with Vagrant. Here's my example Vagrantfile.::

    Vagrant.configure("2") do |config|
    
      config.vm.define :ubuntu1204 do |ubuntu1204|
        ubuntu1204.vm.box = 'ubuntu-12.04'
        ubuntu1204.vm.box_url = 'http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box'
        ubuntu1204.vm.hostname = "ubuntu1204"
      end

    end

And, boot the VM.::

    vagrant up ubuntu1204
    vagrant ssh-config ubuntu1204 > ssh-config

The ssh-config is used by Teefaa to login the VM.

Next, write the configuration for making ISO image and save the file named as Teefaafile.::

    ssh_config: ssh-config

    iso_config:
      base_iso: debian-live-7.2-amd64-standard.iso
      base_iso_url: http://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/debian-live-7.2-amd64-standard.iso
      builder:
        hostname: ubuntu1204
        distro: ubuntu
      save_as: teefaa-debian-live.iso

Then, execute this command.::

    teefaa make-iso

This will generate the custom ISO image and save it as teefaa-debian-live.iso.

Make a snapshot of your system
------------------------------

To make a snapshot of your system, you need to update your ssh-config to be able to login
to the host by ssh <hostname>.::

   Host ubuntu1204
     HostName 127.0.0.1
     User vagrant
     Port 2222
     UserKnownHostsFile /dev/null
     StrictHostKeyChecking no
     PasswordAuthentication no
     IdentityFile /home/ktanaka/.vagrant.d/insecure_private_key
     IdentitiesOnly yes
     LogLevel FATAL 
   # Add the host to make a snapshot
   Host host001
     HostName 192.168.32.102
     User myuser
     IdentityFile /path/to/private_key
     UserKnownHostsFile /dev/null
     StrictHostKeyChecking no


