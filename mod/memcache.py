#!/usr/bin/env python

import os, socket 

def get(report):
    hosts = []
    index = 0

    while report.config.get_str('memcache_host%d' % index):
        hosts.append(_get(report, index)) 
        index += 1

    if len(hosts):
        report.data('hosts', hosts) 
    else:
        report.hide()

def _get(report, index):
    info = {}
    label   = report.config.get_str('redis_label%d' % index)
    host    = report.config.get_str('memcache_host%d' % index)
    port    = report.config.get_int('memcache_port%d' % index, 1121)

    if label:
        info['label'] = label
    info['host'] = host
    info['port'] = port

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect((host, port)) 
        client.send('stats\r\n')
        status_text = client.recv(4096)
        client.close()
    except Exception, e:
        info['error'] = 'can\'t connnect to memcache server %s' % str(e)
        return info
    
    for line in status_text.split('\r\n'):
        if not line.startswith('STAT'):
            continue
        tmp = line.strip().split(' ')
        if tmp[2].isdigit():
            info[tmp[1].strip()] = int(tmp[2])
        else:
            info[tmp[1].strip()] = tmp[2]

    return info
