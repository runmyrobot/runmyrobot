import os
import time
import traceback
import urllib2
import getpass
import json



ConfigFilename = "/home/pi/config_" + getpass.getuser() + ".json"


def getWithRetry(url):

    for retryNumber in range(2000):
        try:
            print "GET", url
            response = urllib2.urlopen(url).read()
            break
        except:
            print "could not open url", url
            traceback.print_exc()
            time.sleep(2)

    return response



def sendSerialCommand(ser, command):


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


