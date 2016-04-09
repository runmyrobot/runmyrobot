try:
    from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
    motorsEnabled = True
except ImportError:
    print "You need to install Adafruit_MotorHAT"
    print "Please install Adafruit_MotorHAT for python and restart this script."
    print "Running in test mode."
    print "Ctrl-C to quit"
    motorsEnabled = False

import time
import atexit
import sys
import thread

from socketIO_client import SocketIO, LoggingNamespace

steeringSpeed = 255
steeringHoldingSpeed = 180
drivingSpeed = 255
handlingCommand = False


if len(sys.argv) >= 2:
    robot_id = sys.argv[1]
else:
    robot_id = raw_input("Please enter your Robot ID: ")

if len(sys.argv) >= 3:
    print 'DEV MODE ***************'
    print "using dev port 8122"
    port = 8122
else:
    print 'PROD MODE *************'
    print "using prod port 8022"
    port = 8022

print 'using socket io to connect to runmyrobot.com'
socketIO = SocketIO('runmyrobot.com', port, LoggingNamespace)
print 'finished using socket io to connect to runmyrobot.com'

def times(lst, number):
    return [x*number for x in lst]


def runMotor(motorIndex, direction):
    motor = mh.getMotor(motorIndex+1)
    if direction == 1:
        motor.setSpeed(drivingSpeed)
        motor.run(Adafruit_MotorHAT.FORWARD)
    if direction == -1:
        motor.setSpeed(drivingSpeed)
        motor.run(Adafruit_MotorHAT.BACKWARD)


if robot_id != "22027911": # if not Zip
    left = (1, -1, 1, 1)
    right = times(left, -1)
    forward = (1, 1, 1, -1)
    backward = times(forward, -1)
else:  # Zip
    left = (-1, -1, -1, 1)
    right = times(left, -1)
    forward = (1, -1, 1, 1)
    backward = times(forward, -1)

        
        
def handle_command(args):

        global handlingCommand
        if handlingCommand:
            return
        handlingCommand = True

        if 'command' in args and 'robot_id' in args and args['robot_id'] == robot_id:

            print('got something', args)

            command = args['command']
            if motorsEnabled:
                motorA.setSpeed(drivingSpeed)
                motorB.setSpeed(drivingSpeed)
                if command == 'F':
                    for motorIndex in range(4):
                        runMotor(motorIndex, forward[motorIndex])
                    time.sleep(0.2)
                if command == 'B':
                    for motorIndex in range(4):
                        runMotor(motorIndex, backward[motorIndex])
                    time.sleep(0.2)
                if command == 'L':
                    for motorIndex in range(4):
                        runMotor(motorIndex, left[motorIndex])
                    time.sleep(0.1)
                if command == 'R':
                    for motorIndex in range(4):
                        runMotor(motorIndex, right[motorIndex])
                    time.sleep(0.1)


            turnOffMotors()
            
        handlingCommand = False



        
def on_handle_command(*args):
   thread.start_new_thread(handle_command, args)

#from communication import socketIO
socketIO.on('command_to_robot', on_handle_command)

def myWait():
  socketIO.wait()
  thread.start_new_thread(myWait, ())


if motorsEnabled:
    # create a default object, no changes to I2C address or frequency
    mh = Adafruit_MotorHAT(addr=0x60)


def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

if motorsEnabled:
    atexit.register(turnOffMotors)
    motorA = mh.getMotor(1)
    motorB = mh.getMotor(2)


while True:
    socketIO.wait(seconds=10)
