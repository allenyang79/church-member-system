# -*- coding: utf-8 -*-
import json
import os
import sys

from ConfigParser import SafeConfigParser

import argparse



class CustomConfigParser(SafeConfigParser):
    def getlist(self, section, option, map_fn=lambda x: x):
        val = self.get(section, option)
        val = val.split(',')
        return map(map_fn, val)

    def getjson(self, section, option):
        val = self.get(section, option)
        return json.loads(val)

    def getpath(self, section, option):
        path = self.get(section, option)
        if path.startswith('/'):
            return path
        else:
            return os.path.abspath(os.path.join(os.path.dirname(__file__), self.get(section, option)))

#global config
env = os.getenv('ENV', 'default')

config = CustomConfigParser()
config.add_section('global')
config.set('global', 'root_dir', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


config_path = os.path.join(config.get('global', 'root_dir'), 'configs/default.ini')
config.read(config_path)

if env != 'default':
    config_path = os.path.join(config.get('global', 'root_dir'), 'configs/%s.ini' % env)
    if not os.path.exists(config_path):
        raise Exception('config file is not existed. %s' % config_path)
    config.read(config_path)


if __name__ == '__main__':
    print config.get('global', 'root_dir')
    print os.path.join(config.getpath('global', 'logs_dir'), 'log.log')
