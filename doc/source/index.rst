.. raw:: html

Welcome to Cloudmesh Teefaa!
====================

Cloudmesh Teefaa is a simplified baremetal provisioner of Linux based system. 
It allows you to make a snapshot of system and provision it on another
baremetal/virtual machine.

  .. toctree::
   :maxdepth: 2

   usersguide
   adminguide
   modules
   license

Requirements
------------

* Python, version 2.7 ~ 2.7.6
* Python Modules

  - Fabric >= version 1.6
  - Cuisine >= version 0.6
  - PyYAML >= version 3.10

Installation
------------

* Download FG Teefaa from the github repository::

     git clone https://github.com/cloudmesh/teefaa.git

* Install required software::

     cd teefaa
     python setup.py install
     
* Confirm::

     teefaa --help

Support
-------

If you run into problems when using this framework, please use our 
help form at `https://portal.futuregrid.org/help <https://portal.futuregrid.org/help>`_.
 
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

