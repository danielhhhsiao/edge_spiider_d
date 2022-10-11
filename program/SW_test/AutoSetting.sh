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


selfPath=$(dirname "$(readlink -f "$0")")
cd $selfPath

newValue /boot/config.txt core_freq 250 Y
newValue /boot/config.txt core_freq_min 250 Y
insert /boot/config.txt dtoverlay=spi1-3cs,cs0_pin=16,cs1_pin=5,cs2_pin=6 Y

sed -i -e "s/ /\n/gi" /boot/cmdline.txt
newValue /boot/cmdline.txt isolcpus 1,2,3 Y

while [ "$(cat /boot/cmdline.txt | grep "\n" | wc -l)" != "1" ]
do
    sed -i "N;s/\n/ /gi" /boot/cmdline.txt
done

while [ "$(cat /boot/cmdline.txt | grep "  ")" != "" ]
do 
    sed -i -e "s/  / /gi" /boot/cmdline.txt
done

echo "Set the start.sh authority"
chmod 777 start.sh

echo "Mudify boot auto start setting..."
replace /home/pi/.config/autostart/autostart.desktop PHM_v2 PHM_v3


echo "search audio module..."
mList=$(apt list --installed | grep "libasound2-dev")
if [ -z "$mList" ];then
    sudo dpkg -i /home/pi/PHM_v3/Library/libasound2-dev_1.1.8-1+rpt1_armhf.deb
else
    echo "alreay install "$mList
fi

mList=$(apt list --installed | grep "portaudio19-dev")
if [ -z "$mList" ];then
    sudo dpkg -i /home/pi/PHM_v3/Library/portaudio19-dev_19.6.0-1_armhf.deb
else
    echo "alreay install "$mList
fi

echo "search python module..."
mList=$(pip3 list | grep "VL53L0X")
if [ -z "$mList" ];then
#    pip3 install git+https://github.com/naisy/VL53L0X_rasp_python.git
    pip3 install --no-index --find-links=Library VL53L0X-rasp-python
else
    echo "alreay install "$mList
fi

mList=$(pip3 list | grep "PyAudio")
if [ -z "$mList" ];then
    pip3 install --no-index --find-links=Library PyAudio
else
    echo "alreay install "$mList
    
fi

mList=$(pip3 list | grep "pyalsaaudio")
if [ -z "$mList" ];then
    pip3 install --no-index --find-links=Library pyalsaaudio
else
    echo "alreay install "$mList
    
fi

balence=30
while [ "$balence" != "0" ]
do
    echo "system will auto reboot after "$balence" sec.\r\c"
    balence=$((balence-1))
    sleep 1
done
echo ""

reboot





