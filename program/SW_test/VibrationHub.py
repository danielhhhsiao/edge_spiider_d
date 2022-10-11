#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:08:16 2021

@author: pi
"""

import spidev
import time

class VibHub():
    def __init__(self,spiChannel):
        pinArr=[[0,0],[0,1],[1,0],[1,1],[1,2]]
        self.MPU_CHILD_MAX_LEN       = 6
        self.MPU_SCALE_VALUE         = dict()
        self.MPU_SCALE_VALUE[2]      = 1
        self.MPU_SCALE_VALUE[4]      = 2
        self.MPU_SCALE_VALUE[8]      = 3
        self.MPU_SCALE_VALUE[16]     = 4
        self.MPU_FS_VALUE            = dict()
        self.MPU_FS_VALUE[1000]      = 1
        self.MPU_FS_VALUE[4000]      = 2
        self.WHO_AM_I                = 0xF1
        self.RPI_CMD_WHO_AM_I        = 0xF5
        self.RPI_CMD_CH_ENABLE       = 0x81
        self.RPI_CMD_BUFFER_LEN_H    = 0x82
        self.RPI_CMD_BUFFER_LEN_L    = 0x83
        self.RPI_CMD_GET_BUFFER      = 0x84
        self.RPI_CMD_START           = 0x18
        self.RPI_CMD_STOP            = 0x28
        self.RPI_CMD_RESET           = 0x38
        self.RPI_CMD_SET_CH          = 0x48
        self.RPI_CMD_SET_FS          = 0x58
        self.RPI_CMD_SET_SCALE       = 0x60
        self.MPU_HUB_CLOCK           = 8000000 #8MHz
        
        self.spiChannel = spiChannel
        self.sampleRate = 1000
        self.select = [False]*self.MPU_CHILD_MAX_LEN
        self.enable = [False]*self.MPU_CHILD_MAX_LEN
        self.scale = [4]*self.MPU_CHILD_MAX_LEN
        
        
        self.spi=spidev.SpiDev()
        self.spi.open(pinArr[spiChannel][0],pinArr[spiChannel][1]) # bus,device
        self.spi.mode=0
        self.spi.max_speed_hz =self.MPU_HUB_CLOCK
        
        self.ResetHub()
        

    def CheckSlave(self):
        data=self.spi.xfer2([self.RPI_CMD_WHO_AM_I,0x0,0x0])
        data=data[2]
        if data==self.WHO_AM_I:
            return True
        else:
            return False
        
    def ScanSensor(self):
        data=self.spi.xfer2([self.RPI_CMD_CH_ENABLE,0x0,0x0])
        data=data[2]
        mask=0x01
        for i in range(self.MPU_CHILD_MAX_LEN):
            if mask & data:
                self.enable[i]=True
            else:
                self.enable[i]=False
            mask=mask<<1
        return self.enable
            
    def UnSelectOneSensor(self,slave):#0~5
        if(slave >= self.MPU_CHILD_MAX_LEN):
            return False
        self.select[slave]=False
        self.SelectAllSensor(self.select)
        return True
    
    def SelectOneSensor(self,slave):#0~5
        if(slave >= self.MPU_CHILD_MAX_LEN):
            return False
        self.select[slave]=True
        self.SelectAllSensor(self.select)
        return True
        
    def SelectAllSensor(self,value):
        self.select=value
        tran=0x0;
        mask=0x1;
        for val in self.select:
            if val:
                tran=tran|mask
            mask=mask<<1
        self.spi.xfer2([self.RPI_CMD_SET_CH,tran])
        
    def ResetHub(self):
        self.spi.xfer2([self.RPI_CMD_RESET])
        time.sleep(0.005)
        
    def StartSample(self):
        self.spi.xfer2([self.RPI_CMD_START])
        
    def StopSample(self):
        self.spi.xfer2([self.RPI_CMD_STOP])
        
    def GetBufferLen(self):
        data = self.spi.xfer2([self.RPI_CMD_BUFFER_LEN_H,self.RPI_CMD_BUFFER_LEN_L,0x0,0x0])
        ret = self.byte2int([data[3],data[2]])
        if ret>0:
            return ret
        else:
            return 0
    
    def GetBuffer(self,count):
        cmd=[self.RPI_CMD_GET_BUFFER]*(count)
        cmd=cmd+[0,0]
        data = self.spi.xfer3(cmd)#get all FIFO
        return data[2:]
        
    def SetScale(self,channel,value):
        if(value in list(self.MPU_SCALE_VALUE.keys()) and channel < self.MPU_CHILD_MAX_LEN):
            self.scale[channel] = value
            self.spi.xfer2([self.RPI_CMD_SET_SCALE | channel,self.MPU_SCALE_VALUE[value]])
            return True
        return False
        
    def SetFs(self,value):
        if(value in list(self.MPU_FS_VALUE.keys())):
            self.sampleRate = value
            self.spi.xfer2([self.RPI_CMD_SET_FS,self.MPU_FS_VALUE[value]])
            return True
        return False
    
    def ConvertData(self, arr):
        max_reading=65536
        arr[arr>=(max_reading/2)]=arr[arr>= (max_reading/2)] - max_reading
        return arr
        
    def byte2long(self,b=[0,0,0,0]):
        return b[0] | b[1]<<8 | b[2]<<16 | b[3]<<24
    
    def byte2int(self,b=[0,0]):
        return b[0] | b[1]<<8
    
    
    
