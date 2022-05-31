#!/usr/bin/env python

import requests
import HTTP_POST
import time
from datetime import datetime
from gpiozero import *
from time import sleep
from smbus2 import SMBus, i2c_msg
import spidev
import time
import ADS1248
import MuxCtrl
import LED_UI

mac_address = HTTP_POST.getMAC('wlan0');
http_post_info = []
http_link = "http://cprod.sensoiot.com/api/DataLog"


def spi_init():
    spi = spidev.SpiDev()
    spi.open(0,0) # Bus: 0, CS: 0
    spi.max_speed_hz = 195300
    spi.bits_per_word = 8 # 8 bits per byte-word
    return spi

def init():
    ads1248_spi = spi_init()
    ADS1248.ads1248_init(ads1248_spi)
    if ADS1248.configure(ads1248_spi) == False:
        print("!! ADS1248 Configuration Unsuccessful !!")
        LED_UI.LED_RED_blink(2) # Blinks Red LED twice
    if MuxCtrl.initMux() != 0:
        LED_UI.LED_RED_blink(2) # Blinks Red LED twice
    if MuxCtrl.sensorTypeEn('RTD') != 0:
        LED_UI.LED_RED_blink(2) # Blinks Red LED twice
    return ads1248_spi

def wakeup(ads1248_spi):
    ADS1248.ads1248_wakeup(ads1248_spi)

def read(ads1248_spi, pin):
    if(MuxCtrl.EnableSingleProbe(i) != 0):
        print()
        print('! Mux Enable Error !')
        LED_UI.LED_RED_blink(2) # Blinks Red LED twice
        return -274
    time.sleep(1)
    ADS1248.ads1248_read_single(ads1248_spi)
    return ADS1248.ads1248_read_single_read(ads1248_spi)[1]

def sleep(ads1248_spi):
    ADS1248.ads1248_sleep(ads1248_spi)

LED_UI.LED_init()

while True:
    try:
        LED_UI.LED_GREEN_pulse() # Pulse Green forever when taking readings
        http_post_info = []
        now = datetime.now() 
        current_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
        print("Start Read: " + current_datetime)
        ads1248_spi = init()
        wakeup(ads1248_spi)
        start = time.time()
        for i in range(1,43):
            print("Progress {:2.1%}".format((i-1) / 42), end="\r")
            now = datetime.now()
            current_datetime = now.strftime("%m/%d/%Y %H:%M:%S")                # Get and Format Day
            reading = read(ads1248_spi, i)
            if reading != -274:
                http_post_info.append({"nodeid":i,"Tempurature":reading,"Datetime":current_datetime, "Status":"(Testing)"})  # Add to list of info
        print("Progress {:2.1%}".format(1), end="\n")
        http_post_info = {"set":http_post_info,"Status":"(Testing)","Mac":mac_address.replace(":", "")}
        http_post_info = str(http_post_info).replace("\'", "\"")
        print("Length of Post: " + str(len(http_post_info)))
        if len(http_post_info) > 57:
            print(HTTP_POST.send(http_link,http_post_info))
        end = time.time()
        print("Program took " + str(end - start) + " seconds to run.")
    except:
        LED_UI.LED_RED_pulse(0) # Turn off green pulses
        LED_UI.LED_RED_blink(2) # Error blink twice red
        print("Failure... Try again")
        time.sleep(1)
