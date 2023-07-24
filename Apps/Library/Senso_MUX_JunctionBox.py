from gpiozero import *
from time import sleep
from smbus2 import SMBus, i2c_msg
import time

class MUX_JunctionBox:
    # Mux Addresses
    MUX1_ADDR = 0x20
    MUX2_ADDR = 0x21
    MUX3_ADDR = 0x22
    MUX4_ADDR = 0x23

    # Mux Registers
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

    # Sensor Types
    SENSOR_TYPE_NONE = 0
    SENSOR_TYPE_I2C = 1
    SENSOR_TYPE_DTP = 2
    SENSOR_TYPE_RTD = 3
    SENSOR_TYPE_STATUS = SENSOR_TYPE_NONE

    # Mux Commands
    MUX1_CMD = 0
    MUX2_CMD = 0
    MUX3_CMD = 0
    MUX4_CMD = 0

#---------------------------------------------------------------------------#
# Mux Initialization
    def __init__(self, probeType:str = "None"):
        """
        Resets the MUX and set the pobeType to be used
        probeType: "DTP", "I2C", "RTD", or "None"
        """
        self._resetMUX()
        self.sensorTypeEn(probeType)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._resetMUX()
        self._sensorTypeEn("None")

    def _resetMUX(self):
        """
        Sets the I/O Expander all to LOW output
        Raises an exception if failed
        """
        self._resetSingleMUX(self.MUX1_ADDR)
        self.MUX1_CMD = 0
        self._resetSingleMUX(self.MUX2_ADDR)
        self.MUX2_CMD = 0
        self._resetSingleMUX(self.MUX3_ADDR)
        self.MUX3_CMD = 0
        self._resetSingleMUX(self.MUX4_ADDR)
        self.MUX4_CMD = 0

    def _resetSingleMUX(self, MUX_ADDR):
        """
        Clears the I/O expander output to LOW and configure to output
        Returns Result of Operation
        Raises an exception if failed
        """
        self._i2cDetect(MUX_ADDR) # Raises exception if address is not detected
        self._clearMux(MUX_ADDR) # Set all outputs to zero
        time.sleep(10/1000)
        self._configMux(MUX_ADDR, self.MUX_CMD_SET_CFG0_OUT, self.MUX_CMD_SET_CFG1_OUT) # Set to Output

#---------------------------------------------------------------------------#
# I2C Diagnostic
    def _i2cDetect(self, address = None) -> list(str, ...):
        """
        Detect a specific address or all addresses
        Input the address to check it, otherwise all addresses will be checked
        Returns list of addresses
        Raises an exception if the selected address couldn't be found
        """
        if address is None:
            deviceStats = list(str()) * 128
            with SMBus(1) as bus:
                for addr in range(8,118):
                    try:
                        bus. write_byte_data(addr, 0, 0) #write to addr, offset 0, data to write
                        found = True
                        deviceStats[addr] = hex(addr) #assign addr of successful write addr
                    except Exception as e:
                        print(e)
                        deviceStats[addr] = str() #if write is unsuccessful, set to an empty string
        else:
            deviceStats = list(str())
            with SMBus(1) as bus:
                try:
                    bus.write_byte_data(address, 0, 0) #check since addr
                    found = True
                    deviceStats[0] = hex(address)
                except:
                    raise
        return deviceStats

#---------------------------------------------------------------------------#
# Command Construction
    def _orMuxCmd(self, COMMAND, MUX_ADDR):
        """
        Adds to the Mux Command by OR'ing
        Returns the current command which is stored
        """
        if MUX_ADDR == self.MUX1_ADDR:
            self.MUX1_CMD = self.MUX1_CMD | COMMAND
            COMMAND = self.MUX1_CMD
        elif MUX_ADDR == self.MUX2_ADDR:
            self.MUX2_CMD |= COMMAND
            COMMAND = self.MUX2_CMD
        elif MUX_ADDR == self.MUX3_ADDR:
            self.MUX3_CMD |= COMMAND
            COMMAND = self.MUX3_CMD
        elif MUX_ADDR == self.MUX4_ADDR:
            self.MUX4_CMD |= COMMAND
            COMMAND = self.MUX4_CMD
        return COMMAND

    def _andMuxCmd(self, COMMAND, MUX_ADDR):
        """
        Clears and adds to the Mux Command by ANG'ing
        Returns the current command which is stored
        """
        if MUX_ADDR == self.MUX1_ADDR:
            self.MUX1_CMD &= COMMAND
            COMMAND = self.MUX1_CMD
        elif MUX_ADDR == self.MUX2_ADDR:
            self.MUX2_CMD &= COMMAND
            COMMAND = self.MUX2_CMD
        elif MUX_ADDR == self.MUX3_ADDR:
            self.MUX3_CMD &= COMMAND
            COMMAND = self.MUX3_CMD
        elif MUX_ADDR == self.MUX4_ADDR:
            self.MUX4_CMD &= COMMAND
            COMMAND = self.MUX4_CMD
        return COMMAND

#---------------------------------------------------------------------------#
# Configuration Commands
    def _configMux(self, MUX_ADDR, CONFIG0, CONFIG1):
        """
        Configures the I/O expander to input or output
        Returns True if successful, False otherwise
        Raises an exception if failed
        """
        self._i2cDetect(MUX_ADDR)
        with SMBus(1) as bus:
            # Set configuration to Output
            msg = i2c_msg.write(MUX_ADDR, CONFIG0)
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, 0, self.MUX_REG_CFG0)
            if msg != CONFIG0:
                raise Exception(f"{__name__}: configMux(MUX_ADDR = {MUX_ADDR}) set MUX_REG_CFG0 failed!")
            msg = i2c_msg.write(MUX_ADDR, CONFIG1)
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, 0, self.MUX_REG_CFG1)
            if msg != CONFIG1:
                raise Exception(f"{__name__}: configMux(MUX_ADDR = {MUX_ADDR}) set MUX_REG_CFG1 failed!")

    def _clearMux(self, MUX_ADDR):
        """
        Clears the I/O expander output to LOW
        Returns Result of Operation
        Raises an exception if failed
        """
        self._i2cDetect(MUX_ADDR)
        with SMBus(1) as bus:
            # Set output LOW
            msg = i2c_msg.write(MUX_ADDR, self.MUX_CMD_SET_OUT0_LOW)
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, 0, self.MUX_REG_OUT0)
            if msg != 0:
                raise Exception(f"{__name__}: clearMux(MUX_ADDR = {MUX_ADDR}) set MUX_REG_OUT0 failed!")
            msg = i2c_msg.write(MUX_ADDR, self.MUX_CMD_SET_OUT1_LOW)
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, 0, self.MUX_REG_OUT1)
            if msg != 0:
                raise Exception(f"{__name__}: clearMux(MUX_ADDR = {MUX_ADDR}) set MUX_REG_OUT1 failed!")

#---------------------------------------------------------------------------#
# Lookup Functions
    def _getMuxFromUNo(self, UNo) -> int:
        """
        Gets the MUX address from a given UNo (Mux Designator Number)
        Returns the I/O Expander Address
        """
        if UNo <= 16: result = self.MUX1_ADDR
        elif UNo >= 17 and UNo <= 32: result = self.MUX2_ADDR
        elif UNo >= 33 and UNo <= 48: result = self.MUX3_ADDR
        elif UNo >= 49 and UNo <= 56: result = self.MUX4_ADDR
        return result

    def _getPortFromUNo(self, UNo) -> list(int, int):
        """
        Gets the Port address from a given UNo (Mux Designator Number)
        Returns the I/O Expander Port Number
        """
        if UNo <= 8: Port = [0, UNo-1]
        elif UNo >= 9 and UNo <= 16: Port = [1, UNo-9]
        elif UNo >= 17 and UNo <= 24: Port = [0, UNo-17]
        elif UNo >= 25 and UNo <= 32: Port = [1, UNo-25]
        elif UNo >= 33 and UNo <= 40: Port = [0, UNo-33]
        elif UNo >= 41 and UNo <= 48: Port = [1, UNo-41]
        elif UNo >= 49 and UNo <= 56: Port = [0, UNo-49]
        else: Port = [0, 0]
        return Port

    def _probeNoLookup(self, Probe_No):
        """
        Insert the probe number as seen from the top of the junction box
        and the function outputs the unique address of the chip (U#)
        Updated to V2 Board on May 27, 2022
        """
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

#---------------------------------------------------------------------------#
# Internal Probe Control
    def _probeEn(self, UNo):
        """
        Turns on the MUX by setting the I/O Expander Output HIGH for one specific probe
        Also, it updates the global variable command
        Returns the result of the operation
        Raises an exception if failed
        """
        self._i2cDetect(MUX_ADDR)
        #print("CMD - Enable ENo: " + str(UNo))
        MUX_ADDR = self._getMuxFromUNo(UNo)
        PORT = self._getPortFromUNo(UNo)
        REGISTER = 0
        if PORT[0] == 0: REGISTER = self.MUX_REG_OUT0
        else: REGISTER = self.MUX_REG_OUT1
        COMMAND = 1<<PORT[1]
        COMMAND = self._orMuxCmd(COMMAND, MUX_ADDR)
        #print("Probe Enable COMMAND: " + str(COMMAND))
        with SMBus(1) as bus:
            msg = i2c_msg.write(MUX_ADDR, [REGISTER, COMMAND])
            #print("Probe Enable Command: " + str(list(msg)))
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, REGISTER)
            #print("Probe Enable Read:" + str(msg))
            if msg != COMMAND:
                raise Exception(f"{__name__}: probeEn(UNo = {UNo}) failed!")
            else: None #print("Probe Enable Successful")

    def _probeDis(self, UNo):
        """
        Turns off the MUX by setting the I/O Expander Output LOW for one specific probe
        Also, it updates the global variable command
        Returns the result of the operation
        Raises an exception if failed
        """
        self._i2cDetect(MUX_ADDR)
        #print("CMD - Disable ENo: " + UNo)
        MUX_ADDR = self._getMuxFromUNo(UNo)
        PORT = self._getPortFromUNo(UNo)
        REGISTER = 0
        if PORT[0] == 0: REGISTER = self.MUX_REG_OUT0
        else: REGISTER = self.MUX_REG_OUT1
        COMMAND = 0<<PORT[1] # Low value at the port
        COMMAND = self._andMuxCmd(COMMAND, MUX_ADDR)
        with SMBus(1) as bus:
            msg = i2c_msg.write(MUX_ADDR, [REGISTER, COMMAND])
            #print("Probe Disable Command: " + str(list(msg)))
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, REGISTER)
            #print("Probe Disable Read:" + str(msg))
            if msg != COMMAND:
                raise Exception(f"{__name__}: probeDis(UNo = {UNo}) failed!")
            else: None #print("Probe Disable Successful")

#---------------------------------------------------------------------------#
# User Probe Control
    def sensorTypeEn(self, Probe:str):
        """
        Enables the type of sensor processing
        Also, it updates the global variable command
        Returns the result of the operation
        Raises an exception if failed
        """
        self._i2cDetect(MUX_ADDR)
        MUX_ADDR = self.MUX4_ADDR
        REGISTER = 3
        if Probe.upper() == 'I2C':
            COMMAND = self.SENSOR_TYPE_I2C # 0x01
        elif Probe.upper() == 'DTP':
            COMMAND = self.SENSOR_TYPE_DTP # 0x02
        elif Probe.upper() == 'RTD':
            COMMAND = self.SENSOR_TYPE_RTD # 0x04
        elif Probe.upper() == 'NONE':
            COMMAND = self.SENSOR_TYPE_NONE # 0x00 
        else:
            raise Exception(f"{__name__}: sensorTypeEn(UNo = {Probe}), {Probe} is not a valid configuration!")
        with SMBus(1) as bus:
            msg = i2c_msg.write(MUX_ADDR, [REGISTER, COMMAND])
            #print("Sensor Type Enable Command:" + str(list(msg)))
            bus.i2c_rdwr(msg)
            msg = bus.read_byte_data(MUX_ADDR, REGISTER)
            #print("Sensor Type Enable Read:" + str(msg))
            if msg != COMMAND:
                if msg == 0: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_NONE
                elif msg == 1: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_I2C
                elif msg == 2: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_DTP
                elif msg == 4: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_RTD
                print(f"{__name__}: sensorTypeEn(UNo = {Probe}), failed!")
                print(f"    COMMAND = {COMMAND}")
                print(f"    SENSOR_TYPE_STATUS = {self.SENSOR_TYPE_STATUS}")
            else:
                #print("Sensor Type " + str(Probe) + " Enabled Successfully")
                if msg == 0: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_NONE
                elif msg == 1: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_I2C
                elif msg == 2: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_DTP
                elif msg == 4: self.SENSOR_TYPE_STATUS = self.SENSOR_TYPE_RTD

    def EnableSingleProbe(self, probeNo):
        """
        Enable a single probe on the Junction Box
        The probeNo correlates to the symbol printed
        on the top of the box
        Raises an exception if failed
        """
        self._resetMUX()
        UNo = self._probeNoLookup(probeNo)
        self._probeEn(UNo)