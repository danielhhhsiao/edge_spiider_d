#!/bin/bash
for usbdev in $(ls /sys/bus/usb/drivers/usb-storage | grep [1-9])
do
    echo "unmounting  $usbdev"
    echo "$usbdev" > /sys/bus/usb/drivers/usb-storage/unbind
done

