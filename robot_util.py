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



