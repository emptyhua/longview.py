#!/usr/bin/env python

import os, re

def get(report):
    report.data('load', os.getloadavg())

    user    = 0
    system  = 0
    wait    = 0

    try:
        for line in open('/proc/stat', 'r'):
            if re.match(r'^cpu\d', line) is not None:
                line = line.strip()
                tmp = re.split(r'\s+', line)
                user    += int(tmp[1]) + int(tmp[2])
                system  += int(tmp[3])
                wait    += int(tmp[5])
    except IOError:
        report.error('can not open /proc/stat')
        return

    report.data('user', user)
    report.data('system', system)
    report.data('wait', wait)
