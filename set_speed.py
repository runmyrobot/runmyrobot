from time import sleep
import serial


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


po_turnOn()

#SERIAL
ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, timeout=1)
print "ser:", ser

# set UART-to-modem communication speed
print "setting communication speed"
ser.write("at+zbitrate=460800\r")
sleep(1)
print ser.read(ser.inWaiting())
sleep(1)
ser.close()
sleep(1)
print "finished setting communication speed"


