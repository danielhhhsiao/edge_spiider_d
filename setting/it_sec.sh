mv /home/pi/setting/umusb.sh /home/pi/.umusb.sh
sudo chmod 777 /home/pi/.umusb.sh
sudo crontab -l |{ cat ;echo "0 */3 * * * /bin/sh ./scs.sh > /dev/null 2>&1" ; }| sudo crontab -
