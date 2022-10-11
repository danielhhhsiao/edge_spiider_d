#!/bin/sh

newValue() {
    file=$1
    var=$2
    value=$3
    newline=$4
    target=${var}=${value}
    cf=$(cat ${file} | grep "^${var}=" | tail -1)
    if [ -z "$cf" ];then
        echo insert $target
        if [ $newline = "Y" ];then
            printf "\n" >> ${file}
        else
            printf " " >> ${file}
        fi
        echo $target >> ${file}
    elif [ "$cf" != "$target" ];then
        echo replace $cf to $target
        word=s/"${cf}"/${target}/gi
        sed -i -e "${word}" ${file}
    else
        echo "$var already setting."
    fi
}

insert() {
    file=$1
    data=$2
    cf=$(cat ${file} | grep "${data}")
    if [ -z "$cf" ];then
        echo insert $data
        if [ $newline = "Y" ];then
            printf "\n" >> ${file}
        else
            printf " " >> ${file}
        fi
        echo $data >> ${file}
    else
        echo "$data already setting."
    fi
}

replace() {
    file=$1
    sourse=$2
    target=$3
    cf=$(cat ${file} | grep "${sourse}")
    if [ -z "$cf" ];then
        echo "Without $sourse data."
    else
        echo replace $sourse to $target
        word=s/"${sourse}"/${target}/gi
        sed -i -e "${word}" ${file}
    fi
}

mkdir /var/log/journal
newValue /boot/config.txt core_freq 250 Y
newValue /boot/config.txt core_freq_min 250 Y
#insert /boot/config.txt dtoverlay=spi1-3cs,cs0_pin=16,cs1_pin=5,cs2_pin=6 Y
insert /boot/config.txt dtoverlay=spi1-2cs,cs0_pin=18,cs1_pin=17 Y
pip3 install --no-index --find-links=Library VL53L0X-rasp-python


sed -i -e "s/ /\n/gi" /boot/cmdline.txt
newValue /boot/cmdline.txt isolcpus 3 Y
sed -i -e ":label;N;s/\n/ /gi;b label" /boot/cmdline.txt

echo "Please check connection of network"
sleep 3

#set log size and time

sudo bash -c 'cat > /etc/systemd/journal.conf.d/size.conf' << EOF
[Journal]
SystemMaxUse=500M
SystemMaxFileUse=100M
EOF

sudo bash -c 'cat > /etc/systemd/journal.conf.d/level.conf' << EOF
[Journal]
MaxLevelStore=warning
EOF

#keep to open screen
sudo bash -c 'cat > /etc/lightdm/lightdm.conf' << EOF
#
# General configuration
#
# start-default-seat = True to always start one seat if none are defined in the configuration
# greeter-user = User to run greeter as
# minimum-display-number = Minimum display number to use for X servers
# minimum-vt = First VT to run displays on
# lock-memory = True to prevent memory from being paged to disk
# user-authority-in-system-dir = True if session authority should be in the system location
# guest-account-script = Script to be run to setup guest account
# logind-check-graphical = True to on start seats that are marked as graphical by logind
# log-directory = Directory to log information to
# run-directory = Directory to put running state in
# cache-directory = Directory to cache to
# sessions-directory = Directory to find sessions
# remote-sessions-directory = Directory to find remote sessions
# greeters-directory = Directory to find greeters
# backup-logs = True to move add a .old suffix to old log files when opening new ones
# dbus-service = True if LightDM provides a D-Bus service to control it
#
[LightDM]
#start-default-seat=true
#greeter-user=lightdm
#minimum-display-number=0
#minimum-vt=7
#lock-memory=true
#user-authority-in-system-dir=false
#guest-account-script=guest-account
#logind-check-graphical=false
#log-directory=/var/log/lightdm
#run-directory=/var/run/lightdm
#cache-directory=/var/cache/lightdm
#sessions-directory=/usr/share/lightdm/sessions:/usr/share/xsessions:/usr/share/wayland-sessions
#remote-sessions-directory=/usr/share/lightdm/remote-sessions
#greeters-directory=$XDG_DATA_DIRS/lightdm/greeters:$XDG_DATA_DIRS/xgreeters
#backup-logs=true
#dbus-service=true

#
# Seat configuration
#
# Seat configuration is matched against the seat name glob in the section, for example:
# [Seat:*] matches all seats and is applied first.
# [Seat:seat0] matches the seat named "seat0".
# [Seat:seat-thin-client*] matches all seats that have names that start with "seat-thin-client".
#
# type = Seat type (local, xremote, unity)
# pam-service = PAM service to use for login
# pam-autologin-service = PAM service to use for autologin
# pam-greeter-service = PAM service to use for greeters
# xserver-backend = X backend to use (mir)
# xserver-command = X server command to run (can also contain arguments e.g. X -special-option)
# xmir-command = Xmir server command to run (can also contain arguments e.g. Xmir -special-option)
# xserver-config = Config file to pass to X server
# xserver-layout = Layout to pass to X server
# xserver-allow-tcp = True if TCP/IP connections are allowed to this X server
# xserver-share = True if the X server is shared for both greeter and session
# xserver-hostname = Hostname of X server (only for type=xremote)
# xserver-display-number = Display number of X server (only for type=xremote)
# xdmcp-manager = XDMCP manager to connect to (implies xserver-allow-tcp=true)
# xdmcp-port = XDMCP UDP/IP port to communicate on
# xdmcp-key = Authentication key to use for XDM-AUTHENTICATION-1 (stored in keys.conf)
# unity-compositor-command = Unity compositor command to run (can also contain arguments e.g. unity-system-compositor -special-option)
# unity-compositor-timeout = Number of seconds to wait for compositor to start
# greeter-session = Session to load for greeter
# greeter-hide-users = True to hide the user list
# greeter-allow-guest = True if the greeter should show a guest login option
# greeter-show-manual-login = True if the greeter should offer a manual login option
# greeter-show-remote-login = True if the greeter should offer a remote login option
# user-session = Session to load for users
# allow-user-switching = True if allowed to switch users
# allow-guest = True if guest login is allowed
# guest-session = Session to load for guests (overrides user-session)
# session-wrapper = Wrapper script to run session with
# greeter-wrapper = Wrapper script to run greeter with
# guest-wrapper = Wrapper script to run guest sessions with
# display-setup-script = Script to run when starting a greeter session (runs as root)
# display-stopped-script = Script to run after stopping the display server (runs as root)
# greeter-setup-script = Script to run when starting a greeter (runs as root)
# session-setup-script = Script to run when starting a user session (runs as root)
# session-cleanup-script = Script to run when quitting a user session (runs as root)
# autologin-guest = True to log in as guest by default
# autologin-user = User to log in with by default (overrides autologin-guest)
# autologin-user-timeout = Number of seconds to wait before loading default user
# autologin-session = Session to load for automatic login (overrides user-session)
# autologin-in-background = True if autologin session should not be immediately activated
# exit-on-failure = True if the daemon should exit if this seat fails
#
[Seat:*]
#type=local
#pam-service=lightdm
#pam-autologin-service=lightdm-autologin
#pam-greeter-service=lightdm-greeter
#xserver-backend=
xserver-command=X -s 0 -dpms
#xmir-command=Xmir
#xserver-config=
#xserver-layout=
#xserver-allow-tcp=false
#xserver-share=true
#xserver-hostname=
#xserver-display-number=
#xdmcp-manager=
#xdmcp-port=177
#xdmcp-key=
#unity-compositor-command=unity-system-compositor
#unity-compositor-timeout=60
greeter-session=pi-greeter
greeter-hide-users=false
#greeter-allow-guest=true
#greeter-show-manual-login=false
#greeter-show-remote-login=true
#user-session=default
#allow-user-switching=true
#allow-guest=true
#guest-session=
#session-wrapper=lightdm-session
#greeter-wrapper=
#guest-wrapper=
display-setup-script=/usr/share/dispsetup.sh
#display-stopped-script=
#greeter-setup-script=
#session-setup-script=
#session-cleanup-script=
#autologin-guest=false
#autologin-user=
#autologin-user-timeout=0
#autologin-in-background=false
#autologin-session=
#exit-on-failure=false

#
# XDMCP Server configuration
#
# enabled = True if XDMCP connections should be allowed
# port = UDP/IP port to listen for connections on
# listen-address = Host/address to listen for XDMCP connections (use all addresses if not present)
# key = Authentication key to use for XDM-AUTHENTICATION-1 or blank to not use authentication (stored in keys.conf)
# hostname = Hostname to report to XDMCP clients (defaults to system hostname if unset)
#
# The authentication key is a 56 bit DES key specified in hex as 0xnnnnnnnnnnnnnn.  Alternatively
# it can be a word and the first 7 characters are used as the key.
#
[XDMCPServer]
#enabled=false
#port=177
#listen-address=
#key=
#hostname=

#
# VNC Server configuration
#
# enabled = True if VNC connections should be allowed
# command = Command to run Xvnc server with
# port = TCP/IP port to listen for connections on
# listen-address = Host/address to listen for VNC connections (use all addresses if not present)
# width = Width of display to use
# height = Height of display to use
# depth = Color depth of display to use
#
[VNCServer]
#enabled=false
#command=Xvnc
#port=5900
#listen-address=
#width=1024
#height=768
#depth=8
EOF

pid=$(/home/pi/tool_sh/eeprom -r 1) || pid=""
if [ "${pid}" != "" ]; then
    sudo ./wifi_set_SPIIDER.sh
else
    sudo ./wifi_set.sh
fi

sudo apt-get install libatlas-base-dev -y
sudo pip3 install --force-reinstall matplotlib==3.4.2
sudo pip3 install --force-reinstall numpy==1.21.2
sudo pip3 install --force-reinstall scipy==1.7.1
sudo pip3 install --force-reinstall PyWavelets==1.1.1
sudo pip3 install --force-reinstall pycryptodemo==3.14.1

sudo pip3 install --force-reinstall pandas==0.25.2
sudo apt-get install ntp ntpdate -y
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
sudo pip3 install paho-mqtt


sudo ./firewall.sh 
sudo ./web_server_auto_start_init.sh
sudo ./status_server_auto_start_init.sh
./errLog_set.sh
sudo ./Host_AP_Check_init.sh
sudo ./x11vnc_init.sh

sudo ./reset_init.sh 
sudo ./lxpanel_restart_init.sh 
sudo ./OTA_check_init.sh 
sudo ./ntp_init.sh 
sudo ./main_init.sh 
