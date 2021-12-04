#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from ruamel.yaml import YAML, YAMLError

class Config(object):
    """ Config loader class """

    ## Class constructor
    def __init__(self, logger: logging, path: str) -> None:

        ## get class name
        self.module_name = type(self).__name__

        self.logger = logger
        self.rootPath = path
        self.configDir = 'config'
        self.configFile = 'app.yaml'

        ## for caching configuration
        self.modulesConfigCache = None
        self.sensorsConfigCache = None

    def load_config(self, entity: str):
        try:
            stream = "{}{}{}{}{}".format(self.rootPath, os.sep, self.configDir, os.sep, self.configFile)
            yaml = YAML(typ='safe')
            content = yaml.load(open(stream))
            return content[entity]
        except (FileNotFoundError, AttributeError, YAMLError, KeyError, IndexError, ValueError, TypeError) as e:
            self.logger.critical('[{}] Cannot load configuration file. Details {}.'.format(self.module_name, e))  
            sys.exit(1)

    def modules(self):
        if self.modulesConfigCache is None:
            self.logger.debug('[Config] Loading configuration of modules from config file.')
            self.modulesConfigCache = self.load_config('modules')

        return self.modulesConfigCache

    def sensors(self):
        if self.sensorsConfigCache is None:
            self.logger.debug('[Config] Loading configuration of sensors from config file.')
            self.sensorsConfigCache = self.load_config('sensors')

        return self.sensorsConfigCache
