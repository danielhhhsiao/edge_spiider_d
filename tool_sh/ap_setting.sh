#!/bin/sh
name_str=$1
pwd_str=$2
pid=$(/home/pi/tool_sh/eeprom -r 1) || pid=""
if [ "${pid}" != "" ]; then
	ap_str='wlan1'
else
	ap_str='ap0'
fi
sudo ifdown "${ap_str}" --force
sudo bash -c 'cat > /etc/hostapd/hostapd.conf' << EOF
ctrl_interface=/var/run/hostapd
ctrl_interface_group=0
interface=${ap_str}
driver=nl80211
ssid=${name_str}

hw_mode=g
ieee80211ac=1
ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]
channel=11
macaddr_acl=0
auth_algs=1
wpa=2
wpa_passphrase=${pwd_str}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP CCMP
rsn_pairwise=CCMP
EOF

sudo ifup "${ap_str}"
sleep 1
