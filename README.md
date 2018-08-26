# Let's Robot

<h1> Open Robot Control Code For Connecting to LetsRobot.tv </h1>

LetsRobot.tv is a site for interacts with other using telepresence robots. User create their own robots and add them to the site.
https://letsrobot.tv

You can find additional documentation including information about our API on our [readme.io](https://letsrobot.readme.io/) page as well. 


<h2> Quick Install </h2>

The quickest option is to just download our complete image with everything already compiled and flash this to an SD card for your raspberry pi or other linux based computer:

[Download the Let's Robot Image](https://drive.google.com/open?id=1pH-xN40-iPPhvj9dFYjv4AI26jw4qc40)

--- or ---- 

Copy this into the terminal on your raspberry pi (or robot's OS), and follow the instructions.
This script has been tested on a Raspberry Pi 3, with a fresh flash of "2017-04-10-raspbian-jessie-lite".

```
sudo wget https://raw.githubusercontent.com/runmyrobot/runmyrobot/master/scripts/install.sh -O /tmp/install.sh && bash /tmp/install.sh
```

After end installtion, all the files needed should be installed and ready for use, but you still might need to change some arguments in your "/home/pi/start_robot" file, to make it suit your robot.

To edit your start_robot file, put this into the terminal.

```sudo nano /home/pi/start_robot```

<h2> Manual Install </h2>


We recommend using [Raspian Lite](https://www.raspberrypi.org/downloads/raspbian/), however any version of [Raspian](https://www.raspberrypi.org/downloads/raspbian/) or [NOOBS](https://www.raspberrypi.org/downloads/noobs/) should work. 

Make sure the Raspberry Pi software is up to date. 

```
sudo apt-get update
```

Install ffmpeg and other software needed to run our code. 

```
sudo apt-get install ffmpeg python-serial python-dev libgnutls28-dev espeak python-smbus python-pip git
```

Download the Let’s Robot / Run My Robot software from our github

```
git clone https://github.com/runmyrobot/runmyrobot
```

Go into the /runmyrobot directory

```
cd runmyrobot
```

Install requirements

```
sudo python -m pip install -r requirements.txt
```


<h2> Bring you Bot to life: Programs to run on the Raspberry Pi </h2>

Start by cloning the runmyrobot repository
```
cd ~
git clone https://github.com/runmyrobot/runmyrobot
cd runmyrobot
```

Go to new robot page to create a robot. If you already have one, got to manage robots. There you'll find your Robot ID and Camera ID.

These two scripts need to be running in the background to bring your robot to life: controller.py, send_video.py. Here are instructions about how to start them.

Copy the 'start_robot' Script from runmyrobot/Scripts to the pi home folder

```cp ~/runmyrobot/scripts/start_robot ~/```

Edit the script so you can adjust some settings for controller.py and send_video.py:

```nano ~/start_robot```

Edit the YOURROBOTID to your robot ID.

Edit the YOURCAMERAID to your camera ID.

You are getting both IDs when you are creating a new bot on the website.

The second parameter on send_video.py 0 is assuming you have one camera plugged into your Pi and you are using it, which is usually the case.

There are more parameter possible for controller.py:

```robot_id```

Your Robot ID. Required

```--env prod | dev```

Environment for example dev or prod | default='prod'

```--type motor_hat | serial | l298n | motozero```

What type of motor controller should be used | default='motor_hat'

```--serial-device /dev/ttyACM0```

Serial device | default='/dev/ttyACM0'

```--male```

Use TTS with a male voice

```--female```

Use TTS with a female voice

```--voice-number 1```

What voice should be used | default=1

```--led max7219```

What LEDs should be used (if any) | default=none

```--ledrotate 180```

Rotates the LED matrix | default=none

Example start_robot:

```
cd /home/pi/runmyrobot
nohup scripts/repeat_start python controller.py YOURROBOTID --type motor_hat --male --voice-number 1 --led max7219 --ledrotate 180 &> /dev/null &
nohup scripts/repeat_start python send_video.py YOURCAMERAID 0 &> /dev/null &
```

<h3> Start script on boot </h3>
Use crontab to start the start_robot script on booting:

```
crontab -e
```

insert following line and save:

```
@reboot /bin/bash /home/pi/start_robot
```

That's it!

<h2> How does this work </h2>

We use ffmpeg to stream audio and socket.io to send control messages.

<h2> How to contribute </h2>

The is a community project. Making your own bot? Adding your own control stuff? Cool! We'd like to hear from you.


<h1> Hardware Compatibility </h1>

Adafruit Motor Hat

Serial Port based commands

GoPiGo

L298N

MotoZero

Missing something?, you can add it, open source!


<h1> Instructions for Specific Hardward Configurations </h1>

<h2> GoPiGo3 </h2>

For GoPiGo3, you will need to install the gopigo3 python module (which is different than older versions). It will need to be installed with the installation script from Dexter. Also, PYTHONPATH needs to be set to "/home/pi/Dexter/GoPiGo3/Software/Python"

Refer to this:
https://github.com/DexterInd/GoPiGo3
```
sudo git clone http://www.github.com/DexterInd/GoPiGo3.git /home/pi/Dexter/GoPiGo3
sudo bash /home/pi/Dexter/GoPiGo3/Install/install.sh
sudo reboot
```



<h1> High Level Overview </h1>

![robot client topology](https://raw.githubusercontent.com/runmyrobot/runmyrobot/master/documentation/RobotClientTopology.png)

The robot client connects via websockets to the API service to retrieve configuration information, to the chat to receive chat messages, the video/audio relays to send its camera and microphone capture, and to the control service to receive user commands.

<h2>Interfaces: </h2>
Control server via socket.io
Application server via socket.io and HTTP
Chat server via socket.io
Sends video stream via websockets
Sends audio stream via websockets

<h2>Responsibilities: </h2>
Capturing Audio and Video
Relays commands to robot hardware
Text to Speech
Supports remote login for diagnostics and updates
Configuration updates from the web client (partially implemented)

<h2>Detailed Description: </h2>
The robot client connects to four external services: API Service, Chat Service, Video/Audio Service, and the Control Service.

<h4>API Service</h4>
Provides information about which host and port to connect to for the chat service, video/audio service, and control service

<h4>Chat Service</h4>
Relays chat messages sent from the web clients to the robot

<h4>Video/Audio Service</h4>
The robot client streams ffmpeg output to the video/audio service

<h4>Control Service</h4>
Relays control messages sent from the web clients to the robot


