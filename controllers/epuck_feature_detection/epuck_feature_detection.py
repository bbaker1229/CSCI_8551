"""epuck_feature_detection controller."""

from controller import Robot
import numpy as np
import random
import struct
import uuid
import time

# body length in meters
BODYLENGTH = 71/1000
MAX_SPEED = 6.28
MAX_ROTATION = 0.628  # 1 full rotation in 10s
# comm range is in meters
COM_RADIUS = 3 * BODYLENGTH
myid = uuid.uuid4()

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# Enable ground sensor
gs = robot.getDevice('gs1')
gs.enable(timestep)

# Enable distance sensor
ps = robot.getDevice('ps0')
ps.enable(timestep)

# Enable motors
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

# Enable Receiver and Emitter
emitter = robot.getDevice('emitter')
emitter.setRange(COM_RADIUS)
receiver = robot.getDevice('receiver')
receiver.enable(timestep)

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

received_estimates = dict()
concentration = 0.5
first_belief = True
decision = False
decison_check = False
start_decison_check = robot.getTime()

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
        # Send message in format id,estimate,belief
        msg = struct.pack("36sii",myid.bytes,estimate,belief)
        emitter.send(msg)
        com_time_delta =  robot.getTime() - start_com_period

        # if a decision has been made, stay in communication mode
        # for remainder of run
        if com_time_delta >= com_period and not decision:
            # calculate new belief
            black_count = 0
            white_count = 0
            for (id,(time_estimate, estimate)) in received_estimates.items():
                if estimate == 1:
                    white_count += 1
                else:
                    black_count  += 1

            if white_count > black_count:
                belief = 1
            else:
                belief = 0

            forward_flg = True
            turn_flg = False
            com_flg = False
            window_target_time = robot.getTime() + 60
            leftMotor.setVelocity(MAX_SPEED)
            rightMotor.setVelocity(MAX_SPEED)

    else:
        if robot.getTime() >= window_target_time:  # If we reach the full time window then reset the timers
            estimate = round(white_time / (white_time + black_time))
            confidence = max(white_time, black_time) / (white_time + black_time)
            com_period = confidence * 120
            start_com_period = robot.getTime()
            window_target_time = robot.getTime() + 60
            white_time = 0
            black_time = 0
            com_flg = True
            if first_belief:
                belief = estimate
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

    if receiver.getQueueLength() > 0:
        # get message from reciever
        data = receiver.getData()
        receiver.nextPacket()
        # unpack message
        (newid, received_estimate, received_belief) = struct.unpack("36sii", data)
        # clear old data
        # this could be improved with a custom class
        to_remove = list()
        for id,(time_estimate, estimate) in received_estimates.items():
            if (robot.getTime()-time_estimate) > 180:
                to_remove.append(id)

        for id in to_remove:
            received_estimates.pop(id)

        # update
        str_id = str(newid)
        if str_id not in received_estimates.keys():
            concentration = 0.9*concentration + 0.1*received_belief
        received_estimates[str_id] = (robot.getTime(), received_estimate)

    # check for decision
    if not decision:
        if (concentration > 0.9 or concentration < 0.1) and (not decison_check):
            decison_check = True
            start_decison_check = robot.getTime()

        decision_time = robot.getTime() - start_decison_check
        if concentration > 0.9 and decision_time > 30 and decison_check:
            decision = True
            belief = 1
            com_flg = True
            print(
                myid,
                ",white,",
                time.strftime('%H:%M:%S', time.gmtime(robot.getTime()))
            )
        elif concentration < 0.1 and decision_time > 30 and decison_check:
            decision = True
            belief = 0
            # if a decision has been made, switch to communication mode
            # for remainder of run
            com_flg = True
            print(
                myid,
                ",black,",
                time.strftime('%H:%M:%S', time.gmtime(robot.getTime()))
            )
        elif (concentration < 0.9 and concentration > 0.1):
            # reset decision_check
            decison_check = False
    pass

# Enter here exit cleanup code.
