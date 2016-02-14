import subprocess
import re
import os
import time
import urllib2


p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()

lines = err.split('\n')

count = 0

devices = []

cameraIDAnswer = raw_input("Enter the Camera ID for your robot, you can get it from the runmyrobot.com website: ")

url = 'http://runmyrobot.com:3100/init_video_port/%s' % cameraIDAnswer
print "GET", url

response = urllib2.urlopen(url).read()
print response



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
commandLine = 'ffmpeg -s 320x240 -f dshow -i video="%s" -f mpeg1video -b 400k -r 20 http://runmyrobot.com:8082/hello/320/240/' % device

while(True):
    os.system(commandLine)
    print "Press Ctrl-C to quit"
    time.sleep(3)
    print "Retrying"

print commandLine






