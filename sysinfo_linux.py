#!/usr/bin/env python

import os, re
import socket, fcntl, struct
import glob
import pwd

def cpu_rp():
    info = {}
    info['user']    = 0
    info['system']  = 0
    info['wait']    = 0
    info['load']    = os.getloadavg()
    for line in open('/proc/stat', 'r'):
        if re.match(r'^cpu\d', line) is not None:
            line = line.strip()
            tmp = re.split(r'\s+', line)
            info['user']    += int(tmp[1]) + int(tmp[2])
            info['system']  += int(tmp[3])
            info['wait']    += int(tmp[5])
    return info
             
def mem_rp():
    info = {}
    keys = ('MemTotal', 'MemFree', 'Buffers', 'Cached', 'SwapTotal', 'SwapFree')
    for line in open('/proc/meminfo', 'r'):
        tmp = line.split(':')
        if tmp[0] in keys:
            info[tmp[0]] = int(tmp[1].replace('kB', '').strip())
    return info

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
    s.close()
    return ip

def net_rp():
    info = {}
    info['ifaces'] = []
    for line in open('/proc/net/dev', 'r'):
        line = line.strip()
        tmp = re.split(r'[: ]+', line.strip())
        if not tmp[1].isdigit():
            continue
        if tmp[0] == 'lo':
            continue
        iface = {}
        iface['rx_bytes'] = int(tmp[1])
        iface['tx_bytes'] = int(tmp[9])
        if iface['rx_bytes'] == 0 and ifaces['tx_bytes'] == 0:
            continue
        iface['ip']     = get_ip_address(tmp[0])
        iface['mac']    = open('/sys/class/net/' + tmp[0] + '/address').read().strip()
        info['ifaces'].append(iface) 
    return info

def sys_rp():
    info = {}
    info['sysname'], _, info['release'], info['version'], info['arch'] = os.uname()
    info['hostname'] = socket.gethostname()
    info['cpu_num']  = 0
    info['cpu_type'] = None
    info['uptime']   = 0
    for line in open('/proc/cpuinfo', 'r'):
        if line.find('processor') == 0:
            info['cpu_num'] += 1
        elif line.startswith('model name') and info['cpu_type'] is None:
            info['cpu_type'] = line.split(':')[1].strip()
    info['uptime']   = int(float(open('/proc/uptime').read().split(' ')[0]))
    return info

def disk_rp():
    info = {}
    info['disks'] = []
    types = ('ext2', 'ext3', 'ext4')
    for line in open('/proc/mounts', 'r'):
        tmp = line.strip().split(' ')
        if tmp[2] in types:
            stat= os.statvfs(tmp[1])
            disk = {}
            disk['path']    = tmp[1]
            disk['total']   = stat.f_blocks * stat.f_frsize
            disk['avail']   = stat.f_bavail * stat.f_frsize
            info['disks'].append(disk)
    return info

def proc_rp():
    info = {}
    info['process_list'] = []
    exclude_proc = ('rsyslogd', 'mingetty', 'udevd', 'init', 'sshd')
    io_fields = ('read_bytes', 'write_bytes')
    for proc_dir in glob.glob('/proc/[0-9]*'):
        if not os.path.exists(proc_dir + '/status') \
            or not os.path.exists(proc_dir + '/stat') \
            or not os.path.exists(proc_dir + '/cmdline'):
            continue
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
                proc['vmrss'] = int(tmp[1].replace('kB', '').strip())
        if proc['name'] in exclude_proc:
            continue 
        if not len(proc['cmd']):
            continue
        if not 'vmrss' in proc:
            continue
        
        stat = re.split(r'\s+', open(proc_dir + '/stat', 'r').read())
        proc['cpu']   = int(stat[13]) + int(stat[14])
        info['process_list'].append(proc)
    return info

def sysinfo():
    report = {}
    report['sys']   = sys_rp()
    report['net']   = net_rp()
    report['mem']   = mem_rp()
    report['disk']  = disk_rp()
    report['proc']  = proc_rp()
    report['cpu']   = cpu_rp()
    return report

if __name__ == '__main__':
    import json
    report = sysinfo()
    print json.dumps(report, indent=2)
