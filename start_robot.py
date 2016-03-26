#!/usr/bin/python

import os
import subprocess
import argparse
from subprocess import Popen, PIPE
from time import sleep
import RPi.GPIO as GPIO
import serial

pin_mp = 7
pin_mwa = 11
pin_ar = 12
pin_awm = 13
pin_mr = 15
pin_po = 16
pin_prn = 18
pin_ledR = 22
pin_ledB = 24
pin_ledG = 26



#--------------------------------------

def po_turnOn():
	print "PO: TurnOn"
	sleep(1)
	GPIO.output(pin_po, False)
	sleep(1)
	GPIO.output(pin_po, True)

def led_read(): 
	print "LED: Read"
	print " ledB: ", GPIO.input(pin_ledB)
	print " ledR: ", GPIO.input(pin_ledR)
	print " ledG: ", GPIO.input(pin_ledG)

def debug_inputs():
	print "DEBUG: Inputs"
	print " Module Wakeup AP: ", GPIO.input(pin_mwa)
	print " Module Poweron: ", GPIO.input(pin_mp)
	print " Module Ready: ", GPIO.input(pin_mr)

#--------------------------------------

def turnOnSparqee():

    try:

            #SERIAL
            ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)

            GPIO.setmode(GPIO.BOARD)

            GPIO.setup(pin_mp,   GPIO.IN)
            GPIO.setup(pin_mwa,  GPIO.IN)
            GPIO.setup(pin_awm,  GPIO.OUT)
            GPIO.setup(pin_mr,   GPIO.IN)
            GPIO.setup(pin_ar,   GPIO.OUT)
            GPIO.setup(pin_po,   GPIO.OUT)
            GPIO.setup(pin_prn,  GPIO.OUT)
            GPIO.setup(pin_ledB, GPIO.IN)
            GPIO.setup(pin_ledR, GPIO.IN)
            GPIO.setup(pin_ledG, GPIO.IN)

            GPIO.output(pin_awm, False)
            GPIO.output(pin_ar,  False)
            GPIO.output(pin_po,  True)
            GPIO.output(pin_prn, True)

    #--------------------------------------

            print "------------------"
            print "------------------"

            print "---> Main DEBUG INPUTS 1:"
            debug_inputs()
            print "------------------"

            print "---> Main PO TurnOn:"
            po_turnOn()
            sleep(5)

            print "---> Main DEBUG INPUTS 2:"
            debug_inputs()
            print "------------------"


            for i in range(3):
                    ser.write("ate1\r")
                    sleep(1)	
                    print ser.read(ser.inWaiting())
                    #ser.flush()
                    #ser.flushInput()
                    #ser.flushOutput()
                    sleep(1)
                    debug_inputs()
                    sleep(1)
                    ser.write("at+cpin?\r")
                    sleep(1)
                    print ser.read(ser.inWaiting())
                    #ser.flush()
                    #ser.flushInput()
                    #ser.flushOutput()
                    print "------------------"

    finally:
            GPIO.cleanup()







path = os.path.dirname(os.path.realpath(__file__))

FNULL = open(os.devnull, 'w')

parser = argparse.ArgumentParser()
parser.add_argument("robot_id")
parser.add_argument("camera_id")
args = parser.parse_args()
print args


print "path to runmyrobot:", path
os.chdir(path)


outputFile = FNULL




# turn on cellular modem
turnOnSparqee()

# connect to the internet via ppp
os.system('/home/pi/sakis3g connect --console --nostorage --pppd APN="Internetd.gdsp" BAUD=115200 CUSTOM_TTY="/dev/ttyAMA0" MODEM="OTHER" OTHER="CUSTOM_TTY" APN_USER="user" APN_PASS="pass" CUSTOM_APN="hello" --noprobe')


print "output file:", outputFile

outputFile = open("/tmp/robotoutputcontroller.txt", 'w')
cmd = ['nohup', 'python', 'controller.py', args.robot_id]
print cmd
subprocess.Popen(cmd, stdout=outputFile, stderr=subprocess.STDOUT)
#subprocess.call(cmd)

outputFile = open("/tmp/robotoutputsendvideo.txt", 'w')
cmd = ['nohup', 'python', 'send_video.py', args.camera_id, '0']
print cmd
subprocess.Popen(cmd, stdout=outputFile, stderr=subprocess.STDOUT)
#subprocess.call(cmd)



