#!/bin/bash

# Clear screen
cd ~/
printf "\ec"
echo -en "\ec"

echo

echo -e "\e[31m**************************************************"
echo -e "\e[31m* \e[39mYou are now about to install everything needed \e[31m*"
echo -e "\e[31m* \e[39mto get your robot connected to letsrobot.tv    \e[31m*"
echo -e "\e[31m* \e[39mBefore we can start, you need to get a robot,  \e[31m*"
echo -e "\e[31m* \e[39mand camera ID. You can get that by pressing    \e[31m*"
echo -e "\e[31m* \e[39mthe \"connect your robot\" button              \e[31m*"
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

echo -e "\e[33mThank you, sit back and relax, we'll see you on letsrobot.tv\e[39m"
echo
sleep 1s


# Write the start_robot file with the ID for robot and camera in
echo '#!/bin/bash' > ~/start_robot
echo '# suggested use for this:' >> ~/start_robot
echo '# (1) Put in the ids for your robot, YOURROBOTID and YOURCAMERAID' >> ~/start_robot
echo '# (2) use sudo to create a crontab entry: @reboot /bin/bash /home/pi/start_robot' >> ~/start_robot
echo 'dt=$(date +"%d-%m-%Y %H:%M:%S")' >> ~/start_robot
echo 'cd /home/pi/runmyrobot' >> ~/start_robot
echo "nohup scripts/repeat_start python controller.py ${input_robot} --type serial --serial-device /dev/ttyUSB0 &> '/home/pi/logs/controller_$dt.log' &" >> ~/start_robot
echo "nohup scripts/repeat_start python send_video.py ${input_camera} 0 --mic-channels 2 --audio-device-name C920 --pipe-audio &> '/home/pi/logs/video_$dt.log' &" >> ~/start_robot

#make logs directory
mkdir ~/logs

# Make sure the system is up to date
sudo apt-get -y update

# Start installing everything needed
sudo apt-get -y install ffmpeg python-serial python-dev libgnutls28-dev espeak python-smbus python-pip git

#clone runmyrobot repo
git clone https://github.com/runmyrobot/runmyrobot

#install python prereqs
cd runmyrobot/
sudo python -m pip install -r requirements.txt

# Add start_robot script to crontab, it might throw an error, but it works anyways
sudo crontab -l | { cat; echo "@reboot /bin/bash /home/pi/start_robot"; } | sudo crontab -

# Make start_robot executable
chmod +x ~/start_robot

echo
echo

echo -e "\e[33mInstall has completed, please run start_robot, or reboot your robot to bring it online.\e[39m"
