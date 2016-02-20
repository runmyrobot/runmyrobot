import subprocess
import re
import os
import time
import urllib2
import platform
import json
import sys


#ffmpeg -f qtkit -i 0 -f mpeg1video -b 400k -r 30 -s 320x240 http://52.8.81.124:8082/hello/320/240/



def getVideoPort():

    if len(sys.argv) > 1:
        cameraIDAnswer = sys.argv[1]
    else:
        cameraIDAnswer = raw_input("Enter the Camera ID for your robot, you can get it from the runmyrobot.com website: ")

    url = 'http://runmyrobot.com/get_video_port/%s' % cameraIDAnswer
    print "GET", url
    response = urllib2.urlopen(url).read()

    return json.loads(response)['mpeg_stream_port']




def handleDarwin(deviceNumber, videoPort):

    p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    print err

    deviceAnswer = raw_input("Enter the number of the camera device for your robot from the list above: ")
    commandLine = 'ffmpeg -f qtkit -i %s -f mpeg1video -b 400k -r 30 -s 320x240 http://runmyrobot.com:%s/hello/320/240/' % (deviceAnswer, videoPort)
    
    while(True):
        print commandLine
        os.system(commandLine)
        print "Press Ctrl-C to quit"
        time.sleep(3)
        print "Retrying"
    
    print commandLine



def handleLinux(deviceNumber, videoPort):

    #p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #out, err = p.communicate()
    #print err


    if deviceNumber is None:
        deviceAnswer = raw_input("Enter the number of the camera device for your robot: ")
    else:
        deviceAnswer = str(deviceNumber)

        
    commandLine = 'ffmpeg -s 320x240 -f video4linux2 -i /dev/video%s -f mpeg1video -b 1k -r 20 http://runmyrobot.com:%s/hello/320/240/' % (deviceAnswer, videoPort)

    while(True):
        print commandLine
        os.system(commandLine)
        print "Press Ctrl-C to quit"
        time.sleep(3)
        print "Retrying"
    
    print commandLine



def handleWindows(deviceNumber, videoPort):

    p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    
    out, err = p.communicate()
    
    lines = err.split('\n')
    
    count = 0
    
    devices = []
    
    for line in lines:
    
        #if "]  \"" in line:
        #    print "line:", line
    
        m = re.search('.*\\"(.*)\\"', line)
        if m != None:
            #print line
            if m.group(1)[0:1] != '@':
                print count, m.group(1)
                devices.append(m.group(1))
                count += 1
    
    
    deviceAnswer = raw_input("Enter the number of the camera device for your robot from the list above: ")
    device = devices[int(deviceAnswer)]
    commandLine = 'ffmpeg -s 320x240 -f dshow -i video="%s" -f mpeg1video -b 400k -r 20 http://runmyrobot.com:%s/hello/320/240/' % (device, videoPort)
    
    while(True):
        os.system(commandLine)
        print "Press Ctrl-C to quit"
        time.sleep(3)
        print "Retrying"
    
    print commandLine
    

videoPort = getVideoPort()
print "video port:", videoPort

if len(argv) >= 3:
    deviceNumber = argv[2]
else:
    deviceNumber = None

if platform.system() == 'Darwin':
    handleDarwin(deviceNumber, videoPort)
elif platform.system() == 'Linux':
    handleLinux(deviceNumber, videoPort)
elif platform.system() == 'Windows':
    handleWindows(devideNumber, videoPort)
else:
    print "unknown platform", platform.system()




