import RPi.GPIO as GPIO
from time import sleep

import time
import serial
import sys

#from pynput import keyboard

import threading
import random

# Direction pin from controller
DIR  = [10,5,11,15,21,16,22,26,40]
# Step pin from controller
STEP = [8, 3, 7,13,19,12,18,24,38]
# 0/1 used to signify clockwise or counterclockwise.
DR  = [1,1,1,1,1,1,1,1,1]

num_motors = 9;

#positions
current_position = [0,0,0,0,0,0,0,0,0]
target_position  = [0,0,0,0,0,0,0,0,0]
zero_position   = [0,0,0,0,0,0,0,0,0]

init_offset = 1000
1
delay_time = [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001
              
              ] 

#threading
st   = []
lock = []

# Setup pin layout on PI
GPIO.setmode(GPIO.BOARD)

break_program = False

next_update = 0
update_time = 30

serialStop = serial.Serial(
    port = '/dev/ttyUSB0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 0.050)

zeroLock = threading.Lock()

'''
def on_press(key):
    global break_program
    print(key)
    if key == keyboard.Key.end:
        print('End pressed')
        break_program = True
        return False
'''

def readSerial():
    # receive serial data from controller
    try:
        line = serialStop.readline().rstrip()
        
        if not line:
            return -1
        
        data = int(line)
        serialStop.reset_output_buffer()
        
        zero_position[data] = 1
        
        return data
    
    except:
        pass
        return -1

def initializePins():
    # Establish Pins in software
    print('INITIALIZING PIN OUTPUT')
    for i in range(0,num_motors):
        GPIO.setup(DIR[i], GPIO.OUT)
        GPIO.setup(STEP[i], GPIO.OUT)

    # Set the first direction you want it to spin
    for i in range(0,num_motors):
        GPIO.output(DIR[i], DR[i])

def initializeThreads():
    print('INITIALIZING THREADS')
    for i in range(0,num_motors):
        st.append(threading.Thread())
        lock.append(threading.Lock())

def stepperMoveTo(id, numsteps):
    for x in range(numsteps):
        GPIO.output(DIR[id],0)
            # Set one coil winding to high
        GPIO.output(STEP[id],GPIO.HIGH)
            # Allow it to get there.
        sleep(delay_time[id]) # Dictates how fast stepper motor will run
            # Set coil winding to low
        GPIO.output(STEP[id],GPIO.LOW)
        sleep(delay_time[id]) # Dictates how fast stepper motor will run
    

def stepper_worker(id, numsteps):
    
    global current_position
    global target_position
    global zero_position
    
    at_zero = False
    
    GPIO.output(DIR[id],DR[id])
    
    for x in range(numsteps):
        
        # check if it meet the zero position lock
        if zero_position[id] == 1:
            at_zero = True
            continue
        
        # Set one coil winding to high
        GPIO.output(STEP[id],GPIO.HIGH)
        # Allow it to get there.
        sleep(delay_time[id]) # Dictates how fast stepper motor will run
        # Set coil winding to low
        GPIO.output(STEP[id],GPIO.LOW)
        sleep(delay_time[id]) # Dictates how fast stepper motor will run
        
    with lock[id]:
        
        if at_zero:
            # if get zero feedback
            current_position[id] = 0
            target_position[id] = 0
            with zeroLock:
                 zero_position[id] = 0
            
        else:
            # update current position
            if DR[id] == 1:
                current_position[id] = current_position[id] - numsteps
            else:
                current_position[id] = current_position[id] + numsteps
        
    if at_zero:
        for x in range(init_offset):
            GPIO.output(DIR[id],0)
            # Set one coil winding to high
            GPIO.output(STEP[id],GPIO.HIGH)
            # Allow it to get there.
            sleep(delay_time[id]) # Dictates how fast stepper motor will run
            # Set coil winding to low
            GPIO.output(STEP[id],GPIO.LOW)
            sleep(delay_time[id]) # Dictates how fast stepper motor will run
        
def updatePosition(id):
    if not st[id].isAlive():
        
        if zero_position[id] == 1:

            pass
            '''
            st[id] = threading.Thread(
                target=stepperMoveTo,
                args=(
                    id,
                    init_offset,
                ),
            )
            st[id].start()
            '''
        else:
            target = target_position[id] - current_position[id]
        
            if target != 0:
                if target < 0:
                    DR[id] = 1
                    target = -target
                else:
                    DR[id] = 0
                
                st[id] = threading.Thread(
                    target=stepper_worker,
                    args=(
                        id,
                        target,
                    ),
                )
                st[id].start()
                print('{}--MOVE IN--{}'.format(id, target))
        
def newPosition():
    for i in range(0,num_motors):
        #if random.random() > .8:
        target_position[i] = random.randint(-3000,10000)
        #target_position[i] = 15000
            
def resetPosition():
    
    for i in range(0, num_motors):
        target_position[i] = 3000
        updatePosition(i)
    
    sleep(10)
    
    for i in range(0, num_motors):
        target_position[i] = -100000
        updatePosition(i)
    
    next_update = time.time() + 120
        
    
# amin cycle funstion
def main():
    
    # initialization
    initializePins()
    initializeThreads()
    
    next_update = 0
    
    resetPosition()
    
    try:
        
        while True:
            # short delay in the cycle
            sleep(.01)
            
            #read data from lock controller
            lockReceived = readSerial()
            #if lockReceived >= 0:
            #    print(zero_position)
                
            if next_update < time.time():
                # update position
                newPosition()
                next_update = time.time() + update_time

            
            # move to the new position
            for i in range(0,num_motors):
                updatePosition(i)
                
            print("current: ", current_position)
            print("target: ", target_position)
                
            print("lock: ", zero_position)
            
            for i in range(0, num_motors):
                zero_position[i] = 0

                
    # Once finished clean everything up
    except KeyboardInterrupt:
        print("cleanup")
        GPIO.cleanup()

# main cycle
if __name__ == "__main__":
    main()