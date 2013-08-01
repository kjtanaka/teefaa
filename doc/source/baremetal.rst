.. raw:: html

 <a href="https://github.com/futuregrid/teefaa"
     class="visible-desktop"><img
    style="position: absolute; top: 40px; right: 0; border: 0;"
    src="https://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png"
    alt="Fork me on GitHub"></a>


Baremetal
==============================

baremetal.provisioning
----------------------

Command::

    fab baremetal.provisioning:<host>,<image>

This will install the <image> on the <host>. To make it work,
you have to set the <host> on `ymlfile/baremetal/hosts.yml 
<https://github.com/cloudmesh/teefaa/blob/master/ymlfile/baremetal/hosts.yml-example>`_, 
and the <image> on `ymlfile/baremetal/images.yml <https://github.com/cloudmesh/teefaa/blob/master/ymlfile/baremetal/images.yml-example>`_ .
