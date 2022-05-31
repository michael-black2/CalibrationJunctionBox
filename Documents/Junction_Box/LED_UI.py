from gpiozero import PWMLED
from time import sleep

LED_GREEN = []
LED_RED = []

def LED_init():
    global LED_GREEN
    global LED_RED
    LED_RED = PWMLED(4)
    LED_GREEN = PWMLED(22)
    LED_GREEN.value = 0
    LED_RED.value = 0

def LED_RED_pulse(n=None):
    if (LED_RED.is_lit == False) and (n != 0):
        LED_RED.pulse(1,1,n)
    elif (n == 0):
        LED_RED.off()
    
def LED_GREEN_pulse(n=None):
    if (LED_GREEN.is_lit == False) and (n != 0):
        LED_GREEN.pulse(1,1,n)
    elif (n == 0):
        LED_GREEN.off()
    
def LED_RED_blink(n=None):
    if (LED_RED.is_lit == False) and (n != 0):
        LED_RED.blink(1,1,n)
    elif (n == 0):
        LED_RED.off()
    
def LED_GREEN_blink(n=None):
    if (LED_GREEN.is_lit == False) and (n != 0):
        LED_GREEN.blink(1,1,n)
    elif (n == 0):
        LED_GREEN.off()
