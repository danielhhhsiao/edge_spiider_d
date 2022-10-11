#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 13:07:25 2021

@author: etao
"""
import spidev

Who_Am_I = 0xF5
Who_Am_I_Value=dict()
Who_Am_I_Value[0x71]="Vibration sensor"
Who_Am_I_Value[0xf1]="Vibration board"
Who_Am_I_Value[0xf2]="Voltage board"
Who_Am_I_Value[0xf3]="Current board"
Who_Am_I_Value["None"]="None"

def scanSlave():
    slaveData=[]
    pinArr=[[0,0],[0,1],[1,0],[1,1]]
    spi=spidev.SpiDev()
    for pin in pinArr:
        spi.open(pin[0],pin[1])
        spi.mode =0
        spi.max_speed_hz=500000
        data=spi.xfer([Who_Am_I,0x0,0x0,0x0,0x0])
        #print(data)
        
        if(data[1] in list(Who_Am_I_Value.keys())):
            slaveData.append(Who_Am_I_Value[data[1]])
        else:
            slaveData.append(Who_Am_I_Value["None"])
        spi.close()
    return slaveData
    
    
def listName():
    return list(Who_Am_I_Value.values())
