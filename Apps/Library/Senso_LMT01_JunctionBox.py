import gpiozero
import time
import statistics
from threading import Thread, Semaphore
from Senso_MUX_JunctionBox import *
from Senso_LED_JunctionBox import *



class LMT01_OBJ:
    def __init__(self, PC_GPIO, GATE_GPIO):
        self.PC = gpiozero.DigitalInputDevice(PC_GPIO)       # Pulse Count Output Pin
        self.GATE = gpiozero.DigitalOutputDevice(GATE_GPIO)  # Control gate to counter
        self.IDLE = False                    # Idle is true if sensor is not pulsing for timeout period
        self.CHECK_IDLE = False              # Check if the idle is true continuously
        self.COUNT = 0                       # Pulse count
        self.TEMP = -50                      # Temperature in celsius
        self.THREAD = None
        self.SEM_CHECK_IDLE = Semaphore(0)
        self.SEM_UPON_IDLE = Semaphore(0)
        
class LMT01:
    def __init__(self, LED_UI: Jnx_Box_LED_UI, timeout = 0.04, PC1_GPIO = 17, GATE1_GPIO = 23,
                 PC2_GPIO = 27, GATE2_GPIO = 24, RESET_GPIO = 18):
        self.TIMEOUT = timeout
        self.PC1 = LMT01_OBJ(PC1_GPIO, GATE1_GPIO)
        self.PC2 = LMT01_OBJ(PC2_GPIO, GATE2_GPIO)
        self.RESET = gpiozero.DigitalOutputDevice(RESET_GPIO) # Resets the counter upon On() / Off() cycle

    def __enter__(self):
        self.LMT01_GATE(self.PC1, False)
        self.LMT01_GATE(self.PC2, False)
        self.LMT01_RESET_COUNT()
        if not self.LMT01_INIT_MUX():
            return False
        if not self.LMT01_THREAD_INIT(self.PC1):
            return False
        if not self.LMT01_THREAD_INIT(self.PC1):
            return False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.LMT01_PWR(self.PC1, True)
        self.LMT01_PWR(self.PC2, True)
        self.LMT01_RESET_COUNT()
    
    def LMT01_READ_ALL(self, NUM = 43) -> list(float):
        output = list()
        for n in range(1, NUM):
            output.append(self.LMT01_READ(n))
        return output
        
    # Read Sensor Value
    # Returns array of temperatures PC1 and PC2
    # Value is None if no data is read
    def LMT01_READ(self, probeNo):        
        self.LMT01_RESET_COUNTER()
        if not self.LMT01_PROBE_ENABLE(probeNo):
            return 0
        
        self.LMT01_START_CHECK_IDLE(self.PC1) # Start check idle thread       
        self.LMT01_WAIT_FOR_IDLE(self.PC1)    # Wait for Idle
        self.LMT01_GATE(self.PC1, True)       # Enable buffer gate, pulses reach counter
        self.PC1.wait_for_active(timeout=0.1)
        self.PC1.IDLE = False
        self.LMT01_WAIT_FOR_IDLE(self.PC1)    # Wait for Idle
        self.LMT01_GATE(self.PC1, False)      # Disable buffer gate, pulses reach counter
        self.PC1.COUNT = self.LMT01_READ_COUNTER()
        self.LMT01_RESET_COUNTER()
        self.PC1.IDLE = False
        
        self.PC2.IDLE = False
        self.LMT01_START_CHECK_IDLE(self.PC2) # Start check idle thread       
        self.LMT01_WAIT_FOR_IDLE(self.PC2)    # Wait for Idle
        self.LMT01_GATE(self.PC2, True)       # Enable buffer gate, pulses reach counter
        self.PC2.wait_for_active(timeout=0.1)
        self.PC2.IDLE = False
        self.LMT01_WAIT_FOR_IDLE(self.PC2)    # Wait for Idle
        self.LMT01_GATE(self.PC2, False)      # Disable buffer gate, pulses reach counter
        self.PC2.COUNT = self.LMT01_READ_COUNTER()
        self.LMT01_RESET_COUNTER()
        self.LMT01_PROBE_DISABLE()
        
        output = list()
        if self.PC1.COUNT == 0:
            output.append(None)
        else:
            self.PC1.TEMP = self.LMT01_COUNT_TO_TEMP(self.PC1.COUNT)
            output.append(self.PC1.TEMP)
        if self.PC2.COUNT == 0:
            output.append(None)
        else:
            self.PC2.TEMP = self.LMT01_COUNT_TO_TEMP(self.PC2.COUNT)
            output.append(self.PC2.TEMP)
        print(output)
        return output
        
    def LMT01_GATE(self, SENSOR, ENABLE):
        if(ENABLE): SENSOR.PWR.off() # Turns on Non-inverting Buffer
        else: SENSOR.PWR.on()        # Turns off Non-inverting Buffer
            
    def LMT01_INIT_MUX(self):
        if MuxCtrl.initMux() != 0:
            print("Mux Init error")
            LED_UI.LED_RED_blink(2) # Blinks Red LED twice
            return False
        time.sleep(0.1)
        if MuxCtrl.sensorTypeEn('DTP') != 0:
            LED_UI.LED_RED_blink(2) # Blinks Red LED twice
            print("DTP Enable error")
            return False
        return True

    def LMT01_THREAD_INIT(self, SENSOR):
        SENSOR.THREAD = Thread(target=thread_function, args=(self, SENSOR))
        SENSOR.CHECK_IDLE = False
        SENSOR.THREAD.start()
        
    def LMT01_START_CHECK_IDLE(self, SENSOR):
        SENSOR.CHECK_IDLE = True
        SENSOR.SEM_CHECK_IDLE.release()
    
    def LMT01_STOP_CHECK_IDLE(self, SENSOR):
        SENSOR.CHECK_IDLE = False
    
    # Checks if the sensor becomes idle
    def LMT01_UPDATE_IDLE_STATE(self, SENSOR):
        while True:
            SENSOR.SEM_CHECK_IDLE.acquire()
            while SENSOR.CHECK_IDLE:
                try:
                    if(SENSOR.PC.inactive_time > TIMEOUT):
                        if not SENSOR.CHECK_IDLE:
                            SENSOR.IDLE = True
                            SEM_UPON_IDLE.release()
                    else:
                        if SENSOR.IDLE:
                            SENSOR.IDLE = False
                except:
                    if SENSOR.IDLE:
                        SENSOR.IDLE = False
        
    def LMT01_WAIT_FOR_IDLE(self, SENSOR):
        SENSOR.SEM_UPON_IDLE.acquire()
        
    def LMT01_PROBE_ENABLE(self, probeNo) -> bool:
        if not MuxCtrl.EnableSingleProbe(probeNo):
            print('Probe enable error')
            LED_UI.LED_RED_blink(2) # Blinks Red LED twice
            return False
        return True
    
    def LMT01_PROBE_DISABLE(self):
        if MuxCtrl.initMux():
            print('Probe enable error')
            LED_UI.LED_RED_blink(2) # Blinks Red LED twice
            return False
        return True
    
    def LMT01_COUNT_ENABLE(self, SENSOR):
        SENSOR.PC.on()
    
    def LMT01_COUNT_DISABLE(self, SENSOR):
        SENSOR.PC.off()
        
    def LMT01_READ_COUNTER():
        return MuxCtrl.read_counter_value()
    
    def LMT01_RESET_COUNTER(self):
        self.RESET.on()
        time.sleep(0.012)
        self.RESET.off()
    
    # Converts pulses to celsius
    def LMT01_COUNT_TO_TEMP(COUNT):
        if(COUNT == 0 or COUNT > 3218):
            return -50
        Cs = [-50,-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
        Ps = [26,181,338,494,651,808,966,1125,1284,1443,1602,1762,1923,2084,2245,2407,2569,2731,2893,3057,3218]
        index = 0
        for P in Ps:
            if(P > COUNT):
                # Arrived at high value
                x2 = Ps[index]
                y2 = Cs[index]
                try:
                    x1 = Ps[index - 1]
                    y1 = Cs[index - 1]
                    x2 = Ps[index]
                    y2 = Cs[index]
                except IndexError:
                    x1 = Ps[index]
                    y1 = Cs[index]
                    x2 = Ps[index + 1]
                    y2 = Cs[index + 1]
                slope = (y2 - y1) / (x2 - x1)
                x1 = Ps[index]
                y1 = Cs[index]
                temp = slope * (COUNT - x1) + y1
                return temp
            elif(P == COUNT):
                return Cs[index]
            else:
                index += 1
        return -50
        
    def removeInaccurateValues(values, repeat = 2):
        """
            Removes inaccurate values from a list repeat times. Returns
            a tuple where it's first value is the accurate list, the second
            value is the invalled values removed, and the third element
            is the difference beetween the invalled values and the average
            of the valid numbers.
        """
        output = values + []
        inv = []
        for i in range(repeat):
            dev = statistics.pstdev(output)
            avg = sum(output) / len(output)
            for value in values:
                if(value > avg + dev or value < avg - dev):
                    try:
                        output.remove(value)
                    except:
                        None
                    else:
                        inv.append(value)
        d = []
        newAvg = statistics.mean(output)
        for val in inv:
            d.append(abs(val - newAvg))
        return (output, inv, d)
    

