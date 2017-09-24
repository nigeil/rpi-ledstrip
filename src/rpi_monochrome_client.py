#!/bin/python
# Main client; interfaces to MQTT broker and rpi_gpio pins to power LED strip

# Library imports
import pigpio
import paho.mqtt.client as mqtt
from time import sleep
import configparser as cp
import os
import time

# src code imports
from determine_monochrome_pwm import determine_monochrome_pwm
from fade_monochrome import fade_monochrome
from gracefulkiller import GracefulKiller

# pause for a few seconds for systemd to get network interfaces up
# (assuming you start this at boot - safely removed otherwise)
time.sleep(10)

# Parse config file
config = cp.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "client_settings.conf"))

## Get PWM pinouts
LED_PIN   = int(config["PINOUT"]["LED_PIN"])

## Get MQTT topic trees
topic_intensity = config["TOPICS"]["topic_intensity"]
topic_fadeSetting = config["TOPICS"]["topic_fadesetting"]
topic_speed       = config["TOPICS"]["topic_speed"]
TOPICS = [topic_intensity, topic_fadeSetting, topic_speed]

## Get MQTT server settings
MQTTserver = config["MQTT"]["MQTTserver"]
MQTTport = int(config["MQTT"]["MQTTport"])
MQTTuser = config["MQTT"]["MQTTuser"]
MQTTpassword = config["MQTT"]["MQTTpassword"]
MQTTcapath = config["MQTT"]["MQTTcapath"]


# RPI Helper functions
## Directly sets the PWM on the red, green, and blue pins
## which are defined globally
def set_pwm(led_duty):
    pi.set_PWM_dutycycle(LED_PIN, led_duty)
    return 0


# MQTT state variables
## Placed in lists so that they can be accessed persistently
intensity = [100] # %, 0 is off
fadeSetting = ["solid"]
speed = [0] # range from [0,60] Hz 

# MQTT helper functions
## What to do when a connection is established to the MQTT broker
def on_connect(client, userdata, flags, rc):
    # If we subscribe to topics on-connect, disconnects will be more graceful 
    for topic in TOPICS:
        client.subscribe(topic, qos=2)

    print("[LOG] Connected to broker with result code " + str(rc))
    return 0

## What to do when a connection is lost (wait a bit, then reconnect)
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("[LOG] Unexpected MQTT disconnection. Reconnect in 5s")
        time.sleep(5)
        client.reconnect()


## What to do when a message is recieved from any subscribed topic
def on_message(client, userdata, msg):
    print("[LOG] message from topic " + str(msg.topic)
          + ": " + str(msg.payload))
    if (msg.topic == intensity):
        print("[DEBUG] setting new intensity to " + (msg.payload).decode('utf-8'))
        intensity[0] = (msg.payload).decode('utf-8')
    if (msg.topic == topic_fadeSetting):
        print("[DEBUG] setting new fadeSetting to " + (msg.payload).decode('utf-8'))
        fadeSetting[0] = (msg.payload).decode('utf-8')
    if (msg.topic == topic_speed):
        print("[DEBUG] setting new speed to " + (msg.payload).decode('utf-8'))
        try:
            speed[0] = int((msg.payload).decode('utf-8'))
        except ValueError:
            print("[ERROR] speed cannot be converted to integer - set to 30fps")
            speed[0] = 30
    return 0


# ---SET UP THE CLIENT---

# RPI setup
## Open up the RPI GPIO ports for writing, default to OFF (0,0,0)
pi = pigpio.pi()
set_pwm(0) 


# MQTT setup
## Create the client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
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

prevIntensity = 0
fadeColors = []
fadeCount = 0
subdivisions = 400

while (shouldRun == True):

    # update fade delay in case new speed was set
    fadeDelay = 1.0/(1 + speed[0])

    # no fade - just use solid color0 
    if (fadeSetting[0] == "solid"):
        # set new PWM if there is a new color0; otherwise do nothing
        if (intensity[0] != prevIntensity):
            colorToSet = determine_monochrome_pwm(intensity[0])
            prevIntensity = intensity[0] 
            set_pwm(*colorToSet)
            #print("[DEBUG] new pwm: " + str(colorToSet))
        sleep(0.25)
    
    # normal fade from color0 --> color1
    elif (fadeSetting[0] == "fade"):
        # reset the fade if it is 1) just starting, 
        # or 2) has a new start/end color, otherwise proceed to next color
        if ((fadeCount == 0) 
         or (intensity[0] != prevIntensity)):
            fadeColors = fade_monochrome(intensity[0], int(float(intensity[0]) / 3), subdivisions=subdivisions)
            prevIntensity = intensity[0]
            fadeCount  = 0
        colorToSet = determine_pwm(fadeColors[fadeCount%len(fadeColors)])
        set_pwm(*colorToSet)
        #print("[DEBUG] new pwm: " + str(colorToSet))
        fadeCount = (fadeCount + 1)
        sleep(fadeDelay)
    
    # strobe light between color0 and black
    elif (fadeSetting[0] == "strobe"):
        if (fadeCount == 0):
            colorToSet = determine_monochrome_pwm(intensity[0])
        elif (fadeCount == 1):
            colorToSet = determine_monochrome_pwm(0)
        set_pwm(*colorToSet)
        fadeCount = (fadeCount + 1) % 2
        sleep(fadeDelay)
    
    # turn off the strip
    elif (fadeSetting[0] == "off"):
        colorToSet = determine_monochrome_pwm(0)
        set_pwm(*colorToSet)
        sleep(0.25)


# --- END THE CLIENT ---
# TODO: exit gracefully
exit()
