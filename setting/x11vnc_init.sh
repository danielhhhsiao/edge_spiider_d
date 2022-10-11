#sudo apt-get update
#sudo apt-get install x11vnc -y

sudo x11vnc -storepasswd /etc/x11vnc.pass

sudo bash -c 'cat > /lib/systemd/system/x11vnc.service' << EOF
[Unit]
Description = Start X11VNC
After = multi-user.target
 
 
[Service]
Type = simple
ExecStart = sudo /usr/bin/x11vnc -display :0 -auth guess -forever -loop -noxdamage -repeat -rfbauth /etc/x11vnc.pass -rfbport 5900 -shared -scale 800x600
 
 
[Install]
WantedBy = multi-user.target
EOF

sudo chmod 644 /lib/systemd/system/x11vnc.service
sudo systemctl daemon-reload
sudo systemctl enable x11vnc.service
