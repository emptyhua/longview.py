#!/usr/bin/env python

import os

def get(report):
    keys = ('MemTotal', 'MemFree', 'Buffers', 'Cached', 'SwapTotal', 'SwapFree')
    try:
        for line in open('/proc/meminfo', 'r'):
            tmp = line.split(':')
            if tmp[0] in keys:
                report.data(tmp[0], int(tmp[1].replace('kB', '').strip()))
    except IOError as e:
        report.error('can not open /proc/meminfo')
