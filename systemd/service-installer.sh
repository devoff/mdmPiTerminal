#!/bin/bash

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