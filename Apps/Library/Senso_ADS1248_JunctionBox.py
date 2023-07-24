#!/usr/bin/env python

from gpiozero import *
import spidev
import time
from math import *
from Senso_MUX_JunctionBox import *
from Senso_LED_JunctionBox import *

class ADS_JunctionBox:
    SPI_SPEED_HZ = 1000000
    DELAY_1_MS = 1000

    COMMAND_WAKEUP   =    0x00 #  Exit power-down mode
    COMMAND_SLEEP    =    0x02 #  Enter power-down mode
    COMMAND_SYNC     =    0x04 #  Synchronize ADC conversions (sent twice)
    COMMAND_RESET    =    0x06 #  Reset to default values
    COMMAND_NOP      =    0xFF #  No operation
    COMMAND_RDATA    =    0x12 #  Read data once
    COMMAND_RDATAC   =    0x14 #  Read data continuous mode
    COMMAND_SDATAC   =    0x16 #  Stop read data continuous mode
    COMMAND_SYSOCAL  =    0x60 #  System offset calibration
    COMMAND_SYSGCAL  =    0x61 #  System gain calibration
    COMMAND_SELFOCAL =    0x62 #  Self offset calibration

    # these are followed by (number of regs to r/w - 1)
    COMMAND_RREG     =   0x20 #  Read from register [lower nibble]
    COMMAND_WREG     =   0x40 #  Write to register [lower nibble]
    #---------------------------------------------------------------------------#
    REGISTER_MUX0    =   0x00 #  BCS[1:0] MUX_SP[2:0] MUX_SN[2:0]
    REGISTER_VBIAS   =   0x01 # VBIAS[7:0]
    REGISTER_MUX1    =   0x02 # CLKSTAT VREFCON[1:0] REFSELT[1:0] MUXCAL[2:0]
    REGISTER_SYS0    =   0x03 # 0 PGA[2:0] DR[3:0]
    REGISTER_OFC0    =   0x04 # OFC[7:0]
    REGISTER_OFC1    =   0x05 # OFC[15:8]
    REGISTER_OFC2    =   0x06 # OFC[23:16]
    REGISTER_FSC0    =   0x07 # FSC[7:0]
    REGISTER_FSC1    =   0x08 # FSC[15:8]
    REGISTER_FSC2    =   0x09 # FSC[23:16]
    REGISTER_IDAC0   =   0x0A # ID[3:0] DRDY MODE IMAG[2:0]
    REGISTER_IDAC1   =   0x0B # I1DIR[3:0] I2DIR[3:0]
    REGISTER_GPIOCFG =   0x0C # IOCFG[7:0]
    REGISTER_GPIODIR =   0x0D # IODIR[7:0]
    REGISTER_GPIODAT =   0x0E # IODAT[7:0]
    #---------------------------------------------------------------------------*/
    # Burnout Settings
    SETTING_MUX0_BURNOUT_OFF   =  (0 << 6) # 00: off
    SETTING_MUX0_BURNOUT_0_5   =  (1 << 6) # 01: 0.5uA
    SETTING_MUX0_BURNOUT_2_0   =  (2 << 6) # 10: 2uA
    SETTING_MUX0_BURNOUT_10    =  (3 << 6) # 11: 10uA

    # positive input
    SETTING_MUX0_MUXSP_AIN0    =  (0 << 3) # default
    SETTING_MUX0_MUXSP_AIN1    =  (1 << 3)
    SETTING_MUX0_MUXSP_AIN2    =  (2 << 3)
    SETTING_MUX0_MUXSP_AIN3    =  (3 << 3)
    SETTING_MUX0_MUXSP_AIN4    =  (4 << 3)
    SETTING_MUX0_MUXSP_AIN5    =  (5 << 3)
    SETTING_MUX0_MUXSP_AIN6    =  (6 << 3)
    SETTING_MUX0_MUXSP_AIN7    =  (7 << 3)

    # negative input
    SETTING_MUX0_MUXSN_AIN0    =  (0 << 0)
    SETTING_MUX0_MUXSN_AIN1    =  (1 << 0) # default
    SETTING_MUX0_MUXSN_AIN2    =  (2 << 0)
    SETTING_MUX0_MUXSN_AIN3    =  (3 << 0)
    SETTING_MUX0_MUXSN_AIN4    =  (4 << 0)
    SETTING_MUX0_MUXSN_AIN5    =  (5 << 0)
    SETTING_MUX0_MUXSN_AIN6    =  (6 << 0)
    SETTING_MUX0_MUXSN_AIN7    =  (7 << 0)

    SETTING_VBIAS_DISABLE      =  (0 << 0)
    SETTING_VBIAS_0_ENABLE     =  (1 << 0)
    SETTING_VBIAS_1_ENABLE     =  (1 << 1)
    SETTING_VBIAS_2_ENABLE     =  (1 << 2)
    SETTING_VBIAS_3_ENABLE     =  (1 << 3)

    SETTING_MUX1_CLKSTAT_INT   =  (0 << 7)
    SETTING_MUX1_CLKSTAT_EXT   =  (1 << 7)
    SETTING_MUX1_VREFCON_INT_ALW_OFF  =  (0 << 5)
    SETTING_MUX1_VREFCON_INT_ALW_ON   =  (1 << 5)
    SETTING_MUX1_VREFCON_INT_SAMPLING =  (2 << 5)
    SETTING_MUX1_REFSELT_REF0  =  (0 << 3)
    SETTING_MUX1_REFSELT_REF1  =  (1 << 3)
    SETTING_MUX1_REFSELT_INT   =  (2 << 3)
    SETTING_MUX1_REFSELT_INT_REF0 = (3 << 3)

    SETTING_MUX1_MUXCAL_NORMAL = (0 << 0)

    SETTING_SYS0_PGA_GAIN_1    =  (0 << 4) # default
    SETTING_SYS0_PGA_GAIN_2    =  (1 << 4)
    SETTING_SYS0_PGA_GAIN_4    =  (2 << 4)
    SETTING_SYS0_PGA_GAIN_8    =  (3 << 4)
    SETTING_SYS0_PGA_GAIN_16   =  (4 << 4)
    SETTING_SYS0_PGA_GAIN_32   =  (5 << 4)
    SETTING_SYS0_PGA_GAIN_64   =  (6 << 4)
    SETTING_SYS0_PGA_GAIN_128  =  (7 << 4)

    SETTING_SYS0_ODR_5         =  (0 << 0)
    SETTING_SYS0_ODR_10        =  (1 << 0)
    SETTING_SYS0_ODR_20        =  (2 << 0)
    SETTING_SYS0_ODR_40        =  (3 << 0)
    SETTING_SYS0_ODR_80        =  (4 << 0)
    SETTING_SYS0_ODR_160       =  (5 << 0)
    SETTING_SYS0_ODR_320       =  (6 << 0)
    SETTING_SYS0_ODR_640       =  (7 << 0)
    SETTING_SYS0_ODR_1K        =  (8 << 0)
    SETTING_SYS0_ODR_2K        =  (9 << 0)

    SETTING_IDAC0_DRDY_SPI     =  (0 << 3)
    SETTING_IDAC0_DRDY_DUAL    =  (1 << 3)

    SETTING_IDAC0_IMAG_OFF     =  (0 << 0)
    SETTING_IDAC0_IMAG_50_UA   =  (1 << 0)
    SETTING_IDAC0_IMAG_100_UA  =  (2 << 0)
    SETTING_IDAC0_IMAG_250_UA  =  (3 << 0)
    SETTING_IDAC0_IMAG_500_UA  =  (4 << 0)
    SETTING_IDAC0_IMAG_750_UA  =  (5 << 0)
    SETTING_IDAC0_IMAG_1000_UA =  (6 << 0)
    SETTING_IDAC0_IMAG_1500_UA =  (7 << 0)

    SETTING_IDAC1_I1_AIN2      =  (2 << 4)
    SETTING_IDAC1_I1_AIN6      =  (6 << 4)
    SETTING_IDAC1_I1_IEXC0     =  (8 << 4)
    SETTING_IDAC1_I1_IEXC1     =  (9 << 4)
    SETTING_IDAC1_I1_DISCONN   =  (12 << 4)
    SETTING_IDAC1_I2_IEXC0     =  (8 << 0)
    SETTING_IDAC1_I2_IEXC1     =  (9 << 0)
    SETTING_IDAC1_I2_DISCONN   =  (12 << 0)

    # enable GPIOx to their respective use, see 9.6.4.9 #
    SETTING_GPIOCFG_GPIO0_EN   =  (1 << 0)
    SETTING_GPIOCFG_GPIO1_EN   =  (1 << 1)
    SETTING_GPIOCFG_GPIO2_EN   =  (1 << 2)
    SETTING_GPIOCFG_GPIO3_EN   =  (1 << 3)
    SETTING_GPIOCFG_GPIO4_EN   =  (1 << 4)
    SETTING_GPIOCFG_GPIO5_EN   =  (1 << 5)
    SETTING_GPIOCFG_GPIO6_EN   =  (1 << 6)
    SETTING_GPIOCFG_GPIO7_EN   =  (1 << 7)

    # Input Settings
    M8_1_MUX0_SETTINGS      =    (SETTING_MUX0_BURNOUT_OFF) | (SETTING_MUX0_MUXSP_AIN0) | (SETTING_MUX0_MUXSN_AIN1)
    M8_1_VBIAS_SETTINGS     =    (SETTING_VBIAS_DISABLE)
    M8_1_MUX1_SETTINGS      =    (SETTING_MUX1_CLKSTAT_INT) | (SETTING_MUX1_VREFCON_INT_ALW_ON) |  (SETTING_MUX1_REFSELT_REF0) | (SETTING_MUX1_MUXCAL_NORMAL)
    M8_1_SYS0_SETTINGS      =    (SETTING_SYS0_PGA_GAIN_1) | (SETTING_SYS0_ODR_5)
    M8_1_IDAC0_SETTINGS     =    (SETTING_IDAC0_DRDY_SPI) | (SETTING_IDAC0_IMAG_1000_UA)
    M8_1_IDAC1_SETTINGS     =    (SETTING_IDAC1_I1_AIN2) | (SETTING_IDAC1_I2_DISCONN)

    M8_2_MUX0_SETTINGS      =    (SETTING_MUX0_BURNOUT_OFF) | (SETTING_MUX0_MUXSP_AIN4) |  (SETTING_MUX0_MUXSN_AIN5)
    M8_2_VBIAS_SETTINGS     =    (SETTING_VBIAS_DISABLE)
    M8_2_MUX1_SETTINGS      =    (SETTING_MUX1_CLKSTAT_INT) | (SETTING_MUX1_VREFCON_INT_ALW_ON) |  (SETTING_MUX1_REFSELT_REF1) | (SETTING_MUX1_MUXCAL_NORMAL)
    M8_2_SYS0_SETTINGS      =    (SETTING_SYS0_PGA_GAIN_1) | (SETTING_SYS0_ODR_5)
    M8_2_IDAC0_SETTINGS     =    (SETTING_IDAC0_DRDY_SPI) | (SETTING_IDAC0_IMAG_1000_UA)
    M8_2_IDAC1_SETTINGS     =    (SETTING_IDAC1_I1_AIN6) | (SETTING_IDAC1_I2_DISCONN)

#---------------------------------------------------------------------------#
# Initialization
    def __init__(self, spi = None):
        self.timer = 0
        self.rtd_scaler_constant = float(1.0)
        self.drdy = InputDevice(pin = 6, active_state = False) #Pin 6, No Pull, Active State LOW
        self.reset = OutputDevice(pin = 8, active_high = False, initial_value = True) #Pin 8, On is LOW, Initial Value is HIGH
        if spi is None:
            self.spi = self._spi_init()
        else:
            self.spi = spi
        self._wakeup()
        self._ads_init()
        self._configure()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._sleep()

    def _spi_init(self):
        """
            Initializes the SPI object
        """
        spi = spidev.SpiDev()
        spi.open(0,0) # Bus: 0, CS: 0
        spi.max_speed_hz = 195300
        spi.bits_per_word = 8 # 8 bits per byte-word
        return spi

    def _ads_init(self):
        """
            Sets the SPI mode for compatibility with the
            ADS1248 and sets the calibration constant
        """
        self.spi.mode = 0b01 # [CPOL|CPHA]  SPI_CPOL_0_CPHA_1 # Override default SPI mode */
        time.sleep(20/1000) #20ms wait
        self.spi.xfer([self.COMMAND_SLEEP])
        try:
            with open('calibration.txt') as f:
                calibration = f.readlines(1)
            self.rtd_scaler_constant = float(calibration[0][20:len(calibration[0])])
        except:
            print("Configuration File Not Found")
            self.rtd_scaler_constant = float(1.0)    

#---------------------------------------------------------------------------#
# Bit Functions
    def _bitRead(self, value, bit):
        """
        Reads the value of a bit
        Returns the bit value
        """
        return ( (value >> bit) & 0x01 )
    def _bitSet(self, value, bit):
        """
        Sets the value of a bit
        Returns the new value
        """
        return ( value | (1 << (bit)) )
    def _bitClear(self, value, bit):
        """
        Clears the value of a bit position
        Returns the new value
        """
        return ( value & (not (1 << (bit))) )

#---------------------------------------------------------------------------#
# Timer
    def _timer_set(self, delay_s):
        """
        Sets the timer
        """
        if delay_s <= 0:
            raise Exception(f"{__name__}: _timer_set(delay_s = {delay_s}) delay_s must be greater than zero!")
        self.timer = time.time() + delay_s

    def _timer_expired(self):
        """
        Checks if the timer is expired
        Returns True if the timer is expire, false otherwise
        """
        return (time.time() >= self.timer)

#---------------------------------------------------------------------------*/
# Data Communication
    def _send_command(self, command):
        """
        Transfers an spi command to the ADS1248
        """
        self.spi.xfer([command])
        if command == self.COMMAND_SYNC:
            # this command needs to be sent twice
            self.spi.xfer([command])

#---------------------------------------------------------------------------*/
# Data Retrieval
    def _read_conversiondata(self):
        """
        Reads the data and converts it into an integer
        Returns the 24-bit raw data
        """
        In = [0, 0, 0]
        self.spi.xfer([self.COMMAND_RDATA])
        In = self.spi.readbytes(3)
        # uint8_t -> uint32_t, MSB first
        raw = 0
        raw = raw|(In[0] << 16)
        raw = raw|(In[1] << 8)
        raw = raw|(In[2] << 0)
        return raw

    def _data_ready(self):
        """
        Checks if the drdy pin is LOW (active)
        Returns True if the pin is active, false otherwise
        """
        return self.drdy.is_active

#---------------------------------------------------------------------------*/
# Data Processing
    def _sample_convert(self, raw):
        """
        Converts 24-bit raw data to an adc value
        """
        # ads1248 is 24-bit adc across full neg--pos range */
        if(raw > 0x1000000):
            # overflow; positive saturation */
            return 8388607

        if(raw == 0x800000):
            # overflow; negative saturation */
            return -8388607
        if(raw & 0x800000):
            # signbit set, this is negative */
            adc = float(raw & 0x7fffff)
            adc = -adc
        else:
            adc = raw
        return adc

    def _rtd_to_celcius(rtd):
        """
        Converts resistance data to an RTD Temperature value in °C
        """
        if(rtd >= 100.0 and rtd < 390):
            output = (-0.0039083+sqrt(0.00001758480889-0.0000000231*rtd))/(-0.000001155)
            if output > -274 and output < 850:
                return output
            else: return -274
        elif(rtd <100):
            output = -241.9863388 + (2.218293592 * rtd) + (0.00279590 * pow(rtd, 2)) + \
                   (-0.00000921 * pow(rtd, 3)) + (0.0000000139874 * pow(rtd, 4))
            if output > -274 and output < 850:
                return output
            else: return -274
        else:
            return -274

    def _process_raw_data(self, raw) -> tuple(float, float):
        """
        Converts raw data into temperature data in °C 
        """
        adc = self._sample_convert(raw)
        uV = 0.16331672668 * float(adc)
        excur = 1000.0
        rtd_uncalibrated = uV / excur
        #print("RTD Uncalibrated:", end=' ')
        #print(rtd_uncalibrated, end=' Ohms\n')
        # Calibrated rtd */
        rtd = self.rtd_scaler_constant * rtd_uncalibrated
        #print("RTD Calibrated:", end=' ')
        #print(rtd, end=' Ohms\n')

        celsius_uncalibrated = self.rtd_to_celcius(rtd_uncalibrated)
        #print("Temp Uncalibrated:", end = ' ')
        #print(celsius_uncalibrated, end='°C\n')
    
        celsius = self._rtd_to_celcius(rtd)
        #print("Temp Calibrated:", end = ' ')
        #print(celsius, end = '°C\n')
        return rtd, celsius

#---------------------------------------------------------------------------*/
# Register Control
    def _read_reg(self, reg):
        """
        Read the value of a register
        """
        Out = [0, 0]
        Out[0] = self.COMMAND_RREG | reg;
        Out[1] = 0; # 1 byte read
        self.spi.writebytes(Out)
        In = self.spi.readbytes(1)
    #     print("Read Register:", end =' ')
    #     print(In)
        time.sleep(10/1000)
        return In[0]

    def _write_reg(self, reg, setting):
        """
        Write a setting to a register
        """
        Out = [0, 0, 0]
        Out[0] = self.COMMAND_WREG | reg
    #     print("Register Number: ", end='')
    #     print(hex(Out[0]))
        Out[1] = 0 # 1 byte to be written
        Out[2] = setting
        self.spi.writebytes(Out)
        time.sleep(10/1000)

    def _set_reg(self, reg, setting):
        """
        Writes and checks the register
        Raises an error if the register does not match the setting
        """
        self._write_reg(reg, setting)
        if not self._read_reg(reg) == setting:
            raise Exception(f"{__name__} set_reg(reg = {reg}, setting: {setting}) failed!")

#---------------------------------------------------------------------------*/
# Configuration
    def _configure(self):
        """
        Configures the ADS1248 for RTD measurement under the conditions of the Junction Box
        Raises an exception if the configuration failed
        """
        self._set_reg(self.REGISTER_MUX0, self.M8_1_MUX0_SETTINGS)
        self._set_reg(self.REGISTER_VBIAS, self.M8_1_VBIAS_SETTINGS)
        self._set_reg(self.REGISTER_MUX1, self.M8_1_MUX1_SETTINGS)
        self._set_reg(self.REGISTER_SYS0, self.M8_1_SYS0_SETTINGS)
        self._set_reg(self.REGISTER_IDAC0, self.M8_1_IDAC0_SETTINGS)
        self._set_reg(self.REGISTER_IDAC1, self.M8_1_IDAC1_SETTINGS)

#---------------------------------------------------------------------------*/
# ADS Control
    def _wakeup(self):
        """
        Request the ADS1248 to wake up
        """
        self.spi.xfer([self.COMMAND_WAKEUP])
        time.sleep(20/1000) #20ms wait
    
    # Request the ADS1248 to go to wake up
    def _sleep(self):
        """
        Request the ADS1248 to go to wake up
        """
        self.spi.xfer([self.COMMAND_SLEEP])
    
#---------------------------------------------------------------------------*/
# ADS1248 Read
    def _start_read_single(self, timeout_ms = 350):
        """
        Triggers the ADS1248 to perform a read cycle
        Sets a timer for the read
        """
        self.spi.xfer([self.COMMAND_SYNC])
        self._timer_set(timeout_ms/1000)

    def _get_read_single(self) -> tuple(float, float):
        """
        Gets a reading from the ADS1248
        If background is True, starts a thread that waits for a reading
        If background is False, waits until a reading or timeout occurs to return
        Returns resistance (ohms), temperature (°C)
        """
        while not self._data_ready() and not self._timer_expired():
            pass
        if self._data_ready():
            raw = self._read_conversiondata()
            data_vector = self._process_raw_data(raw);
            return data_vector
        elif self._timer_expired():
            raise Exception(f"{__name__}: _get_read_single() data not ready timeout!")
        else:
            raise Exception(f"{__name__}: _get_read_single() unknown error!")

    def read_single(self, timeout_ms = 350) -> tuple(float, float):
        """
        Gets a single reading from the ADS1248
        Returns resistance (ohms), temperature (°C)
        """
        self._start_read_single(timeout_ms)
        return self._get_read_single()

