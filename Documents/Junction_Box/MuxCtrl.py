from gpiozero import *
from time import sleep
from smbus2 import SMBus, i2c_msg
import spidev
import time
import ADS1248

SUCCESS = 0
I2C_FAIL = 1 # NOT ABE TO COMPLETE I2C READ/WRITE
CHECK_FAIL = 2 # CONFIRMATION CHECK FAILED
CONFIG_FAIL = 3 # CONFIGURATION IS NOT PROPERLY SET UP TO PERFORM A MEASUREMENT

MUX1_ADDR = 0x20
MUX2_ADDR = 0x21
MUX3_ADDR = 0x22
MUX4_ADDR = 0x23

MUX_REG_OUT0 = 0x02
MUX_REG_OUT1 = 0x03
MUX_REG_CFG0 = 0x06
MUX_REG_CFG1 = 0x07
MUX_CMD_SET_OUT0_LOW = [MUX_REG_OUT0, 0]
MUX_CMD_SET_OUT1_LOW = [MUX_REG_OUT1, 0]
MUX_CMD_SET_CFG0_OUT = [MUX_REG_CFG0, 0]
MUX_CMD_SET_CFG1_OUT = [MUX_REG_CFG1, 0]

MUX_INPUT_READ = 1
MUX_B1 = 1<<1
MUX_B2 = 1<<2

SENSOR_TYPE_NONE = 0
SENSOR_TYPE_I2C = 1
SENSOR_TYPE_DTP = 2
SENSOR_TYPE_RTD = 3
SENSOR_TYPE_STATUS = SENSOR_TYPE_NONE

MUX1_CMD = 0
MUX2_CMD = 0
MUX3_CMD = 0
MUX4_CMD = 0

def orMuxCmd(COMMAND, MUX_ADDR):
    global MUX1_CMD
    global MUX2_CMD
    global MUX3_CMD
    global MUX4_CMD
    if(MUX_ADDR == MUX1_ADDR):
        MUX1_CMD = MUX1_CMD | COMMAND
        COMMAND = MUX1_CMD
    elif(MUX_ADDR == MUX2_ADDR):
        MUX2_CMD = MUX2_CMD | COMMAND
        COMMAND = MUX2_CMD
    elif(MUX_ADDR == MUX3_ADDR):
        MUX3_CMD = MUX3_CMD | COMMAND
        COMMAND = MUX3_CMD
    elif(MUX_ADDR == MUX4_ADDR):
        MUX4_CMD = MUX4_CMD | COMMAND
        COMMAND = MUX4_CMD
    return COMMAND

def andMuxCmd(COMMAND, MUX_ADDR):
    global MUX1_CMD
    global MUX2_CMD
    global MUX3_CMD
    global MUX4_CMD
    if(MUX_ADDR == MUX1_ADDR):
        MUX1_CMD = MUX1_CMD & COMMAND
        COMMAND = MUX1_CMD
    elif(MUX_ADDR == MUX2_ADDR):
        MUX2_CMD = MUX2_CMD & COMMAND
        COMMAND = MUX2_CMD
    elif(MUX_ADDR == MUX3_ADDR):
        MUX3_CMD = MUX3_CMD & COMMAND
        COMMAND = MUX3_CMD
    elif(MUX_ADDR == MUX4_ADDR):
        MUX4_CMD = MUX4_CMD & COMMAND
        COMMAND = MUX4_CMD
    return COMMAND

def i2cDetect(address=None):
    result = SUCCESS
    if address == None: 
        with SMBus(1) as bus:
            addr = 0
            deviceStats = [None] * 128
            for addr in range(8,118,1):
                try:
                    bus.write_byte_data(addr, 0, 0) #write to addr, offset 0, data to write
                    deviceStats[addr] = hex(addr) #assign addr of successful write addr
                    addr = addr + 1
                except:
                    result = I2C_FAIL
                    deviceStats[addr] = 0 #if write is unsuccessful, except is thrown and device stat for addr set to 0
                    addr = addr + 1
    else:
        deviceStats = 0
        with SMBus(1) as bus:
            addr = address
            try:
                bus.write_byte_data(addr, 0, 0) #check since addr
                deviceStats = 1
            except:
                result = I2C_FAIL
                deviceStats = 0 #return stat on single addr
    return deviceStats


#---------------------------------------------------------------------------#
# Configures the I/O expander to output
# Returns Result of Operation
def configMux(MUX_ADDR, CONFIG0, CONFIG1):
    result = SUCCESS
    with SMBus(1) as bus:
        try:
            if i2cDetect(MUX_ADDR) == 1:
                # Set configuration to Output
                msg = i2c_msg.write(MUX_ADDR, CONFIG0)
                bus.i2c_rdwr(msg)
                msg = bus.read_byte_data(MUX_ADDR, 0, MUX_REG_CFG0)
                if msg != 0:
                    result = CHECK_FAIL
                    return result
                
                msg = i2c_msg.write(MUX_ADDR, CONFIG1)
                bus.i2c_rdwr(msg)
                msg = bus.read_byte_data(MUX_ADDR, 0, MUX_REG_CFG1)
                if msg != 0:
                    result = CHECK_FAIL
                    return result
        except: result = I2C_FAIL
    return result

#---------------------------------------------------------------------------#
# Clears the I/O expander output to LOW
# Returns Result of Operation
def clearMux(MUX_ADDR):
    result = SUCCESS
    with SMBus(1) as bus:
        try:
            if(i2cDetect(MUX_ADDR) == 1):
                # Set output LOW
                msg = i2c_msg.write(MUX_ADDR, MUX_CMD_SET_OUT0_LOW)
                bus.i2c_rdwr(msg)
                msg = bus.read_byte_data(MUX_ADDR, 0, MUX_REG_OUT0)
                if msg != 0:
                    result = CHECK_FAIL
                    return result
                
                msg = i2c_msg.write(MUX_ADDR, MUX_CMD_SET_OUT1_LOW)
                bus.i2c_rdwr(msg)
                msg = bus.read_byte_data(MUX_ADDR, 0, MUX_REG_OUT1)
                if msg != 0:
                    result = CHECK_FAIL
                    return result
        except: result = I2C_FAIL
    return result

#---------------------------------------------------------------------------#
# Clears the I/O expander output to LOW and configure to output
# Returns Result of Operation
def resetMux(MUX_ADDR):
    result = SUCCESS
    if i2cDetect(MUX_ADDR) == 1:
        result = result & clearMux(MUX_ADDR) # Set all outputs to zero
        time.sleep(10/1000)
        result = result & configMux(MUX_ADDR, MUX_CMD_SET_CFG0_OUT, MUX_CMD_SET_CFG1_OUT) # Set to Output
    else:
        result = I2C_FAIL #MUX not found
    return result

#---------------------------------------------------------------------------#
# Decodes the results of the opreation and outputs in a printable string
def decodeErr(result):
    output = ["MUX1: ", "SUCCESS", "\n\r", "MUX2: ", "SUCCESS", "\n\r", \
              "MUX3: ", "SUCCESS", "\n\r", "MUX4: ", "SUCCESS"]
    if(((result >> 0) & 0x03) == I2C_FAIL): output[1] = "I2C_FAIL"
    elif(((result >> 0) & 0x03) == CHECK_FAIL): output[1] = "CHECK_FAIL"
    if(((result >> 2) & 0x03) == I2C_FAIL): output[4] = "I2C_FAIL"
    elif(((result >> 2) & 0x03) == CHECK_FAIL): output[4] = "CHECK_FAIL"
    if(((result >> 4) & 0x03) == I2C_FAIL): output[7] = "I2C_FAIL"
    elif(((result >> 4) & 0x03) == CHECK_FAIL): output[7] = "CHECK_FAIL"
    if(((result >> 6) & 0x03) == I2C_FAIL): output[10] = "I2C_FAIL"
    elif(((result >> 6) & 0x03) == CHECK_FAIL): output[10] = "CHECK_FAIL"
    return output

#---------------------------------------------------------------------------#
# Initializes the I/O Expander to be used on the MUX's
# Returns Result of Operation in a printable string
def initMux():
    global MUX1_CMD
    global MUX2_CMD
    global MUX3_CMD
    global MUX4_CMD
    result = SUCCESS
    result = result & resetMux(MUX1_ADDR)
    if(result == SUCCESS): MUX1_CMD = 0
    result = result & resetMux(MUX2_ADDR)<<2
    if(result == SUCCESS): MUX2_CMD = 0
    result = result & resetMux(MUX3_ADDR)<<4
    if(result == SUCCESS): MUX3_CMD = 0
    result = result & resetMux(MUX4_ADDR)<<6
    if(result == SUCCESS): MUX4_CMD = 0
    if(result != SUCCESS): print("! MUX Initialization Unsuccessful !")
    #result = decodeErr(result)
    return result

#---------------------------------------------------------------------------#
# Gets the MUX address from a given UNo (Mux Designator Number)
# Returns the I/O Expander Address
def getMuxFromUNo(UNo):
    if UNo <= 16: result = MUX1_ADDR
    elif UNo >= 17 and UNo <= 32: result = MUX2_ADDR
    elif UNo >= 33 and UNo <= 48: result = MUX3_ADDR
    elif (UNo >= 49 and UNo <= 56): result = MUX4_ADDR
    return result

#---------------------------------------------------------------------------#
# Gets the Port address from a given UNo (Mux Designator Number)
# Returns the I/O Expander Port Number
def getPortFromUNo(UNo):
    if UNo <= 8: Port = [0, UNo-1]
    elif UNo >= 9 and UNo <= 16: Port = [1, UNo-9]
    elif UNo >= 17 and UNo <= 24: Port = [0, UNo-17]
    elif UNo >= 25 and UNo <= 32: Port = [1, UNo-25]
    elif UNo >= 33 and UNo <= 40: Port = [0, UNo-33]
    elif UNo >= 41 and UNo <= 48: Port = [1, UNo-41]
    elif UNo >= 49 and UNo <= 56: Port = [0, UNo-49]
    else: Port = [0, 0]
    return Port

#---------------------------------------------------------------------------#
# Turns on the MUX by setting the I/O Expander Output HIGH for one specific probe
# Also, it updates the global variable command
# Returns the result of the operation
def probeEn(UNo):
    result = SUCCESS
    #print("CMD - Enable ENo: " + str(UNo))
    MUX_ADDR = getMuxFromUNo(UNo)
    PORT = getPortFromUNo(UNo)
    REGISTER = 0
    if PORT[0] == 0: REGISTER = MUX_REG_OUT0
    else: REGISTER = MUX_REG_OUT1
    COMMAND = 1<<PORT[1]
    COMMAND = orMuxCmd(COMMAND, MUX_ADDR)
    #print("Probe Enable COMMAND: " + str(COMMAND))
    with SMBus(1) as bus:
        try:
            msg = i2c_msg.write(MUX_ADDR, [REGISTER, COMMAND])
            #print("Probe Enable Command: " + str(list(msg)))
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, REGISTER)
            #print("Probe Enable Read:" + str(msg))
            if msg != COMMAND:
                result = CHECK_FAIL
                print("Probe Enable Unsuccessful")
            else: None #print("Probe Enable Successful")
        except:
            result = I2C_FAIL
            print("probeEn Error")
    return result

#---------------------------------------------------------------------------#
# Turns off the MUX by setting the I/O Expander Output LOW for one specific probe
# Also, it updates the global variable command
# Returns the result of the operation
def probeDis(UNo):
    result = SUCCESS
    #print("CMD - Disable ENo: " + UNo)
    MUX_ADDR = getMuxFromUNo(UNo)
    PORT = getPortFromUNo(UNo)
    REGISTER = 0
    if PORT[0] == 0: REGISTER = MUX_REG_OUT0
    else: REGISTER = MUX_REG_OUT1
    COMMAND = 0<<PORT[1] # Low value at the port
    COMMAND = andMuxCmd(COMMAND, MUX_ADDR)
    with SMBus(1) as bus:
        try:
            msg = i2c_msg.write(MUX_ADDR, [REGISTER, COMMAND])
            #print("Probe Disable Command: " + str(list(msg)))
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, REGISTER)
            #print("Probe Disable Read:" + str(msg))
            if msg != COMMAND:
                result = CHECK_FAIL
                print("Probe Disable Unsuccessful")
            else: None #print("Probe Disable Successful")
        except:
            result = I2C_FAIL
            print("probeDis Error")
    return result

#---------------------------------------------------------------------------#
# Enables the type of sensor processing
# Also, it updates the global variable command
# Returns the result of the operation
def sensorTypeEn(Probe):
    global SENSOR_TYPE_STATUS
    result = SUCCESS
    MUX_ADDR = MUX4_ADDR
    REGISTER = 3
    if Probe == 'I2C':
        SENSOR_TYPE_STATUS = SENSOR_TYPE_I2C
        COMMAND = 0x01
    elif Probe == 'DTP':
        SENSOR_TYPE_STATUS = SENSOR_TYPE_DTP
        COMMAND = 0x02
    elif Probe == 'RTD':
        SENSOR_TYPE_STATUS = SENSOR_TYPE_RTD
        COMMAND = 0x04
    elif Probe == 'NONE':
        SENSOR_TYPE_STATUS = SENSOR_TYPE_NONE
        COMMAND = 0x00 
    with SMBus(1) as bus:
        try:
            msg = i2c_msg.write(MUX_ADDR, [REGISTER, COMMAND])
            #print("Sensor Type Enable Command:" + str(list(msg)))
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, REGISTER)
            #print("Sensor Type Enable Read:" + str(msg))
            if msg != COMMAND:
                result = CHECK_FAIL
                print("*!* Sensor Type Enable Failed *!*")
                if msg == 0: SENSOR_TYPE_STATUS = SENSOR_TYPE_NONE
                elif msg == 1: SENSOR_TYPE_STATUS = SENSOR_TYPE_I2C
                elif msg == 2: SENSOR_TYPE_STATUS = SENSOR_TYPE_DTP
                elif msg == 4: SENSOR_TYPE_STATUS = SENSOR_TYPE_RTD
            else:
                #print("Sensor Type " + str(Probe) + " Enabled Successfully")
                if Probe == 'I2C': SENSOR_TYPE_STATUS = SENSOR_TYPE_I2C
                elif Probe == 'RTD': SENSOR_TYPE_STATUS = SENSOR_TYPE_RTD
                elif Probe == 'DTP': SENSOR_TYPE_STATUS = SENSOR_TYPE_DTP
        except:
            result = I2C_FAIL
            print("sensorTypeEn Error I2C Fail")
    return result

# Insert the probe number as seen from the top of the junction box
# and the function outputs the unique address of the chip (U#)
# Updated to V2 Board on May 27, 2022
def ProbeNoLookup(Probe_No):
    switcher = {
        1: 38,
        2: 37,
        3: 36, 
        4: 31,
        5: 30,
        6: 29,
        7: 24,
        8: 23,
        9: 22,
        10: 39,
        11: 32,
        12: 25,
        13: 42,
        14: 41,
        15: 40,
        16: 35,
        17: 34,
        18: 33,
        19: 28,
        20: 27,
        21: 26,
        22: 17,
        23: 16,
        24: 15,
        25: 10,
        26: 9,
        27: 8,
        28: 3,
        29: 2,
        30: 1,
        31: 18,
        32: 11,
        33: 4,
        34: 21,
        35: 20,
        36: 19,
        37: 14,
        38: 13,
        39: 12,
        40: 7,
        41: 6,
        42: 5
    }
    return switcher.get(Probe_No, -1)

def EnableSingleProbe(Probe_No):
    global SENSOR_TYPE_STATUS
    result = SUCCESS
    result = initMux() # Turn of all MUX's
    if(SENSOR_TYPE_STATUS == SENSOR_TYPE_I2C): result = result | sensorTypeEn('I2C')
    elif(SENSOR_TYPE_STATUS == SENSOR_TYPE_DTP): result = result | sensorTypeEn('DTP')
    elif(SENSOR_TYPE_STATUS == SENSOR_TYPE_RTD): result = result | sensorTypeEn('RTD')
    elif(SENSOR_TYPE_STATUS == SENSOR_TYPE_NONE):
        result = CONFIG_FAIL
        print("Congifuration Fail")
        return result
    UNo = ProbeNoLookup(Probe_No)
    result = result | probeEn(UNo)
    return result
    