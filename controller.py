import platform


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

    
from Adafruit_PWM_Servo_Driver import PWM
    
import time
import atexit
import sys
import thread
import subprocess
import time
import RPi.GPIO as GPIO
import datetime
from socketIO_client import SocketIO, LoggingNamespace


    
        

GPIO.setmode(GPIO.BCM)
chargeIONumber = 17
GPIO.setup(chargeIONumber, GPIO.IN)


steeringSpeed = 90
steeringHoldingSpeed = 90

global drivingSpeed


drivingSpeed = 90
handlingCommand = False




#turningSpeedActuallyUsed = 200
#drivingSpeedActuallyUsed = 200

# Marvin
turningSpeedActuallyUsed = 250
dayTimeDrivingSpeedActuallyUsed = 250
nightTimeDrivingSpeedActuallyUsed = 170







# Initialise the PWM device
pwm = PWM(0x42)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)
servoMin = [150, 150, 400]  # Min pulse length out of 4096
servoMax = [600, 600, 565]  # Max pulse length out of 4096
armServo = [300, 300, 300]

#def setMotorsToIdle():
#    s = 65
#    for i in range(1, 2):
#        mh.getMotor(i).setSpeed(s)
#        mh.getMotor(i).run(Adafruit_MotorHAT.FORWARD)



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


def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

  
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz


def incrementArmServo(channel, amount):

    armServo[channel] += amount

    print "arm servo positions:", armServo

    if armServo[channel] > servoMax[channel]:
        armServo[channel] = servoMax[channel]
    if armServo[channel] < servoMin[channel]:
        armServo[channel] = servoMin[channel]
    pwm.setPWM(channel, 0, armServo[channel])

        

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
    forward = (-1, 1, 1, -1)
    backward = times(forward, -1)
    left = (1, 1, 1, 1)
    right = times(left, -1)
    straightDelay = 1.6
    turnDelay = 0.4
elif robotID == "88359766": # Skippy_old
    forward = (1, 1, 1, -1)
    backward = times(forward, -1)
    left = (1, -1, 1, 1)
    right = times(left, -1)
    straightDelay = 1.6
    turnDelay = 0.8
elif robotID == "22027911": # Zip
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    left = (0, 1, 1, 0) # was 1,1,1,1
    right = (0, -1, -1, 0)
    straightDelay = 0.5
    turnDelay = 0.8
elif robotID == "78929358": # ZombieZip
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    left = (0, 1, 1, 0) # was 1,1,1,1
    right = (0, -1, -1, 0)
    straightDelay = 1.6
    turnDelay = 0.8
elif robotID == "52225122": # Pippy
    forward = (-1, 1, 1, -1)
    backward = times(forward, -1)
    left = (1, 1, 1, 1)
    right = times(left, -1)
    straightDelay = 0.5
    turnDelay = 0.8
elif robotID == "72378514": # Skippy
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    left = (1, 1, 1, 1)
    right = times(left, -1)
    straightDelay = 1.6
    turnDelay = 0.4
elif robotID == "19359999": # Mikey
    forward = (-1, 1, 1, -1)
    backward = times(forward, -1)
    left = (1, 1, 1, 1)
    right = times(left, -1)
    straightDelay = 0.5
    turnDelay = 0.4
elif robotID == "86583531": # Dilbert
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    left = (1, 1, 1, 1)
    right = times(left, -1)
    straightDelay = 1.6
    turnDelay = 0.4
elif robotID == "48853711": # Marvin
    forward = (1, -1, 1, -1)
    backward = times(forward, -1)
    left = (-1, -1, -1, -1)
    right = times(left, -1)
    straightDelay = 0.5
    turnDelay = 0.1
elif robotID == "11543083": # RedBird
    forward = (1, -1, 1, -1)
    backward = times(forward, -1)
    left = (-1, -1, -1, -1)
    right = times(left, -1)
    straightDelay = 1.6
    turnDelay = 0.4
else: # default settings
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    left = (1, 1, 1, 1)
    right = times(left, -1)
    straightDelay = 0.5
    turnDelay = 0.4

    
        
def handle_command(args):


        now = datetime.datetime.now()
        now_time = now.time()
        # if it's late, make the robot slower
        if now_time >= datetime.time(21,30) or now_time <= datetime.time(9,30):
            print "within the late time interval"
            drivingSpeedActuallyUsed = nightTimeDrivingSpeedActuallyUsed
        else:
            drivingSpeedActuallyUsed = dayTimeDrivingSpeedActuallyUsed
        

    
        global drivingSpeed
    
        global handlingCommand


        #print "received command:", args
        # Note: If you are adding features to your bot,
        # you can get direct access to incomming commands right here.

        

        if handlingCommand:
            return

        handlingCommand = True

        #if 'robot_id' in args:
        #    print "args robot id:", args['robot_id']

        #if 'command' in args:
        #    print "args command:", args['command']


            
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
                    #mhArm.getMotor(1).setSpeed(127)
                    #mhArm.getMotor(1).run(Adafruit_MotorHAT.BACKWARD)
                    incrementArmServo(1, 10)
                    time.sleep(0.05)
                if command == 'D':
                    #mhArm.getMotor(1).setSpeed(127)
                    #mhArm.getMotor(1).run(Adafruit_MotorHAT.FORWARD)
                    incrementArmServo(1, -10)
                    time.sleep(0.05)
                if command == 'O':
                    #mhArm.getMotor(2).setSpeed(127)
                    #mhArm.getMotor(2).run(Adafruit_MotorHAT.BACKWARD)
                    incrementArmServo(2, -10)
                    time.sleep(0.05)
                if command == 'C':
                    #mhArm.getMotor(2).setSpeed(127)
                    #mhArm.getMotor(2).run(Adafruit_MotorHAT.FORWARD)           
                    incrementArmServo(2, 10)
                    time.sleep(0.05)

            turnOffMotors()
            #setMotorsToIdle()
            
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
    #mhArm = Adafruit_MotorHAT(addr=0x61)
    

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
  

    
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



#setMotorsToIdle()
    
waitCounter = 0
identifyRobotId()
if platform.system() == 'Darwin':
    ipInfoUpdate()
elif platform.system() == 'Linux':
    ipInfoUpdate()
while True:
    socketIO.wait(seconds=10)
    if (waitCounter % 10) == 0:
        ipInfoUpdate()
        sendChargeState()

    waitCounter += 1


