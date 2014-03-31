#!/usr/bin/env python

class ConfigError(Exception):
    pass

class Config:
    def __init__(self, config_path):
        self.pool = {}
        try:
            for line in open(config_path, 'r'):
                line = line.strip()
                if line.startswith('#'):
                    continue
                tmp = line.split('=')
                if len(tmp) < 2:
                    continue
                self.pool[tmp[0].strip()] = '='.join(tmp[1:]).strip()
        except IOError:
            raise ConfigError('can\'t open %s' % config_path)

    def get_bool(self, key, default=False):
        if not self.pool.get(key):
            return default
        return self.pool.get(key).lower() == 'on'  

    def get_str(self, key, default=None):
        return self.pool.get(key) or default

    def get_int(self, key, default=None):
        v = self.pool.get(key)
        if v and v.isdigit():    
            return int(v)

    def get_list(self, key, default=None):
        v = self.pool.get(key)
        if v:
            return [i.strip() for i in v.split(',')]
        else:
            return default
