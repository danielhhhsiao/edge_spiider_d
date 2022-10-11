MAC_ADDRESS="$(cat /sys/class/net/wlan0/address)"
mac=$(cat /sys/class/net/wlan0/address | tr -d ':')
mac_tail6=$(echo "${mac}" | cut -c 7-12)


#CLIENT_SSID="TC"
#CLIENT_PASSPHRASE="Autc+84149738"
CLIENT_SSID="Simba"
CLIENT_PASSPHRASE="19960709"
AP_SSID="DAQ_"${mac_tail6}
AP_PASSPHRASE="00000000"

# Install dependencies
#sudo apt -y update
#sudo apt -y upgrade
sudo apt -y install dnsmasq dhcpcd hostapd

# Populate `/etc/udev/rules.d/70-persistent-net.rules`
sudo bash -c 'cat > /etc/udev/rules.d/70-persistent-net.rules' << EOF
SUBSYSTEM=="ieee80211", ACTION=="add|change", ATTR{macaddress}=="${MAC_ADDRESS}", KERNEL=="phy0", \
  RUN+="/sbin/iw phy phy0 interface add ap0 type __ap", \
  RUN+="/bin/ip link set ap0 address ${MAC_ADDRESS}
EOF

# Populate `/etc/dnsmasq.conf`
sudo bash -c 'cat > /etc/dnsmasq.conf' << EOF
interface=lo,ap0
no-dhcp-interface=lo,wlan0,eth0
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=192.168.10.2,192.168.10.250,12h
EOF

# Populate `/etc/hostapd/hostapd.conf`
sudo bash -c 'cat > /etc/hostapd/hostapd.conf' << EOF
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
interface=ap0
driver=nl80211
ssid=${AP_SSID}
hw_mode=g
channel=11
macaddr_acl=0
auth_algs=1
wpa=2
wpa_passphrase=${AP_PASSPHRASE}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
EOF

# Populate `/etc/default/hostapd`
sudo bash -c 'cat > /etc/default/hostapd' << EOF
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Populate `/etc/wpa_supplicant/wpa_supplicant.conf`
sudo bash -c 'cat > /etc/wpa_supplicant/wpa_supplicant.conf' << EOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
    ssid="${CLIENT_SSID}"
    psk="${CLIENT_PASSPHRASE}"
    id_str="AP1"
}
EOF

# Populate `/etc/network/interfaces`
sudo bash -c 'cat > /etc/network/interfaces' << EOF
source-directory /etc/network/interfaces.d
auto lo
auto ap0
auto wlan0
iface lo inet loopback

allow-hotplug ap0
iface ap0 inet static
    address 192.168.10.1
    netmask 255.255.255.0
    hostapd /etc/hostapd/hostapd.conf
    
allow-hotplug wlan0
iface wlan0 inet manual
    wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
iface AP1 inet dhcp

auto eth0
iface eth0 inet manual

EOF

# sudo systemctl disable dhcpcd.service

# Populate `/bin/start_wifi.sh`
sudo bash -c 'cat > /bin/start_wifi.sh' << EOF
#!/bin/bash
echo 'Starting Wifi AP and client...'
#sudo ifdown --force wlan0
#sudo ifdown --force ap0
#sudo ifup ap0
#sudo ifup wlan0
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -s 192.168.10.0/24 ! -d 192.168.10.0/24 -j MASQUERADE
sudo systemctl restart dnsmasq
sudo wpa_cli -i wlan0 enable_network 0
EOF
sudo chmod +x /bin/start_wifi.sh
#crontab -l | { cat; echo "@reboot /bin/start_wifi.sh"; } | crontab -

sudo bash -c 'cat > /lib/systemd/system/network.service' << EOF
[Unit]
Description = Start AP/STA mode init
After = multi-user.target
 
 
[Service]
Type = oneshot
ExecStart = /bin/start_wifi.sh
 
 
[Install]
WantedBy = multi-user.target
EOF

sudo chmod 644 /lib/systemd/system/network.service
sudo systemctl daedmon-reload
sudo systemctl enable network.service

echo "Wifi configuration is finished! Please reboot your Raspberry Pi to apply changes..."
