
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
import subprocess
import time
import RPi.GPIO as GPIO
from socketIO_client import SocketIO, LoggingNamespace

GPIO.setmode(GPIO.BCM)
chargeIONumber = 17
GPIO.setup(chargeIONumber, GPIO.IN)

straightDelay = 1.6

#steeringSpeed = 255
steeringSpeed = 200
steeringHoldingSpeed = 180
#drivingSpeed = 255
drivingSpeed = 200
handlingCommand = False



if len(sys.argv) >= 2:
    robotID = sys.argv[1]
else:
    robotID = raw_input("Please enter your Robot ID: ")

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
    if direction == 0.5:
        motor.setSpeed(128)
        motor.run(Adafruit_MotorHAT.FORWARD)
    if direction == -0.5:
        motor.setSpeed(128)
        motor.run(Adafruit_MotorHAT.BACKWARD)


if robotID == "3444925": # if Timmy
    left = (1, 1, 1, 1)
    right = times(left, -1)
    forward = (-1, 1, 1, -1)
    backward = times(forward, -1)
    turnDelay = 0.8
elif robotID == "88359766": # Skippy_old
    left = (1, -1, 1, 1)
    right = times(left, -1)
    forward = (1, 1, 1, -1)
    backward = times(forward, -1)
    turnDelay = 0.8
elif robotID == "22027911": # Zip
    left = (0, 1, 1, 0) # was 1,1,1,1
    right = (0, -1, -1, 0)
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    turnDelay = 0.8
elif robotID == "52225122": # Pippy
    left = (1, 1, 1, 1)
    right = times(left, -1)
    forward = (-1, 1, 1, -1)
    backward = times(forward, -1)
    turnDelay = 0.8
elif robotID == "72378514": # Skippy
    left = (1, 1, 1, 1)
    right = times(left, -1)
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    turnDelay = 0.4
elif robotID == "19359999": # Mikey
    left = (1, 1, 1, 1)
    right = times(left, -1)
    forward = (-1, 1, 1, -1)
    backward = times(forward, -1)
    turnDelay = 0.4
else: # default settings
    left = (1, 1, 1, 1)
    right = times(left, -1)
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    turnDelay = 0.4

    
        
def handle_command(args):

        global handlingCommand
        if handlingCommand:
            return
        handlingCommand = True

        #if 'robot_id' in args:
        #    print "args robot id:", args['robot_id']

        #if 'command' in args:
        #    print "args command:", args['command']

        #print "args:", args
            
        if 'command' in args and 'robot_id' in args and args['robot_id'] == robotID:

            print('got something', args)

            command = args['command']
            if motorsEnabled:
                motorA.setSpeed(drivingSpeed)
                motorB.setSpeed(drivingSpeed)
                if command == 'F':
                    for motorIndex in range(4):
                        runMotor(motorIndex, forward[motorIndex])
                    time.sleep(straightDelay)
                if command == 'B':
                    for motorIndex in range(4):
                        runMotor(motorIndex, backward[motorIndex])
                    time.sleep(straightDelay)
                if command == 'L':
                    for motorIndex in range(4):
                        runMotor(motorIndex, left[motorIndex])
                    time.sleep(turnDelay)
                if command == 'R':
                    for motorIndex in range(4):
                        runMotor(motorIndex, right[motorIndex])
                    time.sleep(turnDelay)


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

def ipInfoUpdate():
    socketIO.emit('ip_information', subprocess.check_output(["hostname", "-I"]))

def sendChargeState():
    charging = GPIO.input(chargeIONumber) == 1
    chargeState = {'robot_id': robotID, 'charging': charging}
    socketIO.emit('charge_state', chargeState)
    print "charge state:", chargeState

def sendChargeStateCallback(x):
    sendChargeState()

GPIO.add_event_detect(chargeIONumber, GPIO.BOTH)
GPIO.add_event_callback(chargeIONumber, sendChargeStateCallback)



waitCounter = 0
ipInfoUpdate()
while True:
    socketIO.wait(seconds=10)
    if (waitCounter % 10) == 0:
        ipInfoUpdate()
        sendChargeState()

    waitCounter += 1


