#!/bin/sh
#sudo dhcpcd

eth0_title=""
eth0_ip=""
eth0_route=""

eth1_title=""
eth1_ip=""
eth1_route=""

wlan0_title=""
wlan0_ip=""
wlan0_route=""

if [ "${3}" != "--" ] ; then
	sudo ifdown eth0 
fi
if [ "${6}" != "--" ] ; then
	sudo ifdown eth1 
fi
if [ "${9}" != "--" ] ; then
	sudo ifdown wlan0 
fi

if [ "${1}" != "--" ] ; then
	eth0_title="interface eth0"
	eth0_ip="static ip_address="${1}
	if [ "${2}" != "--" ] ; then
		eth0_route="static routers="${2}
	fi
fi

if [ "${4}" != "--" ] ; then
	eth1_title="interface eth1"
	eth1_ip="static ip_address="${4}
	if [ "${5}" != "--" ] ; then
		eth1_route="static routers="${5}
	fi
fi

if [ "${7}" != "--" ] ; then 
	wlan0_title="interface wlan0"
	wlan0_ip="static ip_address="${7}
	if [ "${8}" != "--" ] ; then
		wlan0_route="static routers="${8}
	fi
fi

echo ${eth0_title}
echo ${eth0_ip}
echo ${eth0_route}

echo ${eth1_title}
echo ${eth1_ip}
echo ${eth1_route}

echo ${wlan0_title}
echo ${wlan0_ip}
echo ${wlan0_route}


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

interface wlan1
static ip_address=192.168.10.1/24
nohook wpa_supplicant
#static routers=192.168.10.1
static domain_name_servers=8.8.8.8


${eth0_title}
${eth0_ip}
${eth0_route}

${eth1_title}
${eth1_ip}
${eth1_route}

${wlan0_title}
${wlan0_ip}
${wlan0_route}

EOF


if [ "${3}" != "--" ] ; then
	sudo ifup eth0
	sudo ip addr flush dev eth0
	sudo dhcpcd -n eth0
fi


if [ "${6}" != "--" ] ; then
	sudo ifup eth1
	sudo ip addr flush dev eth1
	sudo dhcpcd -n eth1
fi


if [ "${9}" != "--" ] ; then
	sudo ifup wlan0
	sudo ip addr flush dev wlan0
	sudo dhcpcd -n wlan0
fi



