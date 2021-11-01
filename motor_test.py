from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit()

kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
