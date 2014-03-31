#!/usr/bin/env python

import os, urllib2, sys, socket

def get(report):
    nginx_status    = report.config.get_str('nginx_status')
    if not nginx_status:
        report.hide()
        return

    headers = {}
    user_agent      = report.config.get_str('nginx_ua')
    if user_agent:
        report.debug('use agent %s' % user_agent)
        headers['User-Agent'] = user_agent
    request = urllib2.Request(nginx_status, None, headers)

    try:
        if sys.version_info < (2, 6):
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(3)
            response = urllib2.urlopen(request)
        else:
            response = urllib2.urlopen(request, timeout=3)
    except Exception, e:
        response = None
        report.error('can\'t get %s %s' % (nginx_status, str(e)))

    if sys.version_info < (2, 6):
        socket.setdefaulttimeout(old_timeout)

    if not response:
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
