#!/usr/bin/env python

import os, re, glob, pwd

def get(report):
    excludes        = report.config.get_list('process_excludes')
    io_fields       = ('read_bytes', 'write_bytes')

    try:
        uptime  = int(float(open('/proc/uptime').read().split(' ')[0]))
    except IOError:
        report.error('can not open /proc/uptime')
        uptime  = None

    ticks       = os.sysconf('SC_CLK_TCK') 
    if uptime and ticks != -1:
        current_jiffies = uptime * ticks
    else:
        current_jiffies = None
        
    procs = []

    for proc_dir in glob.glob('/proc/[0-9]*'):
        if not os.path.exists(proc_dir + '/status') \
            or not os.path.exists(proc_dir + '/stat') \
            or not os.path.exists(proc_dir + '/cmdline'):
            continue
        try:
            proc = {}
            proc['cmd'] = open(proc_dir + '/cmdline', 'r').read().split('\0')[0]

            for line in open(proc_dir + '/status', 'r'): 
                tmp = line.strip().split(':')
                if tmp[0] == 'Name':
                    proc['name'] = tmp[1].strip() 
                elif tmp[0] == 'Pid':
                    proc['pid']  = int(tmp[1].strip())
                elif tmp[0] == 'PPid':
                    proc['ppid'] = int(tmp[1].strip())
                elif tmp[0] == 'Uid':
                    proc['user'] = pwd.getpwuid(int(re.split(r'\s+', tmp[1].strip())[0]))[0]
                elif tmp[0] == 'VmRSS':
                    proc['mem'] = int(tmp[1].replace('kB', '').strip())

            if excludes and proc['name'] in excludes:
                continue 
            if proc['ppid'] == 2 or proc['pid'] == 2:
                continue
            
            stat = re.split(r'\s+', open(proc_dir + '/stat', 'r').read())
            proc['cpu']   = int(stat[13]) + int(stat[14])
            if current_jiffies:
                start_jiffies   = int(stat[21])
                proc['age']     = (current_jiffies - start_jiffies) / ticks 
        except IOError:
            continue
        try:
            for line in open(proc_dir + '/io', 'r'): 
                tmp = line.strip().split(':') 
                if tmp[0] in io_fields:
                    proc[tmp[0]] = int(tmp[1])
        except IOError:
            pass
        procs.append(proc)

    proc_pool = {}
    for proc in procs:
        pool_key = proc['name'] + proc['user']
        if not pool_key in proc_pool:
            proc_pool[pool_key] = {
                'name':     proc['name'],
                'user':     proc['user'],
                'cmd':      proc['cmd'],
                'count':    0,
                'mem':      0,
                'cpu':      0,
                'ioread':   0,
                'iowrite':  0,
                'age':      0
                }
        proc_pool[pool_key]['count']    += 1
        proc_pool[pool_key]['mem']      += proc.get('mem') or 0
        proc_pool[pool_key]['cpu']      += proc.get('cpu') or 0
        proc_pool[pool_key]['ioread']   += proc.get('read_bytes') or 0
        proc_pool[pool_key]['iowrite']  += proc.get('write_bytes') or 0
        if proc.get('age') or 0 > proc_pool[pool_key]['age']:
            proc_pool[pool_key]['age']  = proc['age']
    
    process_list = [p for p in proc_pool.values() if p['age'] >= 60]
    report.data('process_list', process_list)

