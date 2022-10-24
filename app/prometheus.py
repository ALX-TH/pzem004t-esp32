#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import datetime
from app.config import Config
from prometheus_client import start_http_server, Counter, Gauge, Summary, Histogram, Info

TOTAL = Gauge('energy_power_total', 'Total consumed electrical network power for all time, kWh', ['measurement', 'deviceclass', 'sensor'])
YESTERDAY = Gauge('energy_power_yesterday_total', 'Consumed electrical network power for yesterday, kWh', ['measurement', 'deviceclass', 'sensor'])
TODAY = Gauge('energy_power_today_total', 'Total electrical network consumption power for current day, kWh', ['measurement', 'deviceclass', 'sensor'])
PERIOD = Gauge('energy_period', 'Consumed electrical network period', ['measurement', 'deviceclass', 'sensor'])
CURRENT_POWER = Gauge('energy_power_current', 'Current electrical network consumption power, W', ['measurement', 'deviceclass', 'sensor'])
APPARENT_POWER = Gauge('energy_power_apparent_current', 'Current electrical network apparent power (volt-amperes), VA', ['measurement', 'deviceclass', 'sensor'])
REACTIVE_POWER = Gauge('energy_power_reactive_current', 'Current electrical network reactive power (volt-amperes), VAr', ['measurement', 'deviceclass', 'sensor'])
FACTOR = Gauge('energy_power_factor_current', 'Current electrical network power factor (energy loss, cosφ), PF', ['measurement', 'deviceclass', 'sensor'])
FREQUENCY = Gauge('energy_frequency_current', 'Current electrical network frequency, Hz', ['measurement', 'deviceclass', 'sensor'])
VOLTAGE = Gauge('energy_voltage_current', 'Current electrical network voltage, V', ['measurement', 'deviceclass', 'sensor'])
CURRENT = Gauge('energy_amperes_current', 'Current electrical network amperes, A', ['measurement', 'deviceclass', 'sensor'])
TOTAL_START_TIME = Gauge('energy_device_first_start_timestamp', 'Timestamp of device first start', ['measurement', 'deviceclass', 'sensor'])
LAST_MEASUREMENT_TIME = Gauge('energy_last_scrape_timestamp', 'Timestamp of lastest measurement', ['measurement', 'deviceclass', 'sensor'])
SUBSCRIPTION_ID = Gauge('energy_subscription_id', 'Current subscription id', ['measurement', 'deviceclass', 'sensor'])

TOTAL_START_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

class PrometheusClient(object):

    ## Class constructor
    def __init__(self, logger: logging, config: Config) -> None:

        ## get class name
        self.module_name = type(self).__name__
        self.client = None
        self.logger = logger
        self.EXPORTER_PORT, self.PROMETHEUS_ENABLED = self._config(config)

    ## Class destructor
    def __del__(self) -> None:
        self.logger.info('[PROM] Removing client')

    ## Read module configuration
    def _config(self, config: Config):
        try:
            ## load configuration
            config = config.modules()
            module = config[self.module_name]

            ## parse configuration
            port = os.getenv('PROMETHEUS_EXPORTER_PORT', module['port'])
            enabled = os.getenv('PROMETHEUS_EXPORTER_ENABLED', module['enabled'])
            return port, enabled
        except Exception as e:
            self.logger.critical('[Prometheus] Cannot read configuration for module. Details {}'.format(e))
            sys.exit(1)

    ## Check of module enabled
    def isEnabled(self) -> bool:
        if self.PROMETHEUS_ENABLED:
            self.logger.debug('[PROM] Module is enabled. Module will process request.')
            return True
        else: 
            self.logger.debug('[PROM] Module is disabled. Enable module in config/app.yaml if needed.')
            return False

    ## Create exporter
    def start(self) -> None:
        self.logger.info('[PROM] Creating client')
        start_http_server(self.EXPORTER_PORT)

    ## Update metric
    def publish(self, data: list) -> None:
        for metric in data:
            TOTAL.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["total"])

            YESTERDAY.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["yesterday"])

            TODAY.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["today"])

            PERIOD.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["period"])

            CURRENT_POWER.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["power"])

            APPARENT_POWER.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["apparent_power"])

            REACTIVE_POWER.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["reactive_power"])

            FACTOR.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["factor"])

            FREQUENCY.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["frequency"])

            VOLTAGE.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["voltage"])

            CURRENT.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["fields"]["current"])

            TOTAL_START_TIME.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(round(datetime.datetime.strptime(metric["fields"]["total_start_time"], TOTAL_START_TIME_FORMAT).timestamp()))

            LAST_MEASUREMENT_TIME_TIMESTAMP = datetime.datetime.now()
            LAST_MEASUREMENT_TIME.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(round(datetime.datetime.timestamp(LAST_MEASUREMENT_TIME_TIMESTAMP)))

            SUBSCRIPTION_ID.labels(
                measurement = metric["measurement"], 
                deviceclass = metric["tags"]["class"], 
                sensor = metric["tags"]["sensor"]
            ).set(metric["tags"]["time_period_id"])
