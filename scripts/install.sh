#!/bin/bash

# Clear screen
printf "\ec"
echo -en "\ec"

echo

echo -e "\e[31m**************************************************"
echo -e "\e[31m* \e[39mYou are now about to install everything needed \e[31m*"
echo -e "\e[31m* \e[39mto get your robot connected to runmyrobot.com  \e[31m*"
echo -e "\e[31m* \e[39mBefore we can start, you need to get a robot,  \e[31m*"
echo -e "\e[31m* \e[39mand camera ID. You can get that by pressing    \e[31m*"
echo -e "\e[31m* \e[39mthe \"connect your robot\" button                \e[31m*"
echo -e "\e[31m**************************************************"

echo

echo -e "\e[33mPlease enter your Robot ID:\e[39m "
read input_robot

re='^[0-9]+$'
if ! [[ $input_robot =~ $re ]] ; then
   echo "Error: Robot ID is not a number" >&2; exit 1
fi

echo

echo -e "\e[33mPlease enter your Camera ID:\e[39m "
read input_camera

echo
echo

if ! [[ $input_camera =~ $re ]] ; then
   echo "Error: Camera ID is not a number" >&2; exit 1
fi

echo -e "\e[33mThank you, sit back and relax, we'll see you on runmyrobot.com\e[39m"
echo
sleep 3s

# Write the start_robot file with the ID for robot and camera in
echo '#!/bin/bash' >> ~/start_robot
echo '# suggested use for this:' >> ~/start_robot
echo '# (1) Put in the ids for your robot, YOURROBOTID and YOURCAMERAID' >> ~/start_robot
echo '# (2) use sudo to create a crontab entry: @reboot /bin/bash /home/pi/start_robot' >> ~/start_robot
echo 'cd /home/pi/runmyrobot' >> ~/start_robot
echo "nohup scripts/repeat_start python reverse_ssh.py ${input_robot} &> /dev/null &" >> ~/start_robot
echo "nohup scripts/repeat_start python controller.py ${input_robot} &> /dev/null &" >> ~/start_robot
echo "nohup scripts/repeat_start python send_video.py ${input_camera} 0 &> /dev/null &" >> ~/start_robot

# Make sure the system is up to date
sudo apt-get -y update

# This stuff takes forever, therefore not a default, but enable it if you want
#sudo apt-get -y upgrade
#sudo apt-get -y dist-upgrade

# Start installing everything needed
sudo apt-get -y install python-serial python-dev libgnutls28-dev espeak python-smbus python-pip git

sudo pip install -U socketIO-client &&\

cd ~ &&\

git clone https://github.com/adafruit/Adafruit-Motor-HAT-Python-Library.git &&\
cd Adafruit-Motor-HAT-Python-Library &&\

sudo apt-get -y install emacs &&\
sudo apt-get -y install python-dev &&\
sudo python setup.py install &&\

cd ~ &&\
wget ftp://ftp.alsa-project.org/pub/lib/alsa-lib-1.0.25.tar.bz2 &&\
tar xjf alsa-lib-1.0.25.tar.bz2 &&\
cd alsa-lib-1.0.25 &&\
./configure --host=arm-unknown-linux-gnueabi &&\
make -j4 &&\
sudo make install &&\

cd ~ &&\
git clone git://git.videolan.org/x264 &&\
cd x264 &&\
./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl &&\
make -j4 &&\
sudo make install &&\

cd ~ &&\
git clone https://github.com/FFmpeg/FFmpeg.git &&\
cd FFmpeg &&\
./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree --extra-libs=-ldl &&\
make -j4 &&\
sudo make install

cd ~ &&\
git clone https://github.com/runmyrobot/runmyrobot &&\

# Add start_robot script to crontab, it might throw an error, but it works anyways
sudo crontab -l | { cat; echo "@reboot /bin/bash /home/pi/start_robot"; } | sudo crontab -

echo
echo

echo -e "\e[33mInstall has completed, please run start_robot, or reboot your robot to bring it online.\e[39m"
