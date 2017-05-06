import platform
import serial
import os
import uuid
import urllib2
import json
import traceback



import argparse
parser = argparse.ArgumentParser(description='start robot control program')
parser.add_argument('robot_id', help='Robot ID')
parser.add_argument('--env', help="Environment for example dev or prod, prod is default", default='prod')
parser.add_argument('--type', help="serial or motor_hat or gopigo", default='motor_hat')
parser.add_argument('--serial-device', help="serial device", default='/dev/ttyACM0')
parser.add_argument('--male', dest='male', action='store_true')
parser.add_argument('--female', dest='male', action='store_false')
parser.add_argument('--voice-number', type=int, default=1)
parser.add_argument('--secret-key', default=None)


# set volume level

# tested for 3.5mm audio jack
#os.system("amixer set PCM -- -100")

# tested for USB audio device
#os.system("amixer cset numid=3 100%")
os.system("amixer -c 2 cset numid=3 80%")


commandArgs = parser.parse_args()
print commandArgs



server = "runmyrobot.com"
#server = "52.52.213.92"

if commandArgs.type == 'serial':
    pass
elif commandArgs.type == 'motor_hat':
    pass
elif commandArgs.type == 'gopigo':
    import gopigo
else:
    print "invalid --type in command line"
    exit(0)

#serialDevice = '/dev/tty.usbmodem12341'
#serialDevice = '/dev/ttyUSB0'

serialDevice = commandArgs.serial_device



if commandArgs.type == 'motor_hat':
    try:
        from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
        motorsEnabled = True
    except ImportError:
        print "You need to install Adafruit_MotorHAT"
        print "Please install Adafruit_MotorHAT for python and restart this script."
        print "Running in test mode."
        print "Ctrl-C to quit"
        motorsEnabled = False

if commandArgs.type == 'motor_hat':
    from Adafruit_PWM_Servo_Driver import PWM

import time
import atexit
import sys
import thread
import subprocess
if commandArgs.type == 'motor_hat':
    import RPi.GPIO as GPIO
import datetime
from socketIO_client import SocketIO, LoggingNamespace


chargeIONumber = 17

        
if commandArgs.type == 'motor_hat':
    GPIO.setmode(GPIO.BCM)
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
if commandArgs.type == 'motor_hat':
    pwm = PWM(0x42)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)
servoMin = [150, 150, 130]  # Min pulse length out of 4096
servoMax = [600, 600, 270]  # Max pulse length out of 4096
armServo = [300, 300, 300]

#def setMotorsToIdle():
#    s = 65
#    for i in range(1, 2):
#        mh.getMotor(i).setSpeed(s)
#        mh.getMotor(i).run(Adafruit_MotorHAT.FORWARD)




robotID = commandArgs.robot_id


if commandArgs.env == 'dev':
    print 'DEV MODE ***************'
    print "using dev port 8122"
    port = 8122
elif commandArgs.env == 'prod':
    print 'PROD MODE *************'
    print "using prod port 8022"
    port = 8022
else:
    print "invalid environment"
    sys.exit(0)


if commandArgs.type == 'serial':
    # initialize serial connection
    serialBaud = 9600
    print "baud:", serialBaud
    #ser = serial.Serial('/dev/tty.usbmodem12341', 19200, timeout=1)  # open serial
    ser = serial.Serial(serialDevice, serialBaud, timeout=1)  # open serial

    
    
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


if commandArgs.type == 'motor_hat':
    pwm.setPWMFreq(60)                        # Set frequency to 60 Hz


WPA_FILE_TEMPLATE = """ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=GB

network={{
            ssid=\"beepx\"
            psk=\"yellow123\"
            key_mgmt=WPA-PSK
    }}

network={{
            ssid=\"{name}\"
            psk=\"{password}\"
            key_mgmt=WPA-PSK
    }}
"""
    
    
def configWifiLogin(secretKey):

    url = 'http://%s/get_wifi_login/%s' % (server, secretKey)
    try:
        print "GET", url
        response = urllib2.urlopen(url).read()
        responseJson = json.loads(response)
        print "get wifi login response:", response


        wpaFile = open("/etc/wpa_supplicant/wpa_supplicant.conf", 'w')
        wpaText = WPA_FILE_TEMPLATE.format(name=responseJson['wifi_name'], password=responseJson['wifi_password'])
        print wpaText
        print
        wpaFile.write(wpaText)
        wpaFile.close()

        
    except:
        print "exception while configuring setting wifi", url
        traceback.print_exc()



    



def sendSerialCommand(command):


    print(ser.name)         # check which port was really used
    ser.nonblocking()

    # loop to collect input
    #s = "f"
    #print "string:", s
    print str(command.lower())
    ser.write(command.lower() + "\r\n")     # write a string
    #ser.write(s)
    ser.flush()

    #while ser.in_waiting > 0:
    #    print "read:", ser.read()

    #ser.close()







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
elif robotID == "12692512": # Pita 
    forward = (1, 1, 1, 1)
    backward = (-1,-1,-1,-1)
    left = (-1, 0, 0, 0)
    right = times(left, -1)
    straightDelay = 0.5
    turnDelay = 0.4
else: # default settings
    forward = (-1, 1, -1, 1)
    backward = times(forward, -1)
    left = (1, 1, 1, 1)
    right = times(left, -1)
    straightDelay = 0.5
    turnDelay = 0.4

    
def handle_exclusive_control(args):
        if 'status' in args and 'robot_id' in args and args['robot_id'] == robotID:

            status = args['status']

	    if status == 'start':
                print "start exclusive control"
	    if status == 'end':
                print "end exclusive control"


def handle_chat_message(args):

    print "chat message received:", args
    rawMessage = args['message']
    withoutName = rawMessage.split(']')[1:]
    message = "".join(withoutName)
    tempFilePath = os.path.join("/tmp", "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()
    #os.system('festival --tts < /tmp/speech.txt')
    #os.system('espeak < /tmp/speech.txt')

    for hardwareNumber in (2, 0, 1):
        if commandArgs.male:
            os.system('cat ' + tempFilePath + ' | espeak --stdout | aplay -D plughw:%d,0' % hardwareNumber)
        else:
            os.system('cat ' + tempFilePath + ' | espeak -ven-us+f%d -s170 --stdout | aplay -D plughw:%d,0' % (commandArgs.voice_number, hardwareNumber))

    os.remove(tempFilePath)


def moveGoPiGo(command):
    if command == 'L':
        gopigo.left_rot()
        time.sleep(0.15)
        gopigo.stop()
    if command == 'R':
        gopigo.right_rot()
        time.sleep(0.15)
        gopigo.stop()
    if command == 'F':
        gopigo.forward()
        time.sleep(0.35)
        gopigo.stop()
    if command == 'B':
        gopigo.backward()
        time.sleep(0.35)
        gopigo.stop()

    
                
def handle_command(args):
        now = datetime.datetime.now()
        now_time = now.time()
        # if it's late, make the robot slower
        if now_time >= datetime.time(21,30) or now_time <= datetime.time(9,30):
            #print "within the late time interval"
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

            print('got command', args)

            command = args['command']

            if commandArgs.type == 'gopigo':
                moveGoPiGo(command)
            
            if commandArgs.type == 'serial':
                sendSerialCommand(command)

            if commandArgs.type == 'motor_hat' and motorsEnabled:
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

            if commandArgs.type == 'motor_hat':
                turnOffMotors()

            #setMotorsToIdle()
            
        handlingCommand = False


def handleStartReverseSshProcess(args):
    subprocess.call(["ssh", "-i", "/home/pi/reverse_ssh_key0.pem", "-N", "-R", "2222:localhost:22", "ubuntu@52.8.25.95"])

def handleEndReverseSshProcess(args):
    subprocess.call(["killall", "ssh"])
        
def on_handle_command(*args):
   thread.start_new_thread(handle_command, args)

def on_handle_exclusive_control(*args):
   thread.start_new_thread(handle_exclusive_control, args)

def on_handle_chat_message(*args):
   thread.start_new_thread(handle_chat_message, args)

   
#from communication import socketIO
socketIO.on('command_to_robot', on_handle_command)
socketIO.on('exclusive_control', on_handle_exclusive_control)
socketIO.on('chat_message_with_name', on_handle_chat_message)


def startReverseSshProcess(*args):
   thread.start_new_thread(handleStartReverseSshProcess, args)

def endReverseSshProcess(*args):
   thread.start_new_thread(handleEndReverseSshProcess, args)

socketIO.on('reverse_ssh_8872381747239', startReverseSshProcess)
socketIO.on('end_reverse_ssh_8872381747239', endReverseSshProcess)

def myWait():
  socketIO.wait()
  thread.start_new_thread(myWait, ())


if commandArgs.type == 'motor_hat':
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
  

if commandArgs.type == 'motor_hat':
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

if commandArgs.type == 'motor_hat':
    GPIO.add_event_detect(chargeIONumber, GPIO.BOTH)
    GPIO.add_event_callback(chargeIONumber, sendChargeStateCallback)


def identifyRobotId():
    socketIO.emit('identify_robot_id', robotID);



#setMotorsToIdle()





waitCounter = 0


identifyRobotId()
if commandArgs.secret_key is not None:
    configWifiLogin(commandArgs.secret_key)


if platform.system() == 'Darwin':
    pass
    #ipInfoUpdate()
elif platform.system() == 'Linux':
    ipInfoUpdate()


while True:
    socketIO.wait(seconds=10)
    if (waitCounter % 10) == 0:
        if platform.system() == 'Linux':
            ipInfoUpdate()
        if commandArgs.type == 'motor_hat':
            sendChargeState()

    waitCounter += 1


