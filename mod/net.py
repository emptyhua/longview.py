#!/usr/bin/env python

import os, socket, fcntl, struct, re

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])
    s.close()
    return ip

def get(report):
    try:
        net_dev_fp = open('/proc/net/dev', 'r')
    except IOError:
        report.error('can not open /proc/net/dev')
        return 
    ifaces = []
    for line in net_dev_fp:
        line = line.strip()
        tmp = re.split(r'[:\s]+', line.strip())
        if not tmp[1].isdigit():
            continue
        if tmp[0] == 'lo':
            continue
        iface = {}
        iface['name']       = tmp[0] 
        iface['rx_bytes']   = int(tmp[1])
        iface['tx_bytes']   = int(tmp[9])
        if iface['rx_bytes'] == 0 and iface['tx_bytes'] == 0:
            continue
        iface['ip']         = get_ip_address(tmp[0])
        try:
            address_path    = '/sys/class/net/' + tmp[0] + '/address'
            iface['mac']    = open(address_path).read().strip()
        except IOError:
            report.error('can not open %s' % address_path)
        ifaces.append(iface) 

    if len(ifaces):
        report.data('ifacee', ifaces)
