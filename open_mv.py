# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# MQTT Example.
# This example shows how to use the MQTT library to publish to a topic.
#
# 1) Copy the mqtt.py library to OpenMV storage.
# 2) Run this script on the OpenMV camera.
# 3) Install the mosquitto client on PC and run the following command:
#    mosquitto_sub -h test.mosquitto.org -t "openmv/test" -v
#
# NOTE: If the mosquitto broker is unreachable, try another broker (For example: broker.hivemq.com or broker.emqx.io)

import time
import network
from mqtt import MQTTClient

import sensor
import time
import math

SSID = "Tufts_Robot"  # Network SSID
KEY = ""  # Network key

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

# We should have a valid IP now via DHCP
print("WiFi Connected", wlan.ifconfig())

mqtt_broker = "broker.hivemq.com"
port = 1883     # this reads anything sent to ME35
topic_pub = "ME35-24/Rachael"

client = MQTTClient("Rachael", mqtt_broker, port)
client.connect()

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()

prev_error = 0
integral = 0

while True:
    clock.tick()
    img = sensor.snapshot()
    for tag in img.find_apriltags():
        img.draw_rectangle(tag.rect, color=(255, 0, 0))
        img.draw_cross(tag.cx, tag.cy, color=(0, 255, 0))

        curr_dist = tag.z_translation  # z_translation gives an estimate of the distance
        des_dist = -10

        error = des_dist - curr_dist

        kp = 100
        P = kp * error


        kd = 10
        dt = clock.avg() / 1000.0
        D = (error - prev_error) * kd/ dt


        ki = 0.1
        integral = integral + error * dt
        I = integral * ki

        # Anti-windup-prevent integral from growing too large
        integral = min(max(integral, -50), 50)

        # Don't include integral at first

        if abs(error) < 1:  # Only start integrating once the error is small
            I = ki * integral
        else:
            I = 0  # Ignore the integral until error stabilizes

        speed_adjust = P + D + I
        print(speed_adjust)

        prev_error = error

        client.publish(topic_pub, str(speed_adjust))
        time.sleep_ms(10)
