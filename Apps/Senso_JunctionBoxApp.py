#!/usr/bin/env python

import requests
import time
import datetime
import spidev
from gpiozero import *
from time import sleep
from smbus2 import SMBus, i2c_msg
try:
    from Library.Senso_CloudAPI_JunctionBox import *
    from Library.Senso_ADS1248_JunctionBox import *
    from Library.Senso_MUX_JunctionBox import *
    from Library.Senso_LED_JunctionBox import *
    from Library.Senso_LMT01_JunctionBox import *
except:
    from Senso_CloudAPI_JunctionBox import *
    from Senso_ADS1248_JunctionBox import *
    from Senso_MUX_JunctionBox import *
    from Senso_LED_JunctionBox import *
    from Senso_LMT01_JunctionBox import *

def logTimeToExecute(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(f"{__name__}: {func.__name__}({args}, {kwargs}) delta time = {end - start} seconds")
    return wrapper

class JunctionBox:
    BeatRate = 1 # in minutes

    def __init__(self):
        self.LED = LED_JunctionBox()
        self.API = CloudAPI_JunctionBox()
        self.MUX = MUX_JunctionBox()
        self.ADS = ADS_JunctionBox()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.LED.critical()
            end_time = time.time() + 20
            while not LED.isComplete() or timeout:
                timeout = end_time < time.time()
            if timeout:
                print("LED.isComplete() timeout")
        self.close()

    def close(self):
        self.LED.close()
        self.API.close()

    def testInternet(self):
        self.API.testInternet()

    def success(self):
        self.LED.success()

    def warning(self):
        self.LED.warning()

    def critical(self):
        self.LED.critical()

    def calibrate_100ohm(self):
        if self._config == "RTD":
            resistance, temperature = self.read(1)
            calibration_factor = 100/resistance
            print("Marginal Calibration Factor: " + str(calibration_factor))
        try: 
            with open('calibration.txt') as f:
                calibration = f.readlines(1)
            cal_factor = float(calibration[0][20:len(calibration[0])])
        except:
            print('Configuration File Not Found')
            cal_factor = float(1.0)

        calibration_factor = cal_factor * calibration_factor
        print("Effective Calibration Factor: " + str(calibration_factor))
        if calibration_factor > float(2.0) | calibration_factor < float(0.5):
            raise Exception(f"{__name__}: calibrate_100ohm() Calibration factor {calibration_factor} invalid!")
        with open('calibration.txt', 'w') as f:
            f.write("Calibration Factor: " + str(calibration_factor))
        try: 
            with open('calibration.txt') as f:
                calibration = f.readlines(1)
        except:
            print('Configuration File Not Found')
        cal_factor = float(calibration[0][20:len(calibration[0])])
        if cal_factor == calibration_factor:
            print("Calibration Stored")
        else:
            raise Exception(f"{__name__}: calibrate_100ohm() Calibration not stored!")
        print(f"Calibration Results:")
        resistance, temperature = self.read(1)
        print(f"Resistance: {resistance}, Error: {resistance - 100}")
        print(f"Temperature: {temperature}, Error: {temperature - 0}")
        print("Calibration Complete")

    def getConfig(self):
        """
        Get the Junction Box configuration from the cloud response
        This is not currently configured in the cloud
        """
        self._config = "RTD"

    def read(self, ProbeNo) -> tuple(float, float) | None:
        if self._config == "RTD":
            self.MUX.EnableSingleProbe(ProbeNo)
            return self.ADS.read_single()
        return None

    def readAll(self):
        """
        Read all probes and output the HTTP_Data_Value
        """
        data = {}
        for i in range(1,43):
            reading = self.read(i)
            if reading != -274:
                print("Progress {:2.1%}".format((i-1) / 42), end="\r")
                now = datetime.datetime.now()
                current_datetime = now.strftime("%d/%m/%Y %H:%M:%S")
                data.append({"ProbeId":i,"Temperature":reading,"Datetime":current_datetime,"Status":self._config})
        count = len(data)
        if count > 0:
            print(f"Number of Readings: {count}")
            data = {"set":data,"Status":"Active","Mac":self.API.getMAC()}
            return data, count
        return {}, 0

    def sendAll(self, data):
        """
        Send all http data to cloud
        """
        self.API.send(data)

@logTimeToExecute
def main():
    while True:
        start = time.time()
        try:
            with JunctionBox() as JB:
                JB.testInternet()
                JB.success()
                start = time.time()
                data, count = JB.readAll()
                if count == 0:
                    print("No Data to be sent")
                else:
                    resp = JB.sendAll(data)
                    if resp["BeatRate"] is not None: 
                        JB.BeatRate = float(resp["BeatRate"]) # unit received in minutes
                JB.success()
        except Exception as e:
            print(e.__traceback__)
            print(e._cause__)
        end = time.time()
        time_left_s = JB.BeatRate*60 - (end - start)
        time.sleep(time_left_s)
               

if __name__ == "__main__":
    main()

"""
if RESP:
    if RESP.SENSOR == 'PT100':
        with PT100() as PT:
            output = PT.PT100_READ_ALL()
    elif RESP.SENSOR == 'LMT01':
        with LMT01() as DTP:
            output = DTP.LMT01_READ_ALL()
            
    elif RESP.SENSOR == 'TMP117':
        pass
        #TMP117
    elif RESP.SENSOR == 'SHT85':
        pass
        #SHT85
    else:
        pass
        #Error
"""