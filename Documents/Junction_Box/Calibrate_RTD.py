from gpiozero import *
from time import sleep
import datetime
from smbus2 import SMBus, i2c_msg
import spidev
import time
import ADS1248
import MuxCtrl
    
def spi_init():
    spi = spidev.SpiDev()
    spi.open(0,0) # Bus: 0, CS: 0
    spi.max_speed_hz = 195300
    spi.bits_per_word = 8 # 8 bits per byte-word
    return spi

ads1248_spi = spi_init()
ADS1248.ads1248_init(ads1248_spi)
if ADS1248.configure(ads1248_spi) == True:
    print("ADS1248 Configuration Successful")
else:
    print("!! ADS1248 Configuration Unsuccessful !!")
ADS1248.ads1248_wakeup(ads1248_spi)
MuxCtrl.initMux()
MuxCtrl.sensorTypeEn('RTD')
if(MuxCtrl.EnableSingleProbe(1) != 0):
    print()
    print('! Mux Enable Error !')
time.sleep(1)
ADS1248.ads1248_read_single(ads1248_spi) #initiate read command
print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), end=',  ') #timestamp
output = ADS1248.ads1248_read_single_read(ads1248_spi)
print(output, end = '°C\n') #data

MuxCtrl.initMux()
ADS1248.ads1248_sleep(ads1248_spi)

calibration_factor = 100/output[0]
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
with open('calibration.txt', 'w') as f:
    f.write("Calibration Factor: " + str(calibration_factor))

try: 
    with open('calibration.txt') as f:
        calibration = f.readlines(1)
except:
    print('Configuration File Not Found')
    
cal_factor = float(calibration[0][20:len(calibration[0])])
if(cal_factor == calibration_factor):
    print("Calibration Stored")
else:
    print("! ERROR !")
    
ADS1248.ads1248_wakeup(ads1248_spi)
MuxCtrl.initMux()
MuxCtrl.sensorTypeEn('RTD')
if(MuxCtrl.EnableSingleProbe(1) != 0):
    print()
    print('! Mux Enable Error !')
time.sleep(1)
ADS1248.ads1248_read_single(ads1248_spi) #initiate read command
print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), end=',  ') #timestamp
output = ADS1248.ads1248_read_single_read(ads1248_spi)
print(output, end = '°C\n') #data
print("Calibration Complete")
