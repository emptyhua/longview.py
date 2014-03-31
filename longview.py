#!/usr/bin/env python
import sys, os
import traceback
try:
    import json
except:
    import simplejson as json
import urllib, urllib2, socket
import datetime
import sysinfo, config_parser

if __name__ == '__main__':

    print >>sys.stderr, datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')

    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = '/etc/longview_py.conf'

    try:
        cfg = config_parser.Config(config_path)
    except config_parser.ConfigError:
        print >> sys.stderr, 'can\'t read conf', config_path
        sys.exit(1)

    
    print >>sys.stderr, 'config ->', json.dumps(cfg.pool, indent=2)

    try:
        report = sysinfo.Sysinfo(cfg).report()
    except:
        report = {}
        report['unexpected_error'] = traceback.format_exc()
    
    print >>sys.stderr, 'report ->', json.dumps(report, indent=2)

    if not cfg.get_str('report_url'):
        print >> sys.stderr, 'can\'t get report_url from %s' % config_path
        sys.exit(1)

    report_data     = json.dumps(report)

    if cfg.get_bool('report_gzip'): 
        report_data     = report_data.encode('zlib')
    
    post_data = {}

    for key in cfg.pool:
        if key.startswith('post_'):
            post_data[key.replace('post_', '')] = cfg.pool[key]
    print >>sys.stderr, 'addtion post fields -> ', json.dumps(post_data, indent=2)

    post_data['report']     = report_data

    if cfg.get_bool('report_gzip'): 
        post_data['gzip'] = 'on'; 
    else:
        post_data['gzip'] = 'off'; 
    
    post_data_encode = urllib.urlencode(post_data)

    request = urllib2.Request(cfg.get_str('report_url'), post_data_encode)
    request.add_header('Content-type', 'application/x-www-form-urlencoded')
    
    retry       = 0 
    retry_max   = cfg.get_int('http_retry', 3)
    timeout     = cfg.get_int('http_timeout', 10)

    if sys.version_info < (2, 6):
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)

    while retry <= retry_max:
        try:
            if sys.version_info < (2, 6):
                response = urllib2.urlopen(request)
            else:
                response = urllib2.urlopen(request, timeout=timeout)
            break
        except Exception, e:
            response = None
            print >>sys.stderr, 'error: %s' % str(e)
            retry += 1
            continue

    if sys.version_info < (2, 6):
        socket.setdefaulttimeout(old_timeout)
    
    if response:
        print >>sys.stderr, 'report success'
        print >>sys.stderr, ''.join(response.info().headers)
        print >>sys.stderr, response.read()
    else:
        sys.exit(1)
