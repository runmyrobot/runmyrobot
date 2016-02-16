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

steeringSpeed = 200
steeringHoldingSpeed = 110
drivingSpeed = 255
handlingCommand = False


if len(sys.argv) >= 2:
    robot_id = sys.argv[1]
else:
    robot_id = raw_input("Please enter your Robot ID: ")

if len(sys.argv) >= 3:
    port = 8122
    print "using port 8122"
else:
    port = 8022


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
                    motorA.run(Adafruit_MotorHAT.FORWARD);
                    motorB.run(Adafruit_MotorHAT.FORWARD);
                if command == 'B':
                    motorA.run(Adafruit_MotorHAT.BACKWARD);
                    motorB.run(Adafruit_MotorHAT.BACKWARD);
                if command == 'L':
                    motorA.run(Adafruit_MotorHAT.FORWARD);
                    motorB.run(Adafruit_MotorHAT.BACKWARD);
                if command == 'R':
                    motorA.run(Adafruit_MotorHAT.BACKWARD);
                    motorB.run(Adafruit_MotorHAT.FORWARD);

                    
            time.sleep(0.3)

            turnOffMotors()
            
        handlingCommand = False



        
def on_handle_command(*args):
   thread.start_new_thread(handle_command, args)

socketIO = SocketIO('runmyrobot.com', port, LoggingNamespace)
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
