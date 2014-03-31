#!/usr/bin/env python

import os

def get(report):
    types = ('ext2', 'ext3', 'ext4')
    disks = []

    try:
        for line in open('/proc/mounts', 'r'):
            tmp = line.strip().split(' ')
            if tmp[2] in types:
                stat= os.statvfs(tmp[1])
                disk = {}
                disk['path']    = tmp[1]
                disk['total']   = stat.f_blocks * stat.f_frsize
                disk['avail']   = stat.f_bavail * stat.f_frsize
                disks.append(disk)
    except IOError:
        report.error('can not open /proc/mounts')

    if len(disks):
        report.data('disks', disks)
