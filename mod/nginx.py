#!/usr/bin/env python

import os, urllib2

def get(report):
    nginx_status = report.config.get_str('nginx_status', 'http://127.0.0.1/nginx_status')
    try:
        response = urllib2.urlopen(nginx_status, timeout=3)
    except Exception as e:
        report.error('can\'t get %s' % nginx_status)
        return
    text = response.read()

    server = response.info().getheader('Server')
    if server:
        report.data('version', server)

    if text.find('server accepts handled requests') == -1:
        report.error('The Nginx status page doesn\'t look right.')
        return
    '''
    Active connections: 1 
    server accepts handled requests
     16 16 16 
    Reading: 0 Writing: 1 Waiting: 0 
    '''
    find_requests = False
    for line in text.split('\n'):
        if line.startswith('Active connections'):
            report.data('active', int(line.split(':')[1].strip()))
        elif line.startswith('server accepts'):
            find_requests = True
        elif find_requests:
            tmp = [int(i.strip()) for i in line.strip().split(' ')] 
            report.data('accepted_cons', tmp[0])
            report.data('handled_cons', tmp[1])
            report.data('requests', tmp[2])
            find_requests = False
        elif line.startswith('Reading'):
            tmp = [int(i) for i in line.strip().split(' ') if i.isdigit()]
            report.data('reading', tmp[0])
            report.data('writing', tmp[1])
            report.data('waiting', tmp[2])
