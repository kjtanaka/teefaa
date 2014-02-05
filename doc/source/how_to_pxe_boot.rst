Configure DHCP, NFS, PXE and IPMI
=================================

Prerequisites
-------------
* DHCP server
* PXE boot server
* NFS server
* `ipmitool <https://www.google.com/#q=ipmitool>`_ 
  and IPMI access to ``baremetal1``'s BMC

Setup DHCP
----------
1. Configure DHCP for PXE boot ``baremetal1`` and restart dhcpd.
   Here's an example of the entry on ``/etc/dhcpd.conf``. ::
      
      host baremetal1 {
        hardware ethernet aa:bb:cc:11:22:33;
        fixed-address 192.168.1.101;
        option host-name baremetal1;
        filename "pxelinux.0";
        next-server 192.168.1.1;
        server-name mgmt;
      }

   .. note::
    
     If you have Dnsmasq instead of dhcpd, please configure it as equivalent to above.

Setup NFS
---------
1. Set the livecd boot image on NFS. ::
   
      $ mkdir /mnt/livecd
      $ sudo mount -o loop /path/to/.teefaa/teefaa-debian-live.iso /mnt/livecd
      $ sudo mkdir -p /nfsroot/teefaa
      $ sudo cp -pr /mnt/livecd /nfsroot/teefaa/netboot

2. Add entry on ``/etc/exports`` to export ``/nfsroot/teefaa/netboot``. ::
   
      /nfsroot/teefaa/netboot 192.168.1.0/24(rw,async,no_subtree_check,no_root_squash)

3. sync exports. ::
   
      sudo exportfs -rv

Setup PXE
---------
1. Copy ``initrd.img`` and ``vmlinuz``. ::
   
      mkdir /mnt/squashfs
      sudo mount -o loop /mnt/livecd/live/filesystem.squashfs /mnt/squashfs
      sudo mkdir /tftproot/teefaa
      sudo cp -p /mnt/squashfs/boot/initrd.img-* /tftproot/teefaa/initrd.img
      sudo cp -p /mnt/squashfs/boot/vmlinuz-* /tftproot/teefaa/vmlinuz
      chmod -R 777 /tftproot/teefaa

2. Unmount SquashFS and ISO image. ::

      sudo umount /mnt/squashfs /mnt/livecd

3. Create ``netboot`` config file. ::
   
      $ vi /tftpboot/pxelinux.cfg/netboot

   ::

      DEFAULT teefaa
      PROMPT 1
      TIMEOUT 30

      LABEL teefaa
        KERNEL teefaa/vmlinuz
        APPEND teefaa/initrd.img boot=live netboot=nfs nfsroot=<IP of NFS server>:/nfsroot/teefaa console=tty0 console=ttyS0,115200n8r text --

4. Create ``localboot`` config file. ::
   
      $ vi /tftpboot/pxelinux.cfg/localboot
   
   ::
   
      DEFAULT localboot
      LABEL localboot
      LOCALBOOT 0

Setup Teefaafile.yml
-------------------
1. Comment out the config for VirtualBox and update it for Baremetal. ::
   
      $ cd /path/to/Teefaa
      $ vi baremetal1/Teefaafile.yml

   ::
   
      # VirtualBox
      #host_config:
      #  hostname: baremetal1
      #  power_driver: virtualbox
      #  power_driver_config:
      #    vbox_name: baremetal1_baremetal1_XXXXXXXXXX_XXXXX
      #  boot_driver: virtualbox
      #  boot_driver_config:
      #    installer_boot: iso
      #    iso_file: /path/to/Teefaa/.teefaa/teefaa-debian-live.iso
        
      # Baremetal
      host_config:
        hostname: baremetal1
        power_driver: ipmi
        power_driver_config:
          bmc_address: <bmc's ip address>
          ipmi_password: <ipmi password>
          ipmi_user: <ipmi username>
        boot_driver: pxe
        boot_driver_config:
          pxe_server: <pxe server address>
          pxe_server_user: <ssh login username>
          boot_config_file: /tftpboot/pxelinux.cfg/01-aa-bb-cc-11-22-33
          installer_boot_config_file: /tftpboot/pxelinux.cfg/netboot
          disk_boot_config_file: /tftpboot/pxelinux.cfg/localboot

2. Register your ``.teefaa/ssh_key.pub`` to your ``pxe_server_user``'s ``.ssh/authorized_keys`` on the ``pxe_server``. 
   
3. Make sure you can login with this. ::
   
      ssh <ssh login username>@<pxe server address> -i .teefaa/ssh_key

4. Make sure you have write permission of ``boot_config_file``. ::

      <username>@<pxe server> ~$ ls -la /tftpboot/pxelinux.cfg/01-aa-bb-cc-11-22-33

5. If all is well, you should be able to provision ``virtual1``'s snapshot on
   ``baremetal1`` with this; ::
   
      $ cd baremetal1
      $ teefaa provision
