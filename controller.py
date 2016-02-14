try:
    from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
except ImportError:
    print 'You need to install Adafruit_MotorHAT'
    print 'Please install Adafruit_MotorHAT for python and restart this script.'

import time
import atexit
import sys
import thread

from socketIO_client import SocketIO, LoggingNamespace
#print "press q to quit"
steeringSpeed = 200
steeringHoldingSpeed = 110
drivingSpeed = 255
handlingCommand = False


robot_id = raw_input("Please enter your Robot ID: ")


def handle_command(args):
        global handlingCommand
        if handlingCommand:
            return
        handlingCommand = True
        print('got something', args)
        ##if len(args) > 0 and 'command' in args[0]:
        ##    print args[0]['command']
        if 'command' in args and 'robot_id' in args and args['robot_id'] == robot_id:
            #command = args[0]['command']
            command = args['command']
            if command == 'F':
                driveMotor.setSpeed(drivingSpeed)
                driveMotor.run(Adafruit_MotorHAT.FORWARD);
            if command == 'B':
                driveMotor.setSpeed(drivingSpeed)
                driveMotor.run(Adafruit_MotorHAT.BACKWARD);
            time.sleep(0.3)
        handlingCommand = False

def on_handle_command(*args):
   thread.start_new_thread(handle_command, args)
   socketIO = SocketIO('52.8.81.124', 8022, LoggingNamespace)

socketIO.on('command_to_robot', on_handle_command)

def myWait():
  socketIO.wait()
  thread.start_new_thread(myWait, ())

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)
################################# DC motor test!
steeringMotor = mh.getMotor(3)
driveMotor = mh.getMotor(4)
# set the speed to start, from 0 (off) to 255 (max speed)
steeringMotor.setSpeed(150)
steeringMotor.run(Adafruit_MotorHAT.FORWARD);
# turn on motor
steeringMotor.run(Adafruit_MotorHAT.RELEASE);
while (True):
        time.sleep(0.1)

