#!/bin/sh

sudo apt-get install libasound2-dev -y
sudo apt-get install portaudio19-dev -y
sudo pip3 install pyaudio
sudo pip3 install pyalsaaudio


sudo bash -c 'cat > /etc/udev/rules.d/98-usb-id-rule.rules' << EOF
ACTION!="add", GOTO="my_usb_audio_end"

KERNELS=="1-1.6:1.0", ATTR{id}="usb1"
KERNELS=="1-1.2:1.0", ATTR{id}="usb2"

LABEL="my_usb_audio_end"
EOF

sudo udevadm control --reload-rules ;sudo udevadm trigger


