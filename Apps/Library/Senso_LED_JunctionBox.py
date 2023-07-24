#!/usr/bin/env python

from gpiozero import PWMLED
from queue import Queue
from threading import Thread


class LED_JunctionBox:
    """
        Junction Box LED User Interface.
        Creates a thread with a queue
        and processes commands in the queue.
    """

    def __init__(self, RED_GPIO = 4, GREEN_GPIO = 22, max_queue = 5, 
                 name = "Junction Box LED UI", *args, **kwargs):
        self.LED_RED = PWMLED(RED_GPIO, *args, **kwargs)
        self.LED_GREEN = PWMLED(GREEN_GPIO, *args, **kwargs)
        self._queue = Queue(max_queue)
        self._thread = Thread(target = self._process_thread, name = name, args=(self))
        self._name = name
        self._processing = False
        self._thread.start()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.LED_RED.close()
        self.LED_GREEN.close()
    
    def _process_thread(self):
        while True:
            self._processing = False
            f, count = self._queue.get()
            self._processing = True
            f(count)
        
    def _success(self, count = 2) -> bool:
        """
        Pulses green 'count' times
        """
        self.LED_GREEN.pulse(1, 1, n = count, background = False)

    def _warning(self, count = 2) -> bool:
        """
        Pulses red 'count' times
        """
        self.LED_RED.pulse(1, 1, n = count, background = False)

    def _critical(self, count = 10):
        """
        Blinks red 'count' times
        """
        self.LED_RED.blink(0.5, 0.5, n = count, background = False)

    def success(self, count = 2) -> bool:
        """
        Pulses the green LED 2 times to indicate successful operation
        count: number of times to pulse
        Adds the command to the queue
        """
        try:
            self._queue.put_nowait((self._success, count))
            return True
        except:
            print(f"Failed to add success to LED UI Queue: Queue is full!")
            return False

    def warning(self, count = 2) -> bool:
        """
        Pulses the red LED 2 times to indicate a warning
        count: number of times to pulse
        Adds the command to the queue
        """
        try:
            self._queue.put_nowait((self._warning, count))
            return True
        except:
            print(f"Failed to add warning to LED UI Queue: Queue is full!")
            return False

    def critical(self, count = 10) -> bool:
        """
        Blinks the red LED 10 times to indicate a warning
        count: number of times to pulse
        Adds the command to the queue
        """
        try:
            self._queue.put_nowait((self._critical, count))
            return True
        except:
            print(f"Failed to add critical to LED UI Queue: Queue is full!")
            return False

    def isComplete(self):
        """
        Returns True if all commands are complete, false otherwise
        """
        return not self._processing
    
