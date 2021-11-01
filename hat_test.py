
import time
import atexit
import threading
import random
import board
from adafruit_motor import stepper as STEPPER
from adafruit_motorkit import MotorKit

# Initialise the first hat on the default address
kit1 = MotorKit()
# Initialise the second hat on a different address
#kit2 = MotorKit(address=0x61)

# create empty threads (these will hold the stepper 1 and 2 threads)
st1 = threading.Thread()  # pylint: disable=bad-thread-instantiation
st2 = threading.Thread()  # pylint: disable=bad-thread-instantiation

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    kit1.stepper1.release()
    kit1.stepper2.release()
    
atexit.register(turnOffMotors)

stepstyles = [STEPPER.SINGLE, STEPPER.DOUBLE, STEPPER.INTERLEAVE, STEPPER.MICROSTEP]

def stepper_worker(stepper, numsteps, direction, style):
    # print("Steppin!")
    for _ in range(numsteps):
        stepper.onestep(direction=direction, style=style)
    # print("Done")
    
while True:
    if not st1.isAlive():
        randomdir = 0
        print("Stepper 1")
        if randomdir == 0:
            move_dir = STEPPER.FORWARD
            print("forward")
        else:
            move_dir = STEPPER.BACKWARD
            print("backward")
        randomsteps = 200
        print("%d steps" % randomsteps)
        st1 = threading.Thread(
            target=stepper_worker,
            args=(
                kit1.stepper1,
                randomsteps,
                move_dir,
                stepstyles[0],
            ),
        )
        st1.start()

    if not st2.isAlive():
        print("Stepper 2")
        randomdir = random.randint(0, 1)
        if randomdir == 0:
            move_dir = STEPPER.FORWARD
            print("forward")
        else:
            move_dir = STEPPER.BACKWARD
            print("backward")
        randomsteps = random.randint(10, 50)
        print("%d steps" % randomsteps)
        st2 = threading.Thread(
            target=stepper_worker,
            args=(
                kit1.stepper2,
                randomsteps,
                move_dir,
                stepstyles[random.randint(0, 3)],
            ),
        )
        st2.start()

    time.sleep(0.01)  # Small delay to stop from constantly polling threads
    # see: https://forums.adafruit.com/viewtopic.php?f=50&t=104354&p=562733#p562733
