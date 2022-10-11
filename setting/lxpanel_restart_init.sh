sudo bash -c 'cat > /home/pi/Desktop/open_UI.sh' << EOF
/usr/bin/lxpanel --profile LXDE-pi &
EOF
sudo chmod +x /home/pi/Desktop/open_UI.sh

sudo bash -c 'cat > /home/pi/Desktop/close_UI.sh' << EOF
kill \$(pidof lxpanel)
EOF
sudo chmod +x /home/pi/Desktop/close_UI.sh

LIST=`crontab -l`
SOURCE="/home/pi/Desktop/close_UI.sh"
echo "$LIST"
if echo "$LIST" | grep -q "$SOURCE"; then
    echo "The back job had been added."
else
    crontab -l | { cat; echo "00 00 * * * $SOURCE"; } | crontab -
fi


