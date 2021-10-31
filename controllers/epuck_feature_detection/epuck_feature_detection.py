"""epuck_feature_detection controller."""

from controller import Robot
import numpy as np
import random

BODYLENGTH = 71
MAX_SPEED = 6.28
MAX_ROTATION = 0.628  # 1 full rotation in 10s
COM_RADIUS = 3 * BODYLENGTH
myid = random.randint(0, 100)  # Need a better method to do this
print("My ID is: ", myid)

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# Enable ground sensor
gs = robot.getDevice('gs1')
gs.enable(timestep)

# Enable
ps = robot.getDevice('ps0')
ps.enable(timestep)

# Enable motors
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

# Initialize forward movement
leftMotor.setVelocity(MAX_SPEED)
rightMotor.setVelocity(MAX_SPEED)
forward_time = np.random.exponential(14, 1)  # use 240 instead of 14
forward_flg = True
rotation_time = 0
turn_flg = False
com_period = 0
com_flg = False

# Initialize time
start_time = robot.getTime()

# Initialize observation window timer
window_target_time = start_time + 60
white_time = 0
black_time = 0
time_left = 0

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    time_delta = robot.getTime() - start_time
    if forward_flg:
        if ps.getValue() > 100:  # If the wall is detected go into turn mode
            # Set motors to turn
            leftMotor.setVelocity(MAX_ROTATION)
            rightMotor.setVelocity(-MAX_ROTATION)
            # Adjust flags
            turn_flg = True
            forward_flg = False
            # Set the rotation time
            rotation_time = np.pi / MAX_ROTATION
            start_time = robot.getTime()
            time_delta = robot.getTime() - start_time
            # Pause observation window
            time_left = window_target_time - robot.getTime()
        if time_delta >= forward_time:  # If we are in forward mode and we hit the time limit; turn
            # Adjust flags
            turn_flg = True
            forward_flg = False
            # Set the rotation time
            start_time = robot.getTime()
            time_delta = robot.getTime() - start_time
            rotation = np.random.uniform(-np.pi, np.pi, 1)
            rotation_time = rotation / MAX_ROTATION
            # Set motors to turn
            leftMotor.setVelocity(MAX_ROTATION)
            rightMotor.setVelocity(-MAX_ROTATION)
            # Pause observation window
            time_left = window_target_time - robot.getTime()

    if com_flg:
        print("Myid: ", myid, end=',')
        print("Estimate: ", estimate)
        com_time_delta =  robot.getTime() - start_com_period
        if com_time_delta >= com_period:
            print("Observation time starting")
            forward_flg = True
            turn_flg = False
            com_flg = False
            window_target_time = robot.getTime() + 60
            leftMotor.setVelocity(MAX_SPEED)
            rightMotor.setVelocity(MAX_SPEED)

    else:
        if robot.getTime() >= window_target_time:  # If we reach the full time window then reset the timers
            estimate = round(white_time / (white_time + black_time), 3)
            print(estimate)
            confidence = max(white_time, black_time) / (white_time + black_time)
            print(confidence)
            com_period = confidence * 120
            start_com_period = robot.getTime()
            window_target_time = robot.getTime() + 60
            white_time = 0
            black_time = 0
            com_flg = True
        else:
            if gs.getValue() > 650:
                white_time += 1
            if gs.getValue() < 650:
                black_time += 1

    if turn_flg:
        if time_delta >= rotation_time:  # If we are in turn mode and we hit the time limit; forward
            # Adjust flags
            turn_flg = False
            forward_flg = True
            # Set the forward time
            start_time = robot.getTime()
            time_delta = robot.getTime() - start_time
            forward_time = np.random.exponential(14, 1)
            # Set motors to forward
            leftMotor.setVelocity(MAX_SPEED)
            rightMotor.setVelocity(MAX_SPEED)
            # Reset observation window timer
            window_target_time = robot.getTime() + time_left
    pass

# Enter here exit cleanup code.
