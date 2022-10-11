MAC_ADDRESS="$(cat /sys/class/net/wlan1/address)"
CLIENT_SSID="TC"
CLIENT_PASSPHRASE="Autc+84149738"
AP_SSID="DAQ_Init"
AP_PASSPHRASE="00000000"

# Install dependencies
#sudo apt -y update
#sudo apt -y upgrade
sudo apt-get install iptables
sudo apt -y install dnsmasq dhcpcd hostapd

rm -f /etc/network/if-pre-up.d/hostapd

# Populate `/etc/udev/rules.d/70-persistent-net.rules`
sudo bash -c 'cat > /etc/udev/rules.d/70-persistent-net.rules' << EOF
SUBSYSTEM=="ieee80211", ACTION=="add|change", ATTR{macaddress}=="${MAC_ADDRESS}", KERNEL=="phy0", \
  RUN+="/sbin/iw dev wlan1 set type __ap"
EOF


# Populate `/etc/dnsmasq.conf`
sudo bash -c 'cat > /etc/dnsmasq.conf' << EOF
interface=lo,wlan1
no-dhcp-interface=lo,wlan0,eth0
bind-interfaces
server=8.8.8.8
domain-needed
bogus-priv
dhcp-range=192.168.10.10,192.168.10.150,24h
EOF

# Populate `/etc/hostapd/hostapd.conf`
sudo bash -c 'cat > /etc/hostapd/hostapd.conf' << EOF
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
interface=wlan1
driver=nl80211
ssid=${AP_SSID}
hw_mode=g
channel=11
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
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

# Populate `/etc/dhcpcd.conf`
sudo bash -c 'cat > /etc/dhcpcd.conf' << EOF
# A sample configuration for dhcpcd.
# See dhcpcd.conf(5) for details.

# Allow users of this group to interact with dhcpcd via the control socket.
#controlgroup wheel

# Inform the DHCP server of our hostname for DDNS.
hostname

# Use the hardware address of the interface for the Client ID.
clientid
# or
# Use the same DUID + IAID as set in DHCPv6 for DHCPv4 ClientID as per RFC4361.
# Some non-RFC compliant DHCP servers do not reply with this set.
# In this case, comment out duid and enable clientid above.
#duid

# Persist interface configuration when dhcpcd exits.
persistent

# Rapid commit support.
# Safe to enable by default because it requires the equivalent option set
# on the server to actually work.
option rapid_commit

# A list of options to request from the DHCP server.
option domain_name_servers, domain_name, domain_search, host_name
option classless_static_routes
# Respect the network MTU. This is applied to DHCP routes.
option interface_mtu

# Most distributions have NTP support.
#option ntp_servers

# A ServerID is required by RFC2131.
require dhcp_server_identifier

# Generate SLAAC address using the Hardware Address of the interface
#slaac hwaddr
# OR generate Stable Private IPv6 Addresses based from the DUID
slaac private

# Example static IP configuration:
#interface eth0
#static ip_address=192.168.0.10/24
#static ip6_address=fd51:42f8:caae:d92e::ff/64
#static routers=192.168.0.1
#static domain_name_servers=192.168.0.1 8.8.8.8 fd51:42f8:caae:d92e::1

# It is possible to fall back to a static IP if DHCP fails:
# define static profile
#profile static_eth0
#static ip_address=192.168.1.23/24
#static routers=192.168.1.1
#static domain_name_servers=192.168.1.1

# fallback to static profile on eth0
#interface eth0
#fallback static_eth0

#denyinterfaces wlan1

interface wlan1
static ip_address=192.168.10.1/24
nohook wpa_supplicant
#static routers=192.168.10.1
static domain_name_servers=8.8.8.8


EOF

# Populate `/etc/network/interfaces`
sudo bash -c 'cat > /etc/network/interfaces' << EOF
source-directory /etc/network/interfaces.d
auto lo
auto wlan1
auto wlan0
iface lo inet loopback

allow-hotplug wlan1
iface wlan1 inet static
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
#sudo ifdown --force wlan1
#sudo ifup wlan1
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

echo "Wifi configuration is finished! Please reboot to apply changes..."
