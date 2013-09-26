#-*- coding:utf-8 -*-
'''
Created on Oct 19, 2012

@author: johnny
'''

import ConfigParser, os
import base_utils
from errors import error

root_dir = base_utils.ROOT_PATH

global_file_name = 'global_config.ini'
    
GLOBAL_CONFIG_FILE = os.path.join(root_dir, global_file_name)


class ConfigError(error.CommonError):
    pass

class Configer(object):
    
    def set_config_file(self, config_file=GLOBAL_CONFIG_FILE):
        self.config_file = config_file
        self.config = None
    
    def _ensure_config_parsed(self):
        if self.config is None:
            self.parse_config_file()
    
    def parse_config_file(self):
        self.config = ConfigParser.ConfigParser()
        if self.config_file and os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            raise ConfigError('%s not found' % (self.config_file))
        
    def get_config_value(self, section, key):
        self._ensure_config_parsed()

        try:
            val = self.config.get(section, key)
        except ConfigParser.Error:
            msg = ("Value '%s' not found in section '%s'" %
                   (key, section))
            raise ConfigError(msg)

        return val.strip()