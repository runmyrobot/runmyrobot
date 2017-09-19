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





def setConfigEntry(category, key, value):

    if os.path.isfile(ConfigFilename):
        jsonFile = open(ConfigFilename)
        data = json.load(jsonFile)
        jsonFile.close()
    else:
        data = {}
    

    print data
    if category not in data:
        data[category] = {}
    data[category][key] = value
    print "-----------"
    print data



    with open(ConfigFilename, 'w') as outfile:
        json.dump(data, outfile)

        
def getConfigEntry(category, key):

    if os.path.isfile(ConfigFilename):
        jsonFile = open(ConfigFilename)
        data = json.load(jsonFile)
        return data[category][key]
        jsonFile.close()
    else:
        print "error, missing config file", ConfigFilename

        
def readConfigEntries(arguments):

    #todo: make this read all config entries

    arguments.mic_enabled = getConfigEntry('send_video', 'mic_enabled')

    
    
