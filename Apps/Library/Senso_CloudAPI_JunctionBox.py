#!/usr/bin/env python
"""
Cloud API to store junction box data in the Life Science Cloud
"""

import requests                 # Does HTTPS POST.
from datetime import datetime   # Gets the time
import uuid

class CloudAPI_JunctionBox:
    def __init__(self, http_link = "http://cprod.sensoiot.com/api/DataLog"):
        self.http_link = http_link
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self)
        pass

    def getMAC(self):
        """
        Returns the MAC address of the device
        """
        return hex(uuid.getnode()).replace("0x","").upper()

    def testInternet(self):
        """
        Tests the internet connection
        Raises an exception if an issue occurs
        """
        requests.head("https://www.google.com/", timeout = 1)

    def send(self, data):
        print(f"url = {self.http_link}, data = {data}")                     # Prints url and data
        out = requests.post(self.http_link, data=data)                      # Does HTTP POST
        output = dict()
        output["status_code"] = str(out.status_code)
        output["result"] = str(out.text)
        return output  # Returns result and status code

# def read(pin):
#     print("Reading pin number " + str(pin))
#     return str(random.randint(10,30))                            # Returns random info beetween 10C to 30C