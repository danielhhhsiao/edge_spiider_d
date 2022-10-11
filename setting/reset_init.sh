# Populate `/bin/OTA_check.sh`
sudo bash -c 'cat > /bin/reset_system.sh' << EOF
#!/bin/bash
if test -f /home/pi/tool_sh/reset.py; then
	sudo python3 /home/pi/tool_sh/reset.py 
else
	sudo /home/pi/tool_sh/reset 
fi
EOF
sudo chmod +x /bin/reset_system.sh

sudo bash -c 'cat > /lib/systemd/system/reset_system.service' << EOF
[Unit]
Description = Reset all setting and config
Wants = network-online.target
After = network-online.target
 
 
[Service]
Type = simple
ExecStart = sudo /bin/reset_system.sh
 
[Install]
WantedBy = multi-user.target
WantedBy = network-online.target
EOF

sudo chmod 644 /lib/systemd/system/reset_system.service
sudo systemctl daemon-reload
sudo systemctl enable reset_system.service
