import requests                 # Does HTTPS POST.
import time                     # Measures time.
import random                   # Gets random junk data.
from datetime import datetime   # Gets the time

def getMAC(interface='eth0'):
  # Return the MAC address of named Ethernet interface
  try:
    line = open('/sys/class/net/%s/address' %interface).read()
  except:
    line = "None"
  return line[0:17]

mac_address = getMAC('wlan0');

http_link = "http://cprod.sensoiot.com/api/DataLog"
http_post_info = []


def send(url,info):
    print("url = " + str(url) + " data = " + str(info))                 # Prints url and data
    out = requests.post(url,data=info)                                  # Does HTTP POST
    return {"status_code":str(out.status_code),"result":str(out.text)}  # Returns result and status code

# def read(pin):
#     print("Reading pin number " + str(pin))
#     return str(random.randint(10,30))                            # Returns random info beetween 10C to 30C

