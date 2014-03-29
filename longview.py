#!/usr/bin/env python
import sys, os
import traceback
import json
import urllib, urllib2
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
    except config_parser.ConfigError as e:
        print >> sys.stderr, 'can\'t read conf', config_path
        sys.exit(1)

    for key in ('report_url',):
        if not cfg.get_str(key):
            print >> sys.stderr, 'can\'t get %s from %s' % (key, config_path)
            sys.exit(1)

    print >>sys.stderr, 'config ->', json.dumps(cfg.pool, indent=2)

    try:
        report = sysinfo.Sysinfo(cfg).report()
    except:
        report = {}
        report['unexpected_error'] = traceback.format_exc()
    
    print >>sys.stderr, 'report ->', json.dumps(report, indent=2)

    report_data     = json.dumps(report)

    if cfg.get_bool('report_gzip'): 
        import base64
        import gzip
        import StringIO
        report_stream   = StringIO.StringIO()
        gzipper         = gzip.GzipFile(fileobj=report_stream, mode='w')
        gzipper.write(report_data)
        gzipper.close()
        report_data     = report_stream.getvalue()
        report_data     = base64.b64encode(report_data)
    
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
    while retry <= retry_max:
        try:
            response = urllib2.urlopen(request, timeout=cfg.get_int('http_timeout', 10)) 
            break
        except Exception as e:
            response = None
            print >>sys.stderr, 'error: %r' % e
            retry += 1
            continue

    if response and response.getcode() == 200:
        print >>sys.stderr, 'report success'
    else:
        sys.exit(1)
