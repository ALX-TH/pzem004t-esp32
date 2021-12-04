#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from app.config import Config
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

class InfluxClient(object):

    def __init__(self, logger: logging, config: Config) -> None:
        ## get class name
        self.module_name = type(self).__name__

        self.client = None
        self.logger = logger
        self.write_api = None
        self.INFLUXDB_URL, self.INFLUXDB_TOKEN, self.INFLUXDB_ORG, self.INFLUXDB_BUCKET = self._config(config)

    ## Read module configuration
    def _config(self, config: Config):
        try:
            ## load configuration
            config = config.modules()
            module = config[self.module_name]
            
            ## parse configuration
            url = os.getenv('INFLUXDB_URL', module['url'])
            token = os.getenv('INFLUXDB_TOKEN', module['token'])
            org = os.getenv('INFLUXDB_ORG', module['org'])
            bucket = os.getenv('INFLUXDB_BUCKET', module['bucket'])
            return url, token, org, bucket
        except Exception as e:
            self.logger.critical('[InfluxDB] Cannot read configuration for module. Details {}'.format(e))
            sys.exit(1)

    ## Connect to InfluxDB server
    def connect(self) -> InfluxDBClient or None:
        result = None
        if self.client is None:
            try:
                self.client = InfluxDBClient(
                    url=self.INFLUXDB_URL,
                    token=self.INFLUXDB_TOKEN,
                    org=self.INFLUXDB_ORG
                )

                self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
                self.logger.info('[InfluxDB] Connected to InfluxDB successfully')
                return self.client
            except Exception as e:
                self.logger.critical('[InfluxDB] Cannot connect to InfluxDB {}. Details {}.'.format(self.INFLUXDB_URL, e))

        return result

    def reconnect(self):
        return self.connect()

    def isConnected(self) -> bool:
        try:
            health = self.client.health()
            status = health.status
            if status == 'pass':
                return True
            else:
                return False    
        except Exception as e:
            self.logger.critical('[InfluxDB] Cannot check InfluxDB status. Details {}.'.format(e)) 
            return False


    def write_over_api(self, data):
        if self.client is not None:
            self.logger.debug('[InfluxDB] Writing InfluxDB point: {}'.format(data))    
            try:
                self.write_api.write(bucket=self.INFLUXDB_BUCKET, record=data)
            except Exception as e:
                self.logger.critical('[InfluxDB] Cannot write data into InfluxDB. Details {}.'.format(e))      
        else:
            self.logger.critical('[InfluxDB] Cannot write data into InfluxDB. No active connections.')