#!/bin/sh
enable=$(i2cdetect -y 1 | grep 20:  | cut -d' ' -f11)
if [ "$enable" != "--" ];then
    echo "true"
else
    echo "false"
fi
