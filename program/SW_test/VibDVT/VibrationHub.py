#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:08:16 2021

@author: pi
"""

import spidev
import time
import numpy as np
import RPi.GPIO as GPIO

class VibHub():
    HW_RESET_PIN  = 29 
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
        
        
    @classmethod
    def ResetHubHW(cls):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(cls.HW_RESET_PIN,GPIO.OUT)
        GPIO.output(cls.HW_RESET_PIN,GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(cls.HW_RESET_PIN,GPIO.LOW)
        time.sleep(1)
        GPIO.output(cls.HW_RESET_PIN,GPIO.HIGH)
        time.sleep(0.1)
        
    def ResetHub(self):
        self.spi.xfer2([self.RPI_CMD_RESET])
        time.sleep(0.005)

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
        
    def StartSample(self):
        self.spi.xfer2([self.RPI_CMD_START])
        
    def StopSample(self):
        self.spi.xfer2([self.RPI_CMD_STOP])
        
    def GetBufferLen(self):
        data = self.spi.xfer2([self.RPI_CMD_BUFFER_LEN_H,self.RPI_CMD_BUFFER_LEN_L,0x0,0x0])
        #print(data)
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
        #max_reading=65536
        #arr[arr>=(max_reading/2)]=arr[arr>= (max_reading/2)] - max_reading
        #return arr
        return np.array(arr,dtype=np.int16)
        
    def byte2long(self,b=[0,0,0,0]):
        return b[0] | b[1]<<8 | b[2]<<16 | b[3]<<24
    
    def byte2int(self,b=[0,0]):
        return b[0] | b[1]<<8
    
    
    
if __name__ == "__main__":
        import os
        import sys
        import time
        from datetime import datetime
        import logging
        import argparse
        import pandas as pd
        import numpy as np
        
        
        
        path = "data/"
        if not os.path.exists(path):
                os.makedirs(path)
                
        startTimeStr = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(path+"Vib_log_"+startTimeStr+".txt","w","utf-8")
        handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
        root_logger.addHandler(handler)
        root_logger.addHandler(logging.StreamHandler())
        
        parser = argparse.ArgumentParser()
        parser.add_argument("bus",type=int,help="SPI bus. Example 0 or 1.",choices=[0,1])
        parser.add_argument("cs",type=int,help="SPI CE. Example 0 or 1.",choices=[0,1])
        parser.add_argument("fs",type=int,help="Sampling rate. Example 1000 or 4000."
                ,choices=[1000,4000],nargs='?',default = 4000)
        parser.add_argument("point",type=int,help="Sampling point. Default is 0. if set to zero, processing will not sample. Example 2048"
                ,nargs='?',default = 0)
        parser.add_argument("ch",type=str,help="Enable each sensor channel using binary. Default is 111111. Example input 110000 to enable channel 1 and 2."
                ,nargs='?',default = "111111")
        parser.add_argument("scale",help="Setting sensor scale 2/4/8/16(G). Use comma to separate. Default is 2,2,2,2,2,2. Example input 2,2,2,4,8,16."
                ,nargs='?',default = "2,2,2,2,2,2")
        parser.add_argument("cpu",help="Set the cpu core. Example 0,1,2. Default is 3."
                ,nargs='?',default = "3")
        parser.add_argument("-e","--end",help="Auto endding processing",action="store_true")
        parser.add_argument("-r","--raw",help="Save raw data before conversion",action="store_true")
        
        
        args = parser.parse_args()
        os.system("taskset -cp %s %d" %(args.cpu,os.getpid()))
        if args.bus !=0 and args.bus !=1:
                logging.error("error: invalid spix settng.")
                sys.exit()
        if args.cs !=0 and args.cs !=1:
                logging.error("error: invalid csx settng.")
                sys.exit()
        if args.fs !=1000 and args.fs !=4000:
                logging.error("error: invalid sampling rate value.")
                sys.exit()
        if len(args.ch)!=6:
                logging.error("error: invalid channel enable length.")
                sys.exit()
        else:
                for c in args.ch:
                        if c!="0" and c !="1":
                                logging.error("error: invalid channel value.")
                                sys.exit()
        if len(args.scale.split(','))!=6:
                logging.error("error: invalid scale length.")
                sys.exit()
        else:
                for c in args.scale.split(','):
                        if c not in ["2","4","8","16"]:
                                logging.error("error: invalid scale value. value follow 2/4/8/16")
                                sys.exit()
                
        #----------------------------------
        logging.info("Start testing:")
        logging.info("bus: %d" %args.bus)
        logging.info("cs: %d" %args.cs)
        logging.info("fs: %d" %args.fs)
        logging.info("sample point: %d" %args.point)
        logging.info("ch:"+args.ch)
        logging.info("scale:"+args.scale)
        
        logging.info("Reset board...")
        VibHub.ResetHubHW()
        
        fileName = "Vib_result_"+startTimeStr+".csv"
        
                
        vib = VibHub(args.bus*2+args.cs)
        maxEnableSensor = 0
        columnName = []
        columnScale = []
        if not vib.CheckSlave():
                logging.error("connect error: bus(%d) cs(%d) cannot get device." %(args.bus,args.cs) )
                sys.exit()
        else:
                logging.info("Board connected!")
               
                
        logging.info("Scan sensor at device...")
        sensors = vib.ScanSensor()
        for i,sensor in enumerate(sensors):
                if sensor:
                        logging.info("\tcannel %d Connected." % (i+1))
                else:
                        logging.info("\tcannel %d Disconnected." % (i+1))
               
        if "1" not in  args.ch or args.point<=0:
                if not args.end:
                        input("Press enter to end the processing")
                sys.exit()
                
        logging.info("Enable sensor at device...")
        for i,enableSensor in enumerate(args.ch):
                if enableSensor=="1":
                        if sensors[i]:
                                vib.SelectOneSensor(i)
                                maxEnableSensor = maxEnableSensor+1
                                columnName.append("ch"+str(i+1))
                                logging.info("\tcannel %d sensor enable... OK!" % (i+1))
                        else:
                                logging.error("error: cannel %d did not have sensor." % (i+1))
                                sys.exit()
                else:
                        logging.info("\tcannel %d pass."% (i+1))
                        
                        
        logging.info("Setting scale of sensor...")
        for i,scale in enumerate(args.scale.split(",")):
                if vib.select[i]:
                        s = int(scale)
                        vib.SetScale(i,s)
                        columnScale.append(s)
                
                
        logging.info("Setting sampling rate...")
        vib.SetFs(args.fs)
                
                
        logging.info("Start sample...")
        perSampleLen = maxEnableSensor*6
        totalDataLen = perSampleLen*args.point
        sleepInterval = min(65536/(perSampleLen*args.fs)/10,1)
        logging.info("Sample interval: {:.3f} sec.".format(sleepInterval))
        realFs=0
        resultIndex = 0
        resultArr = np.zeros(totalDataLen)
        vib.StartSample()
        
        time.sleep(0.01)
        startTime = time.time()
        dataLen = vib.GetBufferLen()
        endTime = startTime
        vib.GetBuffer((dataLen//perSampleLen)*perSampleLen)
        #print("sync time",(dataLen//perSampleLen)*perSampleLen)
        #refrech buffer and sync time
        
        
        maxSampleTime = (args.point/args.fs)*1.05
        while time.time()-startTime < maxSampleTime and resultIndex < totalDataLen:
                sleepTime = sleepInterval-(time.time()-endTime)
                if sleepTime>0:
                        time.sleep(sleepTime)
                
                endTime = time.time()
                dataLen = vib.GetBufferLen()
                if dataLen==65536:
                        logging.error("Buffer overflow!")
                        
                if dataLen>0:
                        data = vib.GetBuffer(dataLen)
                        endPoint = resultIndex+dataLen
                        if endPoint>totalDataLen:
                               resultArr[resultIndex:] =  data[:dataLen-(endPoint-totalDataLen)]
                        else:
                               resultArr[resultIndex:resultIndex+dataLen] = data
                               
                        resultIndex = resultIndex+dataLen
                        realFs = resultIndex/(endTime-startTime)/perSampleLen
                        logging.info("Get bugger length: {dataLen} average fs: {a:.2f} , finished: {b:.2f}%".format(dataLen=dataLen,a=realFs,b=min(resultIndex/totalDataLen*100,100)))
        
        vib.StopSample()
        resultArr = resultArr[0::2]*256+resultArr[1::2]
        resultArr = vib.ConvertData(resultArr)
        if not args.raw:
                resultArr = resultArr/32768.0*1000
        resultArr = resultArr.reshape(-1,3*maxEnableSensor).T
        df = pd.DataFrame()
        for i in range(0,resultArr.shape[0],3):
                x= resultArr[i]
                y= resultArr[i+1]
                z= resultArr[i+2]
                if not args.raw:
                        x= x*columnScale[i//3]
                        y= y*columnScale[i//3]
                        z= z*columnScale[i//3]
                df[columnName[i//3]+"_aX"]=x
                df[columnName[i//3]+"_aY"]=y
                df[columnName[i//3]+"_aZ"]=z
                
        for i in df.columns:
                if not args.raw:
                        logging.info("%s mean : %lf mG"%(i,np.mean(df[i])))
                else:
                        logging.info("%s mean : %lf"%(i,np.mean(df[i])))
        
        
        df.to_csv(path+fileName,index=False)
        logging.info("Output data: "+path+fileName)
        
        if not args.end:
                input("Press enter to end the processing")
