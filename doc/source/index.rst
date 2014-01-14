.. raw:: html

 <a href="https://github.com/futuregrid/teefaa"
     class="visible-desktop"><img
    style="position: absolute; top: 40px; right: 0; border: 0;"
    src="https://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png"
    alt="Fork me on GitHub"></a>


Welcome to Cloudmesh Teefaa!
====================

.. sidebar:: Table of Contents

  .. toctree::
   :maxdepth: 2

   usersguide
   adminguide
   modules
   license

Cloudmesh Teefaa is a set of deployment scripts for with focuss on bare metal provisioning. Cloudmesh Teefaa is 
simple and flexible allowing contributors to expand upon it.

Requirements
------------

FG Teefaa requires(/thanks to):

* Python, version 2.7
* Python Modules

  - Fabric, version 1.6
  - Cuisine, version 0.6
  - PyYAML, version 3.10

* Squashfs-tools (for creating snapshots of Operating System)
* Bittorrent Sync (for high-speed multiple Baremetal Provisioning)
* Torque Resource Manager (for scheduing Baremetal Provisioning)


Installation
------------

* Download FG Teefaa from the github repository::

     git clone https://github.com/cloudmesh/teefaa.git

* Install required software::

     cd teefaa
     python setup.py install
     
* Confirm you got everything::

     teefaa -h

* That is all for installation and you should be able to see the list of scripts.


Support
-------

If you run into problems when using this framework, please use our 
help form at `https://portal.futuregrid.org/help <https://portal.futuregrid.org/help>`_.
 
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

