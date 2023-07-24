#!/usr/bin/env python

import datetime

class Dashboard(object):
    _methods = ['add','update','clear_all','print','delete']
    def __init__(self, data:dict, spacing = 1, datestamp = False, alpha = True) -> None:
        """
        Initializes a dashboard that can be printed with keys and values
        spacing sets the distance between the longest item in a column to the beginning of the next column
        datestamp generates a datestamp for each row in the dashboard
        alpha sets the columns in alphabetical order, if false it orders in the order of input
        """
        self._spacing = spacing
        self._keys = list()
        self._alpha = alpha
        for key, value in data.items():
            setattr(self, key, value)
            self._keys.append(key)
        self._update()
        self.print()

    def add(self, **kwargs):
        """
        Adds a new key and value to the dashboard
        """
        for key, value in kwargs.items():
            if not hasattr(self,key):
                setattr(self,key,value)
            else:
                print(key + ": Attribute already exists, use Dashboard.update("+key+"=...)")
        self._update()

    def update(self, **kwargs):
        """
        Update the value of a key in the dashboard
        """
        for key, value in kwargs.items():
            if hasattr(self,key):
                setattr(self,key,value)
            else:
                print(key + ": Attribute not found, use Dashboard.add("+key+"=...)")
        self._update()

    def clear_all(self):
        """
        Clears all key values in the dashboard
        """
        for key in dir(self):
            if not key.startswith("_") and key not in self._methods:
                setattr(self, key, None)
        self._update()

    def delete(self, key):
        """
        Delete a column in the dashboard
        """
        if key in self._keys:
            delattr(self,key)
            self._keys.remove(key)
        else:
            print("delete failed - Attribute not in dashboard")
        self._update()
    
    def print(self):
        """
        Prints the dashboard contents
        """
        print(''.ljust(len(self._key_string)-self._spacing,'-'))
        print(self._key_string)
        print(''.ljust(len(self._key_string)-self._spacing,'-'))
        print(self._value_string)

    def _update(self):
        """
        Internal function to update the print string
        """
        self._key_string = ""
        self._value_string = ""
        keys = list()
        values = list()
        if self._alpha:
            for key in dir(self):
                if not key.startswith("_") and key not in self._methods:
                    keys.append(key)
                    values.append(getattr(self, key))
        else:
            for key in self._keys:
                keys.append(key)
                values.append(getattr(self, key))
        col_width = list()
        for i in range(len(keys)):
            k = len(str(keys[i]))
            v = len(str(values[i]))
            if k >= v:
                col_width.append(k + self._spacing)
            else:
                col_width.append(v + self._spacing)
            self._key_string += keys[i].ljust(col_width[i],' ')
        for i in range(len(values)):
            self._value_string  +=  str(values[i]).ljust(col_width[i],' ')
