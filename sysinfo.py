#!/usr/bin/env python
import sys, os, glob, time

class Report:
    def __init__(self, config):
        self.config = config
        self.report = {'errors':[]}

    def data(self, k, v):
        self.report[k] = v

    def error(self, msg):
        self.report['errors'].append(msg)

    def hide(self):
        self.report = None

class Sysinfo:
    def __init__(self, config):
        self.config = config

    def report(self):
        report = {'errors':[]}
        report['create_time'] = int(time.time())
        for py in glob.glob(os.path.dirname(__file__) + '/mod/*.py'):
            mod_name = os.path.basename(py).replace('.py', '')
            if mod_name == '__init__':
                continue
            if not self.config.get_bool('mod_' + mod_name, True):
                continue
            mod = __import__('mod.' + mod_name, fromlist=[mod_name])
            if hasattr(mod, 'get'):
                sub_rp = Report(self.config)
                mod.get(sub_rp)
                if sub_rp.report is not None:
                    report[mod_name] = sub_rp.report
            else:
                report['errors'].append('can\'t find get method of %s' % mod_name)
        return report   

if __name__ == '__main__':
    import json
    import config_parser
    cfg = config_parser.Config('/etc/longview_py.conf')
    report = Sysinfo(cfg).report()
    errors = []
    for k in report:
        if type(report[k]) == 'dict':
            errors += report[k]['errors']
    print 'report:', json.dumps(report, indent=2)
    print 'errors:', json.dumps(errors, indent=2)
