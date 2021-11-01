import time
import serial
import sys

ser = serial.Serial(
    port = '/dev/ttyUSB0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 0.050)

def readSerial():
    
    try:
        line = ser.readline().rstrip()
        
        if not line:
            return -1
        
        data = int(line)
        ser.reset_output_buffer()
        
        return data
    
    except:
        pass
        return -1

while True:
    
    stop_motor = readSerial()
    
    if stop_motor >= 0:
        print(stop_motor)
    
    
    