# Populate `/bin/OTA_check.sh`
sudo bash -c 'cat > /bin/start_ota_check.sh' << EOF
#!/bin/bash
flag=\$(cat /home/pi/OTA/flag.txt)
if [ "\${flag}" != "0" ]; then
	if test -f /home/pi/OTA/setup.py; then
		sudo python3 /home/pi/OTA/setup.py >> /home/pi/OTA/log.txt
	else
		sudo /home/pi/OTA/setup >> /home/pi/OTA/log.txt
	fi
fi
EOF
sudo chmod +x /bin/start_ota_check.sh

sudo bash -c 'cat > /lib/systemd/system/OTA_check.service' << EOF
[Unit]
Description = Start web server
Wants = network-online.target
After = network-online.target
 
 
[Service]
Type = simple
ExecStartPre=/bin/sleep 10
ExecStart = sudo /bin/start_ota_check.sh
 
 
[Install]
WantedBy = multi-user.target
WantedBy = network-online.target
EOF

sudo chmod 644 /lib/systemd/system/OTA_check.service
sudo systemctl daemon-reload
sudo systemctl enable OTA_check.service
