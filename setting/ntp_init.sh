sudo bash -c 'cat > /bin/start_NTP.sh' << EOF
#!/bin/sh
sudo service ntp stop
if test -f /home/pi/tool_sh/start_NTP.py; then
    sudo python3 /home/pi/tool_sh/start_NTP.py
else
    sudo /home/pi/tool_sh/start_NTP
fi
EOF
sudo chmod +x /bin/start_NTP.sh

sudo bash -c 'cat > /lib/systemd/system/start_NTP.service' << EOF
[Unit]
Description = Start NTP
 
 
[Service]
Type = simple
ExecStart = sudo /bin/start_NTP.sh
 
 
[Install]
WantedBy = multi-user.target
EOF

sudo chmod 644 /lib/systemd/system/start_NTP.service
sudo systemctl daemon-reload
sudo systemctl enable start_NTP.service
