#!/bin/python
# Main client; interfaces to MQTT broker and rpi_gpio pins to power LED strip

# Library imports
import paho.mqtt.client as mqtt
from time import sleep
import configparser as cp
import os
import time
import threading

try:
    from RPI import PWM
except ImportError:
    import dummy_rpi_gpio as PWM

# src code imports
from determine_pwm import determine_pwm
from fade import fade
from determine_monochrome_pwm import determine_monochrome_pwm
from fade_monochrome import fade_monochrome

# --- Parse config file ---
config = cp.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "client_settings.conf"))

# Get type of ledstrip (RGB or monochrome)
ledstrip_type = config["SYSTEM"]["ledstrip_type"]
if (ledstrip_type not in ["rgb", "monochrome"]):
    print("[ERROR] ledstrip type not recognized; use \'rgb\' or \'monochrome\' in config file")
    exit()

## Get the rest of the MQTT topic trees
topic_fadeSetting = config["TOPICS"]["topic_fadesetting"]
topic_speed       = config["TOPICS"]["topic_speed"]
topic_state       = config["TOPICS"]["topic_state"]

## Get PWM pinouts and color topics
if (ledstrip_type == "rgb"):
    RED_PIN      = int(config["PINOUT"]["RED_PIN"])
    GREEN_PIN    = int(config["PINOUT"]["GREEN_PIN"])
    BLUE_PIN     = int(config["PINOUT"]["BLUE_PIN"])
    topic_color0 = config["TOPICS"]["topic_color0"]
    topic_color1 = config["TOPICS"]["topic_color1"]
    TOPICS = [topic_color0, topic_color1, topic_fadeSetting, topic_speed, topic_state]

elif (ledstrip_type == "monochrome"):
    LED_PIN         = int(config["PINOUT"]["LED_PIN"])
    topic_intensity = config["TOPICS"]["topic_intensity"]
    TOPICS = [topic_intensity, topic_fadeSetting, topic_speed, topic_state]


## Get MQTT server settings
MQTTserver = config["MQTT"]["MQTTserver"]
MQTTport = int(config["MQTT"]["MQTTport"])
MQTTuser = config["MQTT"]["MQTTuser"]
MQTTpassword = config["MQTT"]["MQTTpassword"]
MQTTcapath = config["MQTT"]["MQTTcapath"]


# RPI Helper functions
## Directly sets the PWM on the red, green, and blue pins
## which are defined globally
if (ledstrip_type == "rgb"):
    def set_pwm(r_duty, g_duty, b_duty):
        pi.set_servo(RED_PIN, r_duty)
        pi.set_servo(GREEN_PIN, g_duty)
        pi.set_servo(BLUE_PIN, b_duty)
elif (ledstrip_type == "monochrome"):
    def set_pwm(led_duty):
        pi.set_servo(LED_PIN, led_duty)
        return 0


# MQTT state variables
## Placed in lists so that they can be accessed persistently
state  = ["off"]
color0 = ["#ffffff"]
color1 = ["#000000"]
fadeSetting = ["solid"]
speed = [0] # range from [0,60] Hz 
connected = False # True if connected successfully, false otherwise

# MQTT helper functions
## What to do when a connection is established to the MQTT broker
def on_connect(client, userdata, flags, rc):
    # If we subscribe to topics on-connect, disconnects will be more graceful 
    for topic in TOPICS:
        client.subscribe(topic, qos=2)

    print("[LOG] Connected to broker with result code " + str(rc))
    connected = True
    return 0

## What to do when a connection is lost (wait a bit, then reconnect)
def on_disconnect(client, userdata, rc):
    if rc != 0:
        connected = False
        print("[LOG] Unexpected MQTT disconnection. Reconnect in 1s")
        while (connected == False):
            time.sleep(1)
            try:
                client.reconnect()
                connected = True
                print("[LOG] Connected to broker with result code " + str(rc))
            except Exception:
                print("[ERROR] client unable to connect (exception thrown); trying again in 1s...")
                time.sleep(1)
    return 0


## What to do when a message is recieved from any subscribed topic
def on_message(client, userdata, msg):
    print("[LOG] message from topic " + str(msg.topic)
          + ": " + str(msg.payload))
    if (ledstrip_type == "rgb"):
        if   (msg.topic == topic_color0):
            #print("[DEBUG] setting new color0 to " + (msg.payload).decode('utf-8'))
            color0[0] = (msg.payload).decode('utf-8')
        if (msg.topic == topic_color1):
            #print("[DEBUG] setting new color1 to " + (msg.payload).decode('utf-8'))
            color1[0] = (msg.payload).decode('utf-8')
    elif (ledstrip_type == "monochrome"):
        if (msg.topic == topic_intensity):
            #print("[DEBUG] setting new intensity to " + (msg.payload).decode('utf-8'))
            intensity[0] = int((msg.payload).decode('utf-8'))
    if (msg.topic == topic_fadeSetting):
        #print("[DEBUG] setting new fadeSetting to " + (msg.payload).decode('utf-8'))
        fadeSetting[0] = (msg.payload).decode('utf-8')
    if (msg.topic == topic_state):
        #print("[DEBUG] setting new fadeSetting to " + (msg.payload).decode('utf-8'))
        state[0] = (msg.payload).decode('utf-8')
    if (msg.topic == topic_speed):
        #print("[DEBUG] setting new speed to " + (msg.payload).decode('utf-8'))
        try:
            speed[0] = int((msg.payload).decode('utf-8'))
        except ValueError:
            print("[ERROR] speed cannot be converted to integer - set to 30fps")
            speed[0] = 30
    return 0


# ---SET UP THE CLIENT---

# RPI setup
## Open up the RPI GPIO ports for writing, default to OFF (0,0,0)
pi = PWM.Servo()
#set_pwm(0,0,0) 


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

currentColor = [color0[0]]
prevColor0 = [color0[0]]
prevColor1 = [color1[0]]
prevIntensity = [0]

fadeColors = []
fadeCount = [0]
subdivisions = 400

def animation_handler():
    while (shouldRun == True):
        if (state[0] in ["off", "OFF", "Off", "0"]):
            if (ledstrip_type == "rgb"):
                colorToSet = determine_pwm("#000000")
                set_pwm(*colorToSet)
            elif (ledstrip_type == "monochrome"):
                colorToSet = determine_monochrome_pwm(0)
                set_pwm(*colorToSet)
            sleep(0.25)

        elif (state[0] in ["on", "ON", "On", "1"]):
            # update fade delay in case new speed was set
            fadeDelay = 1.0/(1 + speed[0])

            # no fade - just use solid color 
            if (fadeSetting[0] == "solid"):
                if (ledstrip_type == "rgb"):
                    # set new PWM if there is a new color0; otherwise do nothing
                    if (color0[0] != prevColor0[0]):
                        colorToSet = determine_pwm(color0[0])
                        currentColor[0] = color0[0] 
                        prevColor0[0] = color0[0]
                        set_pwm(*colorToSet)
                        #print("[DEBUG] new pwm: " + str(colorToSet))
                elif (ledstrip_type == "monochrome"):
                    if (intensity[0] != prevIntensity[0]):
                        colorToSet[0] = determine_monochrome_pwm(intensity[0])
                        prevIntensity[0] = intensity[0] 
                        set_pwm(*colorToSet)
                sleep(0.25)
            
            # normal fade from color0 --> color1
            elif (fadeSetting[0] == "fade"):
                if (ledstrip_type == "rgb"):
                    # reset the fade if it is 1) just starting, 
                    # or 2) has a new start/end color, otherwise proceed to next color
                    if ((fadeCount[0] == 0) 
                     or (color0[0] != prevColor0[0]) 
                     or (color1[0] != prevColor1[0])):
                        fadeColors = fade(color0[0], color1[0], subdivisions=subdivisions)
                        prevColor0[0] = color0[0]
                        prevColor1[0] = color1[0]
                        fadeCount[0]  = 0
                    colorToSet = determine_pwm(fadeColors[fadeCount[0]%len(fadeColors)])
                    set_pwm(*colorToSet)
                    #print("[DEBUG] new pwm: " + str(colorToSet))
                    fadeCount[0] = (fadeCount[0] + 1)
                elif (ledstrip_type == "monochrome"):
                    if ((fadeCount[0] == 0) 
                    or (intensity[0] != prevIntensity)):
                        fadeColors = fade_monochrome(intensity[0], int(float(intensity[0]) / 3), subdivisions=subdivisions)
                        prevIntensity[0] = intensity[0]
                        fadeCount[0]  = 0
                        colorToSet = determine_monochrome_pwm(fadeColors[fadeCount[0]%len(fadeColors)])
                        set_pwm(*colorToSet)
                        #print("[DEBUG] new pwm: " + str(colorToSet))
                        fadeCount[0] = (fadeCount[0] + 1)
                sleep(fadeDelay)
            
            # strobe light between color0 and black
            elif (fadeSetting[0] == "strobe"):
                if (ledstrip_type == "rgb"):
                    if (fadeCount[0] == 0):
                        colorToSet = determine_pwm(color0[0])
                    elif (fadeCount == 1):
                        colorToSet = determine_pwm("#000000")
                    set_pwm(*colorToSet)
                    fadeCount[0] = (fadeCount[0] + 1) % 2
                elif (ledstrip_type == "monochrome"):
                    if (fadeCount[0] == 0):
                        colorToSet = determine_monochrome_pwm(intensity[0])
                    elif (fadeCount[0] == 1):
                        colorToSet = determine_monochrome_pwm(0)
                    set_pwm(*colorToSet)
                    fadeCount[0] = (fadeCount[0] + 1) % 2
                sleep(fadeDelay)

animation_thread = threading.Thread(target=animation_handler)
animation_thread.start()

# --- END THE CLIENT ---
# TODO: exit gracefully
exit()
