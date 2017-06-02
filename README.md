# runmyrobot

<h1> Open Robot Control Code For Connecting to RunMyRobot.com </h1>

RunMyRobot is a site for interacts with other using telepresence robots. User create their own robots and add them to the site.
https://runmyrobot.com


<h2> Installing robot control and video scripts </h2>


The RasPi will need the following things install so it can talk to your motor and talk to the internet.

(1) Install [motor HAT software](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/installing-software):


(2) Install socket.io client for python:

```pip install socketIO-client```

(3) Install python serial, gnutls, python-dev, espeak, and python-smbus:

```apt-get install python-serial python-dev libgnutls28-dev espeak python-smbus python-pip```

(4) Install alsa-lib
```
cd /usr/local/src 
wget ftp://ftp.alsa-project.org/pub/lib/alsa-lib-1.0.25.tar.bz2 
cd /usr/local/src/alsa-lib-1.0.25 
./configure --host=arm-unknown-linux-gnueabi 
make -j4 
sudo make install
```

(5) Install x264
```
cd /usr/local/src
git clone git://git.videolan.org/x264
cd x264
./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
make -j4
sudo make install
```

(6) Install FFmpeg
```
cd /usr/local/src
git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg
./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree --enable-gnutls --extra-libs=-ldl
make -j4
sudo make install
```



<h2> Bring you Bot to life: Programs to run on the Raspberry Pi </h2>

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

```--type motor_hat | serial | l298n```

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

Example start_robot:

```
cd /home/pi/runmyrobot
nohup scripts/repeat_start python controller.py YOURROBOTID --type motor_hat --male --voice_number 1 --led max7219 &> /dev/null &
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

Missing something?, you can add it, open source!

<h1> Quicker install </h1>

Grab the source
run the install.sh script in the runmyrobot/scripts folder

(This hasn't been tested yet.)




