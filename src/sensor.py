import serial 
import time

from serial.serialutil import SerialBase, SerialException

import os
class Sensor:

    def __init__(self):
        self.find_port()
        try:
            self.ser = serial.Serial(self.port , 115200 , timeout=1 ,dsrdtr=False, rtscts=False,)
            #self.ser.setRTS(True)
        except SerialException:
            self.reconnect()
        time.sleep(1)

    def get_data(self):
        try:

            line = self.ser.readline()
            if line:
                return int(line.decode())

        except:
            print(line)
            return 0
    
    def find_port(self):
        self.port = str(os.popen("ls -la /dev/ttyUSB* | awk '{print $NF}'").read()).strip()
        
    def reconnect(self):
        diss =  True
        while diss:
            self.find_port()
            try:
                self.ser = serial.Serial(self.port , 115200 , timeout=1)
                if self.ser:
                    diss = False
            except SerialException:
                pass
            time.sleep(1)
        
        return 
