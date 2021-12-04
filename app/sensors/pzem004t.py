#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import *
from app.config import Config

SENSOR_CLASS = 'energy'
SENSOR_NAME = 'pzem004t'
SENSOR_MEASUREMENT = 'energy'
SENSOR_MQTT_TOPIC = 'tele/pzem004tv3_87A0B8/SENSOR'

#PZEM004_URL = 'http://192.168.0.176/cm?cmnd=STATUS+8'

class Esp32(object):
    def __init__(self, Temperature: float) -> None:
        self.temperature = Temperature

    def toDictionary(self) -> dict:
        data = {}
        data['temperature'] = self.temperature
        return data

class Energy(object):

    def __init__(self, 
            TotalStartTime: str, 
            Total: float, 
            Yesterday: float, 
            Today: float, 
            Period: int, 
            Power: float, 
            ApparentPower: int, 
            ReactivePower: int, 
            Factor: float,
            Frequency: int,
            Voltage: int,
            Current: float) -> None:

        self.totalStartTime = TotalStartTime
        self.total = Total
        self.yesterday = Yesterday
        self.today = Today
        self.period = Period
        self.power = Power
        self.apparentPower = ApparentPower
        self.reactivePower = ReactivePower
        self.factor = Factor
        self.frequency = Frequency
        self.voltage = Voltage
        self.current = Current

    def toDictionary(self) -> dict:
        data = {}
        data['total_start_time'] = self.totalStartTime
        data['total'] = float(self.total)
        data['yesterday'] = float(self.yesterday)
        data['today'] = float(self.today)
        data['period'] = int(self.period)
        data['power'] = int(self.power)
        data['apparent_power'] = int(self.apparentPower)
        data['reactive_power'] = int(self.reactivePower)
        data['factor'] = float(self.factor)
        data['frequency'] = int(self.frequency)
        data['voltage'] = int(self.voltage)
        data['current'] = float(self.current)
        return data

class EnergySensor(object):

    def __init__(self, Time: str, ENERGY: Energy, ESP32: Esp32, TempUnit: str) -> None:
        self.time = Time
        self.energy = Energy(**ENERGY)
        self.esp32 = Esp32(**ESP32)
        self.tempUnit = TempUnit

    def getTime(self) -> str:
        return self.time

    def getEnergy(self) -> dict:
        return self.energy.toDictionary()

    def getEsp32(self) -> dict:
        return self.esp32.toDictionary()

    def getTempUnit(self) -> str:
        return self.tempUnit

    def toDictionary(self) -> dict:
        data = {}
        data['time'] = self.getTime()
        data['energy'] = self.getEnergy()
        data['esp32'] = self.getEsp32()
        data['temperature_unit'] = self.getTempUnit()
        return data

    def ifDateIsBetween(self, startDate: str, endDate: str, currentDate: str):
        timeFormat = "%H:%M:%S"

        _startH, _startM, _startS = startDate.split(":")
        _endH, _endM, _endS = endDate.split(":")
        _currentH, _currentM, _currentS = currentDate.split(":")

        timeOfStart = datetime.strptime('{}:{}:{}'.format(_startH, _startM, _startS),timeFormat)
        timeOfEnd = datetime.strptime('{}:{}:{}'.format(_endH, _endM, _endS),timeFormat)
        timeCurrent = datetime.strptime('{}:{}:{}'.format(_currentH, _currentM, _currentS),timeFormat)

        print("ifDateIsBetween ||| timeOfStart: {} ||| timeOfEnd: {} ||| timeCurrent: {}".format(timeOfStart, timeOfEnd, timeCurrent)) 
        if timeOfStart <= timeOfEnd:
            return timeOfStart <= timeCurrent < timeOfEnd
        else: # over midnight e.g., 23:30-04:15
            return timeOfStart <= timeCurrent or timeCurrent < timeOfEnd


    def getSubscriptionType(self, config: dict) -> str:
        cfg = config
        schedules = cfg['schedule']

        sensorTime = datetime.strptime(self.getTime(), "%Y-%m-%dT%H:%M:%S")
        timeOfMeasurement = "{}:{}:{}".format(sensorTime.hour, sensorTime.minute, sensorTime.second)

        for schedule in schedules:

            ## get schedule name
            scheduleName = schedule
            
            ## get schedule object full
            schedule = schedules[schedule]

            ## get schedule conditions all
            conditions = schedule['conditions']

            ## foreach each condition
            for condition in conditions:
                if type(condition) is dict:
                    if self.ifDateIsBetween(condition['after'], condition['before'], timeOfMeasurement):
                        return scheduleName
                else:
                    return "undefined"


class PZEM004TSensor():
    def __init__(self, sensorData: str) -> None:

        ## get class name
        self.module_name = type(self).__name__
        
        ## create json object from string input data
        dictionary = json.loads(sensorData)

        ## create object class
        self.sensor = EnergySensor(**dictionary)


    def get(self, config: Config):
        ## get class name
        self.module_name = type(self).__name__

        ## load sensor configuration
        sensorsConfig = config.sensors()
        config = sensorsConfig[self.module_name]


        payload = []
        response = {}
        tags = {}

        tags['class'] = SENSOR_CLASS
        tags['sensor'] = SENSOR_NAME
        tags['time_period'] = self.sensor.getSubscriptionType(config)

        response['measurement'] = SENSOR_MEASUREMENT
        response['tags'] = tags
        response['fields'] = self.sensor.getEnergy()

        payload.append(response)
        return payload