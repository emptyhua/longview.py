#!/usr/bin/env python

import MySQLdb

def get(report):
    hosts = []
    index = 0

    while report.config.get_str('mysql_host%d' % index):
        hosts.append(_get(report, index)) 
        index += 1

    if len(hosts):
        report.data('hosts', hosts) 
    else:
        report.hide()
    
def _get(report, index):
    info    = {}
    label   = report.config.get_str('mysql_label%d' % index)
    host    = report.config.get_str('mysql_host%d' % index, 'localhost')
    port    = report.config.get_int('mysql_port%d' % index, 3306)
    user    = report.config.get_str('mysql_user%d' % index, 'root')
    passwd  = report.config.get_str('mysql_passwd%d' % index, '')
    
    if label:
        info['label'] = label

    info['host'] = host
    info['port'] = port

    try:
        db = MySQLdb.connect(host=host,
                port=port,
                user=user,
                passwd=passwd)
    except Exception, e:
        info['error'] = 'can\'t connect to mysql server %s' % str(e)
        return info

    cursor = db.cursor()
    cursor.execute('''
    SHOW /*!50002 GLOBAL */ STATUS  WHERE Variable_name IN (
                "Com_select", "Com_insert", "Com_update", "Com_delete",
                "Slow_queries", 
                "Bytes_sent", "Bytes_received",
                "Connections", "Max_used_connections", "Aborted_Connects", "Aborted_Clients",
                "Qcache_queries_in_cache", "Qcache_hits", "Qcache_inserts", "Qcache_not_cached", "Qcache_lowmem_prunes"
            )
    ''')
    for item in cursor.fetchall():
        info[item[0]] = int(item[1])

    cursor.execute('''
    SHOW /*!50002 GLOBAL */ VARIABLES LIKE "version"
    ''')
    for item in cursor.fetchall():
        info[item[0]] = item[1]
    
    return info
