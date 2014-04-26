#!/usr/bin/env python

import os, re

def get(report):
    types       = ('ext2', 'ext3', 'ext4')
    disks       = []
    stats_pool  = {}
    total_read_bytes  = 0
    total_write_bytes = 0

    if os.path.exists('/proc/diskstats'):
        #  202 0 xvda 3125353 13998 4980 2974 366 591 760 87320 15 366 9029
        for line in open('/proc/diskstats', 'r'):
            tmp         = re.split('[\s]+', line.strip())   
            device      = tmp[2]
            phys_device = re.sub('[\d]+$', '', tmp[2])

            if os.path.exists('/sys/block/%s/queue/hw_sector_size' % device):
                sector_size = int(open('/sys/block/%s/queue/hw_sector_size' % device, 'r').read())
            elif os.path.exists('/sys/block/%s/queue/hw_sector_size' % phys_device):
                sector_size = int(open('/sys/block/%s/queue/hw_sector_size' % phys_device, 'r').read())
            else:
                continue

            read_sectors    = int(tmp[4])
            write_sectors   = int(tmp[6])
            read_bytes      = read_sectors * sector_size
            write_bytes     = write_sectors * sector_size
            stat = {}
            stat['read_bytes']  = read_bytes
            stat['write_bytes'] = write_bytes
            stats_pool[device]  = stat


    try:
        for line in open('/proc/mounts', 'r'):
            tmp = line.strip().split(' ')
            device = os.path.basename(tmp[0])
            if tmp[2] in types:
                stat= os.statvfs(tmp[1])
                disk = {}
                disk['path']    = tmp[1]
                disk['total']   = stat.f_blocks * stat.f_frsize
                disk['avail']   = stat.f_bavail * stat.f_frsize
                if device in stats_pool:
                    disk['read_bytes']  = stats_pool[device]['read_bytes']
                    total_read_bytes    += stats_pool[device]['read_bytes']
                    disk['write_bytes'] = stats_pool[device]['write_bytes']
                    total_write_bytes   += stats_pool[device]['write_bytes']
                else:
                    disk['read_bytes']  = 0
                    disk['write_bytes'] = 0
                disks.append(disk)
    except IOError:
        report.error('can not open /proc/mounts')

    if len(disks):
        report.data('disks', disks)
        report.data('total_read_bytes',   total_read_bytes)
        report.data('total_write_bytes',  total_write_bytes)
