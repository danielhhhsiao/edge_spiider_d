sudo bash -c 'cat > /etc/logrotate.d/program' << EOF
/var/log/journal/*.log {
        rotate 8
        maxsize 4M
        dateext
        compress
        delaycompress
        missingok
        notifempty
        create 644 root root
        dateformat -%Y%m%d.%H%M%S
}
EOF
sudo chmod +x /etc/logrotate.d/program

#!/bin/sh
if [ ! -d "/var/log/journal" ]; then
        sudo mkdir "/var/log/journal"
        echo "mkdir log path."
else
        echo "The log path had been create."
fi

LIST=`crontab -l`
SOURCE="/etc/logrotate.d/program"
echo "$LIST"
if echo "$LIST" | grep -q "$SOURCE"; then
    echo "The back job had been added."
else
    crontab -l | { cat; echo "1 * * * * $SOURCE"; } | crontab -
fi

sudo /usr/sbin/logrotate -f /etc/logrotate.d/program

