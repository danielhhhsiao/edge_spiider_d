sudo bash -c 'cat > /bin/start_statusServer.sh' << EOF
#!/bin/sh
newPath=\$(cat /home/pi/default/device.ini | grep server_dir | tr -d ' ' | cut -d'=' -f2)
cd "\$newPath"
echo "\$newPath"
pwd
sudo fuser 81/tcp -k
sleep 1
sudo netstat -tuplun
sleep 1
if test -f statusServer.py; then
    sudo python3 statusServer.py
else
    sudo ./statusServer
fi

EOF
sudo chmod +x /bin/start_statusServer.sh

sudo bash -c 'cat > /lib/systemd/system/statusServer.service' << EOF
[Unit]
Description = Start status Server
Wants = network-online.target
After = network-online.target
 
 
[Service]
Type = simple
ExecStartPre=/bin/sleep 8
StandardOutput=null
StandardError=append:/var/log/journal/statusServer.log
ExecStart = /bin/start_statusServer.sh
 
 
[Install]
WantedBy = multi-user.target
WantedBy = network-online.target
EOF

sudo chmod 644 /lib/systemd/system/statusServer.service
sudo systemctl daemon-reload
sudo systemctl enable statusServer.service

