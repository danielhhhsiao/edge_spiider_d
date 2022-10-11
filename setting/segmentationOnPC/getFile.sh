#!/bin/bash

if [ -d "server" ]; then
	rm -r "server"
fi

mkdir "server"
mkdir "server/Library"
cp /home/pi/server/server.py server/server.py 
cp /home/pi/server/css server/css -r
cp /home/pi/server/js server/js -r
cp /home/pi/server/example server/example -r
cp /home/pi/server/img server/img -r
cp /home/pi/server/404error.html server/404error.html
cp /home/pi/server/sample.html server/sample.html
cp /home/pi/program/Library/tool.py server/Library/tool.py
cp /home/pi/program/Library/segmentation.py server/Library/segmentation.py
cp /home/pi/default/work.ini server/work_default.ini
