# ========== Base Imports ==========

import platform
import os
import uuid
import urllib2
import json
import traceback
import tempfile
import re
import getpass
import sys
import argparse
import random
import time
import atexit
import sys
import thread
import subprocess
import datetime
from socketIO_client import SocketIO, LoggingNamespace

# ========== Arguments ==========

parser = argparse.ArgumentParser(description='start robot control program')
parser.add_argument('robot_id', help='Robot ID')
parser.add_argument('--env', help="Environment for example dev or prod, prod is default", default='prod')
parser.add_argument('--type', help="serial or motor_hat or gopigo2 or gopigo3 or l298n or motozero or pololu", default='motor_hat')
parser.add_argument('--serial-device', help="serial device", default='/dev/ttyACM0')
parser.add_argument('--male', dest='male', action='store_true')
parser.add_argument('--female', dest='male', action='store_false')
parser.add_argument('--voice-number', type=int, default=1)
parser.add_argument('--led', help="Type of LED for example max7219", default=None)
parser.add_argument('--ledrotate', help="Rotates the LED matrix. Example: 180", default=None)
parser.add_argument('--tts-volume', type=int, default=80)
parser.add_argument('--secret-key', default=None)
parser.add_argument('--turn-delay', type=float, default=0.4)
parser.add_argument('--straight-delay', type=float, default=0.5)
parser.add_argument('--driving-speed', type=int, default=90)
parser.add_argument('--day-speed', type=int, default=255)
parser.add_argument('--night-speed', type=int, default=255)
parser.add_argument('--forward', default='[-1,1,-1,1]')
parser.add_argument('--left', default='[1,1,1,1]')
parser.add_argument('--festival-tts', dest='festival_tts', action='store_true')
parser.set_defaults(festival_tts=False)
parser.add_argument('--auto-wifi', dest='auto_wifi', action='store_true')
parser.set_defaults(auto_wifi=False)
parser.add_argument('--no-anon-tts', dest='anon_tts', action='store_false')
parser.set_defaults(anon_tts=True)
parser.add_argument('--filter-url-tts', dest='filter_url_tts', action='store_true')
parser.set_defaults(filter_url_tts=False)
parser.add_argument('--slow-for-low-battery', dest='slow_for_low_battery', action='store_true')
parser.set_defaults(slow_for_low_battery=False)
parser.add_argument('--reverse-ssh-key-file', default='/home/pi/reverse_ssh_key1.pem')
parser.add_argument('--reverse-ssh-host', default='ubuntu@52.52.204.174')
parser.add_argument('--claw', type=bool, default=False)
parser.add_argument('--chargepin', type=int, default=255)

commandArgs = parser.parse_args()
print commandArgs

# ========== Variables ==========

server = "runmyrobot.com"
tempDir = tempfile.gettempdir()
print "temporary directory:", tempDir
serialDevice = commandArgs.serial_device
robotID = commandArgs.robot_id


chargeCheckInterval = 5
chargeValue = 0.0
secondsToCharge = 60 * 60 * 3  # value in seconds
secondsToDischarge = 60 * 60 * 8 # value in seconds
chargeIONumber = commandArgs.chargepin

steeringSpeed = 90
steeringHoldingSpeed = 90
drivingSpeed = commandArgs.driving_speed

handlingCommand = False
turningSpeedActuallyUsed = 250
dayTimeDrivingSpeedActuallyUsed = commandArgs.day_speed
nightTimeDrivingSpeedActuallyUsed = commandArgs.night_speed

def times(lst, number):
    return [x*number for x in lst]

forward = json.loads(commandArgs.forward)
backward = times(forward, -1)
left = json.loads(commandArgs.left)
right = times(left, -1)
straightDelay = commandArgs.straight_delay 
turnDelay = commandArgs.turn_delay
l298n_sleeptime=0.2
l298n_rotatetimes=5
waitCounter = 0

mh = None

servoMin = [150, 150, 130]  # Min pulse length out of 4096
servoMax = [600, 600, 270]  # Max pulse length out of 4096
armServo = [300, 300, 300]

lastInternetStatus = False

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


# ========== Specific Imports and --type checking ==========

if commandArgs.type == 'none': # Type: None
    pass

elif commandArgs.type == 'serial': # Type: serial
    import serial

elif commandArgs.type == 'motor_hat': # Type: motor_hat
    global mh
    import RPi.GPIO as GPIO
    try:
        from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
        motorsEnabled = True
        mh = Adafruit_MotorHAT(addr=0x60)
    except ImportError:
        print "You need to install Adafruit_MotorHAT"
        print "Please install Adafruit_MotorHAT for python and restart this script."
        print "To install: cd /usr/local/src && sudo git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git"
        print "cd /usr/local/src/Adafruit-Motor-HAT-Python-Library && sudo python setup.py install"
        print "Running in test mode."
        print "Ctrl-C to quit"
        motorsEnabled = False

elif commandArgs.type == 'gopigo2': # Type: gopigo2
    import gopigo

elif commandArgs.type == 'gopigo3': # Type: gopigo3
    sys.path.append("/home/pi/Dexter/GoPiGo3/Software/Python")
    import easygopigo3
    easyGoPiGo3 = easygopigo3.EasyGoPiGo3()

elif commandArgs.type == 'l298n':
    import RPi.GPIO as GPIO
    try:
        import configparser
    except ImportError:
        print "You need to install configparser (sudo python -m pip install configparser)\n Ctrl-C to quit"
        while True:
            pass # Halt program    to avoid error down the line.

elif commandArgs.type == 'motozero':
    import RPi.GPIO as GPIO

elif commandArgs.type == 'pololu':
    try:
        from pololu_drv8835_rpi import motors, MAX_SPEED
    except ImportError:
        print "You need to install drv8835-motor-driver-rpi"
        print "Please install drv8835-motor-driver-rpi for python and restart this script."
        print "To install: cd /usr/local/src && sudo git clone https://github.com/pololu/drv8835-motor-driver-rpi"
        print "cd /usr/local/src/drv8835-motor-driver-rpi && sudo python setup.py install"
        print "Running in test mode."
        print "Ctrl-C to quit"

elif commandArgs.type == 'screencap':
    pass

elif commandArgs.type == 'adafruit_pwm':
    from Adafruit_PWM_Servo_Driver import PWM

elif commandArgs.type == 'owi_arm':
    import owi_arm

else:
    print "invalid --type in command line"
    exit(0)

if chargeIONumber != 255:
    import RPi.GPIO as GPIO

if commandArgs.led == 'max7219':
    import spidev

if commandArgs.claw == True:
    from Adafruit_PWM_Servo_Driver import PWM

# ========== Function Definitions ==========


def SetLED_On():
    if commandArgs.led == 'max7219':
        for i in range(len(columns)):
            spi.xfer([columns[i],LEDOn[i]])
def SetLED_Off():
     if commandArgs.led == 'max7219': 
        for i in range(len(columns)):
            spi.xfer([columns[i],LEDOff[i]])
def SetLED_E_Smiley():
    if commandArgs.led == 'max7219':
        for i in range(len(columns)):
            spi.xfer([columns[i],LEDEmoteSmile[i]]) 
def SetLED_E_Sad():
    if commandArgs.led == 'max7219':
        for i in range(len(columns)):
            spi.xfer([columns[i],LEDEmoteSad[i]])
def SetLED_E_Tongue():
    if commandArgs.led == 'max7219':
        for i in range(len(columns)):
            spi.xfer([columns[i],LEDEmoteTongue[i]])
def SetLED_E_Suprised():
    if commandArgs.led == 'max7219':
        for i in range(len(columns)):
            spi.xfer([columns[i],LEDEmoteSuprise[i]])
def SetLED_Low():
    if commandArgs.led == 'max7219':
        # brightness MIN
        spi.writebytes([0x0a])
        spi.writebytes([0x00])
def SetLED_Med():
    if commandArgs.led == 'max7219':
        #brightness MED
        spi.writebytes([0x0a])
        spi.writebytes([0x06])
def SetLED_Full():
    if commandArgs.led == 'max7219':
        # brightness MAX
        spi.writebytes([0x0a])
        spi.writebytes([0x0F])


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

def incrementArmServo(channel, amount):

    armServo[channel] += amount

    print "arm servo positions:", armServo

    if armServo[channel] > servoMax[channel]:
        armServo[channel] = servoMax[channel]
    if armServo[channel] < servoMin[channel]:
        armServo[channel] = servoMin[channel]
    pwm.setPWM(channel, 0, armServo[channel])


def isInternetConnected():
    try:
        urllib2.urlopen('http://www.google.com', timeout=1) # 1 second timeout is pretty low.
        return True
    except urllib2.URLError as err:
        return False


def configWifiLogin(secretKey):

    url = 'https://%s/get_wifi_login/%s' % (server, secretKey)
    try:
        print "GET", url
        response = urllib2.urlopen(url).read()
        responseJson = json.loads(response)
        print "get wifi login response:", response

        with open("/etc/wpa_supplicant/wpa_supplicant.conf", 'r') as originalWPAFile:
            originalWPAText = originalWPAFile.read()

        wpaText = WPA_FILE_TEMPLATE.format(name=responseJson['wifi_name'], password=responseJson['wifi_password'])


        print "original(" + originalWPAText + ")"
        print "new(" + wpaText + ")"
        
        if originalWPAText != wpaText:

            wpaFile = open("/etc/wpa_supplicant/wpa_supplicant.conf", 'w')        

            print wpaText
            print
            wpaFile.write(wpaText)
            wpaFile.close()

            say("Updated wifi settings. I will automatically reboot in 10 seconds.")
            time.sleep(8)
            say("Rebooting")
            time.sleep(2)
            os.system("reboot")

        
    except:
        print "exception while configuring setting wifi", url
        traceback.print_exc()

def handle_exclusive_control(args):
    if 'status' in args and 'robot_id' in args and args['robot_id'] == robotID:

        status = args['status']

    if status == 'start':
            print "start exclusive control"
    if status == 'end':
            print "end exclusive control"



def say(message):

    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()


    #os.system('"C:\Program Files\Jampal\ptts.vbs" -u ' + tempFilePath) Whaa?
    
    if commandArgs.festival_tts:
        # festival tts
        os.system('festival --tts < ' + tempFilePath)
    #os.system('espeak < /tmp/speech.txt')

    else:
        # espeak tts
        for hardwareNumber in (2, 0, 3, 1):
            if commandArgs.male:
                os.system('cat ' + tempFilePath + ' | espeak --stdout | aplay -D plughw:%d,0' % hardwareNumber)
            else:
                os.system('cat ' + tempFilePath + ' | espeak -ven-us+f%d -s170 --stdout | aplay -D plughw:%d,0' % (commandArgs.voice_number, hardwareNumber))

    os.remove(tempFilePath)

    
                
def handle_chat_message(args):

    print "chat message received:", args
    rawMessage = args['message']
    withoutName = rawMessage.split(']')[1:]
    message = "".join(withoutName)
    urlRegExp = "(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"
    if message[1] == ".":
       exit()
    elif commandArgs.anon_tts != True and args['anonymous'] == True:
       exit()   
    elif commandArgs.filter_url_tts == True and re.search(urlRegExp, message):
       exit()
    else:
          say(message)



def changeVolumeHighThenNormal():

    os.system("amixer -c 2 cset numid=3 %d%%" % 100)
    time.sleep(25)
    os.system("amixer -c 2 cset numid=3 %d%%" % commandArgs.tts_volume)

def handleLoudCommand():
    thread.start_new_thread(changeVolumeHighThenNormal, ())


def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    #mhArm.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


def moveAdafruitPWM(command):
    print "move adafruit pwm command", command
        
    if command == 'L':
        pwm.setPWM(1, 0, 300) # turn left
        pwm.setPWM(0, 0, 445) # drive forward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neutral
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'R':
        pwm.setPWM(1, 0, 500) # turn right
        pwm.setPWM(0, 0, 445) # drive forward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neutral
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'BL':
        pwm.setPWM(1, 0, 300) # turn left
        pwm.setPWM(0, 0, 270) # drive backward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neutral
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'BR':
        pwm.setPWM(1, 0, 500) # turn right
        pwm.setPWM(0, 0, 270) # drive backward
        time.sleep(0.5)
        pwm.setPWM(1, 0, 400) # turn neurtral
        pwm.setPWM(0, 0, 335) # drive neutral

        
    if command == 'F':
        pwm.setPWM(0, 0, 445) # drive forward
        time.sleep(0.3)
        pwm.setPWM(0, 0, 345) # drive slowly forward
        time.sleep(0.4)
        pwm.setPWM(0, 0, 335) # drive neutral
    if command == 'B':
        pwm.setPWM(0, 0, 270) # drive backward
        time.sleep(0.3)
        pwm.setPWM(0, 0, 325) # drive slowly backward
        time.sleep(0.4)
        pwm.setPWM(0, 0, 335) # drive neutral

    if command == 'S2INC': # neutral
        pwm.setPWM(2, 0, 300)

    if command == 'S2DEC':
        pwm.setPWM(2, 0, 400)

    if command == 'POS60':
        pwm.setPWM(2, 0, 490)        

    if command == 'NEG60':
        pwm.setPWM(2, 0, 100)                



        
    
def moveGoPiGo2(command):
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


def moveGoPiGo3(command):
    e = easyGoPiGo3
    if command == 'L':
        e.set_motor_dps(e.MOTOR_LEFT, -e.get_speed())
        e.set_motor_dps(e.MOTOR_RIGHT, e.get_speed())
        time.sleep(0.15)
        easyGoPiGo3.stop()
    if command == 'R':
        e.set_motor_dps(e.MOTOR_LEFT, e.get_speed())
        e.set_motor_dps(e.MOTOR_RIGHT, -e.get_speed())
        time.sleep(0.15)
        easyGoPiGo3.stop()
    if command == 'F':
        easyGoPiGo3.forward()
        time.sleep(0.35)
        easyGoPiGo3.stop()
    if command == 'B':
        easyGoPiGo3.backward()
        time.sleep(0.35)
        easyGoPiGo3.stop()

def runl298n(direction):
    if direction == 'F':
        GPIO.output(StepPinForward, GPIO.HIGH)
        time.sleep(l298n_sleeptime * l298n_rotatetimes)
        GPIO.output(StepPinForward, GPIO.LOW)
    if direction == 'B':
        GPIO.output(StepPinBackward, GPIO.HIGH)
        time.sleep(l298n_sleeptime * l298n_rotatetimes)
        GPIO.output(StepPinBackward, GPIO.LOW)
    if direction == 'L':
        GPIO.output(StepPinLeft, GPIO.HIGH)
        time.sleep(l298n_sleeptime)
        GPIO.output(StepPinLeft, GPIO.LOW)
    if direction == 'R':
        GPIO.output(StepPinRight, GPIO.HIGH)
        time.sleep(l298n_sleeptime)
        GPIO.output(StepPinRight, GPIO.LOW)

def runmotozero(direction):
    if direction == 'F':
        GPIO.output(Motor1B, GPIO.HIGH)
        GPIO.output(Motor1Enable,GPIO.HIGH)

        GPIO.output(Motor2B, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor3A, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor4B, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.LOW)
        GPIO.output(Motor3A, GPIO.LOW)
        GPIO.output(Motor4B, GPIO.LOW)
    if direction == 'B':
        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor3B, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor4A, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor3B, GPIO.LOW)
        GPIO.output(Motor4A, GPIO.LOW)

    if direction =='L':
        GPIO.output(Motor3B, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2B, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor4B, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor3B, GPIO.LOW)
        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.LOW)
        GPIO.output(Motor4B, GPIO.LOW)

    if direction == 'R':
        GPIO.output(Motor3A, GPIO.HIGH)
        GPIO.output(Motor3Enable, GPIO.HIGH)

        GPIO.output(Motor1B, GPIO.HIGH)
        GPIO.output(Motor1Enable, GPIO.HIGH)

        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2Enable, GPIO.HIGH)

        GPIO.output(Motor4A, GPIO.HIGH)
        GPIO.output(Motor4Enable, GPIO.HIGH)

        time.sleep(0.3)

        GPIO.output(Motor3A, GPIO.LOW)
        GPIO.output(Motor1B, GPIO.LOW)
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor4A, GPIO.LOW)

def runPololu(direction):
    drivingSpeed = commandArgs.driving_speed
    if direction == 'F':
          motors.setSpeeds(drivingSpeed, drivingSpeed)
          time.sleep(0.3)
          motors.setSpeeds(0, 0)
    if direction == 'B':
          motors.setSpeeds(-drivingSpeed, -drivingSpeed)
          time.sleep(0.3)
          motors.setSpeeds(0, 0)
    if direction == 'L':
          motors.setSpeeds(-drivingSpeed, drivingSpeed)
          time.sleep(0.3)
          motors.setSpeeds(0, 0)
    if direction == 'R':
          motors.setSpeeds(drivingSpeed, -drivingSpeed)
          time.sleep(0.3)
          motors.setSpeeds(0, 0)


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

        if 'robot_id' in args and args['robot_id'] == robotID: print "received message:", args
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

            if command == 'LOUD':
                handleLoudCommand()

            
            if commandArgs.type == 'adafruit_pwm':
                moveAdafruitPWM(command)
            
            if commandArgs.type == 'gopigo2':
                moveGoPiGo2(command)

            if commandArgs.type == 'gopigo3':
                moveGoPiGo3(command)
                
            if commandArgs.type == 'owi_arm':
                owi_arm.handleOwiArm(command)

            
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
            if commandArgs.claw == True:
                if command == 'U':
                    incrementArmServo(1, 10)
                    time.sleep(0.05)
                if command == 'D':
                    incrementArmServo(1, -10)
                    time.sleep(0.05)
                if command == 'O':
                    incrementArmServo(2, -10)
                    time.sleep(0.05)
                if command == 'C':
                    incrementArmServo(2, 10)
                    time.sleep(0.05)


            if commandArgs.type == 'motor_hat':
                turnOffMotors()
            if commandArgs.type == 'l298n':
                runl298n(command)                                 
            #setMotorsToIdle()
            if commandArgs.type == 'motozero':
                runmotozero(command)
            if commandArgs.type == 'pololu':
                runPololu(command)
            
            if commandArgs.led == 'max7219':
                if command == 'LED_OFF':
                    SetLED_Off()
                if command == 'LED_FULL':
                    SetLED_On()
                    SetLED_Full()
                if command == 'LED_MED':
                    SetLED_On()
                    SetLED_Med()
                if command == 'LED_LOW':
                    SetLED_On()
                    SetLED_Low()
                if command == 'LED_E_SMILEY':
                    SetLED_On()
                    SetLED_E_Smiley()
                if command == 'LED_E_SAD':
                    SetLED_On()
                    SetLED_E_Sad()
                if command == 'LED_E_TONGUE':
                    SetLED_On()
                    SetLED_E_Tongue()
                if command == 'LED_E_SUPRISED':
                    SetLED_On()
                    SetLED_E_Suprised()
        handlingCommand = False

def handleStartReverseSshProcess(args):
    print "starting reverse ssh"
    socketIO.emit("reverse_ssh_info", "starting")

    returnCode = subprocess.call(["/usr/bin/ssh",
                                  "-X",
                                  "-i", commandArgs.reverse_ssh_key_file,
                                  "-N",
                                  "-R", "2222:localhost:22",
                                  commandArgs.reverse_ssh_host])

    socketIO.emit("reverse_ssh_info", "return code: " + str(returnCode))
    print "reverse ssh process has exited with code", str(returnCode)

    
def handleEndReverseSshProcess(args):
    print "handling end reverse ssh process"
    resultCode = subprocess.call(["killall", "ssh"])
    print "result code of killall ssh:", resultCode

def startReverseSshProcess(*args):
   thread.start_new_thread(handleStartReverseSshProcess, args)

def endReverseSshProcess(*args):
   thread.start_new_thread(handleEndReverseSshProcess, args)

def on_handle_command(*args):
   thread.start_new_thread(handle_command, args)

def on_handle_exclusive_control(*args):
   thread.start_new_thread(handle_exclusive_control, args)

def on_handle_chat_message(*args):
   thread.start_new_thread(handle_chat_message, args)

def ipInfoUpdate():
    socketIO.emit('ip_information',
                  {'ip': subprocess.check_output(["hostname", "-I"]), 'robot_id': robotID})


# true if it's on the charger and it needs to be charging
def isCharging():
    print "is charging current value", chargeValue
    if 'GPIO' in sys.modules: # if we have the module to read the hardware
        if chargeValue < 99: # if it's not full charged already
            print "charge value is low"
            return GPIO.input(chargeIONumber) == 1 # return whether it's connected to the dock

    return False

        
    
def sendChargeState():
    charging = isCharging()
    chargeState = {'robot_id': robotID, 'charging': charging}
    socketIO.emit('charge_state', chargeState)
    print "charge state:", chargeState

def sendChargeStateEvent(x):
    sendChargeState()


def identifyRobotId():
    socketIO.emit('identify_robot_id', robotID);



def setSpeedBasedOnCharge():
    global dayTimeDrivingSpeedActuallyUsed
    global nightTimeDrivingSpeedActuallyUsed
    if chargeValue < 30:
        multiples = [0.2, 1.0]
        multiple = random.choice(multiples)
        dayTimeDrivingSpeedActuallyUsed = int(float(commandArgs.day_speed) * multiple)
        nightTimeDrivingSpeedActuallyUsed = int(float(commandArgs.night_speed) * multiple)
    else:
        dayTimeDrivingSpeedActuallyUsed = commandArgs.day_speed
        nightTimeDrivingSpeedActuallyUsed = commandArgs.night_speed
    

def updateChargeApproximation():

    global chargeValue
    
    username = getpass.getuser()
    path = "/home/pi/charge_state_%s.txt" % username

    # read charge value
    # assume it is zero if no file exists
    if os.path.isfile(path):
        file = open(path, 'r')
        try:
            chargeValue = float(file.read())
            print "error reading float from file", path
        except:
            chargeValue = 0
        file.close()
    else:
        print "setting charge value to zero"
        chargeValue = 0

    chargePerSecond = 1.0 / secondsToCharge
    dischargePerSecond = 1.0 / secondsToDischarge
    
    if GPIO.input(chargeIONumber) == 1:
        chargeValue += 100.0 * chargePerSecond * chargeCheckInterval
    else:
        chargeValue -= 100.0 * dischargePerSecond * chargeCheckInterval

    if chargeValue > 100.0:
        chargeValue = 100.0
    if chargeValue < 0:
        chargeValue = 0.0
        
    # write new charge value
    file = open(path, 'w')
    file.write(str(chargeValue))
    file.close()        

    print "charge value updated to", chargeValue


# ========== Initializations ==========

os.system("sudo modprobe bcm2835_wdt") # Attempt to start watchdog timer.
os.system("sudo /usr/sbin/service watchdog start")

if commandArgs.tts_volume > 50: # Set tts volume to max if above 50?
    os.system("amixer set PCM -- -100")

# tested for USB audio device
os.system("amixer -c 2 cset numid=3 %d%%" % commandArgs.tts_volume)

if chargeIONumber != 255:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(chargeIONumber, GPIO.IN)

if commandArgs.type == 'motor_hat':
    GPIO.setmode(GPIO.BCM)
    if motorsEnabled:
        atexit.register(turnOffMotors)
        motorA = mh.getMotor(1)
        motorB = mh.getMotor(2)

elif commandArgs.type == 'l298n':
    mode=GPIO.getmode()
    print " mode ="+str(mode)
    GPIO.cleanup()
    #Change the GPIO Pins to your connected motors in gpio.conf
    #visit http://bit.ly/1S5nQ4y for reference
    gpio_config = configparser.ConfigParser()
    gpio_config.read('gpio.conf')
    if str(robotID) in gpio_config.sections():
        config_id = str(robotID)
    else:
        config_id = 'default'        
    StepPinForward = int(str(gpio_config[config_id]['StepPinForward']).split(',')[0]),int(str(gpio_config[config_id]['StepPinForward']).split(',')[1])
    StepPinBackward = int(str(gpio_config[config_id]['StepPinBackward']).split(',')[0]),int(str(gpio_config[config_id]['StepPinBackward']).split(',')[1])
    StepPinLeft = int(str(gpio_config[config_id]['StepPinLeft']).split(',')[0]),int(str(gpio_config[config_id]['StepPinLeft']).split(',')[1])
    StepPinRight = int(str(gpio_config[config_id]['StepPinRight']).split(',')[0]),int(str(gpio_config[config_id]['StepPinRight']).split(',')[1])
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(StepPinForward, GPIO.OUT)
    GPIO.setup(StepPinBackward, GPIO.OUT)
    GPIO.setup(StepPinLeft, GPIO.OUT)
    GPIO.setup(StepPinRight, GPIO.OUT)

elif commandArgs.type == 'motozero':
    GPIO.setmode(GPIO.BCM)

    # Motor1 is back left
    # Motor1A is reverse
    # Motor1B is forward
    Motor1A = 24
    Motor1B = 27
    Motor1Enable = 5

    # Motor2 is back right
    # Motor2A is reverse
    # Motor2B is forward
    Motor2A = 6
    Motor2B = 22
    Motor2Enable = 17

    # Motor3 is ?
    # Motor3A is reverse
    # Motor3B is forward
    Motor3A = 23
    Motor3B = 16
    Motor3Enable = 12

    # Motor4 is ?
    # Motor4A is reverse
    # Motor4B is forward
    Motor4A = 13
    Motor4B = 18
    Motor4Enable = 25

    GPIO.setup(Motor1A,GPIO.OUT)
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.setup(Motor1Enable,GPIO.OUT)

    GPIO.setup(Motor2A,GPIO.OUT)
    GPIO.setup(Motor2B,GPIO.OUT)
    GPIO.setup(Motor2Enable,GPIO.OUT) 

    GPIO.setup(Motor3A,GPIO.OUT)
    GPIO.setup(Motor3B,GPIO.OUT)
    GPIO.setup(Motor3Enable,GPIO.OUT)

    GPIO.setup(Motor4A,GPIO.OUT)
    GPIO.setup(Motor4B,GPIO.OUT)
    GPIO.setup(Motor4Enable,GPIO.OUT)
    
elif commandArgs.type == 'serial':
    # initialize serial connection
    serialBaud = 9600
    print "baud:", serialBaud
    #ser = serial.Serial('/dev/tty.usbmodem12341', 19200, timeout=1)  # open serial
    ser = serial.Serial(serialDevice, serialBaud, timeout=1)  # open serial
    
if commandArgs.led == 'max7219':
    spi = spidev.SpiDev()
    spi.open(0,0)
    #VCC -> RPi Pin 2
    #GND -> RPi Pin 6
    #DIN -> RPi Pin 19
    #CLK -> RPi Pin 23
    #CS -> RPi Pin 24
    
    # decoding:BCD
    spi.writebytes([0x09])
    spi.writebytes([0x00])
    # Start with low brightness
    spi.writebytes([0x0a])
    spi.writebytes([0x03])
    # scanlimit; 8 LEDs
    spi.writebytes([0x0b])
    spi.writebytes([0x07])
    # Enter normal power-mode
    spi.writebytes([0x0c])
    spi.writebytes([0x01])
    # Activate display
    spi.writebytes([0x0f])
    spi.writebytes([0x00])
    columns = [0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8]
    LEDOn = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF] 
    LEDOff = [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0]
    LEDEmoteSmile = [0x0,0x0,0x24,0x0,0x42,0x3C,0x0,0x0]
    LEDEmoteSad = [0x0,0x0,0x24,0x0,0x0,0x3C,0x42,0x0]
    LEDEmoteTongue = [0x0,0x0,0x24,0x0,0x42,0x3C,0xC,0x0]
    LEDEmoteSuprise = [0x0,0x0,0x24,0x0,0x18,0x24,0x24,0x18]
    if commandArgs.ledrotate == '180':
        LEDEmoteSmile = LEDEmoteSmile[::-1]
        LEDEmoteSad = LEDEmoteSad[::-1]
        LEDEmoteTongue = LEDEmoteTongue[::-1]
        LEDEmoteSuprise = LEDEmoteSuprise[::-1]
    
    SetLED_Off()


# Initialise the i2c PWM device
if commandArgs.claw == True:
    pwm = PWM(0x42)
elif commandArgs.type == 'adafruit_pwm':
    pwm = PWM(0x40)

if commandArgs.claw == True or commandArgs.type == 'adafruit_pwm':
    pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

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


# ========== Connection ==========

print 'using socket io to connect to', server
socketIO = SocketIO(server, port, LoggingNamespace)
print 'finished using socket io to connect to', server
   
#from communication import socketIO
socketIO.on('command_to_robot', on_handle_command)
socketIO.on('exclusive_control', on_handle_exclusive_control)
socketIO.on('chat_message_with_name', on_handle_chat_message)

socketIO.on('reverse_ssh_8872381747239', startReverseSshProcess)
socketIO.on('end_reverse_ssh_8872381747239', endReverseSshProcess)

identifyRobotId()

if platform.system() == 'Darwin':
    pass
elif platform.system() == 'Linux':
    ipInfoUpdate()


if chargeIONumber != 255: # this goes here to prevent premature charge state events.
    GPIO.add_event_detect(chargeIONumber, GPIO.BOTH)
    GPIO.add_event_callback(chargeIONumber, sendChargeStateEvent)


# ========== Looping events ==========

while True:
    socketIO.wait(seconds=1)

    if chargeIONumber != 255:
        if (waitCounter % chargeCheckInterval) == 0:
            if commandArgs.type == 'motor_hat':
                updateChargeApproximation()
                sendChargeState()
                if commandArgs.slow_for_low_battery:
                    setSpeedBasedOnCharge()

        if (waitCounter % 60) == 0:
            if commandArgs.slow_for_low_battery:
                if chargeValue < 30:
                    say("battery low, %d percent" % int(chargeValue))

                    
        if (waitCounter % 17) == 0:
            if not isCharging():
                if commandArgs.slow_for_low_battery:
                    if chargeValue <= 25:
                        say("need to charge")                
                
            
    if (waitCounter % 1000) == 0:
        
        internetStatus = isInternetConnected()
        if internetStatus != lastInternetStatus:
            if internetStatus:
                say("ok")
            else:
                say("missing internet connection")
        lastInternetStatus = internetStatus

        
    if (waitCounter % 10) == 0:
        if commandArgs.auto_wifi:
            if commandArgs.secret_key is not None:
                configWifiLogin(commandArgs.secret_key)

                
    if (waitCounter % 60) == 0:

        # tell the server what robot id is using this connection
        identifyRobotId()
        
        if platform.system() == 'Linux':
            ipInfoUpdate()


    waitCounter += 1


