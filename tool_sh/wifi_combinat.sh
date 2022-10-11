#!/bin/sh
if [ -f "/home/pi/tool_sh/auo_wpa_supplicant.conf" ]; then
	#sudo ifdown wlan0 --force
	sudo cat "/home/pi/tool_sh/auo_wpa_supplicant.conf" >> "/etc/wpa_supplicant/wpa_supplicant.conf"
	sleep 1
	sudo wpa_cli -i wlan0 reconfigure
	#sudo ifup wlan0 --force
	#sleep 1
	
	#sudo wpa_cli -i wlan0 enable_network all
	#sudo wpa_cli -i wlan0 save_config 
	#for var in {0..23};
	#do
	#	echo "${var}"
	#	sudo wpa_cli -i wlan0 enable $var
	#	sudo wpa_cli -i wlan0 save_config $var
	#done
fi
