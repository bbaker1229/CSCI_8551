from controller import Supervisor
import sys

TIME_STEP = 32

supervisor = Supervisor()

# do this once only
robot_node = supervisor.getFromDef("e-puck")
if robot_node is None:
    sys.stderr.write("No DEF e-puck node found in the current world file\n")
    sys.exit(1)
led_status = robot_node.getFromProtoDef("EPUCK_BODY_LED")
led_status = led_status.getField('color')
led_status = led_status.getMFColor(0)
trans_field = robot_node.getField("translation")
field_ind = robot_node.getNumberOfFields()
pfield_ind = robot_node.getProtoNumberOfFields()
field = robot_node.getFieldByIndex(0)
robot_node.getProtoFieldByIndex(0)
print("Fields:")
for i in range(field_ind):
    field = robot_node.getFieldByIndex(i)
    print(field.getName())
print("Proto Fields:")
for i in range(pfield_ind):
    field = robot_node.getProtoFieldByIndex(i)
    print(field.getName())

   


while supervisor.step(TIME_STEP) != -1:
    # this is done repeatedly
    values = trans_field.getSFVec3f()
    print("MY_ROBOT is at position: %g %g %g" % (values[0], values[1], values[2]))
    print(led_status)
    print(supervisor.getFromDevice('led8')
    