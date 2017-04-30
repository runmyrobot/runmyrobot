# runmyrobot

<h1> Open Robot Control Code For Connecting to RunMyRobot.com </h1>

RunMyRobot is a site for interacts with other using telepresence robots. User create their own robots and add them to the site.
https://runmyrobot.com


<h2> Installing robot control and video scripts </h2>


The RasPi will need the following things install so it can talk to your motor and talk to the internet.

(1) Install motor HAT software:
https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/installing-software

(2) Install socket.io client for python:

```pip install socketIO-client```

(3) Install python serial library:

```apt-get install python-serial```

(4) Install alsa-lib
```
cd /usr/local/src 
wget ftp://ftp.alsa-project.org/pub/lib/alsa-lib-1.0.25.tar.bz2 \
cd /usr/local/src/alsa-lib-1.0.25 \
./configure --host=arm-unknown-linux-gnueabi \
make -j4 \
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
./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree --extra-libs=-ldl
make -j4
sudo make install
```



<h2> Bring you Bot to life: Programs to run on the Raspberry Pi </h2>

Go to new robot page to create a robot. If you already have one, got to manage robots. There you'll find your Robot ID and Camera ID.

These two scripts need to be running in the background to bring your robot to life: controller.py, send_video.py. Here are instructions about how to start them.

Starting the Robot Controller for the Robot

python controller.py YOUR_ROBOT_ID

For example:

```python controller.py 789123```



Starting the Video Streamer for the Robot


```python send_video.py YOUR_CAMERA_ID YOUR_VIDEO_DEVICE_NUMBER```

For example:

```python send_video.py 12345 0```

The second parameter 0 is assuming you have one camera plugged into your Pi and you are using it, which is usually the case.



<h2> How does this work </h2>

We use ffmpeg to stream audio and socket.io to send control messages.

<h2> How to contribute </h2>

The is a community project. Making your own bot? Adding your own control stuff? Cool! We'd like to hear from you.


