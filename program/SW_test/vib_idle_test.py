#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: etao
"""
import spidev

def test(bus,cs):
        
    spi=spidev.SpiDev()
    spi.open(bus,cs) # bus,device
    spi.mode=0
    spi.max_speed_hz = 500000
    
    send = [0xf5,0x0,0x0]
    print("-------------------",bus,",",cs,"-------------------")
    for i in send:
        print(hex(i),end=" , ")
    print("")
    
    data = spi.xfer2(send)
    
    for i in data:
        print(hex(i),end=" , ")
    print("")

if __name__ == "__main__":
    test(0,0)
    test(0,1)
    test(1,0)
        
        
        
        
        
