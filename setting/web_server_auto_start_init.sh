
# Populate `/bin/start_wifi.sh`
sudo bash -c 'cat > /bin/start_server.sh' << EOF
#!/bin/bash
if [ "\$(ifconfig | grep "ap0: flags=")" = "" ]; then
	echo "use on spiider"
	if [ "\$(ifconfig | grep "wlan0: flags=")" = "" ] && [ "\$(ifconfig | grep "wlan1: flags=")" != "" ]; then
		echo "not wlan0"
		sudo reboot -nf
	fi
	if [ "\$(ifconfig | grep "wlan1: flags=")" = "" ] && [ "\$(ifconfig | grep "wlan0: flags=")" != "" ]; then
		echo "not wlan1"
		sudo reboot -nf
	fi
fi

flag="0"
if test -f "/home/pi/default/device.ini"; then
	cmd=\$(du /home/pi/default/device.ini -b )
	size=(\${cmd//\t/ })
	sizeInt=\$(("\${size[0]}"))
	echo "size: \${sizeInt}"
	if [ "\${sizeInt}" -lt "100" ]; then
		flag="1"
	fi
else
	flag="1"
fi

if [ "\${flag}" = "1" ]; then
	echo "copy device"
	if test -f /home/pi/default/device.ini_ub; then
		cp /home/pi/default/device.ini_ub /home/pi/default/device.ini
	else
		cp /home/pi/default/original_device.ini /home/pi/default/device.ini
	fi
fi


programPath=\$(cat /home/pi/default/device.ini | grep home_dir | tr -d ' ' | cut -d'=' -f2)
cd "\$programPath"

flag="0"
if test -f "\$programPath/system.ini"; then
	cmd=\$(du "\$programPath/system.ini" -b )
	size=(\${cmd//\t/ })
	sizeInt=\$(("\${size[0]}"))
	echo "size: \${sizeInt}"

	if [ "\${sizeInt}" -lt "100" ]; then
		flag="1"
	fi
else
	flag="1"
fi

if [ "\${flag}" = "1" ]; then
	echo "copy system"
	if test -f "\$programPath/system.ini_ub"; then
		cp "\$programPath/system.ini_ub" "\$programPath/system.ini"
	else
		cp /home/pi/default/system.ini "\$programPath/system.ini"
	fi
fi


flag="0"
if test -f "\$programPath/work.ini"; then
	cmd=\$(du "\$programPath/work.ini" -b )
	size=(\${cmd//\t/ })
	sizeInt=\$(("\${size[0]}"))
	echo "size: \${sizeInt}"
	if [ "\${sizeInt}" -lt "100" ]; then
		flag="1"
	fi
else
	flag="1"
fi

if [ "\${flag}" = "1" ]; then
	echo "copy work"
	if test -f "\$programPath/work.ini_ub"; then
		cp "\$programPath/work.ini_ub" "\$programPath/work.ini"
	else
		cp /home/pi/default/work.ini "\$programPath/work.ini"
	fi
fi



newPath=\$(cat /home/pi/default/device.ini | grep server_dir | tr -d ' ' | cut -d'=' -f2)
cd "\$newPath"
echo "\$newPath"
pwd
sudo fuser 80/tcp -k
sleep 1
sudo netstat -tuplun
sleep 1
if test -f server.py; then
    sudo nice -n -20 python3 server.py
else
    sudo nice -n -20 ./server
fi
EOF
sudo chmod +x /bin/start_server.sh

sudo bash -c 'cat > /lib/systemd/system/webServer.service' << EOF
[Unit]
Description = Start web server
Wants = network-online.target
After = network-online.target
 
 
[Service]
ExecStartPre=/bin/sleep 5
StandardError=append:/var/log/journal/server.log
Type = simple
ExecStart = /bin/start_server.sh
 
 
[Install]
WantedBy = multi-user.target
WantedBy = network-online.target
EOF

sudo chmod 644 /lib/systemd/system/webServer.service
sudo systemctl daemon-reload
sudo systemctl enable webServer.service
