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


import argparse

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

parser.add_argument('--no-mic', dest='mic', action='store_false')
parser.set_defaults(mic=True)

parser.add_argument('--mic-channels', type=int, help='microphone channels, typically 1 or 2', default=1)

parser.add_argument('--audio-input-device', default='Microphone (HD Webcam C270)') # currently, this option is only used for windows screen capture


args = parser.parse_args()

print "args", args


server = "runmyrobot.com"
#server = "52.52.213.92"


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


def onHandleCameraCommand(*args):
    #thread.start_new_thread(handle_command, args)
    print args


socketIO.on('command_to_camera', onHandleCameraCommand)


def onHandleTakeSnapshotCommand(*args):
    print "taking snapshot"
    inputDeviceID = streamProcessDict['device_answer']
    snapShot(platform.system(), inputDeviceID)
    with open ("snapshot.jpg", 'rb') as f:
        data = f.read()
    print "emit"
    
    socketIO.emit('snapshot', {'image':base64.b64encode(data)})

socketIO.on('take_snapshot_command', onHandleTakeSnapshotCommand)


def randomSleep():
    """A short wait is good for quick recovery, but sometimes a longer delay is needed or it will just keep trying and failing short intervals, like because the system thinks the port is still in use and every retry makes the system think it's still in use. So, this has a high likelihood of picking a short interval, but will pick a long one sometimes."""

    timeToWait = random.choice((0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 5))
    print "sleeping", timeToWait
    time.sleep(timeToWait)

    

def getVideoPort():


    url = 'http://%s/get_video_port/%s' % (server, cameraIDAnswer)


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


    url = 'http://%s/get_audio_port/%s' % (server, cameraIDAnswer)


    for retryNumber in range(2000):
        try:
            print "GET", url
            response = urllib2.urlopen(url).read()
            break
        except:
            print "could not open url ", url
            time.sleep(2)

    return json.loads(response)['audio_stream_port']



def runFfmpeg(commandLine):

    print commandLine
    ffmpegProcess = subprocess.Popen(shlex.split(commandLine))
    print "command started"

    return ffmpegProcess
    


def handleDarwin(deviceNumber, videoPort, audioPort):

    
    p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    print err

    deviceAnswer = raw_input("Enter the number of the camera device for your robot from the list above: ")
    commandLine = 'ffmpeg -f qtkit -i %s -f mpeg1video -b 400k -r 30 -s 320x240 http://%s:%s/hello/320/240/' % (deviceAnswer, server, videoPort)
    
    process = runFfmpeg(commandLine)

    return {'process': process, 'device_answer': deviceAnswer}


def handleLinux(deviceNumber, videoPort, audioPort):

    print "sleeping to give the camera time to start working"
    randomSleep()
    print "finished sleeping"

    
    #p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #out, err = p.communicate()
    #print err

    if (args.brightness is not None) or (args.contrast is not None) or (args.saturation is not None):
        print "adjusting camera settings"
        os.system("v4l2-ctl -c brightness={brightness} -c contrast={contrast} -c saturation={saturation}".format(brightness=args.brightness,
                                  contrast=args.contrast,
                                  saturation=args.saturation))
    else:
        print "camera settings at default"


    if deviceNumber is None:
        deviceAnswer = raw_input("Enter the number of the camera device for your robot: ")
    else:
        deviceAnswer = str(deviceNumber)

        
    #commandLine = '/usr/local/bin/ffmpeg -s 320x240 -f video4linux2 -i /dev/video%s -f mpeg1video -b 1k -r 20 http://runmyrobot.com:%s/hello/320/240/' % (deviceAnswer, videoPort)
    #commandLine = '/usr/local/bin/ffmpeg -s 640x480 -f video4linux2 -i /dev/video%s -f mpeg1video -b 150k -r 20 http://%s:%s/hello/640/480/' % (deviceAnswer, server, videoPort)
    # For new JSMpeg
    #commandLine = '/usr/local/bin/ffmpeg -f v4l2 -framerate 25 -video_size 640x480 -i /dev/video%s -f mpegts -codec:v mpeg1video -s 640x480 -b:v 250k -bf 0 http://%s:%s/hello/640/480/' % (deviceAnswer, server, videoPort) # ClawDaddy
    #commandLine = '/usr/local/bin/ffmpeg -s 1280x720 -f video4linux2 -i /dev/video%s -f mpeg1video -b 1k -r 20 http://runmyrobot.com:%s/hello/1280/720/' % (deviceAnswer, videoPort)


    if args.rotate180:
        rotationOption = "-vf transpose=2,transpose=2"
    else:
        rotationOption = ""

    # video with audio
    videoCommandLine = '/usr/local/bin/ffmpeg -f v4l2 -framerate 25 -video_size 640x480 -i /dev/video%s %s -f mpegts -codec:v mpeg1video -s 640x480 -b:v %dk -bf 0 -muxdelay 0.001 http://%s:%s/hello/640/480/' % (deviceAnswer, rotationOption, args.kbps, server, videoPort)
    audioCommandLine = '/usr/local/bin/ffmpeg -f alsa -ar 44100 -ac %d -i hw:1 -f mpegts -codec:a mp2 -b:a 32k -muxdelay 0.001 http://%s:%s/hello/640/480/' % (args.mic_channels, server, audioPort)

    print videoCommandLine
    print audioCommandLine
    
    videoProcess = runFfmpeg(videoCommandLine)
    if args.mic:
        audioProcess = runFfmpeg(audioCommandLine)
    else:
        audioProcess = videoProcess # this is a hack to prevent errors, should just be None value

    return {'video_process': videoProcess, 'audio_process': audioProcess, 'device_answer': deviceAnswer}



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
    

    if deviceNumber is None:
        deviceAnswer = raw_input("Enter the number of the camera device for your robot from the list above: ")
    else:
        deviceAnswer = str(deviceNumber)

    device = devices[int(deviceAnswer)]
    commandLine = 'ffmpeg -s 640x480 -f dshow -i video="%s" -f mpegts -codec:v mpeg1video -b 200k -r 20 http://%s:%s/hello/640/480/' % (device, server, videoPort)
    

    process = runFfmpeg(commandLine)

    return {'process': process, 'device_answer': device}
    

    
def handleWindowsScreenCapture(deviceNumber, videoPort, audioPort):

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
    

    if deviceNumber is None:
        deviceAnswer = raw_input("Enter the number of the camera device for your robot from the list above: ")
    else:
        deviceAnswer = str(deviceNumber)

        
        
    device = devices[int(deviceAnswer)]

    #commandLine = 'ffmpeg -f dshow -i video="screen-capture-recorder" -vf "scale=640:480" -f mpeg1video -b 50k -r 20 http://%s:%s/hello/640/480/' % (server, videoPort)

    videoCommandLine = 'ffmpeg -f dshow -i video="screen-capture-recorder" -framerate 25 -video_size 640x480 -f mpegts -codec:v mpeg1video -s 640x480 -b:v %dk -bf 0 -muxdelay 0.001 http://%s:%s/hello/640/480/' % (args.kbps, server, videoPort)
    audioCommandLine = 'ffmpeg -f dshow -ar 44100 -ac 1 -i audio="%s" -f mpegts -codec:a mp2 -b:a 32k -muxdelay 0.001 http://%s:%s/hello/640/480/' % (args.audio_input_device, server, audioPort)
    
    print "video command line:", videoCommandLine
    print "audio command line:", audioCommandLine
    
    videoProcess = runFfmpeg(videoCommandLine)
    audioProcess = runFfmpeg(audioCommandLine)
    
    # todo: need to have an audio process not just another video process
    return {'video_process': videoProcess, 'audio_process': audioProcess, 'device_answer': device}
    



def snapShot(operatingSystem, inputDeviceID, filename="snapshot.jpg"):    

    try:
        os.remove('snapshot.jpg')
    except:
        print "did not remove file"

    commandLineDict = {
        'Darwin': 'ffmpeg -y -f qtkit -i %s -vframes 1 %s' % (inputDeviceID, filename),
        'Linux': '/usr/local/bin/ffmpeg -y -f video4linux2 -i /dev/video%s -vframes 1 -q:v 1000 -vf scale=320:240 %s' % (inputDeviceID, filename),
        'Windows': 'ffmpeg -y -s 320x240 -f dshow -i video="%s" -vframes 1 %s' % (inputDeviceID, filename)}

    print commandLineDict[operatingSystem]
    os.system(commandLineDict[operatingSystem])



def startVideoCapture():

    videoPort = getVideoPort()
    audioPort = getAudioPort()
    print "video port:", videoPort
    print "audio port:", audioPort

    #if len(sys.argv) >= 3:
    #    deviceNumber = sys.argv[2]
    #else:
    #    deviceNumber = None
    deviceNumber = args.video_device_number

    result = None
    if platform.system() == 'Darwin':
        result = handleDarwin(deviceNumber, videoPort, audioPort)
    elif platform.system() == 'Linux':
        result = handleLinux(deviceNumber, videoPort, audioPort)
    elif platform.system() == 'Windows':
        if args.screen_capture:
            result = handleWindowsScreenCapture(deviceNumber, videoPort, audioPort)
        else:
            result = handleWindows(deviceNumber, videoPort, audioPort)
    else:
        print "unknown platform", platform.system()

    return result


def timeInMilliseconds():
    return int(round(time.time() * 1000))



def main():

    # clean up, kill any ffmpeg process that are hanging around from a previous run
    print "killing all ffmpeg processes"
    os.system("killall ffmpeg")
    
    print "main"

    streamProcessDict = None


    twitterSnapCount = 0

    while True:



        socketIO.emit('send_video_status', {'send_video_process_exists': True,
                                            'camera_id':cameraIDAnswer})

        
        if streamProcessDict is not None:
            print "stopping previously running ffmpeg (needs to happen if this is not the first iteration)"
            streamProcessDict['video_process'].kill()
            streamProcessDict['audio_process'].kill()

        print "starting process just to get device result" # this should be a separate function so you don't have to do this
        streamProcessDict = startVideoCapture()
        inputDeviceID = streamProcessDict['device_answer']
        print "stopping video capture"
        streamProcessDict['video_process'].kill()
        streamProcessDict['audio_process'].kill()

        #print "sleeping"
        #time.sleep(3)
        #frameCount = int(round(time.time() * 1000))

        videoWithSnapshots = False
        while videoWithSnapshots:

            frameCount = timeInMilliseconds()

            print "taking single frame image"
            snapShot(platform.system(), inputDeviceID, filename="single_frame_image.jpg")

            with open ("single_frame_image.jpg", 'rb') as f:

                # every so many frames, post a snapshot to twitter
                #if frameCount % 450 == 0:
                if frameCount % 6000 == 0:
                        data = f.read()
                        print "emit"
                        socketIO.emit('snapshot', {'frame_count':frameCount, 'image':base64.b64encode(data)})
                data = f.read()

            print "emit"
            socketIO.emit('single_frame_image', {'frame_count':frameCount, 'image':base64.b64encode(data)})
            time.sleep(0)

            #frameCount += 1


        if False:
         if platform.system() != 'Windows':
            print "taking snapshot"
            snapShot(platform.system(), inputDeviceID)
            with open ("snapshot.jpg", 'rb') as f:
                data = f.read()
            print "emit"

            # skip sending the first image because it's mostly black, maybe completely black
            #todo: should find out why this black image happens
            if twitterSnapCount > 0:
                socketIO.emit('snapshot', {'image':base64.b64encode(data)})




        print "starting video capture"
        streamProcessDict = startVideoCapture()


        # This loop counts out a delay that occurs between twitter snapshots.
        # Every 50 seconds, it kills and restarts ffmpeg.
        # Every 40 seconds, it sends a signal to the server indicating status of processes.
        period = 2*60*60 # period in seconds between snaps
        #for count in range(period):
        count = 0
        while True:
            count += 1
            time.sleep(1)

            if count % 20 == 0:
                socketIO.emit('send_video_status', {'send_video_process_exists': True,
                                                    'camera_id':cameraIDAnswer})
            
            if False: #count % 40 == 30:
                print "stopping video capture just in case it has reached a state where it's looping forever, not sending video, and not dying as a process, which can happen"
                streamProcessDict['video_process'].kill()
                streamProcessDict['audio_process'].kill()
                time.sleep(1)

            if count % 30 == 0:
                print "send status about this process and its child process ffmpeg"
                ffmpegProcessExists = True #streamProcessDict['video_process'].poll() is None
                socketIO.emit('send_video_status', {'send_video_process_exists': True,
                                                    'ffmpeg_process_exists': ffmpegProcessExists,
                                                    'camera_id':cameraIDAnswer})

            #if count % 190 == 180:
            #    print "reboot system in case the webcam is not working"
            #    os.system("sudo reboot")
                
            # if the video stream process dies, restart it
            if (streamProcessDict['video_process'].poll() is not None) or \
               (streamProcessDict['audio_process'].poll() is not None):

                # make sure audio and video ffmpeg processes are killed
                #streamProcessDict['video_process'].kill()
                #try:
                #    streamProcessDict['audio_process'].kill()
                #except:
                #    print "error: cound not kill audio process"
                
                # wait before trying to start ffmpeg
                print "ffmpeg process is dead, waiting before trying to restart"
                randomSleep()

                # start video and audio capture again
                streamProcessDict = startVideoCapture()

                
        twitterSnapCount += 1

if __name__ == "__main__":


    #if len(sys.argv) > 1:
    #    cameraIDAnswer = sys.argv[1]
    #else:
    #    cameraIDAnswer = raw_input("Enter the Camera ID for your robot, you can get it by pointing a browser to the runmyrobot server %s: " % server)

    cameraIDAnswer = args.camera_id
    
    
    main()


