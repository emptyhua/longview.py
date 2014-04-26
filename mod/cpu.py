#!/usr/bin/env python

import os, re

def get(report):
    report.data('load', os.getloadavg())

    total   = 0
    user    = 0
    system  = 0
    wait    = 0
    idle    = 0
    steal   = 0
    ticks   = os.sysconf('SC_CLK_TCK') 

    try:
        for line in open('/proc/stat', 'r'):
            if user == 0 and re.match(r'^cpu ', line) is not None:
                line = line.strip()
                tmp  = re.split(r'\s+', line)
                for i in tmp[1:]:
                    total += int(i)
                user    = int(tmp[1]) + int(tmp[2])
                system  = int(tmp[3]) + int(tmp[6]) + int(tmp[7])
                wait    = int(tmp[5])
                idle    = int(tmp[4])
                steal   = int(tmp[8])
                break
    except IOError:
        report.error('can not open /proc/stat')
        return

    total   /= ticks
    user    /= ticks
    system  /= ticks
    wait    /= ticks
    idle    /= ticks
    steal   /= ticks

    report.data('total', total)
    report.data('user', user)
    report.data('system', system)
    report.data('wait', wait)
    report.data('idle', idle)
    report.data('steal', steal)
