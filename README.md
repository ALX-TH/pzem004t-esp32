# PZEM004T to InfluxDB/Prometheus over ESP32 controller

![Dashboard](https://raw.githubusercontent.com/ALX-TH/pzem004-esp32/master/readme/prometheus.png)

This is a simple script witch allow translate messages from MQTT topic to InfluxDB (and/or) Prometheus services.

Script support next features:
```
1) auto-reconnect to services in case if some of them are down
2) queue as message bus
3) async database/queue/mqtt clients
4) configuration over yaml manifest or Os.Env
5) energy tariffs configuration based on time
```

## How its works
Script connects to MQTT server and subscribe for updates on configured topic. When new message received script creates payload for InfluxDB from message payload.
During processing messege scripts can add information about energy tariff to payload, please check example in example.app.yaml at config directory.

## Stack
```
python3
docker
docker-compose
```

## Deploy
```
$ mv config/example.app.yaml config/app.yaml
$ python3 -m pip install -r requirements.txt
$ docker network create pzem004
$ docker-compose up -d
$ python3 bootstrap.py
```

## Docker services  

| Service        | Link                           | Description  |
|----------------| ------------------------------ | -------------|
| Grafana        | http://localhost:3000          |              |
| InfluxDB UI    | http://localhost:8086          |              |
| Prometheus UI  | http://localhost:9090          |              |
| Prometheus exporter page | http://localhost:9163 |             |

## Debug
Script also supports DEBUG mode. Information in this mode will be extended. Please set (pass) variable DEBUG=True to script runtime.


## ESP32 Tasmota snippets

#### Set timezone Europe/Kyiv

```
Backlog TimeZone 99; TimeSTD 0,0,10,1,2,120; TimeDST 0,0,3,1,2,180; NtpServer1 pool.ntp.org; Latitude 50.46594165335294; Longitude 30.34857482144722
```

### Links
Tasmota templates: https://templates.blakadder.com/

### Other

Install ps tool
```
$ apt-get install -y procps
```