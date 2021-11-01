import RPi.GPIO as GPIO
from time import sleep

import threading

# Direction pin from controller
DIR  = 10
# Step pin from controller
STEP = 8
# 0/1 used to signify clockwise or counterclockwise.
CW  = 1
CCW = 0

num_motors = 1;

# Setup pin layout on PI
GPIO.setmode(GPIO.BOARD)

# Establish Pins in software
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

# Set the first direction you want it to spin
GPIO.output(DIR, CW)

st1 = threading.Thread()

def stepper_worker(numsteps):
    
    GPIO.output(DIR,CCW)

    # Run for 200 steps. This will change based on how you set you controller
    for x in range(numsteps):

        # Set one coil winding to high
        GPIO.output(STEP,GPIO.HIGH)
        # Allow it to get there.
        sleep(delay_time) # Dictates how fast stepper motor will run
        # Set coil winding to low
        GPIO.output(STEP,GPIO.LOW)
        sleep(delay_time) # Dictates how fast stepper motor will run

    """Change Direction: Changing direction requires time to switch. The
    time is dictated by the stepper motor and controller. """
    sleep(1.0)
    GPIO.output(DIR,CW)
    for x in range(numsteps):
        GPIO.output(STEP,GPIO.HIGH)
        sleep(delay_time)
        GPIO.output(STEP,GPIO.LOW)
        sleep(delay_time)


try:
    # Run forever.
    delay_time = 0.001    
    while True:

        """Change Direction: Changing direction requires time to switch. The
        time is dictated by the stepper motor and controller. """
        sleep(.3)
        # Esablish the direction you want to go
        if not st1.isAlive():
            st1 = threading.Thread(
                target=stepper_worker,
                args=(
                    5000,
                ),
            )
            st1.start()
            print('------------------STARTED')
            
            
        #print(delay_time)
        #delay_time = delay_time * 1.1

                

# Once finished clean everything up
except KeyboardInterrupt:
    print("cleanup")
    GPIO.cleanup()
