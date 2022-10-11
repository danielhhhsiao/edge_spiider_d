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
        
        #self.ResetHub()
        
    
    
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
        import sys
        import time
        import argparse
        import pandas as pd
        import numpy as np
        
        fs=8000
        point=8000
        voltageRange = ["15","7.5","1.875"]
        currentRange = ["250","125","31.25","2.5","1.25","0.3125"]
        gainMapping = [1,2,8,1,2,8]
                
        
        parser = argparse.ArgumentParser()
        parser.add_argument("bus",type=int,help="SPI bus. Example 0 or 1.",choices=[0,1])
        parser.add_argument("cs",type=int,help="SPI CE. Example 0 or 1.",choices=[0,1])
        parser.add_argument("board_type",type=int,help="Select board type. (0:voltage. 1:current.) Example 0 or 1.",choices=[0,1])
        parser.add_argument("parameter",type=str,help="Input binary to select channel for '-c' (ex: Input 11000000 to use 1 and 2 ch). Input version to be target for '-v'.",nargs='?',default = "")
        parser.add_argument("range",help="Setting each channel range. Voltage module: 15/7.5/1.875 (default is 15). Current module: 250/128/31.25/2.5/1.25/0.3125 (default is 250). Use comma to separate. Example voltage module input 15 to set all channel"
                ,nargs='?',default="default")
        parser.add_argument("max_threshold",type=float,help="Maximum condition of pass. This value have to be greater min_threshold."
                ,nargs='?',default="999")
        parser.add_argument("min_threshold",type=float,help="Minimum condition of pass. This value have to be less max_threshold."
                ,nargs='?',default="-999")
        parser.add_argument("check_type",type=float,help="Select result type. (0:p-p. 1:mean. 2:max. 3:min. 4:RMS. 5:main frequiency.)"
                ,nargs='?',default="0",choices=[0,1,2,3,4,5])
        parser.add_argument("-c","--channel",help="Select channel to validation by binary. Need input 'parameter' to setting.",action="store_true")
        parser.add_argument("-v","--version",help="Check FW version. Need input 'parameter' to be the target.",action="store_true")
        parser.add_argument("-f","--fill",help="Will be fill module buffer.",action="store_true")
        parser.add_argument("-e","--empty",help="Check buffer is empty.",action="store_true")
        
        
        args = parser.parse_args()
        if args.bus !=0 and args.bus !=1:
                print("error: invalid spix settng.")
                sys.exit()
        if args.cs !=0 and args.cs !=1:
                print("error: invalid csx settng.")
                sys.exit()
        if not args.channel and not args.version and not args.fill and not args.empty:
                print("error: Not select any arguments. Use -h to look infotmation.")
                sys.exit()
        if(args.channel):
                if args.parameter=="":
                        args.parameter="00000000"
                        
                if len(args.parameter)!=8:
                        print("error: invalid channel length.")
                        sys.exit()
                else:
                        for c in args.parameter:
                                if c!="0" and c !="1":
                                        print("error: invalid channel value.")
                                        sys.exit()
                if len(args.range.split(','))!=1 and args.range!="default":
                        print("error: invalid range length.")
                        sys.exit()
                        
                if  args.board_type==0 and args.range not in voltageRange and args.range!="default":
                        print("error: invalid range value.")
                        sys.exit()
                        
                if  args.board_type==1 and args.range not in currentRange and args.range!="default":
                        print("error: invalid range value.")
                        sys.exit()
                        
                if  args.max_threshold < args.min_threshold:
                        print("error: invalid value. The max_threshold have to be greater than min_threshold.")
                        sys.exit()
                         
        if(args.version):  
                if len(args.parameter.split('.'))!=3:  
                        print("error: invalid version target format.")
                        sys.exit()  
                else:
                        for c in args.parameter.split('.'):
                                try:
                                        int(c)
                                except:
                                        print("error: invalid version target format.")
                                        sys.exit()   
        
                
        
        
        adc = ADCHub(args.bus*2+args.cs)
        maxEnableSensor = 0
        columnName = []
        columnScale = []
        if not adc.CheckSlave():
                print("FAIL")
                sys.exit()
               
        moduleType = adc.CheckSlaveType()
        if args.board_type==0 and moduleType!="Voltage":
                print("FAIL")
                sys.exit()
        if args.board_type==1 and moduleType!="Current":
                print("FAIL")
                sys.exit()
                
        if args.empty:
                dataLen = adc.GetBufferLen()
                if dataLen==0:
                        print("PASS")
                        sys.exit()
                else:
                        print("FAIL")
                        sys.exit()
        adc.ResetHub()
        if(args.version):
                if args.parameter == adc.GetFWVersion():
                        print("PASS")
                        sys.exit()
                else:
                        print("FAIL")
                        sys.exit()
        elif args.fill:
                adc.SetFs(fs)
                adc.SelectAllSensor([True,True,True,True,True,True,True,True])
                adc.StartSample()
                time.sleep(1)
                
                dataLen = adc.GetBufferLen()
                if dataLen==65535:
                        print("PASS")
                        sys.exit()
                else:
                        print("FAIL")
                        sys.exit()
               
               
               
                        
        elif args.channel: 
                if args.parameter=="00000000":
                        print("PASS")
                        sys.exit()
               
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
                                args.range=",".join([args.range]*8)
                                
                        for i,c in enumerate(args.range.split(',')):
                                RA[i]=255000
                                RB[i]= 46400
                                strRA[i]="255k"
                                strRB[i]="46.4k"
                                gain[i] = gainMapping[voltageRange.index(c)]
                                
                elif moduleType == 'Current':
                        if args.range=="default":
                                args.range="250,250,250,250,250,250,250,250"
                        elif len(args.range.split(','))==1:
                                args.range=",".join([args.range]*8)
                        for i,c in enumerate(args.range.split(',')):
                                if currentRange.index(c)>=3:
                                        strRC[i]="940"
                                        RC[i]= 940
                                else:
                                        strRC[i]="9.53"
                                        RC[i]= 9.53
                                gain[i] = gainMapping[currentRange.index(c)]
                                
                else:
                        print("FAIL")
                        sys.exit()
                
                        
                enableSensorList = []
                for i,enableSensor in enumerate(args.parameter):
                        if enableSensor=="1":
                                maxEnableSensor = maxEnableSensor+1
                                columnName.append("ch"+str(i+1))
                                enableSensorList.append(True)
                        else:
                                enableSensorList.append(False)
                adc.SelectAllSensor(enableSensorList)
                     
                                
                for i,g in enumerate(gain):
                        if adc.select[i]:
                                adc.SetScale(i,g,False)
                                columnScale.append(g)
                        
                adc.SetFs(fs)
                        
                perSampleLen = maxEnableSensor*2
                totalDataLen = perSampleLen*point
                sleepInterval = min(1,65536/(perSampleLen*fs)/10)
                
                realFs=0
                resultIndex = 0
                resultArr = np.zeros(totalDataLen)
                
                adc.StartSample()
                
                time.sleep(0.01)
                startTime = time.time()
                dataLen = adc.GetBufferLen()
                endTime = startTime
                adc.GetBuffer((dataLen//perSampleLen)*perSampleLen)
                
                maxSampleTime = (point/fs)*1.05
                while time.time()-startTime < maxSampleTime and resultIndex < totalDataLen:
                        sleepTime = sleepInterval-(time.time()-endTime)
                        if sleepTime>0:
                                time.sleep(sleepTime)
                        
                        endTime = time.time()
                        dataLen = adc.GetBufferLen()
                        if dataLen==65535:
                                print("FAIL")
                                sys.exit()
                                
                        if dataLen>0:
                                data = adc.GetBuffer(dataLen)
                                endPoint = resultIndex+dataLen
                                if endPoint>totalDataLen:
                                       resultArr[resultIndex:] =  data[:dataLen-(endPoint-totalDataLen)]
                                else:
                                       resultArr[resultIndex:resultIndex+dataLen] = data
                                       
                                resultIndex = resultIndex+dataLen
                                realFs = resultIndex/(endTime-startTime)/perSampleLen
                                #logging.info("Get bugger length: {dataLen} average fs: {a:.2f} , finished: {b:.2f}%".format(dataLen=dataLen,a=realFs,b=min(resultIndex/totalDataLen*100,100)))
                
                adc.StopSample()
                resultArr = resultArr[0::2]*256+resultArr[1::2]
                resultArr = adc.ConvertData(resultArr)
                resultArr = resultArr.reshape(-1,maxEnableSensor).T
                df = pd.DataFrame()
                result=[]
                for i in range(0,resultArr.shape[0]):
                        if moduleType=="Voltage":
                                df[columnName[i]]=resultArr[i]/32768.0*2.4/columnScale[i]/RB[i]*(RA[i]+RB[i])
                        else:
                                df[columnName[i]]=resultArr[i]/32768.0*2.4/columnScale[i]/RC[i]
           
                        if args.check_type==0:
                                result.append(max(df[columnName[i]])-min(df[columnName[i]]))
                        elif args.check_type==1:
                                result.append(np.mean(df[columnName[i]]))
                        elif args.check_type==2:
                                result.append(max(df[columnName[i]]))
                        elif args.check_type==3:
                                result.append(min(df[columnName[i]]))
                        elif args.check_type==4:
                                result.append(np.sqrt(np.mean(np.array(df[columnName[i]])**2)))
                        elif args.check_type==5:
                                f = np.fft.fft(df[columnName[i]])
                                f = abs(f)
                                f = f[:len(f)//2]
                                f_index = np.argmax(f)
                                #delta f is 1, so main f = f_index*1 = f_index
                                result.append(f_index)
                        else:
                                print("FAIL")
                                sys.exit()
                        
                for v in result:
                        if v > args.max_threshold or v < args.min_threshold:
                                print("FAIL")
                                sys.exit()
                print("PASS")
                sys.exit()
        else:
                print("FAIL")
                sys.exit()
                       

