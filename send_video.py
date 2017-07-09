import subprocess
import shlex
import re
import os
import time
import urllib2
import platform
import json
import sys
import base64
import random
import datetime
import traceback


import argparse

class DummyProcess:
    def poll(self):
        return None
    def __init__(self):
        self.pid = 123456789


parser = argparse.ArgumentParser(description='robot control')
parser.add_argument('camera_id')
parser.add_argument('video_device_number', default=0, type=int)
parser.add_argument('--kbps', default=350, type=int)
parser.add_argument('--brightness', type=int, help='camera brightness')
parser.add_argument('--contrast', type=int, help='camera contrast')
parser.add_argument('--saturation', type=int, help='camera saturation')
parser.add_argument('--rotate180', default=False, type=bool, help='rotate image 180 degrees')
parser.add_argument('--env', default="prod")
parser.add_argument('--screen-capture', dest='screen_capture', action='store_true') # tells windows to pull from different camera, this should just be replaced with a video input device option
parser.set_defaults(screen_capture=False)
parser.add_argument('--no-mic', dest='mic_enabled', action='store_false')
parser.set_defaults(mic_enabled=True)
parser.add_argument('--no-camera', dest='camera_enabled', action='store_false')
parser.set_defaults(camera_enabled=True)
parser.add_argument('--dry-run', dest='dry_run', action='store_true')
parser.add_argument('--mic-channels', type=int, help='microphone channels, typically 1 or 2', default=1)
parser.add_argument('--audio-input-device', default='Microphone (HD Webcam C270)') # currently, this option is only used for windows screen capture


#global numVideoRestarts
#numVideoRestarts = 0
#global numAudioRestarts
#numAudioRestarts = 0

args = parser.parse_args()

print "args", args


server = "runmyrobot.com"



from socketIO_client import SocketIO, LoggingNamespace

# enable raspicam driver in case a raspicam is being used
os.system("sudo modprobe bcm2835-v4l2")


if args.env == "dev":
    print "using dev port 8122"
    port = 8122
elif args.env == "prod":
    print "using prod port 8022"
    port = 8022
else:
    print "invalid environment"
    sys.exit(0)

    
print "initializing socket io"
print "server:", server
print "port:", port
socketIO = SocketIO(server, port, LoggingNamespace)
print "finished initializing socket io"

#ffmpeg -f qtkit -i 0 -f mpeg1video -b 400k -r 30 -s 320x240 http://52.8.81.124:8082/hello/320/240/




    

def getVideoPort():


    url = 'http://%s/get_video_port/%s' % (server, args.camera_id)


    for retryNumber in range(2000):
        try:
            print "GET", url
            response = urllib2.urlopen(url).read()
            break
        except:
            print "could not open url ", url
            time.sleep(2)

    return json.loads(response)['mpeg_stream_port']

def getAudioPort():


    url = 'http://%s/get_audio_port/%s' % (server, args.camera_id)


    for retryNumber in range(2000):
        try:
            print "GET", url
            response = urllib2.urlopen(url).read()
            break
        except:
            print "could not open url ", url
            time.sleep(2)

    return json.loads(response)['audio_stream_port']



def randomSleep():
    """A short wait is good for quick recovery, but sometimes a longer delay is needed or it will just keep trying and failing short intervals, like because the system thinks the port is still in use and every retry makes the system think it's still in use. So, this has a high likelihood of picking a short interval, but will pick a long one sometimes."""

    timeToWait = random.choice((0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 5))
    print "sleeping", timeToWait
    time.sleep(timeToWait)
                   


def startVideoCaptureLinux():

    videoPort = getVideoPort()

    # set brightness, contrast, saturation
    if (args.brightness is not None) or (args.contrast is not None) or (args.saturation is not None):
        print "adjusting camera settings"
        os.system("v4l2-ctl -c brightness={brightness} -c contrast={contrast} -c saturation={saturation}".format(brightness=args.brightness,
                                  contrast=args.contrast,
                                  saturation=args.saturation))
    else:
        print "camera settings at default"

    
    videoCommandLine = '/usr/local/bin/ffmpeg -f v4l2 -framerate 25 -video_size 640x480 -i /dev/video%s %s -f mpegts -codec:v mpeg1video -s 640x480 -b:v %dk -bf 0 -muxdelay 0.001 http://%s:%s/hello/640/480/' % (args.video_device_number, rotationOption(), args.kbps, server, videoPort)
    print videoCommandLine
    return subprocess.Popen(shlex.split(videoCommandLine))
    

def startAudioCaptureLinux():

    audioPort = getAudioPort()
    
    audioCommandLine = '/usr/local/bin/ffmpeg -f alsa -ar 44100 -ac %d -i hw:1 -f mpegts -codec:a mp2 -b:a 32k -muxdelay 0.001 http://%s:%s/hello/640/480/' % (args.mic_channels, server, audioPort)
    print audioCommandLine
    return subprocess.Popen(shlex.split(audioCommandLine))



def rotationOption():

    if args.rotate180:
        return "-vf transpose=2,transpose=2"
    else:
        return ""

    

def main():

    if args.camera_enabled:
        if not args.dry_run:
            videoProcess = startVideoCaptureLinux()
        else:
            videoProcess = DummyProcess()

    if args.mic_enabled:
        if not args.dry_run:
            audioProcess = startAudioCaptureLinux()
        else:
            audioProcess = DummyProcess()


    numVideoRestarts = 0
    numAudioRestarts = 0

    count = 0

    
    # loop forever and monitor status of ffmpeg processes
    while True:


        print "------------------------------------------" + str(count) + "-----------------------------------------------------"
        
        time.sleep(1)


        # todo: note about the following ffmpeg_process_exists is not technically true, but need to update
        # server code to check for send_video_process_exists if you want to set it technically accurate
        # because the process doesn't always exist, like when the relay is not started yet.

        # send status to server
        socketIO.emit('send_video_status', {'send_video_process_exists': True,
                                            'ffmpeg_process_exists': True,
                                            'camera_id':args.camera_id})
       
        if count % 10 == 0:
            try:
                with os.fdopen(os.open('/tmp/send_video_summary.txt', os.O_WRONLY | os.O_CREAT, 0o777), 'w') as statusFile:
                    statusFile.write("time" + str(datetime.datetime.now()) + "\n")
                    statusFile.write("video process poll " + str(videoProcess.poll()) + " pid " + str(videoProcess.pid) + " restarts " + str(numVideoRestarts) + " \n")
                    statusFile.write("audio process poll " + str(audioProcess.poll()) + " pid " + str(audioProcess.pid) + " restarts " + str(numAudioRestarts) + " \n")
                print "status file written"
                sys.stdout.flush()
            except:
                print "status file could not be written"
                traceback.print_exc()
                sys.stdout.flush()
                
                
        
        
        
        if args.camera_enabled:
        
            print "video process poll", videoProcess.poll(), "pid", videoProcess.pid, "restarts", numVideoRestarts

            # restart video if needed
            if videoProcess.poll() != None:
                randomSleep()
                videoProcess = startVideoCaptureLinux()
                numVideoRestarts += 1
            
                
        if args.mic_enabled:

            print "audio process poll", audioProcess.poll(), "pid", audioProcess.pid, "restarts", numAudioRestarts

            # restart audio if needed
            if audioProcess.poll() != None:
                randomSleep()
                audioProcess = startAudioCaptureLinux()
                numAudioRestarts += 1
        
        count += 1

        
main()



