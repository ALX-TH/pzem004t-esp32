#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import queue
import asyncio
from time import sleep
from app.config import Config
from app.mqtt import MQTTClient as mqttClk
from app.influxdb import InfluxClient as influxClk
from app.prometheus import PrometheusClient as prometheusClk
from app.sensors.pzem004t import *

MQTT_TOPIC = 'tele/pzem004tv3_87A0B8/SENSOR'

class Application(object):

    def __init__(self, pwd, logger) -> None:
        self.pwd = pwd
        self.logger = logger
        self.config = Config(self.logger, self.pwd)
        self.mqtt = mqttClk(logger, self.config)
        self.influx = influxClk(logger, self.config)
        self.prometheus = prometheusClk(logger, self.config)
        self.queue = queue.Queue()
        #self.sensors = []

    #def loadModules(self):
    #    print('Not implemented')    

    ## MQTT callback processing function
    def onMessageCallback(self, topic, payload):
        self.logger.debug('[APP] Got MQTT callback with topic {} and message {}'.format(topic, payload))

        ## add payload to queue
        self.queue.put(payload)
        self.logger.debug('[APP] Adding to queue payload: {}.'.format(payload))


    ## async mqtt client
    async def asyncMqtt(self, loop):
        task = asyncio.current_task(loop)
        client = self.mqtt.initialize(self.onMessageCallback)
        self.mqtt.subscribe(client, MQTT_TOPIC)
        await asyncio.sleep(3)
        
        ## create loop for MQTT client
        while True:
            if self.mqtt.isConnected(client):
                self.logger.debug('[APP] Connection to MQTT is alive.')
            else:
                self.logger.critical('[APP] Connection to MQTT is dead. Reconnection in progress.')
                client = self.mqtt.reconnect()
                self.mqtt.subscribe(client, MQTT_TOPIC)

            await asyncio.sleep(10)

    ## async influx client
    async def asyncInfluxDb(self, loop):
        task = asyncio.current_task(loop)
        self.influx.connect()
        ## create loop for influx client
        while True:
            if self.influx.isConnected():
                self.logger.debug('[APP] Connection to InfluxDB is alive.')
            else:
                self.logger.critical('[APP] Connection to InfluxDB is dead. Reconecting')
                self.influx.connect()

            await asyncio.sleep(10)

    ## async prometheus client
    async def asyncPrometheusWorker(self, loop):
        task = asyncio.current_task(loop)
        self.prometheus.start()

        #self.logger.debug('[APP] Process: {}, status: alive.'.format(task.get_name()))

    ## async queue client
    async def asyncQueueWorker(self, loop):
        task = asyncio.current_task(loop)
        self.logger.debug('[APP] Process: {}, status: alive.'.format(task.get_name()))

        while True:
            if not self.queue.empty():

                try:
                    message = self.queue.get(block=False)
                    self.logger.debug('[APP] Got message from queue: {}'.format(message))

                    pzem004 = PZEM004TSensor(message)
                    results = pzem004.get(self.config)

                    if self.influx.isEnabled():
                        self.influx.write_over_api(results)

                    if self.prometheus.isEnabled():
                        self.prometheus.publish(results)

                except Exception as error:
                    self.logger.error('[APP] Process: {}. Will clean up queue. Error: {}'.format(task.get_name(), error))
                    self.queue.empty()
                    continue

            await asyncio.sleep(1)
            
    ## entrypoint
    def main(self):
        ## create async thread pool
        loop = asyncio.get_event_loop()
        loop.create_task(self.asyncInfluxDb(loop), name='influxdb')
        loop.create_task(self.asyncMqtt(loop), name='mqtt')
        loop.create_task(self.asyncPrometheusWorker(loop), name='prometheus')
        loop.create_task(self.asyncQueueWorker(loop), name='queue')
        loop.run_forever()