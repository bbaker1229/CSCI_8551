"""epuck_feature_detection controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot
import random
    
def random_walk(leftMotor, rightMotor):
    directions = ["forward", "left", "right"]
    direction = random.choices(directions, weights = [10, 1, 1], k = 1)
    if direction[0] == "left":
        leftMotor.setVelocity(-0.1 * MAX_SPEED)
        rightMotor.setVelocity(0.1 * MAX_SPEED)
    if direction[0] == "right":
        leftMotor.setVelocity(0.1 * MAX_SPEED)
        rightMotor.setVelocity(-0.1 * MAX_SPEED)
    if direction[0] == "forward":
        leftMotor.setVelocity(0.1 * MAX_SPEED)
        rightMotor.setVelocity(0.1 * MAX_SPEED)

MAX_SPEED = 10
# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
    # set up the motor speeds at 10% of the MAX_SPEED.
leftMotor.setVelocity(0.1 * MAX_SPEED)
rightMotor.setVelocity(0.1 * MAX_SPEED)

count = 0
# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    count += 1
    if count == 30:
        random_walk(leftMotor, rightMotor)
        count = 0
    pass

# Enter here exit cleanup code.
