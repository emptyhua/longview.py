#!/usr/bin/env python

import os, socket

def get(report):
    sysname, _, release, version, arch = os.uname()
    report.data('sysname', sysname)
    report.data('release', release)
    report.data('version', version)
    report.data('arch', arch)

    report.data('hostname', socket.gethostname())
    cpu_num     = 0
    cpu_type    = None
    try:
        for line in open('/proc/cpuinfo', 'r'):
            if line.find('processor') == 0:
                cpu_num += 1
            elif line.startswith('model name') and cpu_type is None:
                cpu_type = line.split(':')[1].strip()
    except IOError as e:
        report.error('can not open /proc/cpuinfo')

    if cpu_num > 0:
        report.data('cpu_num', cpu_num)
    if cpu_type:
        report.data('cpu_type', cpu_type)

    try:
        report.data('uptime', int(float(open('/proc/uptime').read().split(' ')[0])))
    except IOError as e:
        report.error('can not open /proc/uptime')
