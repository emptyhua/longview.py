#!/usr/bin/env python

import os, urllib2, json

def get(report):
    pools = []
    index = 0

    while report.config.get_str('php_fpm_status%d' % index):
        pools.append(_get(report, index)) 
        index += 1

    if len(pools):
        report.data('pools', pools) 
    else:
        report.hide()

def _get(report, index):
    info = {}
    fpm_status = report.config.get_str('php_fpm_status%d' % index)
    fpm_status = fpm_status.split('?')[0] + '?json'
    info['status_url'] = fpm_status

    fpm_label  = report.config.get_str('php_fpm_label%d' % index)
    if fpm_label:
        info['label'] = fpm_label

    try:
        response = urllib2.urlopen(fpm_status, timeout=3)
    except Exception as e:
        info['error'] = 'can\'t get %s' % fpm_status
        return info
    text = response.read()

    try:
        stat = json.loads(text)
    except:
        info['error'] = 'The php-fpm status page doesn\'t look right.'
        return info

    for k in stat:
        info[k.replace(' ', '_')] = stat[k] 

    return info
