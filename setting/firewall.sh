sudo apt-get install ufw -y

sudo ufw enable
sudo ufw default deny
sudo ufw allow 80
sudo ufw allow 5900
sudo ufw allow 53
sudo ufw allow 5353
