import RPi.GPIO as GPIO
from time import sleep

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

delay_time = [0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001, 0.001] 

#threading
st   = []
lock = []

# Setup pin layout on PI
GPIO.setmode(GPIO.BOARD)

break_program = False

'''
def on_press(key):
    global break_program
    print(key)
    if key == keyboard.Key.end:
        print('End pressed')
        break_program = True
        return False
'''

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

def stepper_worker(id, numsteps):
    
    global current_position
    
    GPIO.output(DIR[id],DR[id])
    # Run for 200 steps. This will change based on how you set you controller
    for x in range(numsteps):
        
        # Set one coil winding to high
        GPIO.output(STEP[id],GPIO.HIGH)
        # Allow it to get there.
        sleep(delay_time[id]) # Dictates how fast stepper motor will run
        # Set coil winding to low
        GPIO.output(STEP[id],GPIO.LOW)
        sleep(delay_time[id]) # Dictates how fast stepper motor will run
        
    with lock[id]:
        if DR[id] == 0:
            current_position[id] = current_position[id] - numsteps
        else:
            current_position[id] = current_position[id] + numsteps
        
        
def updatePosition(id):
    if not st[id].isAlive():
        
        target = target_position[id] - current_position[id]
        
        
        if target != 0:
        
            if target < 0:
                DR[id] = 0
                target = -target
            else:
                DR[id] = 1
            
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
        if random.random() > .9:
            target_position[i] = random.randrange(1000,8000)

# amin cycle funstion
def main():
    
    initializePins()
    initializeThreads()
    
    try:
        
        while True:
            # short delay in the cycle
            sleep(1)
            # update position
            newPosition()
            # move to the new position
            for i in range(0,num_motors):
                updatePosition(i)
                
            print("current: ", current_position)
            print("target: ", target_position)

                
    # Once finished clean everything up
    except KeyboardInterrupt:
        print("cleanup")
        GPIO.cleanup()

# main cycle
if __name__ == "__main__":
    main()