#!/usr/bin/env python
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import time

from fabric.api import task

from ..teefaa.fabfile import make

@task
def test_mkiso_install_required_pkgs():
    """
    Test functions.
    param: func - function to test.
    """
    func = make.MakeISO()
    func._install_required_pkgs()
