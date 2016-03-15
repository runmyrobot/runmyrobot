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



from socketIO_client import SocketIO, LoggingNamespace

ffmpegProcess = None

if len(sys.argv) >= 4:
    print "using dev port 8122"
    port = 8122
else:
    print "using prod port 8022"
    port = 8022


socketIO = SocketIO('runmyrobot.com', port, LoggingNamespace)


#ffmpeg -f qtkit -i 0 -f mpeg1video -b 400k -r 30 -s 320x240 http://52.8.81.124:8082/hello/320/240/


def onHandleCameraCommand(*args):
    #thread.start_new_thread(handle_command, args)
    print args


socketIO.on('command_to_camera', onHandleCameraCommand)



def getVideoPort():

    if len(sys.argv) > 1:
        cameraIDAnswer = sys.argv[1]
    else:
        cameraIDAnswer = raw_input("Enter the Camera ID for your robot, you can get it from the runmyrobot.com website: ")

    url = 'http://runmyrobot.com/get_video_port/%s' % cameraIDAnswer


    for retryNumber in range(10):
        try:
            print "GET", url
            response = urllib2.urlopen(url).read()
        except:
            print "could not open url ", url
            time.sleep(2)

    return json.loads(response)['mpeg_stream_port']



def runFfmpeg(commandLine):

    global ffmpegProcess
    print commandLine
    ffmpegProcess = subprocess.Popen(shlex.split(commandLine))
    print "command started"



def handleDarwin(deviceNumber, videoPort):

    p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    print err

    deviceAnswer = raw_input("Enter the number of the camera device for your robot from the list above: ")
    commandLine = 'ffmpeg -f qtkit -i %s -f mpeg1video -b 400k -r 30 -s 320x240 http://runmyrobot.com:%s/hello/320/240/' % (deviceAnswer, videoPort)
    
    runFfmpeg(commandLine)


    return deviceAnswer



def handleLinux(deviceNumber, videoPort):

    #p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #out, err = p.communicate()
    #print err


    os.system("v4l2-ctl -c brightness=230 -c contrast=100 -c saturation=100")
    

    if deviceNumber is None:
        deviceAnswer = raw_input("Enter the number of the camera device for your robot: ")
    else:
        deviceAnswer = str(deviceNumber)

        
    commandLine = '/usr/local/bin/ffmpeg -s 320x240 -f video4linux2 -i /dev/video%s -f mpeg1video -b 1k -r 20 http://runmyrobot.com:%s/hello/320/240/' % (deviceAnswer, videoPort)

    runFfmpeg(commandLine)

    return deviceAnswer



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
    commandLine = 'ffmpeg -s 320x240 -f dshow -i video="%s" -f mpeg1video -b 200k -r 20 http://runmyrobot.com:%s/hello/320/240/' % (device, videoPort)
    
    runFfmpeg(commandLine)

    return device



def snapShot(operatingSystem, inputDeviceID):

    os.remove('snapshot.jpg')

    commandLineDict = {
        'Darwin': 'ffmpeg -y -f qtkit -i %s -vframes 1 snapshot.jpg' % inputDeviceID,
        'Linux': '/usr/local/bin/ffmpeg -y -s 320x240 -f video4linux2 -i /dev/video%s -vframes 1 snapshot.jpg' % inputDeviceID,
        'Windows': 'ffmpeg -y -s 320x240 -f dshow -i video="%s" -vframes 1 snapshot.jpg' % inputDeviceID}

    os.system(commandLineDict[operatingSystem])



def startVideoCapture():

    videoPort = getVideoPort()
    print "video port:", videoPort

    if len(sys.argv) >= 3:
        deviceNumber = sys.argv[2]
    else:
        deviceNumber = None

    deviceAnswer = None
    if platform.system() == 'Darwin':
        deviceAnswer = handleDarwin(deviceNumber, videoPort)
    elif platform.system() == 'Linux':
        deviceAnswer = handleLinux(deviceNumber, videoPort)
    elif platform.system() == 'Windows':
        deviceAnswer = handleWindows(deviceNumber, videoPort)
    else:
        print "unknown platform", platform.system()

    return deviceAnswer



def main():

    global ffmpegProcess

    while True:

        inputDeviceID = startVideoCapture()

        print "stopping video capture"
        if ffmpegProcess is not None:
            ffmpegProcess.kill()

        print "taking snapshot"
        snapShot(platform.system(), inputDeviceID)

        with open ("snapshot.jpg", 'rb') as f:
            data = f.read()

        socketIO.emit('snapshot', base64.b64encode(data))

        print "starting video capture"
        inputDeviceID = startVideoCapture()

        for count in range(3000):
            time.sleep(1)

            # if the video process dies, restart it
            if ffmpegProcess.poll() is not None:
                inputDeviceID = startVideoCapture()




if __name__ == "__main__":
    main()

