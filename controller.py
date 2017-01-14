

server = "runmyrobot.com"
#server = "52.52.213.92"




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
steeringSpeed = 90
steeringHoldingSpeed = 90
#drivingSpeed = 255
global drivingSpeed


drivingSpeed = 90
handlingCommand = False
turningSpeedActuallyUsed = 50
drivingSpeedActuallyUsed = 50




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

print 'using socket io to connect to', server
socketIO = SocketIO(server, port, LoggingNamespace)
print 'finished using socket io to connect to', server

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
    turnDelay = 0.4
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
elif robotID == "78929358": # ZombieZip
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
elif robotID == "86583531": # Dilbert
    left = (1, 1, 1, 1)
    right = times(left, -1)
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    turnDelay = 0.4
else: # default settings
    left = (1, 1, 1, 1)
    right = times(left, -1)
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    turnDelay = 0.4

    
        
def handle_command(args):

        global drivingSpeed
    
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
                    drivingSpeed = drivingSpeedActuallyUsed
                    for motorIndex in range(4):
                        runMotor(motorIndex, forward[motorIndex])
                    time.sleep(straightDelay)
                if command == 'B':
                    drivingSpeed = drivingSpeedActuallyUsed
                    for motorIndex in range(4):
                        runMotor(motorIndex, backward[motorIndex])
                    time.sleep(straightDelay)
                if command == 'L':
                    drivingSpeed = turningSpeedActuallyUsed
                    for motorIndex in range(4):
                        runMotor(motorIndex, left[motorIndex])
                    time.sleep(turnDelay)
                if command == 'R':
                    drivingSpeed = turningSpeedActuallyUsed
                    for motorIndex in range(4):
                        runMotor(motorIndex, right[motorIndex])
                    time.sleep(turnDelay)
                if command == 'U':
                    mhArm.getMotor(1).setSpeed(127)
                    mhArm.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
                    time.sleep(0.05)
                if command == 'D':
                    mhArm.getMotor(1).setSpeed(127)
                    mhArm.getMotor(1).run(Adafruit_MotorHAT.FORWARD)           
                    time.sleep(0.05)
                if command == 'O':
                    mhArm.getMotor(2).setSpeed(127)
                    mhArm.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
                    time.sleep(0.05)
                if command == 'C':
                    mhArm.getMotor(2).setSpeed(127)
                    mhArm.getMotor(2).run(Adafruit_MotorHAT.FORWARD)           
                    time.sleep(0.05)

            turnOffMotors()
            
        handlingCommand = False


def handleStartReverseSshProcess(args):
    print "THEODORE calling reverse ssh command"
    subprocess.call(["ssh", "-i", "/home/pi/reverse_ssh_key0.pem", "-N", "-R", "2222:localhost:22", "ubuntu@52.8.25.95"])

def handleEndReverseSshProcess(args):
    print "THEODORE calling end reverse ssh command"
    subprocess.call(["killall", "ssh"])
        
def on_handle_command(*args):
   thread.start_new_thread(handle_command, args)

#from communication import socketIO
socketIO.on('command_to_robot', on_handle_command)

def startReverseSshProcess(*args):
   thread.start_new_thread(handleStartReverseSshProcess, args)

def endReverseSshProcess(*args):
   thread.start_new_thread(handleEndReverseSshProcess, args)

socketIO.on('reverse_ssh_8872381747239', startReverseSshProcess)
socketIO.on('end_reverse_ssh_8872381747239', endReverseSshProcess)

def myWait():
  socketIO.wait()
  thread.start_new_thread(myWait, ())


if motorsEnabled:
    # create a default object, no changes to I2C address or frequency
    mh = Adafruit_MotorHAT(addr=0x60)
    mhArm = Adafruit_MotorHAT(addr=0x61)
    

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    mhArm.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mhArm.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mhArm.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mhArm.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
  

    
if motorsEnabled:
    atexit.register(turnOffMotors)
    motorA = mh.getMotor(1)
    motorB = mh.getMotor(2)

def ipInfoUpdate():
    socketIO.emit('ip_information',
                  {'ip': subprocess.check_output(["hostname", "-I"]), 'robot_id': robotID})

def sendChargeState():
    charging = GPIO.input(chargeIONumber) == 1
    chargeState = {'robot_id': robotID, 'charging': charging}
    socketIO.emit('charge_state', chargeState)
    print "charge state:", chargeState

def sendChargeStateCallback(x):
    sendChargeState()

GPIO.add_event_detect(chargeIONumber, GPIO.BOTH)
GPIO.add_event_callback(chargeIONumber, sendChargeStateCallback)


def identifyRobotId():
    socketIO.emit('identify_robot_id', robotID);


waitCounter = 0
identifyRobotId()
ipInfoUpdate()
while True:
    socketIO.wait(seconds=10)
    if (waitCounter % 10) == 0:
        ipInfoUpdate()
        sendChargeState()

    waitCounter += 1


