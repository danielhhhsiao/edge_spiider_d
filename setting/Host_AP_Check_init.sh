sudo bash -c 'cat > /bin/hostAP_check.sh' << EOF
#!/bin/sh
host=\$(hostname)
pid=\$(/home/pi/tool_sh/eeprom -r 1) || pid=""
interface=\$(cat /etc/hostapd/hostapd.conf | grep '^interface' | cut -d '=' -f2)
echo \${host}
echo \${pid}
echo \${interface}
if [ "\${pid}" != "" ]; then
	mac=\$(cat /sys/class/net/wlan0/address | tr -d ':')
	echo \${mac}
	if [ "\${host}" != "\${mac}" ] && [ "\${mac}" != "" ]; then
		sudo hostnamectl set-hostname \${mac}
		sudo sed -i '/127.0.1.1/d' /etc/hosts
		sudo sed -i '\$a 127.0.1.1	'\${mac} /etc/hosts
		echo "Change hostname to "\${mac}
		#mac_tail6=\$(echo "\${mac}" | cut -c 7-12)
		#correct_AP="DAQ_""\${mac_tail6}"
		home_dir=\$(cat /home/pi/default/device.ini | grep home_dir | tr -d ' ' | cut -d'=' -f2)
		AP_name=\$(cat /home/pi/default/system.ini | grep name | tr -d ' ' | cut -d'=' -f2 | head -n 1)
		#if [ "\${AP_name}" != "\${pid}" ]; then
		echo "Change AP name to ""\${pid}"
		#sed -i "s/\${AP_name}/\${pid}/1" /home/pi/default/system.ini
		sed -i "/^\[ap\]$/,/^\[/ s/^name =.*/name = \${pid}/" /home/pi/default/system.ini
		cp /home/pi/default/system.ini \$home_dir"/system.ini"
		cp /home/pi/default/work.ini \$home_dir"/work.ini"
		#fi
		sudo chmod 777 /home/pi/tool_sh/*
		sudo /home/pi/tool_sh/ap_setting.sh \${pid} 00000000
		host=\$(hostname)
		if [ "\${host}" = "\${mac}" ]; then
			sudo reboot
			#echo "OK"
		fi
	else
		echo "Mac not found."
	fi
	if [ "\${interface}" != "wlan1" ]; then
		echo "Error interface, set to wlan1."
		sudo sed -i.bak "s/^interface=.*/interface=wlan1/" /etc/hostapd/hostapd.conf
		home_dir=\$(cat /home/pi/default/device.ini | grep home_dir | tr -d ' ' | cut -d'=' -f2)
		AP_name=\$(cat /home/pi/default/system.ini | grep name | tr -d ' ' | cut -d'=' -f2 | head -n 1)
		sed -i "/^\[ap\]$/,/^\[/ s/^name =.*/name = \${pid}/" /home/pi/default/system.ini
		cp /home/pi/default/system.ini \$home_dir"/system.ini"
		cp /home/pi/default/work.ini \$home_dir"/work.ini"
		sudo /home/pi/tool_sh/ap_setting.sh \${pid} 00000000
		sudo reboot
	fi

else
	mac=\$(cat /sys/class/net/wlan0/address | tr -d ':')
	if [ "\${host}" != "\${mac}" ] && [ "\${mac}" != "" ]; then
		sudo hostnamectl set-hostname \${mac}
		sudo sed -i '/127.0.1.1/d' /etc/hosts
		sudo sed -i '\$a 127.0.1.1	'\${mac} /etc/hosts
		echo "Change hostname to "\${mac}
		mac_tail6=\$(echo "\${mac}" | cut -c 7-12)
		correct_AP="DAQ_""\${mac_tail6}"
		home_dir=\$(cat /home/pi/default/device.ini | grep home_dir | tr -d ' ' | cut -d'=' -f2)
		AP_name=\$(cat /home/pi/default/system.ini | grep name | tr -d ' ' | cut -d'=' -f2 | head -n 1)
		#if [ "\${AP_name}" != "\${correct_AP}" ]; then
		echo "Change AP name to ""\${correct_AP}"
		sed -i "/^\[ap\]$/,/^\[/ s/^name =.*/name = \${correct_AP}/" /home/pi/default/system.ini
		#sed -i "s/\${AP_name}/\${correct_AP}/1" /home/pi/default/system.ini
		cp /home/pi/default/system.ini \$home_dir"/system.ini"
		cp /home/pi/default/work.ini \$home_dir"/work.ini"
		#fi
		sudo chmod 777 /home/pi/tool_sh/*
		sudo /home/pi/tool_sh/changeAPmac.sh
		sudo /home/pi/tool_sh/ap_setting.sh \${correct_AP} 00000000
		host=\$(hostname)
		if [ "\${host}" = "\${mac}" ]; then
			sudo reboot 
		fi
	else
		echo "Mac not found."
	fi
	if [ "\${interface}" != "ap0" ]; then
		echo "Error interface, set to ap0."
		sudo sed -i.bak "s/^interface=.*/interface=ap0/" /etc/hostapd/hostapd.conf
		sudo reboot
	fi
fi
EOF

sudo chmod +x /bin/hostAP_check.sh

sudo bash -c 'cat > /lib/systemd/system/hostAP_check.service' << EOF
[Unit]
Description = "Check Host and AP name"
 
[Service]
Type = simple
ExecStartPre = /bin/sleep 6
ExecStart = /bin/hostAP_check.sh

[Install]
WantedBy = multi-user.target
EOF

sudo chmod 644 /lib/systemd/system/hostAP_check.service
sudo systemctl daemon-reload
sudo systemctl enable hostAP_check.service
