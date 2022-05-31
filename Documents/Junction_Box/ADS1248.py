from gpiozero import *
import spidev
import time
from math import *

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

rtd_scaler_constant = float(1.0)
Timer = 0
drdy = InputDevice(6, None, False) #Pin 6, No Pull, Active State LOW
reset = OutputDevice(8, False, True) #Pin 8, On is LOW, Initial Value is HIGH

#---------------------------------------------------------------------------#
def bitRead(value, bit):
    return ( (value >> bit) & 0x01 )
def bitSet(value, bit):
    return ( value | (1 << (bit)) )
def bitClear(value, bit):
    return ( value & (not (1 << (bit))) )

#---------------------------------------------------------------------------#
def ads1248_get_rtd_scaler():
    global rtd_scaler_constant
    return rtd_scaler_constant

#---------------------------------------------------------------------------#
def ads1248_set_rtd_scaler(rtd_scaler):
    global rtd_scaler_constant
    rtd_scaler_constant = rtd_scaler

#---------------------------------------------------------------------------#
def timer_set(delay_s):
    Timer = time.time() + delay_s

#---------------------------------------------------------------------------#
def timer_expired():
    return (time.time() >= Timer)

#---------------------------------------------------------------------------*/
def send_command(ads1248_spi, command):
    ads1248_spi.xfer([command])
    if(command == COMMAND_SYNC):
        # this command needs to be twice */
        ads1248_spi.xfer([command])


#---------------------------------------------------------------------------*/
def read_conversiondata(ads1248_spi):
    In = [0, 0, 0]
    ads1248_spi.xfer([COMMAND_RDATA])
    In = ads1248_spi.readbytes(3)
    # uint8_t -> uint32_t, MSB first */
    ret = 0
    ret = ret|(In[0] << 16)
    ret = ret|(In[1] << 8)
    ret = ret|(In[2] << 0)

    return ret

#---------------------------------------------------------------------------*/

def sample_convert(raw):
    # ads1248 is 24-bit adc across full neg--pos range */
    if(raw > 0x1000000):
        # overflow; positive saturation */
        return 8388607

    if(raw == 0x800000):
        # overflow; negative saturation */
        return -8388607
    if(raw & 0x800000):
        # signbit set, this is negative */
        ret = float(raw & 0x7fffff)
        ret = -ret
    else:
        ret = raw
    return ret

#---------------------------------------------------------------------------*/

def rtd_to_celcius(rtd):
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

#---------------------------------------------------------------------------*/

def process_raw_data(raw):
    adc = sample_convert(raw)
    uV = 0.16331672668 * float(adc)
    excur = 1000.0
    rtd_uncalibrated = uV / excur
    #print("RTD Uncalibrated:", end=' ')
    #print(rtd_uncalibrated, end=' Ohms\n')
    # Calibrated rtd */
    rtd = ads1248_get_rtd_scaler() * rtd_uncalibrated
    #print("RTD Calibrated:", end=' ')
    #print(rtd, end=' Ohms\n')

    celsius_uncalibrated = rtd_to_celcius(rtd_uncalibrated)
    #print("Temp Uncalibrated:", end = ' ')
    #print(celsius_uncalibrated, end='°C\n')
    
    celsius = rtd_to_celcius(rtd)
    #print("Temp Calibrated:", end = ' ')
    #print(celsius, end = '°C\n')
    return [rtd, celsius]

#---------------------------------------------------------------------------*/
def data_ready():
    return drdy.is_active

#---------------------------------------------------------------------------*/
def read_reg(ads1248_spi, reg):
    Out = [0, 0]
    Out[0] = COMMAND_RREG | reg;
    Out[1] = 0; # 1 byte read
    ads1248_spi.writebytes(Out)
    In = ads1248_spi.readbytes(1)
#     print("Read Register:", end =' ')
#     print(In)
    time.sleep(10/1000)
    return In[0]

#---------------------------------------------------------------------------*/
def write_reg(ads1248_spi, reg, setting):
    Out = [0, 0, 0]
    Out[0] = COMMAND_WREG | reg
#     print("Register Number: ", end='')
#     print(hex(Out[0]))
    Out[1] = 0 # 1 byte to be written
    Out[2] = setting
    ads1248_spi.writebytes(Out)
    time.sleep(10/1000)
#---------------------------------------------------------------------------*/
# input is which RTD to read, 1 or 2 on M8#1 or M8#2 */
def configure(ads1248_spi):
    # returns 1 at success */
    write_reg(ads1248_spi, REGISTER_MUX0, M8_1_MUX0_SETTINGS)
    check = (read_reg(ads1248_spi, REGISTER_MUX0) == (M8_1_MUX0_SETTINGS))
    write_reg(ads1248_spi, REGISTER_VBIAS, M8_1_VBIAS_SETTINGS)
    check = check and \
            (read_reg(ads1248_spi, REGISTER_VBIAS) == (M8_1_VBIAS_SETTINGS))
    write_reg(ads1248_spi, REGISTER_MUX1, M8_1_MUX1_SETTINGS)
    check = check and \
            (read_reg(ads1248_spi, REGISTER_MUX1) == (M8_1_MUX1_SETTINGS))
    write_reg(ads1248_spi, REGISTER_SYS0, M8_1_SYS0_SETTINGS)
    check = check and \
            (read_reg(ads1248_spi, REGISTER_SYS0) == (M8_1_SYS0_SETTINGS))
    write_reg(ads1248_spi, REGISTER_IDAC0, M8_1_IDAC0_SETTINGS)
    check = check and \
            ((read_reg(ads1248_spi, REGISTER_IDAC0) & 0xF) == (M8_1_IDAC0_SETTINGS))
    write_reg(ads1248_spi, REGISTER_IDAC1, M8_1_IDAC1_SETTINGS)
    check = check and \
            (read_reg(ads1248_spi, REGISTER_IDAC1) == (M8_1_IDAC1_SETTINGS))
    
    return check

#---------------------------------------------------------------------------#
def ads1248_init(ads1248_spi):
    ads1248_spi.mode = 0b01 # [CPOL|CPHA]  SPI_CPOL_0_CPHA_1 # Override default SPI mode */

    time.sleep(20/1000) #20ms wait

    ads1248_spi.xfer([COMMAND_SLEEP])
    
    global rtd_scaler_constant
    try:
        with open('calibration.txt') as f:
            calibration = f.readlines(1)
        rtd_scaler_constant = float(calibration[0][20:len(calibration[0])])
    except:
        print("Configuration File Not Found")
        rtd_scaler_constant = float(1.0)
    

#---------------------------------------------------------------------------*/
# Request the ADS1248 to read data and set a timer to wait for the data to be ready
def ads1248_wakeup(ads1248_spi):
    ads1248_spi.xfer([COMMAND_WAKEUP])
    time.sleep(20/1000) #20ms wait
    
    #---------------------------------------------------------------------------*/
# Request the ADS1248 to go to wake up
def ads1248_sleep(ads1248_spi):
    ads1248_spi.xfer([COMMAND_SLEEP])
    
#---------------------------------------------------------------------------*/
# Request the ADS1248 to go to sleep
def ads1248_read_single(ads1248_spi):
    #int OFC[3];
    #int FSC[3];
    # ads1248_spi.xfer([COMMAND_WAKEUP])
    # time.sleep(1/1000) #1ms wait
    # RTIMER_BUSYWAIT(RTIMER_SECOND / 1000)

    #ads1248_spi.xfer([COMMAND_RESET])
    #time.sleep(1/1000) #1ms wait
    # RTIMER_BUSYWAIT(RTIMER_SECOND / 1000);

    # stop new data from being sampled */
    # ads1248_spi.xfer([COMMAND_SDATAC])
    
#     Offset = float(0.0)
#     OFC = [0, 0, 0]
#     OFC[0] = read_reg(ads1248_spi, REGISTER_OFC0)
#     OFC[1] = read_reg(ads1248_spi, REGISTER_OFC1)
#     OFC[2] = read_reg(ads1248_spi, REGISTER_OFC2)
#     positive = not (bitRead(OFC[0], 7)) #Two's compliment   
#     if(not positive):
#         bitClear(OFC[0], 7)
#         Offset = Offset - float(int('0x7FFFFF',10))
#     Offset = Offset + float((OFC[0] << 16) | (OFC[1] << 8) | (OFC[2]))
#     #print("Offset Factor:", end='')
#     #print(Offset)
#     Scale = float(1.0)
#     FSC = [0, 0, 0]
#     FSC[0] = read_reg(ads1248_spi, REGISTER_FSC0)
#     FSC[1] = read_reg(ads1248_spi, REGISTER_FSC1)
#     FSC[2] = read_reg(ads1248_spi, REGISTER_FSC2)
#     Scale = float(((FSC[0] << 16) | (FSC[1] << 8) | (FSC[2])) / 0x400000)
    #print("Scaling Factor:", end='')
    #print(Scale)
    global rtd_scaler_constant
    try:
        with open('calibration.txt') as f:
            calibration = f.readlines(1)
        ads1248_set_rtd_scaler(float(calibration[0][20:len(calibration[0])]))
    except:
        #print("Configuration File Not Found")
        ads1248_set_rtd_scaler(float(1.0))
    ads1248_spi.xfer([COMMAND_SYNC])
    timer_set(350/1000) #350ms timer

#---------------------------------------------------------------------------*/
# Perform an ads1248_read_single first to prepare data then use this to read the data
def ads1248_read_single_read(ads1248_spi):
    if( (not data_ready()) and (not timer_expired()) ):
        # Data not yet ready */
        print("!! Timer Expired !!")
        return -274
    
    #ads1248_spi.xfer([COMMAND_SLEEP])

    # Read and convert sample */
    raw = read_conversiondata(ads1248_spi)
    data_vector = process_raw_data(raw);
    
    #returns [resistance (ohms), temperature (°C)]
    return data_vector

