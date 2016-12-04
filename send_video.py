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



from socketIO_client import SocketIO, LoggingNamespace


print "test1"


if len(sys.argv) >= 4:
    print "using dev port 8122"
    port = 8122
else:
    print "using prod port 8022"
    port = 8022

print "initializing socket io"
socketIO = SocketIO('runmyrobot.com', port, LoggingNamespace)
print "finished initializing socket io"

#ffmpeg -f qtkit -i 0 -f mpeg1video -b 400k -r 30 -s 320x240 http://52.8.81.124:8082/hello/320/240/


def onHandleCameraCommand(*args):
    #thread.start_new_thread(handle_command, args)
    print args


socketIO.on('command_to_camera', onHandleCameraCommand)



def randomSleep():
    """A short wait is good for quick recovery, but sometimes a longer delay is needed or it will just keep trying and failing short intervals, like because the system thinks the port is still in use and every retry makes the system think it's still in use. So, this has a high likelihood of picking a short interval, but will pick a long one sometimes."""

    timeToWait = random.choice((0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 5))
    print "sleeping", timeToWait
    time.sleep(timeToWait)

    

def getVideoPort():


    url = 'http://runmyrobot.com/get_video_port/%s' % cameraIDAnswer


    for retryNumber in range(2000):
        try:
            print "GET", url
            response = urllib2.urlopen(url).read()
            break
        except:
            print "could not open url ", url
            time.sleep(2)

    return json.loads(response)['mpeg_stream_port']



def runFfmpeg(commandLine):

    print commandLine
    ffmpegProcess = subprocess.Popen(shlex.split(commandLine))
    print "command started"

    return ffmpegProcess
    


def handleDarwin(deviceNumber, videoPort):

    
    p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    print err

    deviceAnswer = raw_input("Enter the number of the camera device for your robot from the list above: ")
    commandLine = 'ffmpeg -f qtkit -i %s -f mpeg1video -b 400k -r 30 -s 320x240 http://runmyrobot.com:%s/hello/320/240/' % (deviceAnswer, videoPort)
    
    process = runFfmpeg(commandLine)

    return {'process': process, 'device_answer': deviceAnswer}


def handleLinux(deviceNumber, videoPort):

    print "sleeping to give the camera time to start working"
    randomSleep()
    print "finished sleeping"

    
    #p = subprocess.Popen(["ffmpeg", "-list_devices", "true", "-f", "qtkit", "-i", "dummy"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #out, err = p.communicate()
    #print err

    #os.system("v4l2-ctl -c brightness=10 -c contrast=25 -c saturation=40")
    os.system("v4l2-ctl -c brightness=180 -c contrast=40 -c saturation=60") # Skippy   
    #os.system("v4l2-ctl -c brightness=50 -c contrast=50 -c saturation=80")
    #os.system("v4l2-ctl -c brightness=200 -c contrast=100 -c saturation=100")
    

    if deviceNumber is None:
        deviceAnswer = raw_input("Enter the number of the camera device for your robot: ")
    else:
        deviceAnswer = str(deviceNumber)

        
    #commandLine = '/usr/local/bin/ffmpeg -s 320x240 -f video4linux2 -i /dev/video%s -f mpeg1video -b 1k -r 20 http://runmyrobot.com:%s/hello/320/240/' % (deviceAnswer, videoPort)
    commandLine = '/usr/local/bin/ffmpeg -s 640x480 -f video4linux2 -i /dev/video%s -f mpeg1video -b 1k -r 20 http://runmyrobot.com:%s/hello/640/480/' % (deviceAnswer, videoPort)
    #commandLine = '/usr/local/bin/ffmpeg -s 1280x720 -f video4linux2 -i /dev/video%s -f mpeg1video -b 1k -r 20 http://runmyrobot.com:%s/hello/1280/720/' % (deviceAnswer, videoPort)


    process = runFfmpeg(commandLine)

    return {'process': process, 'device_answer': deviceAnswer}



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
    

    process = runFfmpeg(commandLine)

    return {'process': process, 'device_answer': device}
    




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
    print "video port:", videoPort

    if len(sys.argv) >= 3:
        deviceNumber = sys.argv[2]
    else:
        deviceNumber = None

    result = None
    if platform.system() == 'Darwin':
        result = handleDarwin(deviceNumber, videoPort)
    elif platform.system() == 'Linux':
        result = handleLinux(deviceNumber, videoPort)
    elif platform.system() == 'Windows':
        result = handleWindows(deviceNumber, videoPort)
    else:
        print "unknown platform", platform.system()

    return result


def timeInMilliseconds():
    return int(round(time.time() * 1000))



def main():

    print "main"

    streamProcessDict = None


    twitterSnapCount = 0

    while True:



        socketIO.emit('send_video_status', {'send_video_process_exists': True,
                                            'camera_id':cameraIDAnswer})

        
        if streamProcessDict is not None:
            print "stopping previously running ffmpeg (needs to happen if this is not the first iteration)"
            streamProcessDict['process'].kill()

        print "starting process just to get device result" # this should be a separate function so you don't have to do this
        streamProcessDict = startVideoCapture()
        inputDeviceID = streamProcessDict['device_answer']
        print "stopping video capture"
        streamProcessDict['process'].kill()

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



        if 1:
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
        for count in range(period):
            time.sleep(1)

            if count % 20 == 0:
                socketIO.emit('send_video_status', {'send_video_process_exists': True,
                                                    'camera_id':cameraIDAnswer})
            
            if count % 161 == 30:
                print "stopping video capture just in case it has reached a state where it's looping forever, not sending video, and not dying as a process, which can happen"
                streamProcessDict['process'].kill()

            if count % 80 == 75:
                print "send status about this process and its child process ffmpeg"
                ffmpegProcessExists = streamProcessDict['process'].poll() is None
                socketIO.emit('send_video_status', {'send_video_process_exists': True,
                                                    'ffmpeg_process_exists': ffmpegProcessExists,
                                                    'camera_id':cameraIDAnswer})

            #if count % 190 == 180:
            #    print "reboot system in case the webcam is not working"
            #    os.system("sudo reboot")
                
            # if the video stream process dies, restart it
            if streamProcessDict['process'].poll() is not None:
                # wait before trying to start ffmpeg
                print "ffmpeg process is dead, waiting before trying to restart"
                randomSleep()
                streamProcessDict = startVideoCapture()




        #print "taking snapshot"
        #snapShot(platform.system(), inputDeviceID)
        #with open ("snapshot.jpg", 'rb') as f:
        #    data = f.read()
        #print "emit"
        #socketIO.emit('snapshot', {'image':base64.b64encode(data)})

        twitterSnapCount += 1




print "test2"

if __name__ == "__main__":


    if len(sys.argv) > 1:
        cameraIDAnswer = sys.argv[1]
    else:
        cameraIDAnswer = raw_input("Enter the Camera ID for your robot, you can get it from the runmyrobot.com website: ")

    
    main()


