#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import json
import logging
import random
import paho.mqtt.client
from typing import Optional
from app.config import Config

class MQTTClient(object):

    ## Class constructor
    def __init__(self, logger: logging, config: Config) -> None:

        ## get class name
        self.module_name = type(self).__name__

        self.client = None
        self.logger = logger
        self.subscriptions = []
        self.MQTT_BROKER_HOST, self.MQTT_BROKER_PORT, self.MQTT_BROKER_USER, self.MQTT_BROKER_PASS, self.MQTT_CLIENT_ID = self._config(config)

    ## Class destructor
    def __del__(self) -> None:
        self.disconnect()


    ## Read module configuration
    def _config(self, config: Config):
        try:
            ## load configuration
            config = config.modules()
            module = config[self.module_name]

            ## parse configuration
            host = os.getenv('MQTT_HOST', module['host'])
            port = os.getenv('MQTT_PORT', module['port'])
            user = os.getenv('MQTT_AUTH_USER', module['user'])
            password = os.getenv('MQTT_AUTH_PASS', module['password'])
            client = f'python-mqtt-{random.randint(0, 1000)}'
            return host, port, user, password, client
        except Exception as e:
            self.logger.critical('[MQTT] Cannot read configuration for module. Details {}'.format(e))
            sys.exit(1)


    ## Close MQTT Broker connection
    def disconnect(self) -> None:
        if self.client is not None:
            self.client.disconnect()
            self.client.loop_stop(force=True)
            self.client = None

    ## Check MQTT Broker connection state
    def isConnected(self, client: paho.mqtt.client.Client) -> bool:
        return client.is_connected()

    ## Process blocking loop thread
    def loop_forever(self) -> None:
        try:
            ## Start networking daemon
            self.client.loop_forever()
        except KeyboardInterrupt as e:
            self.disconnect()
            self.logger.info('[MQTT] Connection to MQTT Broker interrupted by user request. Details: {}'.format(e))


    ## Process single loop thread
    def loop_start(self) -> None:
        try:
            ## Start networking standalone
            self.client.loop_start()
        except KeyboardInterrupt as e:
            self.disconnect()
            self.logger.info('[MQTT] Connection to MQTT Broker interrupted by user request. Details: {}'.format(e))  


    ## Subscribe for MQTT topic
    def subscribe(self, client: paho.mqtt.client.Client, topic: str) -> None:
        if client is not None:
            self.logger.info('[MQTT] Subscribing on events in topic {}'.format(topic))
            try:
                client.subscribe(topic, qos=1)
                self.logger.info('[MQTT] Subscribed on events in topic {}'.format(topic))
            except Exception as e:
                self.logger.critical('[MQTT] Cannot subscribe on topic {}. Details: {}'.format(e))    
        else:
            self.logger.critical('[MQTT] Cannot subscribe for topic {}, no live connection to MQTT broker'.format(topic)) 


    ## Send message to topic on MQTT Broker
    def publish(self, topic: str, message: Optional[bytes] = None, qos: int = 0, retain: bool = False):
        # return MQTTMessageInfo
        try:
            self.client.publish(topic, message, qos, retain)
        except Exception as e:
            self.logger.critical('[MQTT] Cannot publish send message to topic {}. Error: {}'.format(topic, e))


    ## Reconnect to las MQTT server
    def reconnect(self, onMessageCallback) -> paho.mqtt.client.Client or None:
        self.logger.debug('[MQTT] Reconnecting to last use server.') 
        self.disconnect()
        return self.initialize(onMessageCallback)

    ## Initialization of MQTT client
    def initialize(self, onMessageCallback) -> paho.mqtt.client.Client or None:

        ## MQTT callback
        def mqtt_onConnect(client, userdata, flags, reasonCode: int):
            if reasonCode == 0:
                #self.FLAG_CONNECTED = True
                self.logger.info('[MQTT] Connected to MQTT Broker successfully')
            else:
                self.logger.critical('[MQTT] Cannot connect to MQTT Broker on {}'.format(self.MQTT_BROKER_HOST))

        ## MQTT callback
        def mqtt_onMessage(client, userdata, message: paho.mqtt.client.MQTTMessage):
            try:
                payload = message.payload.decode('utf-8')

                self.logger.debug('[MQTT] Received message {}'.format(payload))
                onMessageCallback(message.topic, payload)

            except Exception as error:    
                self.logger.critical('[MQTT] Message decoding failed: {}'.format(str(error)))
                pass

        ## MQTT callback
        def mqtt_onDisconnect(client, userdata, reasonCode: int):
            #self.FLAG_CONNECTED = False

            if reasonCode == 0:
                self.logger.info('[MQTT] Disconnected from MQTT Broker successfully')
            else:    
                self.logger.critical('[MQTT] Unexpected disconnection from MQTT Broker with code: {}.'.format(str(reasonCode)))

        ## MQTT callback
        def mqtt_onSubscribe(client, userdata, mid, granted_qos):
            self.logger.info('[MQTT] Subscribed on topic {} with qos {} successfully'.format(mid, granted_qos))

        ## MQTT callback
        def mqtt_onPublish(client, userdata, result):
            self.logger.info('[MQTT] Message published to MQTT Broker with result {}'.format(result))

        # Connect to MQTT broker
        if self.client is None:
            self.logger.info('[MQTT] Connecting to MQTT Broker with client ID {}'.format(self.MQTT_CLIENT_ID))
            self.client = paho.mqtt.client.Client(self.MQTT_CLIENT_ID, clean_session=False)
            self.client.username_pw_set(self.MQTT_BROKER_USER, self.MQTT_BROKER_PASS)
            self.client.on_connect = mqtt_onConnect
            self.client.on_message = mqtt_onMessage
            self.client.on_disconnect = mqtt_onDisconnect
            self.client.on_subscribe = mqtt_onSubscribe
            self.client.on_publish = mqtt_onPublish
            self.client.reconnect_delay_set(min_delay=1, max_delay=10)

            try:
                self.client.connect(host=self.MQTT_BROKER_HOST, port=self.MQTT_BROKER_PORT, keepalive=30)
            except Exception as error:
                self.logger.critical('[MQTT] Could not connect to MQTT broker: {}'.format(str(error)))
                self.disconnect()
                return None

            else:
                ## connect in a non-blocking manner
                #self.FLAG_CONNECTED = True
                self.loop_start()
                return self.client

        else:
            return self.client        