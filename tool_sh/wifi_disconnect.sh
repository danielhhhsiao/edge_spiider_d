#!/bin/sh

sudo wpa_cli -i wlan0 set country TW
#sudo ifdown wlan0 --force
#sudo ifup wlan0
#sudo wpa_cli -i wlan0 disable_network 0
sudo wpa_cli -i wlan0 remove_network all
sudo wpa_cli -i wlan0 save_config 0

sudo /home/pi/tool_sh/wifi_combinat.sh


