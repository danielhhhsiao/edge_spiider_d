#!/bin/sh

#sudo ifdown wlan0 --force
#sleep 1
#sudo ifup wlan0


ssid_str=$1
psk_str=$2 

sudo wpa_cli -i wlan0 remove_network all
sudo wpa_cli -i wlan0 set country TW
sudo wpa_cli -i wlan0 add_network 0
sudo wpa_cli -i wlan0 set_network 0 ssid '"'${ssid_str}'"'
sudo wpa_cli -i wlan0 set_network 0 id_str '"AP1"'
sudo wpa_cli -i wlan0 set_network 0 priority 10

if [ "$#" -eq "1" ] ; then
	sudo wpa_cli -i wlan0 set_network 0 key_mgmt NONE
else
	sudo wpa_cli -i wlan0 set_network 0 psk '"'${psk_str}'"'
	sudo wpa_cli -i wlan0 set_network 0 key_mgmt WPA-PSK
fi

sudo wpa_cli -i wlan0 enable_network 0
sudo wpa_cli -i wlan0 save_config 0

#sudo dhclient -r wlan0
#sudo dhclient -v wlan0

sudo /home/pi/tool_sh/wifi_combinat.sh
