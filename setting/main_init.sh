sudo bash -c 'cat > /bin/mainProgram.sh' << EOF
#!/bin/sh
sudo modprobe cdc-acm
if test -f /home/pi/program/main.py; then
    sudo python3 /home/pi/program/main.py
else
    sudo /home/pi/program/main
fi
EOF
sudo chmod +x /bin/mainProgram.sh

sudo bash -c 'cat > /lib/systemd/system/mainProgram.service' << EOF
[Unit]
Description = Start main
Wants = network-online.target
After = network-online.target
 
 
[Service]
Type = simple
ExecStartPre=/bin/sleep 10
StandardError=append:/var/log/journal/main.log
ExecStart = sudo /bin/mainProgram.sh
 
 
[Install]
WantedBy = multi-user.target
WantedBy = network-online.target
EOF

sudo chmod 644 /lib/systemd/system/mainProgram.service
sudo systemctl daemon-reload
sudo systemctl enable mainProgram.service
