#!/usr/bin/python
# Geekworm UPS
# shutdown safely
# 2017-04-30
# add this to crontab to run every 3 minutes
# */3 * * * * /path/to/batteryShutdown.py

import struct
import smbus 
import sys
import os

bus     = smbus.SMBus ( 1 )

address = 0x36

def readVoltage ( bus, address = address ):
   read    = bus.read_word_data ( address, 2 )
   swapped = struct.unpack ( "<H", struct.pack ( ">H", read ) )[0]
   voltage = swapped * 78.125 /1000000
   return voltage

def readCapacity ( bus, address = address ):
   read     = bus.read_word_data ( address, 4 )
   swapped  = struct.unpack ( "<H", struct.pack ( ">H", read ) )[0]
   capacity = swapped/256
   return capacity

if readCapacity(bus) < 10:
        print "Battery below 20% - shutting down..."
        os.system('echo "battery low. shutting down." | espeak --stdout | aplay -D plughw:2,0')
        os.system('echo "battery low. shutting down." | espeak --stdout | aplay -D plughw:2,0')
        os.system('echo "battery low. shutting down." | espeak --stdout | aplay -D plughw:2,0')
        os.system('echo "battery low. shutting down." | espeak --stdout | aplay -D plughw:2,0')
        os.system('echo "battery low. shutting down." | espeak --stdout | aplay -D plughw:2,0')
        os.system('echo "battery low. shutting down." | espeak --stdout | aplay -D plughw:2,0')
        os.system('/sbin/poweroff')
