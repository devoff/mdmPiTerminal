#!/bin/bash

sudo cp systemd/010_services /etc/sudoers.d/

cp /dev/null mdmpiterminal.service

user="$(whoami)"

cd "$(dirname "${BASH_SOURCE[0]}")/.."
repo_path="$PWD"

{
echo '[Unit]'
echo 'Description=MDM Pi Terminal'
echo 'After=network.target'


echo '[Service]'
echo 'Environment=VIRTUAL_ENV='$repo_path'/env'
echo 'Environment=PATH='$repo_path'/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
echo 'ExecStart='$repo_path'/env/bin/python -u '$repo_path'/src/snowboy.py'
echo 'WorkingDirectory='$repo_path
echo 'StandardOutput=inherit'
echo 'StandardError=inherit'
echo 'Restart=always'
echo 'User='$user

echo '[Install]'
echo 'WantedBy=multi-user.target'
} > $repo_path/systemd/mdmpiterminal.service

sudo cp $repo_path/systemd/mdmpiterminal.service /etc/systemd/system/mdmpiterminal.service

cp /dev/null mdmpiterminalsayreply.service

user="$(whoami)"

cd "$(dirname "${BASH_SOURCE[0]}")/.."
repo_path="$PWD"

{
echo '[Unit]'
echo 'Description=MDM Pi Terminal SayReply Module'
echo 'After=network.target'


echo '[Service]'
echo 'Environment=VIRTUAL_ENV='$repo_path'/env'
echo 'Environment=PATH='$repo_path'/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
echo 'ExecStart='$repo_path'/env/bin/python -u '$repo_path'/src/sayreply.py'
echo 'WorkingDirectory='$repo_path
echo 'StandardOutput=inherit'
echo 'StandardError=inherit'
echo 'Restart=always'
echo 'User='$user

echo '[Install]'
echo 'WantedBy=multi-user.target'
} > $repo_path/systemd/mdmpiterminalsayreply.service

sudo cp $repo_path/systemd/mdmpiterminalsayreply.service /etc/systemd/system/mdmpiterminalsayreply.service

echo
read -p $'Please select device type you want to configure:\n 1 - USB microphone\n 2 - OPi built-in microphone\n 3 - PS3 eye\nDevice type selected: ' DEVICETYPE ;
if [[ $DEVICETYPE == 1 ]]; then
  sudo cp systemd/asound_usb.conf /etc/asound.conf
  exit 0
elif [[ `echo $DEVICETYPE` == 2 ]]; then
  sudo cp systemd/asound_pi.conf /etc/asound.conf
  exit 0
elif [[ `echo $DEVICETYPE` == 3 ]]; then
  sudo cp systemd/asound_eye.conf /etc/asound.conf
  exit 0
else
  echo
  echo 'Wrong device type selected.'
  echo
  exit 1
fi
