#!/bin/python
# Main client; interfaces to MQTT broker and rpi_gpio pins to power LED strip

# Library imports
import pigpio
import paho.mqtt.client as mqtt
from time import sleep

# src code imports
from determine_pwm import determine_pwm
from fade import fade
from gracefulkiller import GracefulKiller

# Global defines - modify these to your liking

## PWM pins; broadcom numbering
RED_PIN   = 12
GREEN_PIN = 18 
BLUE_PIN  = 13

## MQTT topic trees
topic_color0 = "home/bedroom/ledstrip/color0"
topic_color1 = "home/bedroom/ledstrip/color1"
topic_fadeSetting = "home/bedroom/ledstrip/fadeSetting"
TOPICS = [topic_color0, topic_color1, topic_fadeSetting]

## MQTT server settings
MQTTserver = "thecloudkingdom.nigelmichki.ninja"
MQTTport = 8883
MQTTuser = "test"         # Set to None if no username/password
MQTTpassword = "for test" # Set to None if no username/password
MQTTcapath = "/etc/ssl/certs/ca-certificates.crt"


# RPI Helper functions
## Directly sets the PWM on the red, green, and blue pins
## which are defined globally
def set_pwm(r_duty, g_duty, b_duty):
    pi.set_PWM_dutycycle(RED_PIN, r_duty)
    pi.set_PWM_dutycycle(GREEN_PIN, g_duty)
    pi.set_PWM_dutycycle(BLUE_PIN, b_duty)
    return 0


# MQTT state variables
color0 = "#000000"
color1 = "#000000"
fadeSetting = "no"

# MQTT helper functions
## What to do when a connection is established to the MQTT broker
def on_connect(client, userdata, flags, rc):
    # If we subscribe to topics on-connect, disconnects will be more graceful 
    for topic in TOPICS:
        client.subscribe(topic, qos=2)

    print("[LOG] Connected to broker with result code " + str(rc))
    return 0

## What to do when a message is recieved from any subscribed topic
def on_message(client, userdata, msg):
    print("[LOG] message from topic " + str(msg.topic)
          + ": " + str(msg.payload))
    if (msg.topic == topic_color0):
        print("[LOG] setting new color0 to " + str(msg.payload))
        color0 = str(msg.payload)
    if (msg.topic == topic_color1):
        print("[LOG] setting new color1 to " + str(msg.payload))
        color1 = str(msg.payload)
    if (msg.topic == topic_fadeSetting):
        print("[LOG] setting new fadeSetting to " + str(msg.payload))
        fadeSetting = str(msg.payload)
    return 0


# ---SET UP THE CLIENT---

# RPI setup
## Open up the RPI GPIO ports for writing, default to OFF (0,0,0)
pi = pigpio.pi()
set_pwm(0,0,0) 


# MQTT setup
## Create the client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(MQTTcapath)

if ((MQTTuser is not None) and (MQTTpassword is not None)):
    client.username_pw_set(MQTTuser, MQTTpassword)

### Call the connection function last
client.connect(MQTTserver, MQTTport)

## Start the client loop to check for messages in background thread
client.loop_start()



# --- START PICKING COLORS ---

# Core color changing loop
# TODO: Change to gracefulkiller for loop condition
shouldRun = True
currentColor = color0
while (shouldRun == True):
    if (color0 != currentColor):
        colorToSet = determine_pwm(color0)
        set_pwm(*colorToSet)
        currentColor = color0 
    sleep(0.5)

# --- END THE CLIENT ---
# TODO: exit gracefully
exit()
