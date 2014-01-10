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
   modules
   adminguide
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


Simple Design
-------------

* Scripts for handling Shell commands are written in Fabric and Cuisine.
* Configuration files are written in YAML format. One of the goals of Teefaa 
  is to make it understandable by reading the YAML files.
* Each scripts has four types of directories as shown below. ::

    |-- fabfile/EXAMPLE.py
    |-- ymlfile/EXAMPLE
    |           |-- config1.yml
    |           `-- config2.yml
    |-- private/EXAMPLE
    |           `-- dir1
    |               |-- file1
    |               `-- file2
    `-- share/EXAMPLE
              `-- dir1
                  |-- file1
                  `-- file2

This stracture enables a simplified separation among concurrent developments, which allows 
people to work on multile projects and multiple versions in a simple fashion. For example, 
while one person is developing EXAMPLE, another person can start developing EXAMPLE2.

Installation
------------

* Download FG Teefaa from the github repository::

     git clone https://github.com/cloudmesh/teefaa.git

* Install required software::

     cd teefaa
     pip install -r requirements.txt
     
* Confirm you got everything::

     cd teefaa
     fab -l

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

