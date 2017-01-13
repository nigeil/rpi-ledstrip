#!/bin/python

import paho.mqtt.client as mqtt
import time 

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
        color0 = msg.payload
    if (msg.topic == topic_color1):
        color1 = msg.payload
    if (msg.topic == topic_fadeSetting):
        fadeSetting = msg.payload
    return 0

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

while True:
    client.publish(topic_color0, "#000000", qos=2)
    time.sleep(1)
