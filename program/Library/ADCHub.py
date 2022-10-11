#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:00:01 2021

@author: etao
"""


import spidev
import time
import numpy as np
import RPi.GPIO as GPIO

class ADCHub():
#1.0.1 improve ref votage
#1.0.2 increate HW reset
#1.0.3 remove HW reset & increate reset delay & FW version check
#1.0.4 improve input keywoord of current range from 31.5mA to 31.25mA

    __version__ = "1.0.4"
    #HW_RESET_PIN  = 29 
    def __init__(self,spiChannel):
        pinArr=[[0,0],[0,1],[1,0],[1,1],[1,2]]
        self.ADS_CHILD_MAX_LEN       = 8
        self.ADS_SCALE_VALUE         = dict()
        self.ADS_SCALE_VALUE[1]      = 1
        self.ADS_SCALE_VALUE[2]      = 2
        self.ADS_SCALE_VALUE[8]      = 3
        self.ADS_SCALE_RELAY_OFFSET      = 3
        self.ADS_FS_VALUE            = dict()
        self.ADS_FS_VALUE[500]       = 1
        self.ADS_FS_VALUE[1000]      = 2
        self.ADS_FS_VALUE[2000]      = 3
        self.ADS_FS_VALUE[4000]      = 4
        self.ADS_FS_VALUE[8000]      = 5
        self.WHO_AM_I_VOL            = 0xF2
        self.WHO_AM_I_CUR            = 0xF3
        self.RPI_CMD_WHO_AM_I        = 0xF5
        self.RPI_CMD_VERSION         = 0xF8
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
        self.ADS_HUB_CLOCK           = 8000000 #8MHz
        
        self.spiChannel = spiChannel
        self.sampleRate = 1000
        self.select = [False]*self.ADS_CHILD_MAX_LEN
        self.enable = [False]*self.ADS_CHILD_MAX_LEN
        self.scale = [2]*self.ADS_CHILD_MAX_LEN
        self.mode = [1]*self.ADS_CHILD_MAX_LEN
        #1:Voltage, 2:Current
        
        
        self.spi=spidev.SpiDev()
        self.spi.open(pinArr[spiChannel][0],pinArr[spiChannel][1]) # bus,device
        self.spi.mode=0
        self.spi.max_speed_hz =self.ADS_HUB_CLOCK
        
        self.ResetHub()
        
    
    
    def ResetHub(self):
        self.spi.xfer2([self.RPI_CMD_RESET])
        time.sleep(2) #wait to static
        

    def CheckSlave(self):
        data=self.spi.xfer2([self.RPI_CMD_WHO_AM_I,0x0,0x0])
        data=data[2]
        if data==self.WHO_AM_I_VOL or data==self.WHO_AM_I_CUR :
            return True
        else:
            return False

    def CheckSlaveType(self):
        data=self.spi.xfer2([self.RPI_CMD_WHO_AM_I,0x0,0x0])
        data=data[2]
        if data==self.WHO_AM_I_VOL:
            return "Voltage"
        elif data==self.WHO_AM_I_CUR :
            return "Current"
        else:
            return "None"
        
    def ScanSensor(self):
        data=self.spi.xfer2([self.RPI_CMD_CH_ENABLE,0x0,0x0])
        data=data[2]
        
        mask=0x01
        for i in range(self.ADS_CHILD_MAX_LEN):
            if mask & data:
                self.enable[i]=True
            else:
                self.enable[i]=False
            mask=mask<<1
        return self.enable
            
    def UnSelectOneSensor(self,slave):#0~5
        if(slave >= self.ADS_CHILD_MAX_LEN):
            return False
        self.select[slave]=False
        self.SelectAllSensor(self.select)
        return True
    
    def SelectOneSensor(self,slave):#0~7
        if(slave >= self.ADS_CHILD_MAX_LEN):
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
        print(hex(tran))
        self.spi.xfer2([self.RPI_CMD_SET_CH,tran])
        
    def StartSample(self):
        self.spi.xfer2([self.RPI_CMD_START])
        
    def StopSample(self):
        self.spi.xfer2([self.RPI_CMD_STOP])

    def GetFWVersion(self):
        data = self.spi.xfer2([
                self.RPI_CMD_VERSION,
                self.RPI_CMD_VERSION+1,
                self.RPI_CMD_VERSION+2,
                0x0,
                0x0])
        ret = ".".join([str(data[2]),str(data[3]),str(data[4])])
        return ret
        
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
        
    def SetScale(self,channel,value,relay): #if relay==True, add 10 ohm on AIN
        time.sleep(0.01)
        if(value in list(self.ADS_SCALE_VALUE.keys()) and channel < self.ADS_CHILD_MAX_LEN):
            self.scale[channel] = value
            cmd=self.ADS_SCALE_VALUE[value]
            if relay is True:
                cmd=cmd+self.ADS_SCALE_RELAY_OFFSET
            self.spi.xfer2([self.RPI_CMD_SET_SCALE | channel,cmd])
            return True
        return False
        
    def SetFs(self,value):
        if(value in list(self.ADS_FS_VALUE.keys())):
            self.sampleRate = value
            self.spi.xfer2([self.RPI_CMD_SET_FS,self.ADS_FS_VALUE[value]])
            return True
        return False
    
    def ConvertData(self, arr):
        #max_reading=65536
        #index = arr>=(max_reading/2)
        #arr[index]=arr[index] - max_reading
        #return arr
        
        return np.array(arr,dtype=np.int16)
        
    def byte2long(self,b=[0,0,0,0]):
        return b[0] | b[1]<<8 | b[2]<<16 | b[3]<<24
    
    def byte2int(self,b=[0,0]):
        return b[0] | b[1]<<8
    
    
"""
    @classmethod
    def ResetHubHW(cls):
        GPIO.setwarnings(False)
        
        if GPIO.getmode()==-1 or GPIO.getmode()==None:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(cls.HW_RESET_PIN,GPIO.OUT)
        GPIO.output(cls.HW_RESET_PIN,GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(cls.HW_RESET_PIN,GPIO.LOW)
        time.sleep(1)
        GPIO.output(cls.HW_RESET_PIN,GPIO.HIGH)
        time.sleep(2.1)
    """
    
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
        voltageRange = ["15","7.5","1.875"]
        currentRange = ["250","125","31.25","2.5","1.25","0.3125"]
        gainMapping = [1,2,8,1,2,8]
        if not os.path.exists(path):
                os.makedirs(path)
                
        startTimeStr = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(path+"DAQ_log_"+startTimeStr+".txt","w","utf-8")
        handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
        root_logger.addHandler(handler)
        root_logger.addHandler(logging.StreamHandler())
        logging.info("Software version: "+ADCHub.__version__)
        
        
        parser = argparse.ArgumentParser()
        parser.add_argument("bus",type=int,help="SPI bus. Example 0 or 1.",choices=[0,1])
        parser.add_argument("cs",type=int,help="SPI CE. Example 0 or 1.",choices=[0,1])
        parser.add_argument("fs",type=int,help="Sampling rate. Default is 8000Hz. Example 500, 1000, 2000, 4000 or 8000."
                ,choices=[500,1000,2000,4000,8000],nargs='?',default = 8000)
        parser.add_argument("point",type=int,help="Sampling point. Default is 0. if set to zero, processing will not sample. Example 2048"
                ,nargs='?',default = 0)
        parser.add_argument("ch",type=str,help="Enable channel using binary. Default is 11111111. Example input 11000000 to enable channel 1 and 2."
                ,nargs='?',default="11111111")
        parser.add_argument("range",help="Setting each channel range. Voltage module: 15/7.5/1.875 (default is all 15). Current module: 250/128/31.25/2.5/1.25/0.3125 (default is all 250). Use comma to separate. Example voltage module input 15,15,15,7.5,7.5,7.5,1.875,1.875 or input 15 to set all channel"
                ,nargs='?',default="default")
        parser.add_argument("RA",type=float,help="Setting shunt risistance A for all channel(default value reference input range to auto setting). AIN = ADC_IN/RB*(RA+RB) for voltage module"
                ,nargs='?',default=-1)
        parser.add_argument("RB",type=float,help="Setting shunt risistance B for all channel(default value reference input range to auto setting). AIN = ADC_IN/RB*(RA+RB) for voltage module"
                ,nargs='?',default=-1)
        parser.add_argument("RC",type=float,help="Setting shunt risistance C for all channel(default value reference input range to auto setting). AIN = ADC_IN/RC for current module."
                ,nargs='?',default=-1)
        parser.add_argument("cpu",help="Set the cpu core. Example 0,1,2. Default is 3."
                ,nargs='?',default = "3")
        parser.add_argument("-e","--end",help="Auto endding processing",action="store_true")
        parser.add_argument("-r","--raw",help="Save raw data (-32768 ~ 32767). The data is before conversion.",action="store_true")
        
        
        args = parser.parse_args()
        os.system("taskset -cp %s %d" %(args.cpu,os.getpid()))
        if args.bus !=0 and args.bus !=1:
                logging.error("error: invalid spix settng.")
                sys.exit()
        if args.cs !=0 and args.cs !=1:
                logging.error("error: invalid csx settng.")
                sys.exit()
        if args.fs not in [500,1000,2000,4000,8000]:
                logging.error("error: invalid sampling rate value.")
                sys.exit()
        if len(args.ch)!=8:
                logging.error("error: invalid channel enable length.")
                sys.exit()
        else:
                for c in args.ch:
                        if c!="0" and c !="1":
                                logging.error("error: invalid channel value.")
                                sys.exit()
        
        
        if len(args.range.split(','))==1 and args.range!="default" and args.range not in voltageRange and args.range not in currentRange:
                logging.error("error: invalid range value.")
                sys.exit()
                
                
        if len(args.range.split(','))!=8 and len(args.range.split(','))!=1 and args.range!="default":
                logging.error("error: invalid range length.")
                sys.exit()
                
        
        
        fileName = "DAQ_result_"+startTimeStr
        
                
        adc = ADCHub(args.bus*2+args.cs)
        
        maxEnableSensor = 0
        columnName = []
        columnScale = []
        if not adc.CheckSlave():
                logging.error("connect error: bus(%d) cs(%d) cannot get device." %(args.bus,args.cs) )
                sys.exit()
        else:
                logging.info("Board connected!")
                logging.info("Board Version: "+adc.GetFWVersion())
               
        moduleType = adc.CheckSlaveType()
        logging.info("Board type :"+moduleType)
               
               
        resetTestFlag=False
        if resetTestFlag:
                logging.info("Test reset pin.")
                adc.SelectAllSensor([True,True,True,True,True,True,True,True])
                adc.StartSample()
                sampleBuffer=0
                while sampleBuffer<65535:
                        sampleBuffer=adc.GetBufferLen()
                        logging.info("Wait buffer full. "+str(sampleBuffer)+"/65535")
                        time.sleep(0.5)
                logging.info("Buffer full!")
                logging.info("Wait HW reset...")
                ADCHub.ResetHubHW()
                if adc.GetBufferLen()!=0:
                        logging.error("HW reset error!")
                        sys.exit()
                else:
                        logging.error("HW reset testing complete. Funtion OK!")
               
               
        RA = [0]*8
        RB = [0]*8
        RC = [0]*8
        strRA = ["none"]*8
        strRB = ["none"]*8
        strRC = ["none"]*8
        gain = [1]*8
        if moduleType == 'Voltage':
                if args.range=="default":
                        args.range="15,15,15,15,15,15,15,15"
                elif len(args.range.split(','))==1:
                        if args.range not in voltageRange:
                                logging.error("Invalid range value. value follow "+",".join(voltageRange))
                                sys.exit()
                        else:
                                args.range=",".join([args.range]*8)
                        
                for i,c in enumerate(args.range.split(',')):
                        if c not in voltageRange:
                                logging.error("Invalid range value. value follow "+",".join(voltageRange))
                                sys.exit()
                        else:
                                RA[i]=255000
                                RB[i]= 46400
                                strRA[i]="255k"
                                strRB[i]="46.4k"
                                gain[i] = gainMapping[voltageRange.index(c)]
                        
        elif moduleType == 'Current':
                if args.range=="default":
                        args.range="250,250,250,250,250,250,250,250"
                elif len(args.range.split(','))==1:
                        if args.range not in currentRange:
                                logging.error("Invalid range value. value follow "+",".join(currentRange))
                                sys.exit()
                        else:
                                args.range=",".join([args.range]*8)
                for i,c in enumerate(args.range.split(',')):
                        if c not in currentRange:
                                logging.error("Invalid gain value. value follow 1, 2 or 8")
                                sys.exit()
                        else:
                                if currentRange.index(c)>=3:
                                        strRC[i]="940"
                                        RC[i]= 940
                                else:
                                        strRC[i]="9.53"
                                        RC[i]= 9.53
                                gain[i] = gainMapping[currentRange.index(c)]
                                
        else:
                logging.error("Invalid gain value. value follow 1, 2 or 8")
                sys.exit()
                
        if args.RA!=-1:
                RA=[args.RA]*8
                strRA = [str(args.RA)]*8
        if args.RB!=-1:
                RB=[args.RB]*8
                strRB = [str(args.RB)]*8
        if args.RC!=-1:
                RC=[args.RC]*8
                strRC = [str(args.RC)]*8
                
               
        #----------------------------------
        logging.info("Start testing:")
        logging.info("bus: %d" %args.bus)
        logging.info("cs: %d" %args.cs)
        logging.info("fs: %d" %args.fs)
        logging.info("sample point: %d" %args.point)
        logging.info("ch:"+args.ch)
        logging.info("range:"+args.range)
        logging.info("RA:"+",".join(strRA))
        logging.info("RB:"+",".join(strRB))
        logging.info("RC:"+",".join(strRC))
        
        
        if "1" not in  args.ch or args.point<=0:
                if not args.end:
                        input("Press enter to end the processing")
                sys.exit()
                
        logging.info("Enable sensor at device...")
        enableSensorList = []
        for i,enableSensor in enumerate(args.ch):
                if enableSensor=="1":
                        maxEnableSensor = maxEnableSensor+1
                        columnName.append("ch"+str(i+1))
                        logging.info("\tcannel %d enable... OK!" % (i+1))
                        enableSensorList.append(True)
                else:
                        logging.error("\tcannel %d pass." % (i+1))
                        enableSensorList.append(False)
        adc.SelectAllSensor(enableSensorList)
        print(enableSensorList)
                        
                        
        logging.info("gain scale of sensor...")
        for i,g in enumerate(gain):
                if adc.select[i]:
                        adc.SetScale(i,g,False)
                        columnScale.append(g)
                
                
        logging.info("Setting sampling rate...")
        adc.SetFs(args.fs)
                
                
        logging.info("Start sample...")
        perSampleLen = maxEnableSensor*2
        totalDataLen = perSampleLen*args.point
        sleepInterval = min(1,65536/(perSampleLen*args.fs)/10)
        
        logging.info("Sample interval: {:.3f} sec.".format(sleepInterval))
        realFs=0
        resultIndex = 0
        resultArr = np.zeros(totalDataLen)
        
        #wiat ADC refer correct
        #time.sleep(3)
        adc.StartSample()
        
        time.sleep(0.01)
        startTime = time.time()
        dataLen = adc.GetBufferLen()
        endTime = startTime
        adc.GetBuffer((dataLen//perSampleLen)*perSampleLen)
        #print("sync time",(dataLen//perSampleLen)*perSampleLen)
        #refrech buffer and sync time
        
        maxSampleTime = (args.point/args.fs)*1.05
        while time.time()-startTime < maxSampleTime and resultIndex < totalDataLen:
                sleepTime = sleepInterval-(time.time()-endTime)
                if sleepTime>0:
                        time.sleep(sleepTime)
                
                endTime = time.time()
                dataLen = adc.GetBufferLen()
                if dataLen==65535:
                        logging.error("Buffer overflow!")
                        
                if dataLen>0:
                        data = adc.GetBuffer(dataLen)
                        endPoint = resultIndex+dataLen
                        if endPoint>totalDataLen:
                               resultArr[resultIndex:] =  data[:dataLen-(endPoint-totalDataLen)]
                        else:
                               resultArr[resultIndex:resultIndex+dataLen] = data
                               
                        resultIndex = resultIndex+dataLen
                        realFs = resultIndex/(endTime-startTime)/perSampleLen
                        logging.info("Get bugger length: {dataLen} average fs: {a:.2f} , finished: {b:.2f}%".format(dataLen=dataLen,a=realFs,b=min(resultIndex/totalDataLen*100,100)))
        
        adc.StopSample()
        resultArr = resultArr[0::2]*256+resultArr[1::2]
        resultArr = adc.ConvertData(resultArr)
        resultArr = resultArr.reshape(-1,maxEnableSensor).T
        df = pd.DataFrame()
        for i in range(0,resultArr.shape[0]):
                if args.raw:
                        df[columnName[i]]=resultArr[i]
                else:
                        if moduleType=="Voltage":
                                df[columnName[i]]=resultArr[i]/32768.0*2.4/columnScale[i]/RB[i]*(RA[i]+RB[i])*1000
                        else:
                                df[columnName[i]]=resultArr[i]/32768.0*2.4/columnScale[i]/RC[i]*1000
                
        unit = "mA"
        if moduleType=="Voltage":
                unit="mV"
        for i in df.columns:
                logging.info(i+":")
                logging.info("\tMean: %lf %s" % (np.mean(df[i]),unit))
                logging.info("\tMax: %lf %s" % (max(df[i]),unit))
                logging.info("\tMin: %lf %s" % (min(df[i]),unit))
                logging.info("\tp-p: %lf %s" % (max(df[i])-min(df[i]),unit))
        
        path = "data/"
        if not os.path.exists(path):
                os.makedirs(path)
        
        if args.raw:
                fileName = fileName+"(raw).csv"
        else:
                fileName = fileName+"("+unit+").csv"
        df.to_csv(path+fileName,index=False)
        logging.info("Output data:"+path+fileName)
        
        
        if not args.end:
                input("Press enter to end the processing")
        

