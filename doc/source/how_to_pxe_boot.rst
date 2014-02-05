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

   ..note::
    
     If you have Dnsmasq instead of dhcpd, please configure it as equivalent to above.

Setup NFS
---------
1. Set the livecd boot image on NFS. ::
   
      $ mkdir /mnt/livecd
      $ sudo mount -o loop /path/to/.teefaa/teefaa-debian-live.iso /mnt/livecd
      $ sudo mkdir -p /nfsroot/teefaa
      $ sudo cp -pr /mnt/livecd /nfsroot/teefaa/netboot

2. Add entry on ``/etc/exports`` to export ``/nfsroot/teefaa/netboot``. ::
   
      /nfsroot/teefaa/netboot 192.168.2.xxx(rw,async,no_subtree_check,no_root_squash)

3. sync exports. ::
   
      sudo exportfs -rv

Setup PXE
---------
1. Set ``initrd.img`` and ``vmlinuz``. ::
   
      mkdir /mnt/squashfs
      sudo mount -o loop /mnt/livecd 
