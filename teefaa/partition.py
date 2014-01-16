#!/usr/bin/env python

import os
import argparse
from fabric.api import execute

from .libexec.partition import make_partition, mount_partition

class TeefaaPartition(object):

    def setup(self, parser):

        make_partition = parser.add_parser('make-partition', help='Make partitions')
        make_partition.set_defaults(func=self.make_partition)
        mount_partition = parser.add_parser('mount-partition', help='Mount partitions')
        mount_partition.set_defaults(func=self.mount_partition)

    def make_partition(self, args):

        execute(make_partition)

    def mount_partition(self, args):

        execute(mount_partition)

