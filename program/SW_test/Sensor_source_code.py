#cython: language_level=3

import sys
sys.path.extend(['',
 '/home/pi',
 '/usr/lib/python37.zip',
 '/usr/lib/python3.7',
 '/usr/lib/python3.7/lib-dynload',
 '/home/pi/.local/lib/python3.7/site-packages',
 '/usr/local/lib/python3.7/dist-packages',
 '/usr/local/lib/python3.7/dist-packages/Adafruit_ADS1x15-1.0.2-py3.7.egg',
 '/usr/lib/python3/dist-packages',
 '/usr/lib/python3/dist-packages/IPython/extensions',
 '/home/pi/.ipython'])


import time
import datetime
from dateutil.relativedelta import relativedelta
import os
import glob
import pandas as pd
import configparser
import shutil
import multiprocessing
import spidev
import board
import busio
import RPi.GPIO as GPIO
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
import adafruit_ads1x15.ads1015 as ADS1
from adafruit_ads1x15.analog_in import AnalogIn
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import urllib.request
import json

try:
    #for self test
    import phm_func  as phm_func
    from PLClib import PLC
except:
    #for compiler
    import Library.phm_func as phm_func
    from Library.PLClib import PLC

from serial.tools import list_ports
import serial
import struct
import matplotlib.pyplot as plt

scale_2G = 0x00    #16384
scale_4G = 0x08    #8192
scale_8G = 0x10    #4096
scale_16G = 0x18   #2048

scale_250dps = 0x00    #16384
scale_500dps = 0x08    #8192
scale_1000dps = 0x10    #4096
scale_2000dps = 0x18   #2048

MAX_ADS1x15_CHIP=4
MAX_KASHIYAMA_CHIP=4
MAX_CHIP_CH_TYPE=4
VIB_SPI_CLOCK=976500
ADXL_SPI_CLOCK=976500
ESP_SPI_CLOCK=1953000
#SPI_CLOCK=7629
#SPI_CLOCK=976500
ESP32_RDY=25
ESP32_RESET=27
ESP32_CS=8
#MPU9250 REGISTER
REGISTER_READ_FLAG          =0x80
REGISTER_SRD                =0x19
REGISTER_CONFIG             =0x1A
REGISTER_GYRO_CONFIG        =0x1B
REGISTER_ACC_CONFIG1        =0x1C
REGISTER_ACC_CONFIG2        =0x1D
REGISTER_FIFO_ENABLE        =0x23
REGISTER_I2C_MST_CTRL       =0x24
REGISTER_INT_ENABLE         =0x38
REGISTER_USER_CTRL          =0x6A
REGISTER_PWR_MGMT_1         =0x6B
REGISTER_PWR_MGMT_2         =0x6C
REGISTER_BUF_VALUE          =0x74
REGISTER_WHO_AM_I           =0x75
CONTENT_I_AM_MPU9250        =0x71
CONTENT_RESET_CHIP          =0x80
CONTENT_RESET_FIFO          =0x04
CONTENT_ENABLE_FIFO         =0x40
CONTENT_CLK_SEL_IN_20M      =0x00
CONTENT_CLK_SEL_PLL1        =0x01
CONTENT_ACC_SCALE_2G        =0x00
CONTENT_ACC_SCALE_4G        =0x08
CONTENT_ACC_SCALE_8G        =0x10
CONTENT_ACC_SCALE_16G       =0x18
CONTENT_GYRO_SCALE_250dps   =0x00
CONTENT_GYRO_SCALE_500dps   =0x08
CONTENT_GYRO_SCALE_1000dps  =0x10
CONTENT_GYRO_SCALE_2000dps  =0x18
CONTENT_FIFO_ACC            =0x8
CONTENT_FIFO_GYRO           =0x70
CONTENT_SAMPLE_RATE_Acc_4K_ACC_CONFIG2    =0x8 
CONTENT_SAMPLE_RATE_Acc_1K_ACC_CONFIG2    =0x0 
CONTENT_SAMPLE_RATE_Gyro_8K_CONFIG        =0x7
CONTENT_SAMPLE_RATE_Gyro_1K_CONFIG        =0x1

#ESP3 REGISTER
#Basic command
COMMAND_INIT        =0x80
COMMAND_START       =0x81
COMMAND_END         =0x82
COMMAND_GET_BUF_C   =0x83
COMMAND_READ_BUF    =0x84
COMMAND_GET_TIME    =0x85
COMMAND_SET_TIMER   =0x86
CONTENT_CTRL_ALL    =0xFF
CONTENT_ENABLE      =0x10
CONTENT_DISABLE     =0x00
CONTENT_BUF_BTYE     =128
CONTENT_GAIN_DICT=dict()
CONTENT_GAIN_DICT["6144mV"]         =0x00
CONTENT_GAIN_DICT["4096mV"]         =0x10
CONTENT_GAIN_DICT["2048mV"]         =0x20
CONTENT_GAIN_DICT["1024mV"]         =0x30
CONTENT_GAIN_DICT["512mV"]          =0x40
CONTENT_GAIN_DICT["256mV"]          =0x50
CONTENT_CHANNEL_DICT=dict()
CONTENT_CHANNEL_DICT["AIN0_AIN1"]    =0x0
CONTENT_CHANNEL_DICT["AIN0_AIN3"]    =0x1
CONTENT_CHANNEL_DICT["AIN1_AIN3"]    =0x2
CONTENT_CHANNEL_DICT["AIN2_AIN3"]    =0x3
CONTENT_CHANNEL_DICT["AIN0_GND"]     =0x4
CONTENT_CHANNEL_DICT["AIN1_GND"]     =0x5
CONTENT_CHANNEL_DICT["AIN2_GND"]     =0x6
CONTENT_CHANNEL_DICT["AIN3_GND"]     =0x7
MODULE_IS_12_BIT=dict()
MODULE_IS_12_BIT["ADS1115"]         =False
MODULE_IS_12_BIT["ADS1015"]         =True
CONTENT_TIMER_FREQ=dict()
CONTENT_TIMER_FREQ[100]             =0
CONTENT_TIMER_FREQ[200]             =1
CONTENT_TIMER_FREQ[400]             =2
CONTENT_TIMER_FREQ[800]             =3
CONTENT_TIMER_FREQ[1000]            =4
CONTENT_TIMER_FREQ[1600]            =5
CONTENT_TIMER_FREQ[2000]            =6
CONTENT_TIMER_FREQ[2500]            =7
CONTENT_TIMER_FREQ[3000]            =8


__version__ = '3.8.2_2022_0302_Improve prognosis processing cpu core.'

def aes_encrypt(data, key):
    _IV = 16 * '\x00'
    data_cnt = len(data) % 16
    if (data_cnt != 0):
        add = 16 - (data_cnt)
        data = data + ('\0' * add)
   
    cryptor = AES.new(key, AES.MODE_CBC, _IV)    
    return b2a_hex(cryptor.encrypt(data))

def decrypt( data, key):  
    _IV = 16 * '\x00'
    cryptor = AES.new(key, AES.MODE_CBC, _IV)
    data_cnt = len(data) % 16
    if (data_cnt != 0):
        add = 16 - (data_cnt)
        data = data + ('\0' * add)
    return cryptor.decrypt(data)    

def GetRaspberryPiInfo() :
    #Serial
    f = open('/proc/cpuinfo','r')
    for line in f:
        if line[0:6] == 'Serial':
            serial_no = line[10:26]
 
    #wlan mac
    f = open('/sys/class/net/wlan0/address','r')
    for line in f:
        wlan_mac_no = line.replace(':','')
 
    id_num = serial_no + wlan_mac_no
    
    return id_num

def createTemporaryKey(key_file_name) :
    _IV = 16 * '\x00'
    id_num = GetRaspberryPiInfo()
    due_day= (datetime.date.today() + relativedelta(months=+6)).strftime('%Y%m%d')
    key = '202005_MMFA00Key'
    #aes_value = str(aes_encrypt(due_day+'00000000'+id_num, key))
    data = due_day+'00000000'+id_num[0:16]
    aes = AES.new(key, AES.MODE_CBC, _IV)
    encd = aes.encrypt(data)
    #encd1 = b2a_hex(aes.encrypt(data))
    key_file_name = phm_func.home_path + '/.tempkey'
    #key_file_name =  './.tempkey'
    fp = open(key_file_name, 'wb')
    fp.write(encd)
    fp.close()
    return True
    


def CheckExpireDate(key_file_name) :
    _IV = 16 * '\x00'
    #id_num = GetRaspberryPiInfo()
    key_file_name = './.tempkey'
    key = '202005_MMFA00Key'
    f = open(key_file_name,'rb')
    for line in f:
        key_no = line
    key = '202005_MMFA00Key'
    aes = AES.new(key, AES.MODE_CBC, _IV)
    decd = aes.decrypt(key_no)
    curr_day= (datetime.date.today()).strftime('%Y%m%d')
    #due_day = '       '
    #for x in range(0,8) :
    due_day = ''
    for i in range(0,8) :
        due_day = due_day + chr(decd[i])
    #due_day = chr(decd[0]) + chr(decd[1])+ chr(decd[2])+ chr(decd[3])+ chr(decd[4])+ chr(decd[5])+ chr(decd[6])+ chr(decd[7])
    if ( curr_day < due_day) :
        #decrypt(key_no, key)
        print('Temporary key, due date :',due_day)
        return True
    else :
        print('Temporary key duedate expired, due date :',due_day)
        return False
 
def aes_decrypt(data, key):
    _IV = 16 * '\x00'
    cryptor = AES.new(key, AES.MODE_CBC, _IV)
    return cryptor.decrypt(data)
    
def key_chk(setting_dic):
    #read key
    key_file_name = phm_func.home_path + '/.key'
    if not os.path.isfile(key_file_name):        
        print('\n\nERROR:Key file is not found!', key_file_name,'\n\n')
        #print(setting_dic.get('temp_key'), setting_dic['eqp_name'])
        tempKey = getDict(setting_dic,'temp_key', 'Key')
        if ( tempKey == 'TemporaryKey') :
            print('Use Temp Key')
            key_file_name = phm_func.home_path + '/.tempkey'
            if not os.path.isfile(key_file_name):
                print('Create temporary key file.')
                createTemporaryKey(key_file_name)
                return True
            else :
                print('Check temporary key file Due date.')                
                return (CheckExpireDate(key_file_name))
        raise Exception('Key file is not found!')
        #return False
       
    f = open(key_file_name,'r')
    for line in f:
        key_no = line
   
    
    id_num = GetRaspberryPiInfo()
    #AES
    key = '2019_mmfa_earlwu'
    aes_value = str(aes_encrypt(id_num, key))
   
    if(key_no == aes_value):
        return True
    else:
        raise Exception('Bad key file!')
        #print('ERROR:Bad key file!')
       
    #return False
 
def getDict(dic,key, default=None):
    val=dic.get(key, default)
    if val=="":
        return default
    return val

CPU_CORE_NUM=3
def pairCPUcore():
    global CPU_CORE_NUM
    ret=CPU_CORE_NUM
    CPU_CORE_NUM -=1
    if CPU_CORE_NUM<0:
        CPU_CORE_NUM=3
    return ret

class esp32_process():
    def __init__(self,ADS_dict,sapleRate,sec):
#                 chip_type = 'ADS1115', chip_no=1, channel_no=1, conn_type=2, signal_type='CT', voltage_rage='4',ct_ohm = 1000, scale_low=-5.0, scale_high=5.0):
        self.ADS_dict = ADS_dict
        self.sapleRate = sapleRate
        self.sec=sec
        print("ESP32 sample rate is",self.sapleRate)
        
        global ESP32_RDY
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ESP32_RDY, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(ESP32_RESET, GPIO.OUT)
        GPIO.output(ESP32_RESET,GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(ESP32_RESET,GPIO.HIGH)
        time.sleep(0.5)
        
        self.spi=spidev.SpiDev()
        self.spi.open(0,0) # bus,device
        self.spi.mode=0
        self.spi.max_speed_hz =ESP_SPI_CLOCK

        print("**debug** esp32 spi clock =",ESP_SPI_CLOCK)
        GPIO.setup(ESP32_CS, GPIO.OUT)
        GPIO.output(ESP32_CS, GPIO.HIGH)
        for chip in range(MAX_ADS1x15_CHIP):
            self.send([COMMAND_INIT,
               CONTENT_DISABLE | chip,
               0x0,0x0])
        for chip in range(MAX_ADS1x15_CHIP):
            if ADS_dict[chip]["enable"] is False:
                continue
            #setting channal
            """
            if ADS_dict[chip]["type"]=="ADS1115":
                self.ADS_dict[chip]["maxResolve"]=2**16
            else:
                self.ADS_dict[chip]["maxResolve"]=2**12
            """
            self.ADS_dict[chip]["maxResolve"]=2**16 #ADS1115,ADS1015 is the same
            #print(chip)
            #print(ADS_dict[chip]["channal"])
            channal=CONTENT_CHANNEL_DICT[ADS_dict[chip]["channal"]] 
            #setting gain
            gain=CONTENT_GAIN_DICT[ADS_dict[chip]["gain"]]
            
            self.send([COMMAND_INIT,
               CONTENT_ENABLE | chip,
               gain | channal,0x0])
                    
                    
        sample_rate=CONTENT_TIMER_FREQ[sapleRate]
        self.send([COMMAND_SET_TIMER,sample_rate,0x0,0x0])
        
    def send(self,data,f=ESP_SPI_CLOCK,wait=0):
        global ESP32_RDY
#        print("spi send",data)
        while GPIO.input(ESP32_RDY)!=1:
    #        print("wiat")
            time.sleep(0.001)
        
        ret = self.spi.xfer2(data,f,wait)
#        print("spi receive",ret)
        return ret
    
    def check_time(self,sec=0.01):
        self.send([COMMAND_GET_TIME,0x0,0x0,0x0])
        startTimeRpi=time.perf_counter()
        startTimeESP=self.send([0x0,0x0,0x0,0x0])
        startTimeESP=self.byte2long(startTimeESP)
        time.sleep(sec)
        self.send([COMMAND_GET_TIME,0x0,0x0,0x0])
        endTimeRpi=time.perf_counter()
        endTimeESP=self.send([0x0,0x0,0x0,0x0])
        endTimeESP=self.byte2long(endTimeESP)
        distanceRpi=endTimeRpi-startTimeRpi
        distanceESp=(endTimeESP-startTimeESP)*0.000001 #us to s
        if endTimeESP<0:
            return self.check_time(sec)
        else:
            return (distanceESp-distanceRpi)/distanceRpi
        
        
    def byte2long(self,b=[0,0,0,0]):
        return b[0] | b[1]<<8 | b[2]<<16 | b[3]<<24
    
    def get_buf_count(self):
        self.send([COMMAND_GET_BUF_C,0x0,0x0,0x0])
        data=self.send([0xFF,0xFF,0xFF,0xFF])
        return data[0]
    
    def get_sample(self):
        debug=False
        err_range=1.03
        wait_sample_dalay=(1/self.sapleRate*61)*3
        sample_target=self.sapleRate*self.sec
        max_sample_len=int(sample_target*err_range)
        result=[]
        timeList=[]
        totalTime=[]
        for i in range(MAX_ADS1x15_CHIP):
            result.append(np.zeros(max_sample_len,dtype=np.int))
            timeList.append(np.zeros(max_sample_len,dtype=np.float))
        sampleCount=[0]*MAX_ADS1x15_CHIP
        sampleOK=[False]*MAX_ADS1x15_CHIP
        resetFlag=[False]*MAX_ADS1x15_CHIP
        zeroCount=0
        #start sample
        self.send([COMMAND_START,CONTENT_CTRL_ALL,0x0,0x0])
        startTime=time.time()
        totalTime=[]
        for i in range(MAX_ADS1x15_CHIP):
            totalTime.append(startTime)
        time.sleep(wait_sample_dalay)
        lastTime=[-1]*MAX_ADS1x15_CHIP
        minFs=[1000]*MAX_ADS1x15_CHIP
        while time.time()-startTime<self.sec:
            #gat buffer count
            count=self.get_buf_count()
            getValue=False
#            print(int(time.time()-startTime),"s, count=",count)
            if count>0:
                self.send([COMMAND_READ_BUF,count,0x0,0x0])
                for j in range(count):
                    data=self.send([0]*CONTENT_BUF_BTYE)
                    if data[1]==66 and data[2]==77 and data[3]==88: #check data
                        print("****************************miss req")
                        break
                    if data[1]==0xFF: #check data
                        print("****************************queue empty")
                        continue
                    if data[1]!=0: #check data
                        print("****************************garbage")
                        break
                    
                    getValue=True
                    module_index=int(data[0])
                    
                    if sampleOK[module_index] is True:
                        continue
                    defaultSampleCount=61
                    if sampleCount[module_index]+defaultSampleCount>=max_sample_len:
                        defaultSampleCount=max_sample_len-sampleCount[module_index]
                    timestamp=self.byte2long(data[2:6])
                    if(timestamp<lastTime[module_index] 
                        and timestamp>20000000): #first 20s don't check
                        print("ADSxx15 module",self.ADS_dict[module_index]["name"],"data error!!!")
                        continue
                    if lastTime[module_index]==-1: #first do it, only get time
                        lastTime[module_index]=timestamp
                        continue
                    else:
                        diffTime=timestamp-lastTime[module_index]
                        if diffTime<0:
                            diffTime=diffTime+0xFFFFFFFF
                        if diffTime==0:
                            print("data replease !!!! skip it.")
                            continue
                        diffTime=diffTime*0.000001
                        timeList[module_index][sampleCount[module_index]:sampleCount[module_index]+defaultSampleCount]=totalTime[module_index]+((diffTime/61)*np.array(range(defaultSampleCount),dtype=np.float))
                        if debug is True:
                            Fs=defaultSampleCount/(diffTime)
                            if(Fs<minFs[module_index]):
                                minFs[module_index]=Fs
                            #print(module_index,", minFs=",minFs[module_index],", Fs=",Fs)
                    lastTime[module_index]=timestamp
                    totalTime[module_index]+=diffTime
                    result[module_index][sampleCount[module_index]:sampleCount[module_index]+defaultSampleCount]=np.array(data[7:6+defaultSampleCount*2:2])*256+data[6:6+defaultSampleCount*2:2]
                    sampleCount[module_index]+=defaultSampleCount
                    
                    if sampleCount[module_index]>=max_sample_len:
                        sampleOK[module_index]=True
                        resetFlag[module_index]=True
                        
                for i in range(MAX_ADS1x15_CHIP):
                    if(resetFlag[i]):
                        resetFlag[i]=False
                        self.send([COMMAND_END,i,0x0,0x0])
            if getValue is True:
                zeroCount=0
            else:
                zeroCount+=1
                
            if zeroCount <3:
                time.sleep(wait_sample_dalay)
            else:
                time.sleep(wait_sample_dalay/2)
                
            if zeroCount >10:
                print("ESP32 is empty")
                raise Exception('I2C bus has error for ESP32. Please check I2C switch.')
                
        self.send([COMMAND_END,CONTENT_CTRL_ALL,0x0,0x0])
        minSampleCount=max_sample_len
        for i in range(MAX_ADS1x15_CHIP):
            if self.ADS_dict[i]["enable"] and sampleCount[i]<minSampleCount:
                minSampleCount=sampleCount[i]
                
        ret={}
        for i in range(MAX_ADS1x15_CHIP):
            if self.ADS_dict[i]["enable"]:
                result[i]=result[i][:minSampleCount]
                ret[self.ADS_dict[i]["name"]]=self.value_convert(
                        result[i],
                        self.ADS_dict[i]["differantial"],
                        self.ADS_dict[i]["maxResolve"],
                        self.ADS_dict[i]["maxV"],
                        self.ADS_dict[i]["V_off"],
                        self.ADS_dict[i]["conv"],
                        self.ADS_dict[i]["offset"])
                ret['timestamp']=timeList[i][:minSampleCount] #use final list
                if debug is True:
                    """ falling edge check for test
                    """
                    thres=sum(result[i][:100])/100
                    folling=0
                    lastS=result[i][0]>thres
                    for j in result[i]:
                        judge=j>thres
                        if(lastS is not judge):
                            if lastS == True:
                                folling=folling+1
                            lastS = judge
                    print(i,"falling edge is",folling,"(Len=",len(result[i]),"). minFs is",minFs[i])
                result[i]=None
                timeList[i]=None
        result=None #release
        return ret
           
    def value_convert(self,arr,differantial,maxResolve,maxV,V_off=0,scale=0,offset=0):
        if differantial:
            arr[arr>=(maxResolve//2)]=arr[arr>=(maxResolve//2)]-maxResolve
        return (arr/(maxResolve//2)*maxV-V_off)*scale+offset

  
class ads1115_process(multiprocessing.Process):
    def __init__(self,address,ADS_dict,sec):
        multiprocessing.Process.__init__(self)
        self.ADS_dict = ADS_dict
        self.sec=sec
        self.CPUcore=pairCPUcore()
        self.exit = multiprocessing.Event()
        self.sapleRate = ADS_dict["Fs"]
        print("Sensor",ADS_dict["name"],"sample rate is",self.sapleRate)
            
        i2c = busio.I2C(board.SCL, board.SDA)
        # Create the ADC object using the I2C bus
        if ( ADS_dict["type"] == 'ADS1015' ):
            ads = ADS1.ADS1015(i2c,address = address)  #0x48, 0x49, 0x4A
            ads.data_rate = 3300
        else :
            ads = ADS.ADS1115(i2c,address = address)  #0x48, 0x49, 0x4A
            ads.data_rate = 860
        ads.mode=0x0000 #continue
        if (ADS_dict["gain"] == '6144mV') :
            ads.gain = 0.6666666666666666
        elif (ADS_dict["gain"] == '4096mV') :
            ads.gain = 1
        elif (ADS_dict["gain"] == '2048mV') :
            ads.gain = 2
        elif (ADS_dict["gain"] == '1024mV') :
            ads.gain = 4
        elif (ADS_dict["gain"] == '512mV') :
            ads.gain = 8
        elif (ADS_dict["gain"] == '256mV') :
            ads.gain = 16
            
        if ADS_dict["channal"]=="AIN0_AIN1":
            self.chan = AnalogIn(ads, ADS.P0, ADS.P1)
        elif ADS_dict["channal"]=="AIN2_AIN3":
            self.chan = AnalogIn(ads, ADS.P2, ADS.P3)
        elif ADS_dict["channal"]=="AIN0_GND":
            self.chan = AnalogIn(ads, ADS.P0)
        elif ADS_dict["channal"]=="AIN1_GND":
            self.chan = AnalogIn(ads, ADS.P1)
        elif ADS_dict["channal"]=="AIN2_GND":
            self.chan = AnalogIn(ads, ADS.P2)
        elif ADS_dict["channal"]=="AIN3_GND":
            self.chan = AnalogIn(ads, ADS.P3)  
    
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception(self.ADS_dict["name"]+', please start this module working!')
            return None
          
    def sub_join(self,timeout=-1):
        print("sub_join",self.ADS_dict["name"])
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('ADS1x15 '+self.ADS_dict["name"]+' sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
                
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print("ADS1x15",self.ADS_dict["name"],"pid is",pid)
        os.system("taskset -cp %d %d" %(self.CPUcore,pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.05)
        sampling_interval=1/self.sapleRate
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            #time.sleep(0.1)#avoid other processing affect

            result=np.zeros(maxCount,dtype=np.float)
            timeList=np.zeros(maxCount,dtype=np.float)
            count=0
            startTime=time.perf_counter()
            while(time.perf_counter()-startTime<self.sec 
                and count < maxCount):
                if ((time.perf_counter() - startTime) >= (sampling_interval*count)):
                    timeList[count]=time.time()
                    result[count]=self.chan.voltage
                    count+=1
            
            result=self.value_convert(
                result,
                self.ADS_dict["V_off"],
                self.ADS_dict["conv"],
                self.ADS_dict["offset"])

            result=result[:count]
            timeList=timeList[:count]
#            dfTime=timeList[101:]-timeList[100:-1]
#            print("*********** max time is",max(dfTime))
#            print("*********** min time is",min(dfTime))
            self.data["value"]=result
            self.data["time"]=timeList
            result=None #release
            timeList=None #release
            
            self.states["new"]=True
            self.states["run"]=False
            
        print(time.time(),self.ADS_dict["name"],"out the main loop.")
        
           
    def value_convert(self,arr,V_off=0,scale=0,offset=0):
        return (arr-V_off)*scale+offset
    
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release ADS1x15 processing',self.ADS_dict["name"],"join timeout!",file=sys.stderr)
                print('release ADS1x15 processing',self.ADS_dict["name"],"join timeout!")
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release ADS1x15 processing',self.ADS_dict["name"])
        self.exit.set()
   
class gy530_process(multiprocessing.Process):
    def __init__(self,name,sec):
        import VL53L0X
        multiprocessing.Process.__init__(self)
        self.name = name
        self.sec=sec
        self.exit = multiprocessing.Event()
        self.sapleRate = 30
    
        # Create a VL53L0X object
        tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)
        tof.open()
        tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE)
        self.chip=tof
        
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('GY530 chip '+self.name+', please start this module working!')
            return None
    
    def sub_join(self,timeout=-1):
        print("sub_join",'GY530 chip '+self.name)
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('GY530 chip '+self.name+' sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print("GY530 pid is",pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.05)
        maxWaitTime=(1/self.sapleRate)*1.1
        sampling_interval=1/self.sapleRate
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            #time.sleep(0.1)#avoid other processing affect
            
            """
            result=np.zeros(maxCount,dtype=np.int)
            timeList=np.zeros(maxCount,dtype=np.float)
            count=0
            startTime=time.time()
            lastPrint=0
            while(time.time()-startTime<self.sec 
                and count < maxCount):
                if ((time.time() - startTime) >= (sampling_interval*count)):
                    timeList[count]=time.time()
                    result[count]=self.chip.get_distance()
                    count+=1
                    waitTime=(sampling_interval*count)-(time.time() - startTime)
                    if waitTime> maxWaitTime:
                        waitTime=maxWaitTime
                    if waitTime>0:
                        time.sleep(waitTime)
                runTime=int(time.time()-startTime)
                if runTime//10 != lastPrint:
                    lastPrint=runTime//10
                    print("GY530",runTime,"/",self.sec,". Count is",count)
            
            result=result[:count]
            timeList=timeList[:count]
#            dfTime=timeList[101:]-timeList[100:-1]
#            print("*********** max time is",max(dfTime))
#            print("*********** min time is",min(dfTime))
            self.data[self.name]=result
            self.data["timestamp"]=timeList
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
            """
            
            try:
                result=np.zeros(maxCount,dtype=np.int)
                timeList=np.zeros(maxCount,dtype=np.float)
                count=0
                startTime=time.time()
                lastPrint=0
            except Exception as e:
                dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sys.stderr.write(dataStr+". brfore while except:"+str(e))
                print(dataStr+". brfore while except:"+str(e))
                
            try:
                while(time.time()-startTime<self.sec 
                    and count < maxCount):
                    try:
                        if ((time.time() - startTime) >= (sampling_interval*count)):
                            timeList[count]=time.time()
                            try:
                                result[count]=self.chip.get_distance()
                            except Exception as e:
                                dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                sys.stderr.write(dataStr+". GY530 except:"+str(e))
                                print(dataStr+". GY530 except:"+str(e))
                            try:
                                count+=1
                                waitTime=(sampling_interval*count)-(time.time() - startTime)
                                if waitTime> maxWaitTime:
                                    waitTime=maxWaitTime
                                if waitTime>0:
                                    time.sleep(waitTime)
                            except Exception as e:
                                dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                sys.stderr.write(dataStr+". wait time except:"+str(e))
                                print(dataStr+". wait time except:"+str(e))
                    except Exception as e:
                        dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        sys.stderr.write(dataStr+". if judge except:"+str(e))
                        print(dataStr+". if judge except:"+str(e))
                    try:
                        runTime=int(time.time()-startTime)
                        if runTime//10 != lastPrint:
                            lastPrint=runTime//10
                            print("GY530",runTime,"/",self.sec,". Count is",count)
                    except Exception as e:
                        dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        sys.stderr.write(dataStr+". runTime except:"+str(e))
                        print(dataStr+". runTime except:"+str(e))
            except Exception as e:
                dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sys.stderr.write(dataStr+". while judge except:"+str(e))
                print(dataStr+". while judge except:"+str(e))
            
            try:
                result=result[:count]
                timeList=timeList[:count]
    #            dfTime=timeList[101:]-timeList[100:-1]
    #            print("*********** max time is",max(dfTime))
    #            print("*********** min time is",min(dfTime))
                self.data[self.name]=result
                self.data["timestamp"]=timeList
                result=None #release
                timeList=None #release
                self.states["new"]=True
                self.states["run"]=False
            except Exception as e:
                dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sys.stderr.write(dataStr+". after while except:"+str(e))
                print(dataStr+". after while except:"+str(e))
            
        print(time.time(),'GY530 chip',self.name,"out the main loop.")
        
           
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release GY530 processing','GY530 chip',self.name,"join timeout!",file=sys.stderr)
                print('release GY530 processing','GY530 chip',self.name,"join timeout!")
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release GY530 processing','GY530 chip',self.name)
        self.exit.set()
        
 
class KashiyamaPump :
    runningTime = 0
    dpCurrent  = 0.0
    mbpCurrent = 0.0
    dpCaseTemperature = 0
    tc1Temperature = 0
    dpBackPressure = 0
    dpCoolingWater = 0.0        
    N2Purge = 0  
class kashi_process(multiprocessing.Process):
    def __init__(self,kashi_device,sec):
        multiprocessing.Process.__init__(self)
        self.sec=sec
        self.exit = multiprocessing.Event()
        self.sapleRate = 5
    
        # Create serial port
        self.device=[]
        for device in kashi_device:
            data=dict()
            data["name"]=device["name"]
            data["port"]=serial.Serial (device["path"],9600,parity=serial.PARITY_EVEN, bytesize=7 )
            data["time"]=self.getRunningTime(data["port"])
            self.device.append(data)
            
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        
    def CalFCS(self,sendBuff) :
        fcsResult = 0
        for ch in sendBuff :                  
            fcsResult = ch  ^ fcsResult
        sendBuff.append((fcsResult >>4)+0x30)
        sendBuff.append((fcsResult  & 0xF)+0x30)
        return sendBuff
     
    def QueryAnalogData(self,serPort) :
        qryAnalogData = [0x02,0x41]  # 'A'
        ary = bytearray(qryAnalogData)    
        ary = self.CalFCS(ary)
        ary.append(0x2A)  #'*'
        ary.append(0x0D)  #CR
        serPort.write(ary)
    
    def getAnalogData(self,serPort) :
        startTime=time.time()
        timeout=1
        while (serPort.in_waiting <46) and time.time()-startTime<timeout : #40byte, double check buffer and wait
            pass
        
        if serPort.in_waiting >=46:
            incomingByte = serPort.read(serPort.in_waiting)
            data = bytearray(incomingByte)
        else:
            serPort.read(serPort.in_waiting) # clean buffer
            print("analog data timeout")
            return None

        if( data[0] == 0x02) and ( data[1] == 0x06) and (data[2] == 0x41):  #
            if ( len(data) > 5) and ( data[-1] == 0x0D) and ( data[-2] == 0x2A):            
                recvData = data[3:-4]
                vp=KashiyamaPump()
                for i in range((len(recvData)//3)) :
                    sData = recvData[i*3:i*3+3]
                    if (sData != b'   ') :
                        if ( i == 0) :
                            vp.dpCurrent = int(sData)/10
                        elif ( i == 1) :
                            vp.mbpCurrent = int(sData)/10
                        elif ( i == 2) :
                            vp.dpCaseTemperature = int(sData)     
                        elif ( i == 3) :
                            vp.tc1Temperature = int(sData)     
                        elif ( i == 6) :
                            vp.dpBackPressure = int(sData)     
                        elif ( i == 7) :
                            vp.dpCoolingWater = int(sData)/10
                        elif ( i == 9) :
                            vp.N2Purge = int(sData)/10
                return vp
            return None
        return None
    
    def getRunningTime(self,serPort) :
        qryAnalogData = [0x02,0x4B]  # 'K'
        ary = bytearray(qryAnalogData)    
        ary = self.CalFCS(ary)
        ary.append(0x2A)  #'*'
        ary.append(0x0D)  #CR
        serPort.write(ary)
        
        time.sleep(0.07)  # 50ms+(6 byte command+13 byte response )*10/9600=70ms
        data = bytearray()
        
        startTime=time.time()
        timeout=1
        while (serPort.in_waiting <13) and time.time()-startTime<timeout : #40byte, double check buffer and wait
            pass
        
        if serPort.in_waiting >=13:
            incomingByte = serPort.read(serPort.in_waiting)
            data = bytearray(incomingByte)
        else:
            serPort.read(serPort.in_waiting) # clean buffer
            print("get running time data timeout")
            return None
    
        if( data[0] == 0x02) and ( data[1] == 0x06) and (data[2] == 0x4B):  #
            if ( len(data) > 5) and ( data[-1] == 0x0D) and ( data[-2] == 0x2A):            
                recvData = data[3:3+6]
                return int(recvData)/10 #return hour
            return None
        return None                      
                            
                            
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('kashiyama processing, please start this module working!')
            return None
          
    def sub_join(self,timeout=-1):
        print("sub_join",'kashiyama processing')
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('kashiyama processing sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print("Kashiyama pid is",pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.2)
        maxWaitTime=(1/self.sapleRate)*1.1
        sampling_interval=1/self.sapleRate
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            #time.sleep(0.1)#avoid other processing affect

        
#        time.sleep(0.05) #50ms wait convertion time
#        time.sleep(0.048)  # 48 msec -->46 byte*10 (7E1 and start bit) /9600=48msec
            result=[]
            for i in range(len(self.device)):
                dic=dict()
                dic["dpCurrent"]=np.zeros(maxCount,dtype=np.float32)
                dic["mbpCurrent"]=np.zeros(maxCount,dtype=np.float32)
                dic["dpCaseTemperature"]=np.zeros(maxCount,dtype=np.int)
                dic["tc1Temperature"]=np.zeros(maxCount,dtype=np.int)
                dic["dpBackPressure"]=np.zeros(maxCount,dtype=np.int)
                dic["dpCoolingWater"]=np.zeros(maxCount,dtype=np.float32)
                dic["N2Purge"]=np.zeros(maxCount,dtype=np.float32)
                result.append(dic)
            timeList=np.zeros(maxCount,dtype=np.float)
            count=0
            startTime=time.time()
            while(time.time()-startTime<self.sec 
                and count < maxCount):
                if ((time.time() - startTime) >= (sampling_interval*count)):
                    timeList[count]=time.time()
                    commandStart=time.time()
                    for device in self.device:
                        self.QueryAnalogData(device["port"])
                    waitTime=0.1042-(time.time()-commandStart)
                    # (6 byte command+46 byte response)*10/9600+50ms=104.2ms
                    if waitTime>0:
                        time.sleep(waitTime)
                        
                    for i,device in enumerate(self.device):
                        vp=self.getAnalogData(device["port"])
                        result[i]["dpCurrent"][count]=vp.dpCurrent
                        result[i]["mbpCurrent"][count]=vp.mbpCurrent
                        result[i]["dpCaseTemperature"][count]=vp.dpCaseTemperature
                        result[i]["tc1Temperature"][count]=vp.tc1Temperature
                        result[i]["dpBackPressure"][count]=vp.dpBackPressure
                        result[i]["dpCoolingWater"][count]=vp.dpCoolingWater
                        result[i]["N2Purge"][count]=vp.N2Purge
                    count+=1
                    waitTime=(sampling_interval*count)-(time.time() - startTime)
                    if waitTime>maxWaitTime:
                        waitTime=maxWaitTime
                    if waitTime>0:
                        time.sleep(waitTime)
            
            for i,device in enumerate(self.device):
                self.data[device["name"]+"_dpCur"]=result[i]["dpCurrent"][:count]
                self.data[device["name"]+"_mbpCur"]=result[i]["mbpCurrent"][:count]
                self.data[device["name"]+"_dpCaseTemp"]=result[i]["dpCaseTemperature"][:count]
                self.data[device["name"]+"_tc1Temp"]=result[i]["tc1Temperature"][:count]
                self.data[device["name"]+"_dpBackPres"]=result[i]["dpBackPressure"][:count]
                self.data[device["name"]+"_dpCoolWat"]=result[i]["dpCoolingWater"][:count]
                self.data[device["name"]+"_N2Purge"]=result[i]["N2Purge"][:count]
                self.data[device["name"]+"_runTime"]=np.ones(count,dtype=np.float32)*device["time"]
            self.data["timestamp"]=timeList[:count]
            dis=self.data["timestamp"][1:]-self.data["timestamp"][:-1]
            print("dis max",max(dis))
            print("dis min",min(dis))
            print("dis mean",sum(dis)/len(dis))
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
        print(time.time(),"Kashiyama process out the main loop.")
        
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release kashi processing','chip',self.name,"join timeout!",file=sys.stderr)
                print('release kashi processing','chip',self.name,"join timeout!")
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release kashi processing','chip',self.name)
        self.exit.set()
    
class minas_process(multiprocessing.Process):
    def __init__(self,
                name,
                port,
                sec,
                axis=1,
                baudrate=9600,
                timeout=0.5,
                writeTimeout=0.5,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False):
        multiprocessing.Process.__init__(self)
        self.name=name
        self.sec=sec
        self.sapleRate = 20
        self.exit = multiprocessing.Event()
        
        self.axis = axis
        self.t1 = 5 #Time out between characters, default is 0.5 sec
        self.t2 = 5 #Protocol time out, default time is 5 sec
        self.rty = 1 #Retry limit, default is once
        self.ms = 0 #Master/Slave
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        self.ser.parity = serial.PARITY_NONE #set parity check
        self.ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        self.ser.timeout = timeout          #non-block read 0.5s
        self.ser.writeTimeout = writeTimeout     #timeout for write 0.5s
        self.ser.xonxoff = False   #disable software flow control
        self.ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False     #disable hardware (DSR/DTR) flow control
        try:
            self.ser.open()
            self.ser.flushInput() #flush input buffer
            self.ser.flushOutput() #flush output buffer
            response = self.get_communication_reply(0,5)
            if response[-1] == 0:
                print("MINAS Driver %s connected!"%(bytearray(response[2:-1]).decode('ascii')))
            else:
                self.ser.close()
                raise Exception('Minas '+self.name+'Connect Failed!')
                exit()
        except Exception as ex:
            raise Exception('Minas '+self.name+'Open serial port error!' + str(ex))
            exit()
            
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
              
    def __do_communicate(self, data_block):
        rty_time = 0
        self.ser.timeout = self.t2 
        try:
            while rty_time <= self.rty:
                rty_time += 1
                response = []
                self.ser.flushInput() #flush input buffer
                self.ser.flushOutput() #flush output buffer
                if self.__do_send_ENQ():
                    self.ser.write(data_block)
                    if self.__do_check_ACK():
                        if self.__do_send_EOT():
                            size = self.ser.read(1)
                            response = self.ser.read(size[0]+3)
                            self.__do_send_ACK(size + response)
                            return response[:-1]
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
            raise Exception('Minas '+self.name+' Communicate Failure.')
        except:
            raise Exception('Minas '+self.name+' Communicate Error!')
        
#=====Sent from Raspberry=====
    def __do_send_ENQ(self):
        self.ser.write([0x05])
        if self.__do_check_EOT(): 
            return True
        else:
            print("MINAS did not respond!")
            return False
            
    def __do_send_EOT(self):
        if self.ser.read(1) == b'\x05':
            self.ser.write([0x04])
            return True
        else:
            print("MINAS did not send ENQ!")
            return False    
            
    def __do_send_ACK(self,block):
        if self.__cal_checksum(block) == 0:
            self.ser.write([0x06])
        else:
            print("Content Error!")
            self.ser.write([0x15])            

#=====Sent from MINAS=====
    def __do_check_EOT(self):
        if self.ser.read(1) == b'\x04':
            return True
        else:
            return False

    def __do_check_ACK(self):
        reply = self.ser.read(1)
        if reply == b'\x06':
            #print('MINAS recieved DataBlcok')
            return True
        elif reply == b'\x15':
            print("Get NAK!")
            return False
        else:
            print("No ACK Check recieved!")
            return False
        
#=====Check=====
    def __cal_checksum(self,lst):
        return (~sum(lst)+1) & 0b11111111
        
    def __check_checksum(self, lst):
        return sum(lst) & 0b1

#====Start and Close=====
    def start_communicate(self):
        try:
            self.ser.open()
            self.ser.flushInput() #flush input buffer
            self.ser.flushOutput() #flush output buffer
            response = self.get_communication_reply(0,5)
            if response[-1] == 0:
                print("MINAS Driver %s connected!"%(bytearray(response[3:-1]).decode('ascii')))
            else:
                print("Connect Failed!")
                self.ser.close()
                exit()
        except Exception as ex:
            print ("Open serial port error " + str(ex))
            exit()
            
    def stop_communicate(self):
        try:
            self.ser.close()
            print("Serial port closed!")
        except Exception as ex:
            print("Close serial port error" + str(ex))
            exit()
#=====Get=====        
    def get_parameters(self,pr_num): #0x00 to 0x7f, or error will be returned
        data_block = [0x01,self.axis,0x08,pr_num]
        data_block.append(self.__cal_checksum(data_block))
        response = list(self.__do_communicate(data_block))
        return response
        
    def get_present_speed(self):
        data_block = [0x00,self.axis,0x42]
        data_block.append(self.__cal_checksum(data_block))
        response = list(self.__do_communicate(data_block))
        value = response[3] << 8 | response[2]
        if 0x8000 & value:
            ret = -(0x10000 - value)
        else:
            ret = value
        return ret
        
    def get_present_torque(self):
        data_block = [0x00,self.axis,0x52]
        data_block.append(self.__cal_checksum(data_block))
        response = list(self.__do_communicate(data_block))
        value = response[3] << 8 | response[2]
        if 0x8000 & value:
            ret = -(0x10000 - value)
        else:
            ret = value
        return ret
        
    def get_present_deviation_counter(self):
        data_block = [0x00,self.axis,0x62]
        data_block.append(self.__cal_checksum(data_block))
        response = list(self.__do_communicate(data_block))
        value = response[2] | response[3] << 8 | response[4] << 16 | response[5] << 24
        if 0x80000000 & value:
            ret = -(0x100000000 - value)
        else:
            ret = value
        return ret
        
    def get_present_3value(self):
        data_block = [0x00,self.axis,0x92]
        data_block.append(self.__cal_checksum(data_block))
        response = list(self.__do_communicate(data_block))
        value = np.zeros(3,dtype = int)
        value[0] = response[3] << 8 | response[2]
        value[1] = response[5] << 8 | response[4]
        value[2] = response[6] | response[7] << 8 | response[8] << 16 | response[9] << 24
        for i in range(2):
            if 0x8000 & value[i]:
                value[i] = -(0x10000 - value[i])
        if 0x80000000 & value[2]:
            value[2] = -(0x100000000 - value[2])
        return value
        
    def get_communication_reply(self, command, mode, parameters_ary=[]):
        mode_cmd = mode << 4 | command
        data_block = [len(parameters_ary),self.axis,mode_cmd] + parameters_ary
        data_block.append(self.__cal_checksum(data_block))
        response = list(self.__do_communicate(data_block))
        return response
        
    def get_sample(self, sampleno=100,freq=20, function=0):
        if function == 0:
            response = np.zeros((sampleno,3),dtype=int)
        else:
            response = np.zeros((sampleno),dtype=int)
        index = 0
        t = 1/freq
        
        while(index < sampleno):    
            start_time = time.time()
            if function == 1:
                response[index] = self.get_present_speed()
            elif function == 2:
                response[index] = self.get_present_torque()
            elif function == 3:
                response[index] = self.get_present_deviation_counter()
            elif function == 0:
                response[index] = self.get_present_3value()
            index +=1
            try:
                time.sleep(t - (time.time()-start_time))
            except:
                print(index, " Error")
        return response

#=====Set=====
    def set_RS232_protocol(self,t1=5,t2=5,ms=0,rty=1):
        ms_rty = ms <<4 | rty
        data_block = [0x03,self.axis,0x11,t1,t2,ms_rty]
        data_block.append(self.__cal_checksum(data_block))
        response = list(self.__do_communicate(data_block))[0]
        if response == 0:
            self.t1 = t1
            self.t2 = t2
            self.ms = ms
            self.rty = rty
            print("Setup Successfully")
        else:
            print("Error Code: ",bin(response))  
                            
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('Minas processing, please start this module working!')
            return None
          
    def sub_join(self,timeout=-1):
        print("sub_join",'Minas processing')
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('Minas processing sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print("Minas["+self.name+"] pid is",pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.2)
        sampling_interval=1/self.sapleRate
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
                
            #time.sleep(0.1)#avoid other processing affect

        
#        time.sleep(0.05) #50ms wait convertion time
#        time.sleep(0.048)  # 48 msec -->46 byte*10 (7E1 and start bit) /9600=48msec
            result=dict()
            result["speed"]=np.zeros(maxCount,dtype=np.int32)
            result["torque"]=np.zeros(maxCount,dtype=np.int32)
            result["deviation"]=np.zeros(maxCount,dtype=np.int64)
            result["time"]=np.zeros(maxCount,dtype=np.float)
            
            count=0
            startTime=time.time()
            while(time.time()-startTime<self.sec 
                and count < maxCount):
                result["time"][count]=time.time()
                speed,torque,deviation = self.get_present_3value()
                result["speed"][count]=speed
                result["torque"][count]=torque
                result["deviation"][count]=deviation
                sleepTime = sampling_interval-(time.time()-result["time"][count])
                if sleepTime>0:
                    time.sleep(sleepTime)
                count+=1
            
            self.data[self.name+"_speed"]=result["speed"][:count]
            self.data[self.name+"_torque"]=result["torque"][:count]
            self.data[self.name+"_deviation"]=result["deviation"][:count]
            self.data["timestamp"]=result["time"][:count]
            diff=self.data["timestamp"][1:]-self.data["timestamp"][:-1]
            print("minas["+self.name+"] diff max",max(diff))
            print("minas["+self.name+"] diff min",min(diff))
            print("minas["+self.name+"] diff mean",sum(diff)/len(diff))
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
        print(time.time(),"Minas process out the main loop.")
        
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release Minas processing','chip',self.name,"join timeout!",file=sys.stderr)
                print('release Minas processing','chip',self.name,"join timeout!")
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release Minas processing','chip',self.name)
        self.exit.set()
    
class audio_process(multiprocessing.Process):
    def __init__(self,name,device_index,channel,rate,sec):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        
        self.FORMAT = pyaudio.paInt16 #or using paFloat32 
        self.INPUT_FRAMES_PER_BLOCK = 4096
        
        self.name = name
        self.sec=sec
        self.device_index=device_index
        self.channel=channel
        self.rate = rate
        
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        
    
    @staticmethod
    def getMapping(pa):
        print("Audio sampling getMapping")
        input_devices_num = 0
        used_index = []
        api_info = pa.get_default_host_api_info()
        api_index = api_info.get('index')
        print('-------------------------------')
        print('audio api_index',api_index)
        for i in range (pa.get_device_count()):
            print ("Device id ", i, " - ", pa.get_device_info_by_host_api_device_index(api_index,i))
        
        for i in range (pa.get_device_count()):
            if(pa.get_device_info_by_host_api_device_index(api_index,i).get('maxInputChannels')>0 
            and "USB" in pa.get_device_info_by_host_api_device_index(api_index,i).get('name').upper()):
                print ("Input Device id ", i, " - ", pa.get_device_info_by_host_api_device_index(api_index,i).get('name'))
                used_index.append(i)
        index=0
        ret=dict()
        for i,d in enumerate(alsaaudio.cards()):
            if "usb" in d and index<len(used_index):
                ret[d]=used_index[index]
                index=index+1
        print('-------------------')
        print(alsaaudio.cards(),'Input device number:',input_devices_num)
        print('Mapping',ret)
        print('-------------------')
        
        return ret
        
    @staticmethod
    def getOffset(pa):
        print("Audio sampling getOffset")
        input_devices_num = 0
        first_index = -1
        api_info = pa.get_default_host_api_info()
        api_index = api_info.get('index')
        print('-------------------------------')
        print('audio api_index',api_index)
        for i in range (pa.get_device_count()):
            print ("Device id ", i, " - ", pa.get_device_info_by_host_api_device_index(api_index,i))
        
        for i in range (pa.get_device_count()):
            if(pa.get_device_info_by_host_api_device_index(api_index,i).get('maxInputChannels')>0 
            and "USB" in pa.get_device_info_by_host_api_device_index(api_index,i).get('name').upper()):
                print ("Input Device id ", i, " - ", pa.get_device_info_by_host_api_device_index(api_index,i).get('name'))
                input_devices_num += 1
                if first_index < 0:
                    #first_index = pa.get_device_info_by_host_api_device_index(api_index,i).get('index')
                    first_index=i
        #index_offset=first_index - (len(alsaaudio.cards())-input_devices_num)
        if "usb1" not in alsaaudio.cards():
            pass
            
        first_usb=0
        for i,d in enumerate(alsaaudio.cards()):
            if "usb" in d:
                first_usb=i
                break
        index_offset=first_index-first_usb
        print('-------------------')
        print(alsaaudio.cards(),'Input device number:',input_devices_num)
        print('First index:',first_index,'Offset',index_offset)
        print('-------------------')
        
        return index_offset
        
        
    def creatStream(self,pa,device_index):
        return pa.open(format = self.FORMAT,
              channels = self.channel,
              rate = self.rate,
              input = True,
              start=False,
              input_device_index = device_index,
              frames_per_buffer = self.INPUT_FRAMES_PER_BLOCK)
              
              
              
              
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('Audio sampling '+self.name+', please start this module working!')
            return None
    
    def sub_join(self,timeout=-1):
        print("sub_join",'Audio sampling '+self.name)
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('Audio sampling '+self.name+' sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
            
    def start_sample(self,sec=1):
        self.states["run"]=True
        
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print("Audio sampling processing [",self.name,"] pid is",pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.rate*self.channel*self.sec*1.1)
        #get_read_available
        
        pa = pyaudio.PyAudio()
        print("Audio sampling processing [",self.name,"] creatStream device_index is",self.device_index)
        stream = self.creatStream(pa,self.device_index)
        
        
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            stream.start_stream()
            
            startTime = time.time()
            bufferArr=np.zeros(maxCount,dtype=np.int16)
            index=0
            
            while(time.time()-startTime<self.sec and index*self.INPUT_FRAMES_PER_BLOCK*self.channel<maxCount):
                data = stream.read(self.INPUT_FRAMES_PER_BLOCK , exception_on_overflow = False)
                bufferArr[index*self.INPUT_FRAMES_PER_BLOCK*self.channel:(index+1)*self.INPUT_FRAMES_PER_BLOCK*self.channel]=np.frombuffer(data,dtype = np.int16)
                index+=1
            
            stream.stop_stream()
            
            bufferArr=bufferArr[:index*self.INPUT_FRAMES_PER_BLOCK*self.channel]
            
            print('Audio done [',self.name,']')
            result = []
            for i in range(self.channel):
                result.append( bufferArr[i::self.channel] )
            result = np.array(result)
            
            self.data['name']=self.name
            self.data['value']=result
            self.data['time']=startTime
            self.data['rate']=self.rate
            self.data['size']=pa.get_sample_size(self.FORMAT)
            self.data['ch']=self.channel
                
            result=None #release
            self.states["new"]=True
            self.states["run"]=False
            
            
        stream.stop_stream()
        stream.close()
        print(time.time(),'Audio sampling processing [',self.name,']',"out the main loop.")
        
           
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release Audio sampling processing [',self.name,']',"join timeout!",file=sys.stderr)
                print('release Audio sampling processing [',self.name,']',"join timeout!")
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release Audio sampling processing [',self.name,']')
        self.exit.set()
        
   
   
class VPA308R_process(multiprocessing.Process):
    def __init__(self,name,port,fs,gain,sec):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.default_Baudrate                    =921600
        self.oneSampleByte                       =1544
        self.VAP308R_GAIN=dict()
        self.VAP308R_GAIN[2]                     =0
        self.VAP308R_GAIN[4]                     =1
        self.VAP308R_GAIN[8]                     =2
        self.VAP308R_FS=dict()
        self.VAP308R_FS[4000]                     =0
        self.VAP308R_FS[2000]                     =1
        self.VAP308R_FS[1000]                     =2
        self.VAP308R_FS[500]                      =3
        self.VAP308R_BR=dict()
        self.VAP308R_BR[9600]                     =0
        self.VAP308R_BR[19200]                    =1
        self.VAP308R_BR[57600]                    =2
        self.VAP308R_BR[115200]                   =3
        self.VAP308R_BR[230400]                   =4
        self.VAP308R_BR[256000]                   =5
        self.VAP308R_BR[460800]                   =6
        self.VAP308R_BR[921600]                   =7
        self.stdCommand = b'*********** FIRMWARE ***********'
        self.CPUcore=pairCPUcore()
        
        self.sec = sec
        self.name = name
        self.sapleRate = fs
        self.port = serial.Serial(port,self.default_Baudrate,parity=serial.PARITY_NONE, bytesize=8 )
        if not self.port.isOpen():
            self.port.open()
            
        #init sensor
        self.stopSample(10)
        rdata=self.get_infor()
        if(self.stdCommand not in rdata):
            self.port_scan_baud()
            if self.port.baudrate != self.default_Baudrate:
                self.set_sensor_baud(self.default_Baudrate)
                rdata=self.get_infor()
                if(self.stdCommand not in rdata):
                    raise Exception('VPA308R ['+self.name+'] processing baudrate setting error.')
        
        
        self.set_fs(fs)
        self.set_gain(gain)
        self.set_bias('X',0)
        self.set_bias('Y',0)
        self.set_bias('Z',0)
        self.set_bias('T',0)
        self.set_hPassOff()
        self.set_raw()
        rdata=self.get_infor()
        print('VPA308R ['+self.name+'] information:',rdata.decode('utf-8'))
        
        
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        
    def stopSample(self,count=-1):
        if count>0:
            for j in range(count):
                self.port.flushInput()
                self.port.write(b'AT$S'+bytes([0x0D]))
                time.sleep(0.1)
        else:
            self.port.flushOutput()
            self.port.flushInput()
            self.port.write(b'AT$S'+bytes([0x0D]))
            time.sleep(0.1)
            while(self.port.in_waiting >0):
                self.port.flushOutput()
                self.port.flushInput()
                self.port.read(self.port.in_waiting)
                self.port.write(b'AT$S'+bytes([0x0D]))
                time.sleep(0.1)
        
    def port_scan_baud(self):
        baud_value = [9600,19200,57600,115200,230400,256000,460800,921600]
        for i in range(len(baud_value)):
            self.rdata=b''
            self.port.baudrate=baud_value[i]
            self.stopSample(10)
            self.port.flushOutput()
            self.port.flushInput()
            self.port.write(bytes([0x0D]))
            time.sleep(0.2)
            self.port.write(bytes([0x0D]))
            time.sleep(0.2)
            
            rdata=self.get_infor()
            #print("rdata",rdata)
            print('VPA308R ['+self.name+'] scan baudrate on %d' %baud_value[i],rdata[:50])
            if(self.stdCommand in rdata):
                print('VPA308R ['+self.name+'] oringinal baulrate is %d' %baud_value[i])
                return baud_value[i]
        raise Exception('VPA308R ['+self.name+'] processing search baudrate error! please check sensor is connected on RS422.')
        return None
                            
               
    def set_sensor_baud(self,baud_param):
        command = self.VAP308R_BR[baud_param]
        
        self.stopSample()
        time.sleep(1)  
        self.port.write(bytes([0x0D]))
        time.sleep(0.2)
        self.port.write(b'AT$BAUD'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        print('VPA308R ['+self.name+'] Setting Baud Success, Mode:%d' %baud_param)

        print('VPA308R ['+self.name+'] Reset Sensor...')
        time.sleep(0.2)
        self.port.write(b'AT$RESET'+bytes([0x0D]))
        time.sleep(5) 
        print('VPA308R ['+self.name+'] Reset Succussful')
        self.port.baudrate=baud_param
        self.stopSample()
        
        
    def set_fs(self,fs):
        command = self.VAP308R_FS[fs]
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$ODR'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        print('VPA308R ['+self.name+'] Setting fs to %d' %fs)
        
    def set_hPassOff(self):
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$HIPASSOFF'+bytes([0x0D]))
        time.sleep(0.2)
        print('VPA308R ['+self.name+'] off high pass filter')
        
        
    def set_gain(self,gain):
        command = self.VAP308R_GAIN[gain]
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$GRAN'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        print('VPA308R ['+self.name+'] Setting gain to %d G' %gain)
        
        
    def set_raw(self):
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$RAW'+bytes([0x0D]))
        time.sleep(0.2)
                 
    def set_bias(self,target,value):
        self.stopSample()
        command=b'AT$BIAS'+bytes(target,'utf-8')+struct.pack('f',float(value))
        self.port.write(command)
        time.sleep(0.2)
                
    def get_infor(self):
        self.port.flushOutput()
        self.port.flushInput()
        self.port.write(b'AT$LIST'+bytes([0x0D]))
        time.sleep(0.2)
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        
        dataLen = self.port.in_waiting
        return self.port.read(dataLen) 
                 
                            
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('VPA308R ['+self.name+'] processing, please start this module working!')
            return None
          
    def sub_join(self,timeout=-1):
        print("sub_join",'VPA308R ['+self.name+'] processing')
        if timeout>0:
            timeout = timeout+2
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('VPA308R ['+self.name+'] processing sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print('VPA308R ['+self.name+'] pid is',pid)
        #os.system("taskset -cp 0 %d" %(pid))
        os.system("taskset -cp %d %d" %(self.CPUcore,pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.2*3) #one sample 4 byte 3 axis
        print("maxCount",maxCount)
        #sampleInteval = 128/self.sapleRate/2
        sampleInteval = 0.01
        lastIndex = -1
        currentIndex = 1
        lastTime = time.time()
        oneSampleByte= 128*3
        stdArr = list(range(oneSampleByte))
        
        self.port.flushOutput()
        self.port.flushInput()
        #self.port.write(b'AT$RS'+bytes([0x0D])) #start sample
        self.port.write(b'AT$RESET'+bytes([0x0D])) #reset and start sample
        while self.port.in_waiting==0:
            time.sleep(0.01) #start sample
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                
                while self.port.in_waiting > self.oneSampleByte:
                    data = self.port.read(self.oneSampleByte)
                    currentIndex = data[3]
                    lastIndex = currentIndex
                continue
            startTime = time.time()
            byteBuffer = b''
            #print('VPA308R ['+self.name+'] start access sample data:',lastIndex)
                
            bufferIndex = 0
            bufferArr = np.zeros(maxCount,dtype=np.float32)
            while(time.time()-startTime<self.sec ):
                time.sleep(sampleInteval)
                #print(self.port.in_waiting,time.time()-startTime,bufferIndex,bufferIndex/(time.time()-startTime)/3)
                while self.port.in_waiting > self.oneSampleByte:
                    lastTime = time.time()
                    if(self.port.in_waiting>=4095):
                        print('time:',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),file=sys.stderr)
                        print('VPA308R ['+self.name+'] data overflow',file=sys.stderr)
                    data = self.port.read(self.oneSampleByte)
                    if data[0:3]!=b'AT3':
                        print('time:',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),file=sys.stderr)
                        print('VPA308R ['+self.name+'] data error:',data[0:3],file=sys.stderr)
                    else:
                        floatData = list(map(lambda x:struct.unpack('f',data[4+x*4:8+x*4])[0],stdArr))
                        bufferArr[bufferIndex:bufferIndex+oneSampleByte] = floatData
                        bufferIndex=bufferIndex+oneSampleByte
                        currentIndex = data[3]
                        diffIndex = abs(currentIndex-lastIndex)
                        if (diffIndex != 1 and diffIndex!=255):
                            print('time:',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),file=sys.stderr)
                            print('VPA308R ['+self.name+'] less data ar index (current/last):',currentIndex,"/",lastIndex,file=sys.stderr)
                        lastIndex=currentIndex
            
            bufferArr=bufferArr[:bufferIndex] / 1000
            bufferArr=np.reshape(bufferArr,(-1,3)).T
            
            timeList=np.arange(len(bufferArr[0]))/len(bufferArr[0])*(lastTime-startTime)
            timeList=timeList+startTime
            
            self.data["timestamp"]=timeList
            self.data["aX_"+self.name]=bufferArr[0]
            self.data["aY_"+self.name]=bufferArr[1]
            self.data["aZ_"+self.name]=bufferArr[2]
                
            
            self.stopSample(10)
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
            
        print(time.time(),"VPA308R ["+self.name+"] process out the main loop.")
        
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print("VPA308R ["+self.name+"] process join timeout!",file=sys.stderr)
                print("VPA308R ["+self.name+"] process join timeout!")
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print("release VPA308R ["+self.name+']  processing')
        self.exit.set()
    
        
   
class plc_process(multiprocessing.Process):
    def __init__(self,HOST,POST,ASCII,protocol,plc_register,plc_name,sec):
        multiprocessing.Process.__init__(self)
        self.sec=sec
        self.exit = multiprocessing.Event()
        self.sapleRate = 5
        self.registerDict = []
        PLC_white_list = ["X","Y","M","D","W","R","RZ"]
        for i in range(len(plc_register)):
            subDict=dict()
            subDict["type"]=plc_register[i][0]
            if subDict["type"].upper() not in PLC_white_list:
                raise Exception("The PLC register type is setting error.")
                
            try:
                subDict["serial"]=int(plc_register[i][1:])
            except:
                raise Exception("The plc register type is not correct!")
            subDict["name"]=plc_name[i]
            self.registerDict.append(subDict)
        
        
        # Create ethernet port
#        HOST="192.168.1.2"
#        POST=5001
        self.plc=PLC(HOST,POST,ASCII,protocol)
            
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
                
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('PLC processing problem, please start this module working!')
            return None
          
    def sub_join(self,timeout=-1):
        print("sub_join",'PLC processing.')
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('PLC processing sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print("PLC processing pid is",pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.2)
        maxWaitTime=(1/self.sapleRate)*1.1
        sampling_interval=1/self.sapleRate
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            
            result=dict()
            for i in range(len(self.registerDict)):
                for name in self.registerDict[i]["name"]:
                    if name!="":
                        result[name]=np.zeros(maxCount,dtype=np.int)
            timeList=np.zeros(maxCount,dtype=np.float)
            count=0
            startTime=time.time()
            while(time.time()-startTime<self.sec 
                and count < maxCount):
                if ((time.time() - startTime) >= (sampling_interval*count)):
                    timeList[count]=time.time()
                    for dict_index in range(len(self.registerDict)):
                        
                        data = self.plc.get(self.registerDict[dict_index]["type"],
                                            self.registerDict[dict_index]["serial"],4)
#                        print(self.registerDict[dict_index]["type"],
#                              self.registerDict[dict_index]["serial"],
#                              self.registerDict[dict_index]["name"],
#                              data)
                        for i in range(4):
                            name = self.registerDict[dict_index]["name"][i]
                            if name !="":
                                result[name][count]=data[i]
                    
                    count+=1
                    waitTime=(sampling_interval*count)-(time.time() - startTime)
                    if waitTime>maxWaitTime:
                        waitTime=maxWaitTime
                    if waitTime>0:
                        time.sleep(waitTime)
            
            self.data["timestamp"]=timeList[:count]
            for key in result.keys():
                self.data[key]=result[key][:count]
            
            dis=self.data["timestamp"][1:]-self.data["timestamp"][:-1]
            print("plc max",max(dis))
            print("plc min",min(dis))
            print("plc mean",sum(dis)/len(dis))
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
            
        print(time.time(),"PLC process out the main loop.")
        
           
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release PLC processing join timeout!',file=sys.stderr)
                print('release PLC processing join timeout!')
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release PLC processing')
        self.exit.set()
    
   
  

class polling_device_process(multiprocessing.Process):
    def __init__(self,
                 HOST,
                 networkNo,
                 stationNo,
                 register,
                 name,
                 sec):
        multiprocessing.Process.__init__(self)
        self.sec=sec
        self.exit = multiprocessing.Event()
        self.sapleRate = 1
        PLC_white_list = ["X","Y","M","D","W","R","RZ"]
        PLC_bit_list = ["X","Y","M"]
     
        subDict=dict()
        subDict["type"]=register[0]
        if subDict["type"].upper() not in PLC_white_list:
            raise Exception("The polling device register type is setting error.")
            
        try:
            subDict["serial"]=int(register[1:])
        except:
            raise Exception("The polling device register type is not correct!")
        
        args = {"device_type":subDict["type"].upper(),"start_address":str(subDict["serial"]),"device_count":len(name),"network_no":networkNo,"station_no":stationNo}
        self.path = f'http://{HOST}:8080/api/getPLCDeviceDataBatch?argument={args}'
        self.nameArr = name
        
        if subDict["type"].upper() in PLC_bit_list:
            self.unit = 1
        else:
            self.unit = 4
        
            
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
                
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('polling device processing problem, please start this module working!')
            return None
          
    def sub_join(self,timeout=-1):
        print("sub_join",'polling device processing.')
        if timeout>0:
            timeout=timeout+3 #protect http requite delay
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('polling device processing sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print("polling device processing pid is",pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.2)
        maxWaitTime=(1/self.sapleRate)*1.1
        sampling_interval=1/self.sapleRate
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            
            result=dict()
            for name in self.nameArr:
                if name!="":
                    result[name]=np.zeros(maxCount,dtype=np.int)
            timeList=np.zeros(maxCount,dtype=np.float)
            count=0
            startTime=time.time()
            while(time.time()-startTime<self.sec 
                and count < maxCount):
                if ((time.time() - startTime) >= (sampling_interval*count)):
                    timeList[count]=time.time()
                    
                    req = urllib.request.Request(self.path)
                    # 在OA區使用需要設定proxy當作跳板到FAB
                    #proxy_host = "TCPXY001:8080"
                    #req.set_proxy(proxy_host,'http')
                    
                    try:
                        response = urllib.request.urlopen(req,timeout=1)
                    except Exception as e:
                        infor="polling device request exception: "+str(e)
                        #sys.stderr.write(infor) 
                        print(infor)
                        for i,name in enumerate(self.nameArr):
                            if name !="":
                                result[name][count]=65536
                    else:
                        conn_code = response.code
                        if conn_code == 200:
                            dic = json.loads(response.read())
                            if dic["rtn_code"] == '0000000':
                                data = dic["rtn_data"]
                                for i,name in enumerate(self.nameArr):
                                    if name !="":
                                        result[name][count]=int(data[i*self.unit:(i+1)*self.unit],16)
                                        
                            else:
                                infor="polling device return code: "+dic["rtn_code"]
                                sys.stderr.write(infor)
                                raise Exception(infor)
                        else:
                            infor="polling device request error code: "+conn_code
                            sys.stderr.write(infor)
                            raise Exception(infor)
                    
                    count+=1
                    waitTime=(sampling_interval*count)-(time.time() - startTime)
                    if waitTime>maxWaitTime:
                        waitTime=maxWaitTime
                    if waitTime>0:
                        time.sleep(waitTime)
            
            self.data["timestamp"]=timeList[:count]
            for key in result.keys():
                self.data[key]=result[key][:count]
            
            dis=self.data["timestamp"][1:]-self.data["timestamp"][:-1]
            print("polling device max period:",max(dis))
            print("polling device min period:",min(dis))
            print("polling device mean period:",sum(dis)/len(dis))
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
            
        print(time.time(),"polling device process out the main loop.")
        
           
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release polling device processing join timeout!',file=sys.stderr)
                print('release polling device processing join timeout!')
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release polling device processing')
        self.exit.set()
   
  

class IO_sample_process(multiprocessing.Process):
    def __init__(self,mapping,sec):
        multiprocessing.Process.__init__(self)
        self.mapping = mapping 
        #dictory dor name map pin 
        self.sec=sec
        self.exit = multiprocessing.Event()
        self.sapleRate = 10
    
        for name in self.mapping.keys():
            GPIO.setup(self.mapping[name], GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
            
        
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('I/O sample, please start this module working!')
            return None
    
    def sub_join(self,timeout=-1):
        print("sub_join I/O sample")
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('I/O sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
      
    def run(self):
        pid=os.getpid()
        print("I/O sample processing pid is",pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.2)
        maxWaitTime=(1/self.sapleRate)*1.1
        sampling_interval=1/self.sapleRate
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            
            result=dict()
            for name in self.mapping.keys():
                result[name]=np.zeros(maxCount,dtype=np.int)
            timeList=np.zeros(maxCount,dtype=np.float)
            count=0
            startTime=time.time()
            while(time.time()-startTime<self.sec 
                and count < maxCount):
                if ((time.time() - startTime) >= (sampling_interval*count)):
                    timeList[count]=time.time()
                    for name in self.mapping.keys():
                        result[name][count]=GPIO.input(self.mapping[name])
                    
                    
                    count+=1
                    waitTime=(sampling_interval*count)-(time.time() - startTime)
                    if waitTime>maxWaitTime:
                        waitTime=maxWaitTime
                    if waitTime>0:
                        time.sleep(waitTime)
            
            self.data["timestamp"]=timeList[:count]
            for key in result.keys():
                self.data[key]=result[key][:count]
            
            dis=self.data["timestamp"][1:]-self.data["timestamp"][:-1]
            print("I/O sample max",max(dis))
            print("I/O sample min",min(dis))
            print("I/O sample mean",sum(dis)/len(dis))
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
            
        print(time.time(),"I/O sample process out the main loop.")
           
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release I/O sample processing join timeout!',file=sys.stderr)
                print('release I/O sample processing join timeout!')
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release I/O sample processing')
        self.exit.set()
   
   
    
class mpu9250_process(multiprocessing.Process):
    '''
    RPI | MPU9250
    17 -> VCC
    19 -> SDA/SDI
    21 -> ADO/SDO
    23 -> SCLK
    24 -> NCS
    25 -> GND
    '''
    CPU_order_now=3
   
    def __init__(self, 
                 slave, 
                 FullScaleRange=4, 
                 gyroScaleRange=4, 
                 sample_rate=1, 
                 data_type=1,
                 spi_clock=976500,
                 recodeTime=1):
        
        multiprocessing.Process.__init__(self)
        self.deamon=True
        
        self.CPUcore=pairCPUcore()
            
        self.exit = multiprocessing.Event()
        self.gyro_arry =  multiprocessing.Array('d', range(3))
        self.vib_arry =  multiprocessing.Array('d', range(3))
        self.spi = spidev.SpiDev()
        self.slave=slave+1
        if (slave <2) :
            self.spi.open(0, slave)
        else :
            self.spi.open(1, (slave-2))
        self.spi.max_speed_hz = spi_clock
        print("**debug** MPU9250 spi clock =",spi_clock)
        self.spi.mode = 0
        self.spi.cshigh = False
        self.dataType = data_type
        self.recodeTime = recodeTime
        self.max_reading = 65536
        self.scaleG = 8192
        self.scaleGy = 65.5
        
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        self.states["err"]=False
        self.states["full"]=-1
            
        if self.dataType==1:
            self.dataForByte=6
        elif self.dataType==2:
            self.dataForByte=6
        elif self.dataType==3:
            self.dataForByte=12
        
        
        data = self.spi.xfer2([REGISTER_WHO_AM_I | REGISTER_READ_FLAG,0x00])
        if data[1]==CONTENT_I_AM_MPU9250:
            print("MPU9250 slave",self.slave,"connect")
            self.initMPU()
        else:
            self.release()
            raise Exception('MPU9250 slave'+str(self.slave)+' disconnect!')
            
        if self.dataType==3 and sample_rate>=8000:
            self.sampleRate = 8000
        elif  self.dataType==3:
            self.sampleRate = 1000
        elif  self.dataType==2 and sample_rate>=8000:
            self.sampleRate = 8000
        elif  self.dataType==2:
            self.sampleRate = 1000
        elif  self.dataType==1 and sample_rate>=4000:
            self.sampleRate = 4000
        elif  self.dataType==1:
            self.sampleRate = 1000
        
        self.setSampleRate(self.dataType,self.sampleRate)
        self.setAccScale(FullScaleRange)
        self.setGyroScale(gyroScaleRange)
        self.scaleG = self.getAccScalePerG(self.dataType)
        self.scaleGy = self.getGyroScalePerD(self.dataType)
        # sensor sample clock max err is 10%
        self.sampleErr=1.1
        self.maxDataLen=int(self.recodeTime*self.sampleRate*self.sampleErr)
        
        print('MPU9250 salve No=', slave,
              "AccScale", FullScaleRange,
              "GyroScale", gyroScaleRange,
              "Fs", self.sampleRate,
              "type", data_type )
#        print("real Fs:",self.SampleRateTest())
        
        
    def initMPU(self):
        self.spi.xfer2([REGISTER_PWR_MGMT_1,CONTENT_RESET_CHIP])  #Write a one to bit 7 reset bit; toggle reset device
    
        time.sleep(0.1)    
        self.spi.xfer2([REGISTER_PWR_MGMT_1,CONTENT_CLK_SEL_PLL1])  #auto select oscillator
    
        if(self.dataType==1):
            self.spi.xfer2([REGISTER_PWR_MGMT_2,0x07])  #disable gyro
        else:
            self.spi.xfer2([REGISTER_PWR_MGMT_2,0x00])  #enable gyro
        time.sleep(0.2)   
        self.spi.xfer2([REGISTER_INT_ENABLE,0x00])  #Disable all interrupts
        self.spi.xfer2([REGISTER_FIFO_ENABLE,0x00])  #Disable FIFO
        self.spi.xfer2([REGISTER_PWR_MGMT_1,0x00])  #Turn on internal clock source 
        self.spi.xfer2([REGISTER_I2C_MST_CTRL,0x00])  #Disable I2C master
        self.spi.xfer2([REGISTER_USER_CTRL,CONTENT_RESET_FIFO])  #Reset FIFO
        time.sleep(0.02)
        
    def resetBuffer(self):
    
        self.spi.xfer2([REGISTER_FIFO_ENABLE,0x00])  #Disable FIFO
        self.spi.xfer2([REGISTER_USER_CTRL,CONTENT_RESET_FIFO])  #reset FIFO
        print('reset FIFO for MPU9250 slave',self.slave) 
        time.sleep(0.01)     
        if self.dataType==1:
            self.spi.xfer2([REGISTER_FIFO_ENABLE, CONTENT_FIFO_ACC])
        elif self.dataType==2:
            self.spi.xfer2([REGISTER_FIFO_ENABLE, CONTENT_FIFO_GYRO])
        elif self.dataType==3:
            self.spi.xfer2([REGISTER_FIFO_ENABLE, CONTENT_FIFO_ACC | CONTENT_FIFO_GYRO])
        self.spi.xfer2([REGISTER_USER_CTRL,CONTENT_ENABLE_FIFO])  #Enable FIFO 

    def setSampleRate(self,dataType,sampleRate):
        if dataType==1 :
            if (sampleRate == 1000): 
                self.spi.xfer2([REGISTER_ACC_CONFIG2, CONTENT_SAMPLE_RATE_Acc_1K_ACC_CONFIG2])
            elif (sampleRate == 4000): 
                self.spi.xfer2([REGISTER_ACC_CONFIG2, CONTENT_SAMPLE_RATE_Acc_4K_ACC_CONFIG2])
            else:
                self.release()
                raise Exception('MPU9250 slave'+str(self.slave)+'sample rate range err!')

        elif dataType==2 :
            if (sampleRate == 1000): 
                self.spi.xfer2([REGISTER_CONFIG, CONTENT_SAMPLE_RATE_Gyro_1K_CONFIG])
            elif (sampleRate == 8000):
                self.spi.xfer2([REGISTER_CONFIG, CONTENT_SAMPLE_RATE_Gyro_8K_CONFIG])
            else:
                self.release()
                raise Exception('MPU9250 slave'+str(self.slave)+'sample rate range err!')

        elif dataType==3:
            if (sampleRate == 1000): 
                self.spi.xfer2([REGISTER_ACC_CONFIG2, CONTENT_SAMPLE_RATE_Acc_1K_ACC_CONFIG2])
                self.spi.xfer2([REGISTER_CONFIG, CONTENT_SAMPLE_RATE_Gyro_1K_CONFIG])
            elif (sampleRate == 8000):
                self.spi.xfer2([REGISTER_ACC_CONFIG2, CONTENT_SAMPLE_RATE_Acc_4K_ACC_CONFIG2])
                self.spi.xfer2([REGISTER_CONFIG, CONTENT_SAMPLE_RATE_Gyro_8K_CONFIG])
            else:
                raise Exception('MPU9250 slave'+str(self.slave)+'sample rate range err!')

        else:
            self.release()
            raise Exception('MPU9250 slave'+str(self.slave)+'data_type range err!')

    def setAccScale(self,FullScaleRange):
        if (FullScaleRange == 2):          
            self.spi.xfer2([REGISTER_ACC_CONFIG1, CONTENT_ACC_SCALE_2G])
        elif (FullScaleRange == 4):
            self.spi.xfer2([REGISTER_ACC_CONFIG1, CONTENT_ACC_SCALE_4G])
        elif (FullScaleRange == 8):
            self.spi.xfer2([REGISTER_ACC_CONFIG1, CONTENT_ACC_SCALE_8G])
        elif (FullScaleRange == 16):
            self.spi.xfer2([REGISTER_ACC_CONFIG1, CONTENT_ACC_SCALE_16G])
        else:
            self.release()
            raise Exception('MPU9250 slave'+str(self.slave)+'FullScaleRange range err!')
        
    def setGyroScale(self,gyroScaleRange):
        if (gyroScaleRange == 1):          
            self.spi.xfer2([REGISTER_GYRO_CONFIG, CONTENT_GYRO_SCALE_250dps])
        elif (gyroScaleRange == 2):
            self.spi.xfer2([REGISTER_GYRO_CONFIG, CONTENT_GYRO_SCALE_500dps])
        elif (gyroScaleRange == 3):
            self.spi.xfer2([REGISTER_GYRO_CONFIG, CONTENT_GYRO_SCALE_1000dps])
        elif (gyroScaleRange == 4):
            self.spi.xfer2([REGISTER_GYRO_CONFIG, CONTENT_GYRO_SCALE_2000dps])
        else:
            self.release()
            raise Exception('MPU9250 slave'+str(self.slave)+'gyroScaleRange range err!')
        
    def SampleRateTest(self,sec=0.5):
        count=0
        self.resetBuffer()
        bufferC=self.getBufferCount()
        startTime=time.perf_counter()
        endTime=time.perf_counter()
        while endTime-startTime < sec:
            if bufferC>0:
                self.getBuffer(bufferC)
                count=count+bufferC
            bufferC=self.getBufferCount()
            endTime=time.perf_counter()
        realFs=(count//self.dataForByte)/(endTime-startTime)
        print("real Fs is",realFs,"Hz")
        return realFs
           
    def getAccScalePerG(self,dataType):
        #print('write result -->', Lconf)
        if (( dataType == 1) | (dataType==3) ) :
            data = self.spi.xfer2([REGISTER_ACC_CONFIG1 | REGISTER_READ_FLAG, 0x0])  #  write 16   
            settingFullScaleRange = data[1] & 0x18
            
            if ( settingFullScaleRange == scale_2G) :
                return 16384
            elif ( settingFullScaleRange == scale_4G) :
                return 8192
            elif ( settingFullScaleRange == scale_8G) :
                return 4096
            elif ( settingFullScaleRange == scale_16G) :
                return 2048
        return -1
            
    def getGyroScalePerD(self,dataType):
        if (( dataType == 2) or (dataType==3) ) :
            data = self.spi.xfer2([REGISTER_GYRO_CONFIG | REGISTER_READ_FLAG, 0x0])  #  write 16   
            settingFullScaleRange = data[1] & 0x18
            if ( settingFullScaleRange == scale_250dps) :
                return 131
            elif ( settingFullScaleRange == scale_500dps) :
                return 65.5
            elif ( settingFullScaleRange == scale_1000dps) :
                return 32.8
            elif ( settingFullScaleRange == scale_2000dps) :
                return 16.4
        return -1
            
    def getBufferCount(self):
        data = self.spi.xfer2([0x72 | 0x80,0x00,0x00]) #get FIFO count
        return data[1]<<8 | data[2]

    def getBuffer(self,count):
        cmd=[0]*(count+1)
        cmd[0]=REGISTER_BUF_VALUE | REGISTER_READ_FLAG
        data = self.spi.xfer2(cmd)#get all FIFO
        return data[1:]
    def acc_value_convert(self, value):               
        if (value >= (self.max_reading /2)):
            value = (value - self.max_reading) / self.scaleG
        else :
            value = value / self.scaleG            
        return value
    
    def gyro_value_convert(self, value):
        #max_reading = 65536       
        if (value >= (self.max_reading /2)):
            value = (value - self.max_reading) / self.scaleGy
        else :
            value = value / self.scaleGy            
        return value
    
    def dataConvert(self, arr,scaleG):
        arr[arr>=(self.max_reading/2)]=arr[arr>= (self.max_reading/2)] - self.max_reading
        return arr/scaleG
    
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('MPU9250 slave'+str(self.slave)+', please start this module working!')
            return None
    
    def full_index(self):
        return self.states["full"]
    
    def sub_join(self,timeout=-1):
        print("sub_join MPU9250 slave",self.slave)
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('MPU9250 slave'+str(self.slave)+' sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
                
        if self.states["err"] is True:
            self.release()
            raise Exception("MPU9250 slave "+str(self.slave)+" SPI signal deviant! End sampling.")
        return self.states["full"]
            
    def start_sample(self):
        self.states["run"]=True
        
    def stop_sample(self):
        self.states["run"]=False
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
        
    def run(self):
        pid=os.getpid()
        print("MPU9250 slave ",self.slave,"pid is",pid)
        os.system("taskset -cp %d %d" %(self.CPUcore,pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=self.maxDataLen*self.dataForByte
        
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            self.states["full"]=-1
            raw=np.zeros(self.maxDataLen*self.dataForByte,dtype=np.int8)
            data=dict()
            count=0
            bufferC=0
            #time.sleep(0.1) #avoid other processing affect
            self.resetBuffer()
            timeStamp=time.time()
            startTime=time.perf_counter()
            endTime=time.perf_counter()
            bufferC=self.getBufferCount()
            while(endTime-startTime<self.recodeTime 
                and count < maxCount 
                and bufferC < 512):
                endTime=time.perf_counter()
                reqLen=(bufferC//self.dataForByte)*self.dataForByte
                buf_data=self.getBuffer(reqLen)
                raw[count:count+reqLen]=buf_data
                count+=reqLen
                bufferC=self.getBufferCount()
            if bufferC==512:
                print("MPU9250 slave",self.slave,"is overflow at",count)
            if bufferC>512 :
                dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                infor=dataStr+". MPU9250 slave "+str(self.slave)+" SPI signal deviant!"
                sys.stderr.write(infor)
                print(infor)
                self.states["err"]=True
                self.states["run"]=False
                self.states["new"]=False
                
            raw=raw[0::2]*256+raw[1::2]
            rawLen=len(raw)
            if self.dataType==1:
                data["accX"]=raw[0:rawLen:3]
                data["accY"]=raw[1:rawLen:3]
                data["accZ"]=raw[2:rawLen:3]
            elif self.dataType==2:
                data["gyroX"]=raw[0:rawLen:3]
                data["gyroY"]=raw[1:rawLen:3]
                data["gyroZ"]=raw[2:rawLen:3]
            elif self.dataType==3:
                data["accX"]=raw[0:rawLen:6]
                data["accY"]=raw[1:rawLen:6]
                data["accZ"]=raw[2:rawLen:6]
                data["gyroX"]=raw[3:rawLen:6]
                data["gyroY"]=raw[4:rawLen:6]
                data["gyroZ"]=raw[5:rawLen:6]
 #           print("testTime",time.perf_counter()-testTime)
            raw=None #release
            
            count=count//self.dataForByte
            data["time"]=np.array(range(count),dtype=np.float)*(endTime-startTime)/count+timeStamp
            if self.dataType==1:
                data["accX"]=data["accX"][:count]
                data["accY"]=data["accY"][:count]
                data["accZ"]=data["accZ"][:count]
                data["accX"]=self.dataConvert(data["accX"],self.scaleG)
                data["accY"]=self.dataConvert(data["accY"],self.scaleG)
                data["accZ"]=self.dataConvert(data["accZ"],self.scaleG)
            elif self.dataType==2:
                data["gyroX"]=data["gyroX"][:count]
                data["gyroY"]=data["gyroY"][:count]
                data["gyroZ"]=data["gyroZ"][:count]
                data["gyroX"]=self.dataConvert(data["gyroX"],self.scaleGy)
                data["gyroY"]=self.dataConvert(data["gyroY"],self.scaleGy)
                data["gyroZ"]=self.dataConvert(data["gyroZ"],self.scaleGy)
            elif self.dataType==3:
                data["accX"]=data["accX"][:count]
                data["accY"]=data["accY"][:count]
                data["accZ"]=data["accZ"][:count]
                data["gyroX"]=data["gyroX"][:count]
                data["gyroY"]=data["gyroY"][:count]
                data["gyroZ"]=data["gyroZ"][:count]
                data["accX"]=self.dataConvert(data["accX"],self.scaleG)
                data["accY"]=self.dataConvert(data["accY"],self.scaleG)
                data["accZ"]=self.dataConvert(data["accZ"],self.scaleG)
                data["gyroX"]=self.dataConvert(data["gyroX"],self.scaleGy)
                data["gyroY"]=self.dataConvert(data["gyroY"],self.scaleGy)
                data["gyroZ"]=self.dataConvert(data["gyroZ"],self.scaleGy)
            if (  self.dataType==1 or self.dataType==3 ) :
                self.data["accX"]=data["accX"]
                data["accX"]=None
                self.data["accY"]=data["accY"]
                data["accY"]=None
                self.data["accZ"]=data["accZ"]
                data["accZ"]=None
            if (  self.dataType==2 or self.dataType==3 ) :
                self.data["gyroX"]=data["gyroX"]
                data["gyroX"]=None
                self.data["gyroY"]=data["gyroY"]
                data["gyroY"]=None
                self.data["gyroZ"]=data["gyroZ"]
                data["gyroZ"]=None
            self.data["time"]=data["time"]
            self.states["new"]=True
            self.states["run"]=False
            data=None #release
            
        print(time.time(),"MPU9250 slave",self.slave,"out the main loop.")
        
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release',"MPU9250 slave",self.slave,'join timeout!',file=sys.stderr)
                print('release',"MPU9250 slave",self.slave,'join timeout!')
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release',"MPU9250 slave",self.slave)
        self.exit.set()
        

class ADXL355_process(multiprocessing.Process):
    # register addresses
    REG_DEVID_AD     = 0x00
    REG_DEVID_MST    = 0x01
    REG_PARTID       = 0x02
    REG_REVID        = 0x03
    REG_STATUS       = 0x04
    REG_FIFO_ENTRIES = 0x05
    REG_TEMP2        = 0x06
    REG_TEMP1        = 0x07
    REG_XDATA3       = 0x08
    REG_XDATA2       = 0x09
    REG_XDATA1       = 0x0A
    REG_YDATA3       = 0x0B
    REG_YDATA2       = 0x0C
    REG_YDATA1       = 0x0D
    REG_ZDATA3       = 0x0E
    REG_ZDATA2       = 0x0F
    REG_ZDATA1       = 0x10
    REG_FIFO_DATA    = 0x11
    REG_OFFSET_X_H   = 0x1E
    REG_OFFSET_X_L   = 0x1F
    REG_OFFSET_Y_H   = 0x20
    REG_OFFSET_Y_L   = 0x21
    REG_OFFSET_Z_H   = 0x22
    REG_OFFSET_Z_L   = 0x23
    REG_ACT_EN       = 0x24
    REG_ACT_THRESH_H = 0x25
    REG_ACT_THRESH_L = 0x26
    REG_ACT_COUNT    = 0x27
    REG_FILTER       = 0x28
    REG_FIFO_SAMPLES = 0x29
    REG_INT_MAP      = 0x2A
    REG_SYNC         = 0x2B
    REG_RANGE        = 0x2C
    REG_POWER_CTL    = 0x2D
    REG_SELF_TEST    = 0x2E
    REG_RESET        = 0x2F
    REG_FIFO_ENTRIES_FAST = (REG_FIFO_ENTRIES<<1) | 0b1
    REG_FIFO_DATA_FAST = (REG_FIFO_DATA<<1) | 0b1
    
    CONTENT_I_AM_ADXL355 = 0xED
    
    # Settings
    SET_RANGE_2G     = 0b01
    SET_RANGE_4G     = 0b10
    SET_RANGE_8G     = 0b11

    SET_ODR_4000     = 0b0000
    SET_ODR_2000     = 0b0001
    SET_ODR_1000     = 0b0010
    SET_ODR_500      = 0b0011
    SET_ODR_250      = 0b0100
    SET_ODR_125      = 0b0101
    SET_ODR_62_5     = 0b0110
    SET_ODR_31_25    = 0b0111
    SET_ODR_15_625   = 0b1000
    SET_ODR_7_813    = 0b1001
    SET_ODR_3_906    = 0b1010

    RANGE_TO_BIT = {2: SET_RANGE_2G,
                  4: SET_RANGE_4G,
                  8: SET_RANGE_8G}
                  
    ODR_TO_BIT = {4000: SET_ODR_4000,
                  2000: SET_ODR_2000,
                  1000: SET_ODR_1000,
                  500: SET_ODR_500,
                  250: SET_ODR_250,
                  125: SET_ODR_125,
                  62.5: SET_ODR_62_5,
                  31.25: SET_ODR_31_25,
                  15.625: SET_ODR_15_625,
                  7.813: SET_ODR_7_813,
                  3.906: SET_ODR_3_906}

    def __init__(self, 
                 slave,
                 name, 
                 FullScaleRange=4,
                 sample_rate=1000,
                 spi_clock=976500,
                 recodeTime=1):
        
        multiprocessing.Process.__init__(self)
        self.deamon=True
        
        self.name = name
        
        self.CPUcore=pairCPUcore()
        self.exit = multiprocessing.Event()
        self.vib_arry =  multiprocessing.Array('d', range(3))
        self.spi = spidev.SpiDev()
        self.slave=slave+1
        if (slave <2) :
            self.spi.open(0, slave)
        else :
            self.spi.open(1, (slave-2))
        self.spi.max_speed_hz = spi_clock
        self.transfer = self.spi.xfer2
        print("**debug** ADXL335 spi clock =",spi_clock)
        self.spi.mode = 0
        self.spi.cshigh = False
        self.recodeTime = recodeTime
        self.FullScaleRange = FullScaleRange
        self.sampleRate = sample_rate
        self.dataForByte=9
        
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        self.states["err"]=False
        self.states["full"]=-1
            
        
        
        if self.readRegister(ADXL355_process.REG_PARTID)[0] == ADXL355_process.CONTENT_I_AM_ADXL355:
            print("ADXL slave",self.slave,"connect")
            self.initChip()
        else:
            self.release()
            raise Exception('ADXL355 slave'+str(self.slave)+' disconnect!')
            
        if sample_rate not in ADXL355_process.ODR_TO_BIT.keys():
            self.release()
            raise Exception('ADXL355 '+str(self.slave)+' fs setting error!')
            
        if FullScaleRange not in ADXL355_process.RANGE_TO_BIT.keys():
            self.release()
            raise Exception('ADXL355 '+str(self.slave)+' acc scale setting error!')
            
        #self.stopMeasurement()
        self.setOutputDataRate(self.sampleRate)
        self.setAccScale(FullScaleRange)
        self.setFifoSample()
        # sensor sample clock max err is 10%
        self.sampleErr=1.1
        self.maxDataLen=int(self.recodeTime*self.sampleRate*self.sampleErr)
        
        
        print('ADXL355 salve No=', slave,
              "AccScale", FullScaleRange,
              "Fs", self.sampleRate)
        
        
    def initChip(self):
        self.writeRegister(ADXL355_process.REG_RESET, 0x52)
#        self.stopMeasurement()
        time.sleep(0.01)
        
    def readRegister(self, register, length=1):
        arr = [0]*(length+1)
        arr[0] = (register << 1) | 0b1
        result = self.transfer(arr)
        return result[1:]
        
    def fastReadRegister(self, register, length=1):
        arr = [0]*(length+1)
        arr[0] = register
        return self.spi.xfer2(arr)[1:]
            
    def writeRegister(self, register, value):
        # Shift register address 1 bit left, and set LSB to zero
        address = (register << 1) & 0b11111110
        result = self.transfer([address, value])

        
    def setOutputDataRate(self,ODR=4000): #set ODR and low-pass filter corner
        #self.stopMeasurement()
        temp = self.readRegister(ADXL355_process.REG_FILTER)[0] >> 4
        cmd = (temp << 4) |ADXL355_process.ODR_TO_BIT[ODR]
        self.writeRegister(ADXL355_process.REG_FILTER,cmd)
        time.sleep(0.05)
        
    def setFifoSample(self, entries=96): #watermark number of samples stored in the FIFO that triggers a FiFO_FULL condition
        #self.stopMeasurement()
        if entries <= 96:
            self.writeRegister(ADXL355_process.REG_FIFO_SAMPLES, entries)
        else:
            raise Exception('ADXL355 slave'+str(self.slave)+'fifo sample entries error!')
        time.sleep(0.05)
            
    def setAccScale(self,FullScaleRange): # set measurement range
        #self.stopMeasurement()
        temp = self.readRegister(ADXL355_process.REG_RANGE)[0]
        cmd = (temp & 0b11111100) |ADXL355_process.RANGE_TO_BIT[FullScaleRange]
        self.writeRegister(ADXL355_process.REG_RANGE, cmd)
        time.sleep(0.05)# not sure why, but without it does not work
         
    def startMeasurement(self): # all configuration must be programmed before enabling measurement mode
        tmp = self.readRegister(ADXL355_process.REG_POWER_CTL)[0]
        self.writeRegister(ADXL355_process.REG_POWER_CTL, tmp & 0b0)

    def stopMeasurement(self):
        tmp = self.readRegister(ADXL355_process.REG_POWER_CTL)[0]
        self.writeRegister(ADXL355_process.REG_POWER_CTL, tmp | 0b1)
        
    def getBufferCount(self): # get FIFO watermark value 
        return self.fastReadRegister(ADXL355_process.REG_FIFO_ENTRIES_FAST)[0]
        #return self.readRegister(ADXL355_process.REG_FIFO_ENTRIES)[0]
        
    def getBuffer(self,count):
        return self.fastReadRegister(ADXL355_process.REG_FIFO_DATA_FAST,count)
        #return self.readRegister(ADXL355_process.REG_FIFO_DATA,count)
        
    def acc_value_convert(self, value):
        H = np.array(value[0::3])<< 12
        M = np.array(value[1::3])<< 4
        L = np.array(value[2::3])>> 4
        data = H | M | L
        #&0x80000 to check bit 20. if bit 20 is 1, value will do revise
        #0x100000 is 2**21
        data[ data&0x80000!=0] = data[ data&0x80000!=0]-0x100000
        data = data/0x7FFFF*self.FullScaleRange
        axis = data.reshape(-1,3).T
        return axis
    
    
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('ADXL355 slave'+str(self.slave+1)+', please start this module working!')
            return None
    
    def full_index(self):
        return self.states["full"]
    
    def sub_join(self,timeout=-1):
        print("sub_join ADXL355 slave",self.slave)
        if timeout>0:
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('ADXL355 slave'+str(self.slave+1)+' sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
                
        if self.states["err"] is True:
            self.release()
            raise Exception("ADXL355 slave "+str(self.slave)+" SPI signal deviant! End sampling.")
        return self.states["full"]
            
    def start_sample(self):
        self.states["run"]=True
        
    def stop_sample(self):
        self.states["run"]=False
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
        
    def run(self):
        pid=os.getpid()
        print("ADXL355 slave ",self.slave,"pid is",pid)
        os.system("taskset -cp %d %d" %(self.CPUcore,pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=self.maxDataLen*self.dataForByte
        
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                continue
            self.states["full"]=-1
            raw=np.zeros(maxCount,dtype=np.int)
            test=np.zeros(maxCount,dtype=np.int)
            testIndex=0
            data=dict()
            count=0
            bufferC=0
            self.startMeasurement()
            timeStamp=time.time()
            startTime=timeStamp
            endTime=timeStamp
            bufferC=self.getBufferCount()
            while(endTime-startTime<self.recodeTime 
                and count < maxCount 
                and bufferC < 96):
                reqLen = (bufferC//3)*self.dataForByte
                buf_data=self.getBuffer(reqLen)
                raw[count:count+reqLen]=buf_data
                count+=reqLen
                endTime=time.time()
                bufferC=self.getBufferCount()
                
            self.stopMeasurement()
            self.getBuffer(self.getBufferCount()*3)#clear FIFO buffer
            count=int((count//3)*3)
            raw = raw[:count]
            if bufferC==96:
                print("ADXL355 slave",self.slave,"is overflow at",count)
            if bufferC>96 :
                dataStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                infor=dataStr+". ADXL355 slave "+str(self.slave+1)+" SPI signal deviant!"
                sys.stderr.write(infor)
                print(infor)
                self.states["err"]=True
                self.states["run"]=False
                self.states["new"]=False
                
            value = self.acc_value_convert(raw)
            self.data["aX_"+self.name]=value[0][64:]
            self.data["aY_"+self.name]=value[1][64:]
            self.data["aZ_"+self.name]=value[2][64:]
            raw=None #release
            realLen = len(value[0])
            self.data["timestamp"]=np.array(range(realLen),dtype=np.float)*(endTime-startTime)/realLen+timeStamp
            self.data["timestamp"]=self.data["timestamp"][64:]
            self.states["new"]=True
            self.states["run"]=False
        print(time.time(),"ADXL355 slave",self.slave,"out the main loop.")
        
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print('release',"ADXL355 slave",self.slave,'join timeout!',file=sys.stderr)
                print('release',"ADXL355 slave",self.slave,'join timeout!')
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print('release',"ADXL355 slave",self.slave)
        self.exit.set()
        
# this dictVar need to follow:
# Need key is timestamp
# All item need the same length
def dataMatch(dictVars):
    startTime=time.time()
    inputLen=len(dictVars)
    
    if inputLen==0:
        return {"timestamp":[]},0
    
    
    #find last time
    lastestTime = 0
    for var in dictVars:
        if lastestTime<var["timestamp"][0]:
            lastestTime=var["timestamp"][0]
    
    #remove early time
    for i in range(inputLen):
        count=0
        while lastestTime>dictVars[i]["timestamp"][count]:
            count=count+1
        for key in dictVars[i].keys():
            dictVars[i][key]=dictVars[i][key][count:]
            
            
    #find max length
    maxLen = 0
    mainIndex = -1
    for index,var in enumerate(dictVars,start=0):
        length=np.size(var["timestamp"])
        if length>maxLen:
            maxLen=length
            mainIndex=index
          
    #create result dict and input main data
    ret=dict()
    ret["datetime"]=np.ndarray(shape=(maxLen,),dtype=object)
    
    for i,d in enumerate(dictVars[mainIndex]["timestamp"]):
        ret["datetime"][i]=datetime.datetime.fromtimestamp(int(d)).strftime("%Y-%m-%d %H:%M:%S")

    endCount=maxLen
    sortIndex=np.zeros(shape=(inputLen,maxLen),dtype=np.int)
    
    for j in range(inputLen):
        if j ==mainIndex:
            continue
        selfLen=np.size(dictVars[j]["timestamp"])
        if selfLen*2>maxLen:
            eachDictIndex=0
            for i in range(maxLen):
                #get main timestamp
                #this need to compare clostest last timestamp, so check index not overflow 
                nowValue=dictVars[mainIndex]["timestamp"][i]
                while(eachDictIndex+1<selfLen and
                    dictVars[j]["timestamp"][eachDictIndex+1] < nowValue):
                    eachDictIndex+=1
                
                #if index overflow, end data match
                if eachDictIndex+1>=selfLen:
                    if i-1<endCount:
                        endCount=i-1
                    break
                
                sortIndex[j][i]=eachDictIndex
        else:     
            preIndex=0
            newIndex=0
            for i in range(selfLen-1):
                nowValue=dictVars[j]["timestamp"][i+1]
                while(newIndex< maxLen and
                    nowValue>dictVars[mainIndex]["timestamp"][newIndex]):
                    newIndex+=1
                sortIndex[j][preIndex:newIndex]=i
                preIndex=newIndex
                
                if newIndex>= maxLen:
                    break 
            if newIndex+1<maxLen and endCount>newIndex-1:
                endCount=newIndex-1
                
    
    #sort
    for j in range(inputLen):
        for key in dictVars[j].keys():
            if key=="timestamp":
                continue
            if j != mainIndex:
                ret[key]=np.array(dictVars[j][key])
                dictVars[j][key]=None
                ret[key]=ret[key][sortIndex[j]]
            else:
                ret[key]=dictVars[j][key]
            #cut each array
            ret[key]=ret[key][:endCount]
    ret["datetime"]=ret["datetime"][:endCount]
    
    Fs= int(endCount/(dictVars[mainIndex]["timestamp"][endCount-1]-dictVars[mainIndex]["timestamp"][0]))
    print("data match OK, time(s):",time.time()-startTime)
    
    pd_result = pd.DataFrame()
    keyList=[]
    for key in ret.keys():
        keyList.append(key)
    for key in keyList:
        pd_result[key]=ret[key]
        del ret[key]
        if pd_result[key].dtypes=="float64":
            pd_result[key]=pd_result[key].astype(np.float32)
        if pd_result[key].dtypes=="int32":
            pd_result[key]=pd_result[key].astype(np.int32)
        time.sleep(0.1)
        
    return pd_result,Fs
     
     
     
def dataMatchOptmize(dictVars):
    startTime=time.time()
    inputLen=len(dictVars)
    if inputLen==0:
        return {"timestamp":[]},0
    
    
    #find last time
    maxTime = []
    minTime = []
    fsList = []
    for var in dictVars:
        maxTime.append(var["timestamp"][-1])
        minTime.append(var["timestamp"][0])
        fsList.append(len(var["timestamp"])/(maxTime[-1]-minTime[-1]))
        
    mainIndex = np.argmax(fsList)
    Fs = int(fsList[mainIndex])
    
    ret = pd.DataFrame()
    for k in dictVars[mainIndex].keys():
        ret[k]=list(dictVars[mainIndex][k])
    for index,var in enumerate(dictVars):
        if index==mainIndex:
            continue
        pdVar = pd.DataFrame()
        for k in var.keys():
            pdVar[k]=list(var[k])
        ret=pd.merge_asof(ret,pdVar,on='timestamp')
    ret.fillna(method='ffill',inplace=True)
    ret.fillna(method='bfill',inplace=True)
    ret = ret[ (ret['timestamp']>max(minTime))&(ret['timestamp']<min(maxTime)) ]
    ret["timestamp"] = list(map(lambda x:datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"),ret["timestamp"]))
    
    
    pd_result = pd.DataFrame()
    for key in ret.keys():
        if key=="timestamp":
            mainKey = "datetime"
        else:
            mainKey = key
            
        pd_result[mainKey]=ret[key]
        del ret[key]
        if pd_result[mainKey].dtypes=="float64":
            pd_result[mainKey]=pd_result[mainKey].astype(np.float32)
        if pd_result[mainKey].dtypes=="int32":
            pd_result[mainKey]=pd_result[mainKey].astype(np.int32)
    print("dataMatchOptmize time:",time.time()-startTime)
    return pd_result,Fs
    
def alignStartTime(otherData,audioData):
    if len(otherData)==0 or len(audioData)==0:
        print("alignStartTime not process.")
        return #end function
    
    startTimes = []
    nameList = []
    removeCount = []
    
    #get start time
    for d in otherData:
        for k in d.keys():
            if k == "timestamp":
                continue
            nameList.append( k )
            startTimes.append( d["timestamp"][0] )
        
    for k in audioData.keys():
        nameList.append( k )
        startTimes.append( audioData[k]["time"] )
        
        
    #get general time
    startTime = max(startTimes)
    
    
    #remove early time
    for d in otherData:
        keepIndex = d["timestamp"]>=startTime
        #removeLen = len(d["timestamp"])-sum(keepIndex)
        for k in d.keys():
            oldLen = len(d[k])
            d[k] = d[k][keepIndex]
            newLen = len(d[k])
            if k != "timestamp":
                removeCount.append(oldLen-newLen)
            
    for k in audioData.keys():
        shiftPoint = int((startTime-audioData[k]["time"])*audioData[k]["rate"])
        newStartTime = audioData[k]["time"]+shiftPoint/audioData[k]["rate"]
        removeCount.append(shiftPoint)
        audioData[k]["value"]=audioData[k]["value"][:,shiftPoint:]
    
    
    print("alignStartTime name/shift/removeCount.")
    for i in range(len(startTimes)):
        print(nameList[i],"/",startTime-startTimes[i],"/",removeCount[i])
    

    
def compute_angles(data, fs):
    win_size = fs//10
    MA = pd.DataFrame()
    for c in data.keys():
        if 'aX_' in c and 'aX_ma' not in MA.columns:
            MA['aX_ma'] = data[c]
        if 'aY_' in c and 'aY_ma' not in MA.columns:
            MA['aY_ma'] = data[c]
        if 'aZ_' in c and 'aZ_ma' not in MA.columns:
            MA['aZ_ma'] = data[c]
    if ('aX_ma' not in MA.columns
     or 'aY_ma' not in MA.columns
     or 'aZ_ma' not in MA.columns):
         return False
    MA['aX_ma'] = MA['aX_ma'].rolling(win_size).mean()
    MA['aY_ma'] = MA['aY_ma'].rolling(win_size).mean()
    MA['aZ_ma'] = MA['aZ_ma'].rolling(win_size).mean()
    angles = pd.DataFrame()
    angles['pitch'] = np.arctan((MA['aX_ma']/(MA['aY_ma'].pow(2)+MA['aZ_ma'].pow(2)).pow(0.5)).tolist())/np.pi*180
    angles['roll'] = np.arctan((MA['aY_ma']/(MA['aX_ma'].pow(2)+MA['aZ_ma'].pow(2)).pow(0.5)).tolist())/np.pi*180
    angles['yaw'] = np.arctan((MA['aZ_ma']/(MA['aY_ma'].pow(2)+MA['aX_ma'].pow(2)).pow(0.5)).tolist())/np.pi*180
    return angles

def angle_detect(name,data, fs,threshold=3):
    angles = compute_angles(data, fs)
    if angles is False:
        raise Exception(name+' column error!')
    angle_diff = angles.diff().abs().max()
    infor = 'threshold='+str(threshold)
    infor += ', diff=\n'+str(angle_diff)
    
    print(name,infor) #debuger
    #print((angle_diff > threshold).any()) #debuger
    #print(angle_diff > threshold) #debuger
    if (angle_diff > threshold).any():
        #raise Exception(name+' signal error! '+infor)
        print(name+' signal error! '+infor) #debuger
     
def ESP32_connect():
    global ESP32_RDY
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ESP32_RDY, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    return GPIO.input(ESP32_RDY)==1 # if connect, handshack will hight
 

def get_value(setting_dic, 
              sensor_dic, 
              ads1115_dic, 
              mpu9250_dic, 
              gy530_dic, 
              kashiyama_dic,
              PLC_config,
              IOsample_dic,
              polling_device_dic,
              VPA308R_dic,
              audio_dic,
              ADXL355_config,
              minas_config):
    signal_dic = {}
    audioResult_dic = {}
    
    signal_detect_threshold = float(getDict(sensor_dic,'signal_detect_threshold',3))
    
    pid=os.getpid()
    mpu9250MaxNum=5 #number of mpu9250 module
    PLC_white_list = ["X","Y","M","D","W","R","RZ"]
    PLC_ip=getDict(setting_dic,'plc_ip',"")
    PLC_port=int(getDict(setting_dic,'plc_port',5001))
    plc_protocol=getDict(setting_dic,'plc_protocol',"UDP")
    plc_protocol=plc_protocol.upper()
    sampling_rate = int(sensor_dic['sampling_rate'])   
    record_second = int(sensor_dic['record_second'])
    record_loop = int(sensor_dic['record_loop'])
    trigger_gpio_no = int(getDict(sensor_dic,'trigger_gpio_no',0))
    trigger_plc_register = getDict(sensor_dic,'trigger_plc_register',None)
    
    trigger_on_delay_time = float(getDict(sensor_dic,'trigger_on_delay_time',0))
    trigger_on_timeout_multiple = float(getDict(sensor_dic,'trigger_on_timeout_multiple',1.5))
    trigger_on = int(getDict(sensor_dic,'trigger_on',0))
    timeout_count = record_second* trigger_on_timeout_multiple
    record_loop_cnt = 0
    data_merge_optmize = int(getDict(setting_dic,'data_merge_optmize',0))
    
    use_buffer = ESP32_connect()
    if use_buffer is True:
        print("ESP32 buffer mode start.")
   
   
    ports = list(list_ports.comports())
    serialList=[]
    locationList=[]
    for port in ports:
        serialList.append(port.device)
        locationList.append(port.location)
    VPA308R_length = int(getDict(VPA308R_dic,'length',2))
    if VPA308R_length<2:
        VPA308R_length=2
    VPA308R_enable=False
    VPA308R_proc=[]
    VPA308R_fs = np.array([500,1000,2000,4000])
    VPA308R_fs_diff = VPA308R_fs-sampling_rate
    VPA308R_fs_diff[VPA308R_fs_diff>0]=min(VPA308R_fs_diff)
    VPA308R_fs_real = VPA308R_fs[np.argmax(VPA308R_fs_diff)]
    print("serialList",serialList)
    print("locationList",locationList)
    for i in range(VPA308R_length):
        VPA308R_name = getDict(VPA308R_dic,'ch'+str(i+1)+'_name',"")
        VPA308R_gain = int(getDict(VPA308R_dic,'ch'+str(i+1)+'_full_scale_range',8))
        VPA308R_local_port = getDict(VPA308R_dic,'ch'+str(i+1)+'_location',"")
        
        if VPA308R_name=="":
            continue
        
        if VPA308R_gain not in [2,4,8]:
            raise Exception('VPA308R ch'+str(i+1)+'_full_scale_range parameter setting error.')
        
        if VPA308R_local_port!="" and VPA308R_local_port not in locationList:
            raise Exception('VPA308R ch'+str(i+1)+'_location['+VPA308R_local_port+'] not found device.')
        
        if VPA308R_name!="" and VPA308R_local_port!="" and VPA308R_local_port in locationList:
            index=locationList.index(VPA308R_local_port)
            VPA308R_port = serialList[index]
            VPA308R_proc.append(VPA308R_process(
                VPA308R_name,
                VPA308R_port,
                VPA308R_fs_real,
                VPA308R_gain,
                record_second
                ))
            VPA308R_proc[-1].start()
            VPA308R_enable=True
    if VPA308R_enable:
        print("VPA308R_fs_real",VPA308R_fs_real)
    
    
    minas_enable=False
    minas_proc=[]
    minas_names=[]
    for i in range(4):
        minas_name = getDict(minas_config,'ch'+str(i+1)+'_name',"")
        minas_local_port = getDict(minas_config,'ch'+str(i+1)+'_location',"")
        
        if minas_name=="":
            continue
            
        if minas_local_port=="":
            continue
        
        if minas_name in minas_names:
            raise Exception('Minas ch'+str(i+1)+'_name already exist.')
        
        if minas_local_port not in locationList:
            raise Exception('Minas ch'+str(i+1)+'_location['+minas_local_port+'] not found device.')
        else :
            index=locationList.index(minas_local_port)
            minas_port = serialList[index]
            minas_proc.append(minas_process(
                minas_name,
                minas_port,
                record_second
                ))
            minas_proc[-1].start()
            minas_enable=True
            
        
    audio_enable=False
    audio_length = int(getDict(audio_dic,'length',4))
    audio_param=[]
    audio_names=[]
    audio_proc=[]
    audio_offset=1
    audio_mapping=dict()
    audio_pyaudio=None
    for i in range(1,audio_length+1):
        
        #chx_channel default is 1
        #chx_rate default is 44100
        #length default is 4
        audio_name = getDict(audio_dic,'ch'+str(i)+'_name',"")
        audio_location = getDict(audio_dic,'ch'+str(i)+'_location',"")
        audio_channel = int(getDict(audio_dic,'ch'+str(i)+'_channel',1))
        audio_rate = int(getDict(audio_dic,'ch'+str(i)+'_rate',44100))
        if audio_name!="" and audio_rate!="":
            if audio_location.find("usb")!=0 :
                raise Exception('Audio sampling ch'+str(i)+'_location_format_error.')
            
            if audio_location.replace("usb","").isnumeric() is False:
                raise Exception('Audio sampling ch'+str(i)+'_location_format_error.')
                
            if audio_name in audio_names:
                raise Exception('Audio sampling ch'+str(i)+'_name_already_exist.')
                
            if audio_enable is False: #first time --> import
                import alsaaudio as _alsaaudio
                import pyaudio as _pyaudio
                global alsaaudio
                global pyaudio
                alsaaudio=_alsaaudio
                pyaudio=_pyaudio
                #for i in range(100):
                #    time.sleep(0.5)
                audio_pyaudio=pyaudio.PyAudio()
                #audio_offset=audio_process.getOffset(audio_pyaudio)
                audio_mapping=audio_process.getMapping(audio_pyaudio)
                
            if audio_location not in alsaaudio.cards():
                raise Exception('Audio sampling ch'+str(i)+'_location_not_in_dev_setting.')
            
            if audio_location not in audio_mapping.keys():
                raise Exception('Audio sampling can not map localtion to index. Please wait moment, and try again.')
            
            
            audio_names.append(audio_name)
            audio_data = dict()
            audio_data["name"]=audio_name
            audio_data["index"]=audio_mapping[audio_location]
            audio_data["channel"]=audio_channel
            audio_data["rate"]=audio_rate
            audio_data["second"]=record_second
            audio_param.append(audio_data)
            audio_enable=True
            
    if audio_enable and audio_pyaudio != None:
        #audio_cards = alsaaudio.cards() 
        #for audio_p in audio_param:
            #audio_p["index"] = audio_cards.index(audio_p["location"]) + audio_offset
            #audio_cards.pop(audio_cards.index(audio_p["location"]))
            
        #print("audio_param:",audio_param)
        
        for audio_p in audio_param:
            audio_proc.append(audio_process(
                audio_p["name"],
                audio_p["index"],
                audio_p["channel"],
                audio_p["rate"],
                audio_p["second"]
            ))
            audio_proc[-1].start()
    
        
   
   
    ADS1x15_enable=False
    ADS1x15dict=[]
    ADS_Fs=3000
    ADS_enable_num=0
    
    for chip in range(MAX_ADS1x15_CHIP):
        ADS1x15dict.append(dict())
        chip_name='chip'+str(chip+1)
       #chip type : ADS1115 or ADS1015    
        ADS1x15dict[chip]["type"]= getDict(ads1115_dic,chip_name+'_type', 'ADS1115') 
        
        if use_buffer is False:
            ADS1x15dict[chip]["Fs"]=sampling_rate
        
        chip_enable=False
        last_ch_enable=""
        for ch in range(MAX_CHIP_CH_TYPE):
            ch_name='ch'+str(chip+1)+str(ch+1)
            name = getDict(ads1115_dic,ch_name+'_name','')
            if name!="":
#                print(ch_name+'_name is',name)
                if last_ch_enable!="":
                    raise Exception(name+' enable fail! The '+last_ch_enable+' already enable.')
                    break
                if use_buffer is True:
                    if ADS1x15dict[chip]["type"]=="ADS1015":
                        for Fs in [3000,2500,2000,1600,1000,800,400,200,100]:
                            if ADS_Fs>=Fs and sampling_rate>=Fs:
                                ADS_Fs=Fs
                                break
                    elif ADS1x15dict[chip]["type"]=="ADS1115":
                        for Fs in [800,400,200,100]:
                            if ADS_Fs>=Fs and sampling_rate>=Fs:
                                ADS_Fs=Fs
                                break
                    else:
                        raise Exception(chip_name+' ADS1x15 type error!')

                ADS1x15dict[chip]["name"]=name
                last_ch_enable=name
                ADS1x15_enable=True
                chip_enable=True
                ADS_enable_num+=1
                
                # voltage range : 5, 4,2,1,0.5,0.25
                conn_type= int(getDict(ads1115_dic,chip_name+'_input_conn_type', 2))
                voltage_range= float(getDict(ads1115_dic,chip_name+'_voltage_range', '4'))
                if voltage_range==0.25:
                    ADS1x15dict[chip]["gain"]="256mV"
                    ADS1x15dict[chip]["maxV"]=0.256
                elif voltage_range==0.5:
                    ADS1x15dict[chip]["gain"]="512mV"
                    ADS1x15dict[chip]["maxV"]=0.512
                elif voltage_range==1:
                    ADS1x15dict[chip]["gain"]="1024mV"
                    ADS1x15dict[chip]["maxV"]=1.024
                elif voltage_range==2:
                    ADS1x15dict[chip]["gain"]="2048mV"
                    ADS1x15dict[chip]["maxV"]=2.048
                elif voltage_range==4:
                    ADS1x15dict[chip]["gain"]="4096mV"
                    ADS1x15dict[chip]["maxV"]=4.096
                elif voltage_range==5:
                    ADS1x15dict[chip]["gain"]="6144mV"
                    ADS1x15dict[chip]["maxV"]=6.144
                    
                #1 : single ended ,2: differentail input
                if ( conn_type == 2 ) :
                    ADS1x15dict[chip]["differantial"]=True
                    if (ch == 0):
                        ADS1x15dict[chip]['channal']="AIN0_AIN1"
                    elif (ch == 1):   
                        ADS1x15dict[chip]['channal']="AIN2_AIN3"
                    scale_low = float(getDict(ads1115_dic,ch_name+'_scale_low', -5.0))
                elif ( conn_type == 1 ) :
                    ADS1x15dict[chip]["differantial"]=False
                    if (ch == 0):
                        ADS1x15dict[chip]['channal']="AIN0_GND"
                    elif (ch == 1):    
                        ADS1x15dict[chip]['channal']="AIN1_GND"
                    elif (ch== 2):   
                        ADS1x15dict[chip]['channal']="AIN2_GND"
                    elif (ch == 3):  
                        ADS1x15dict[chip]['channal']="AIN3_GND"
                    scale_low = float(getDict(ads1115_dic,ch_name+'_scale_low', 0))
                    
                ##chxx_CT_R =1000
                ct_r = int(getDict(ads1115_dic,ch_name+'_ct_r', '1000').strip())
                
                #Signal Type 2,3 : Mapping Engineering Measure Range
                scale_high = float(getDict(ads1115_dic,ch_name+'_scale_high', 5.0)) 
        
                if ch<2:
                    # CT :CTL type Current Sensor, VOL : Voltage, 4_20mA: 4~20 mA (use 250 ohm resistor)
                    signal_type=getDict(ads1115_dic,ch_name+'_input_signal_type', 'CT')
                else:
                    # CT :CTL type Current Sensor, VOL : Voltage, 4_20mA: 4~20 mA (use 250 ohm resistor)
                    signal_type=getDict(ads1115_dic,ch_name+'_input_signal_type', 'VOL')
                    
                #function: (vol + V_off) * conv + offset
                if (signal_type== 'CT') :
                    ADS1x15dict[chip]["conv"]=3000. / ct_r
                    ADS1x15dict[chip]["V_off"]=0
                    ADS1x15dict[chip]["offset"]=0
                elif (signal_type== 'VOL') :
                    ADS1x15dict[chip]["conv"]=(scale_high-scale_low) / (voltage_range*2)
                    ADS1x15dict[chip]["V_off"]=0
                    ADS1x15dict[chip]["offset"]=0
                    if ( conn_type == 1 ) :
                        ADS1x15dict[chip]["conv"] *=2.0
                elif (signal_type== '4_20mA') :
                    if (voltage_range == 5) :
                        ADS1x15dict[chip]["conv"] = (scale_high - scale_low) / 4
                        ADS1x15dict[chip]["V_off"]=1.0
                        ADS1x15dict[chip]["offset"]=scale_low
    #                    self.volHigh = 5
                    elif (voltage_range == 4) :
                        ADS1x15dict[chip]["conv"] = (scale_high - scale_low) / 3.2
                        ADS1x15dict[chip]["V_off"]=0.8
                        ADS1x15dict[chip]["offset"]=scale_low
                    else:
                        raise Exception(ch_name+'_input_signal_type is set 4_20mA, so the '+ch_name+'_voltage_range only set 5 or 4.')
                else:
                    raise Exception(ch_name+'_input_signal_type value error. please set CT, VOL ,or 4_20mA')
    #                    self.volHigh = 4
        ADS1x15dict[chip]["enable"]=chip_enable
    if use_buffer is True and ADS_enable_num*ADS_Fs>3200: #total sample per sec
        for Fs in [3000,2500,2000,1600,1000,800,400,200,100]:
            if ADS_Fs>=Fs and ADS_enable_num*Fs<=3200:
                ADS_Fs=Fs
                break
    
#    print(ADS1x15dict)
    if ADS1x15_enable:
        if use_buffer is True:
            ads1115_proc = esp32_process(ADS1x15dict,
                                         ADS_Fs,
                                         record_second)
        if use_buffer is False:
            ads1115_proc=[]
            proc_id=0
            for i,d in enumerate(ADS1x15dict):
                if d["enable"]:
                    ads1115_proc.append(ads1115_process(i+0x48,
                                                        d,
                                                        record_second))
                    ads1115_proc[proc_id].start()
                    proc_id+=1
        
#        print("time error is %.3f" %(ads1115_proc.check_time(5)*100)+"%")
    
    #mpu9250
    mpu9250_name=[]
    mpu9250_name.append(getDict(mpu9250_dic,'ch1_name', ''))
    mpu9250_name.append(getDict(mpu9250_dic,'ch2_name', ''))
    mpu9250_name.append(getDict(mpu9250_dic,'ch3_name', ''))
    mpu9250_name.append(getDict(mpu9250_dic,'ch4_name', ''))
    mpu9250_name.append(getDict(mpu9250_dic,'ch5_name', ''))
    mpu9250_FullScaleRange=[]
    mpu9250_FullScaleRange.append(int(getDict(mpu9250_dic,'ch1_full_scale_range',4)))
    mpu9250_FullScaleRange.append(int(getDict(mpu9250_dic,'ch2_full_scale_range',4)))
    mpu9250_FullScaleRange.append(int(getDict(mpu9250_dic,'ch3_full_scale_range',4)))
    mpu9250_FullScaleRange.append(int(getDict(mpu9250_dic,'ch4_full_scale_range',4)))
    mpu9250_FullScaleRange.append(int(getDict(mpu9250_dic,'ch5_full_scale_range',4)))
    mpu9250_data_type=[]
    mpu9250_data_type.append(int(getDict(mpu9250_dic,'ch1_data_type',1)))
    mpu9250_data_type.append(int(getDict(mpu9250_dic,'ch2_data_type',1)))
    mpu9250_data_type.append(int(getDict(mpu9250_dic,'ch3_data_type',1)))
    mpu9250_data_type.append(int(getDict(mpu9250_dic,'ch4_data_type',1)))
    mpu9250_data_type.append(int(getDict(mpu9250_dic,'ch5_data_type',1)))
    mpu9250_gyro_scale_range=[]
    mpu9250_gyro_scale_range.append(int(getDict(mpu9250_dic,'ch1_gyro_scale_range',4)))
    mpu9250_gyro_scale_range.append(int(getDict(mpu9250_dic,'ch2_gyro_scale_range',4)))
    mpu9250_gyro_scale_range.append(int(getDict(mpu9250_dic,'ch3_gyro_scale_range',4)))
    mpu9250_gyro_scale_range.append(int(getDict(mpu9250_dic,'ch4_gyro_scale_range',4)))
    mpu9250_gyro_scale_range.append(int(getDict(mpu9250_dic,'ch5_gyro_scale_range',4)))
    #print('==MPU9250==--<',mpu9250_dic['ch1_name'],'>--')
    #print('==MPU9250==--<',mpu9250_dic['ch2_name'],'>--')
    spi_clock=int(getDict(mpu9250_dic,'spi_clock',VIB_SPI_CLOCK))
    mpu9250=[]
    for i in range(mpu9250MaxNum):
        mpu9250.append(dict())
        if(mpu9250_name[i]):
            if(i<=1 and use_buffer):
                raise Exception('The SPI0 is used by ESP32, cannot enable MPU9250 slave'+str(i))
                continue
            mpu9250[i]["proc"] = mpu9250_process(i, 
                   mpu9250_FullScaleRange[i],
                   mpu9250_gyro_scale_range[i],
                   sampling_rate,
                   mpu9250_data_type[i],
                   spi_clock,
                   record_second)
            mpu9250[i]["proc"].start()
#    mpu9250[i]["proc"].SampleRateTest(3)\
          
    
          
    #ADXL355
    ADXL355=[]
    spi_clock=int(getDict(ADXL355_config,'spi_clock',ADXL_SPI_CLOCK))
    
    ADXL355_sampling_rate=4000
    for i in ADXL355_process.ODR_TO_BIT.keys():
        if i>=ADXL355_sampling_rate:
            ADXL355_sampling_rate=i
            break
    
    for i in range(1,6):
        ADXL355_name=getDict(ADXL355_config,'ch'+str(i)+'_name', '')
        if ADXL355_name!="":
            if(i<=2 and use_buffer):
                raise Exception('The SPI0 is used by ESP32, cannot enable ADXL335 slave'+str(i))
                continue
                
            ADXL355_FullScaleRange=int(getDict(ADXL355_config,'ch'+str(i)+'_full_scale_range',4))
            
            if(ADXL355_FullScaleRange not in  ADXL355_process.RANGE_TO_BIT.keys()):
                raise Exception('ch'+str(i)+'_full_scale_range setting not in range {2,4,8}')
                continue
                
            ADXL355.append(ADXL355_process(i-1,
                   ADXL355_name,
                   ADXL355_FullScaleRange,
                   ADXL355_sampling_rate,
                   spi_clock,
                   record_second))
            ADXL355[-1].start()
    
          
            
    gy530_enable=False
    gy530_dic["ch1_name"]=getDict(gy530_dic,'ch1_name',"")
    if gy530_dic["ch1_name"]!="":
        gy530_enable=True
        gy530_proc=gy530_process(gy530_dic["ch1_name"],record_second)
        gy530_proc.start()
            
        
    kashi_enable=False
    kashi_device=[]
    ports = list(list_ports.comports())
    locationList=[]
    serialList=[]
    for port in ports:
        serialList.append(port.device)
        locationList.append(port.location)
    for i in range(MAX_KASHIYAMA_CHIP):
        kashi_name=getDict(kashiyama_dic,"ch"+str(i+1)+"_name","")
        if kashi_name!="":
            kashi_location=getDict(kashiyama_dic,"ch"+str(i+1)+"_location","")
            if kashi_location in locationList:
                index=locationList.index(kashi_location)
                kashi_device.append({
                        "path":serialList[index],
                        "name":kashi_name
                        })
                kashi_enable=True
            else:
                raise Exception("The kashiyama ch"+str(i+1)+"_location "+kashi_location+" is not found.")
    
    if kashi_enable:
        kashi_proc=kashi_process(kashi_device,record_second)
        kashi_proc.start()
        
        
    polling_device_enable=False
    polling_device_name=[]
    polling_device_emp=True
    polling_device_len=int(getDict(polling_device_dic,'length',4))
    
    for i in range(polling_device_len):
        dic_name=getDict(polling_device_dic,'ch'+str(i+1)+'_name',"")
        polling_device_name.append(dic_name)
        if(dic_name!=""):
            polling_device_emp=False
    polling_device_host=getDict(polling_device_dic,'host',"")
    polling_device_networkNo=int(getDict(polling_device_dic,'network',"0"))
    polling_device_stationNo=int(getDict(polling_device_dic,'station',"0"))
    polling_device_register=getDict(polling_device_dic,'register',"")
    print("Polling device infor,(host=",polling_device_host,
                                  ",networkNo=",polling_device_networkNo,
                                  ",stationNo=",polling_device_stationNo,
                                  ",register=",polling_device_register,
                                  ",len=",polling_device_len,")")
    if(polling_device_host!="" and
       polling_device_networkNo!="" and
       polling_device_stationNo!="" and
       polling_device_register!="" and
       polling_device_len>0 and
       polling_device_emp is False):
        polling_device_enable=True
        polling_device_proc=polling_device_process(polling_device_host,
                                                   polling_device_networkNo,
                                                   polling_device_stationNo,
                                                   polling_device_register,
                                                   polling_device_name,
                                                   record_second)
        polling_device_proc.start()
        print("Enable polling device")
    
    
    PLC_enable=False
    PLC_name=[]
    for i in range(4):
        PLC_name.append(getDict(PLC_config,'ch'+str(i+1)+'_name',""))
    PLC_register = [] 
    PLC_name_Arr = []
    
    if trigger_plc_register!= None:
        PLC_register.append(trigger_plc_register)
        PLC_name_Arr.append(["PLC_trigger","","",""])
    PLC_register_dict=getDict(PLC_config,'register',"")
    if PLC_register_dict!="":
        PLC_register.append(PLC_register_dict)
        PLC_name_Arr.append(PLC_name)
    if len(PLC_register)>0:
        if PLC_ip=="":
            raise Exception("Please setting the PLC_ip at setting of config.txt")
        for i in PLC_register:
            if i[0].upper() not in PLC_white_list:
                raise Exception("The PLC register is setting error.")
        PLC_enable=True
        if plc_protocol=="UDP":
            PLC_proc=plc_process(PLC_ip,PLC_port,False,plc_protocol,PLC_register,PLC_name_Arr,record_second)
        elif plc_protocol=="TCP":
            PLC_proc=plc_process(PLC_ip,PLC_port,True,plc_protocol,PLC_register,PLC_name_Arr,record_second)
        else:
            raise Exception("The plc protovol cannot support'"+plc_protocol+"'!")
            
        PLC_proc.start()
     
        
    IO_sample_enable=False   
    IO_sample_name_mapping=dict()
    IO_sample_name_list=[
            "plc_4_name",
            "plc_17_name",
            "plc_18_name",
            "relay_1_name",
            "relay_2_name",
            "relay_3_name",
            "gpio_22_name",
            "gpio_23_name",
            "gpio_24_name",
            "esp_25_name"]
    IO_sample_pin_list=[
            4,
            17,
            18,
            12,
            26,
            13,
            22,
            23,
            24,
            25]
    for index,IO_sample_name in enumerate(IO_sample_name_list):
        IO_sample_name_val=getDict(IOsample_dic,IO_sample_name,"")
        if IO_sample_name_val!="":
            IO_sample_name_mapping[IO_sample_name_val]=IO_sample_pin_list[index]
    
    if len(IO_sample_name_mapping)>0:
        IO_sample_proc=IO_sample_process(IO_sample_name_mapping,record_second)
        IO_sample_proc.start()
        IO_sample_enable=True
        
    time.sleep(0.3) #wait MPU9250, ADS and GY530 init
    if audio_enable: #wait audio init
        time.sleep(0.3)
    if VPA308R_enable : #wait VAP308R heigher than 1sec
        time.sleep(1.7)
    
            
    #wait for register
    #time.sleep(1)
    #trigger_gpio_no = int(sensor_dic.get('trigger_gpio_no',0))
    #trigger_on_delay_time = float(sensor_dic.get('trigger_on_delay_time',0))
    #trigger_on_timeout_multiple = float(sensor_dic.get('trigger_on_timeout_multiple',1.5))
    #trigger_on = int(sensor_dic.get('trigger_on',0))
    if trigger_plc_register!= None and trigger_gpio_no > 0:
        raise Exception("The config cannot enable gpio trgger and plc trgger!")
        
        
    if (trigger_gpio_no > 0 ) :
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trigger_gpio_no, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        print('wait trigger io on, ',trigger_on, ', status=', GPIO.input(trigger_gpio_no) )
        timeStartCheck = time.perf_counter()
        
        while ( ( GPIO.input(trigger_gpio_no) == trigger_on ) and ((time.perf_counter() -timeStartCheck) < timeout_count)) :            
            time.sleep(0.05)            
        while ( (GPIO.input(trigger_gpio_no) != trigger_on ) and ((time.perf_counter() -timeStartCheck) < timeout_count)) :            
            time.sleep(0.05)
        if ( (time.perf_counter() -timeStartCheck) >= timeout_count) :
            record_loop_cnt = record_loop
            print('wait trigger io timeout', ', status=', GPIO.input(trigger_gpio_no) )
        else :
            print('trigger signal matched.', ', status=', GPIO.input(trigger_gpio_no) )
            if ( trigger_on_delay_time > 0 ):
                print('trigger delay --',trigger_on_delay_time)
                time.sleep(trigger_on_delay_time)
                
    if (trigger_plc_register!= None) :
        if trigger_plc_register.upper()[0] not in PLC_white_list:
            raise Exception("The plc processing cannot support register type '"+trigger_plc_register[0]+"'!")
        try:
            int(trigger_plc_register[1:])
        except:
            raise Exception("The plc register type is not correct!")
        if PLC_ip=="":
            raise Exception("Please setting the PLC_ip at setting of config.txt")
            
        plc_trgger_type=trigger_plc_register[0]
        plc_trgger_no=int(trigger_plc_register[1:])
        
        plc_io = PLC_proc.plc.get(plc_trgger_type,plc_trgger_no,1)[0]
        
        print('wait trigger ',trigger_plc_register,' on, ',trigger_on, ', status=', plc_io)
        timeStartCheck = time.perf_counter()
        
        while ( plc_io == trigger_on and (time.perf_counter() -timeStartCheck) < timeout_count) :    
            time.sleep(0.05)
            plc_io = PLC_proc.plc.get(plc_trgger_type,plc_trgger_no,1)[0]
        while ( plc_io != trigger_on  and (time.perf_counter() -timeStartCheck) < timeout_count) :            
            time.sleep(0.05)
            plc_io = PLC_proc.plc.get(plc_trgger_type,plc_trgger_no,1)[0]
            
        if ( (time.perf_counter() -timeStartCheck) >= timeout_count) :
            record_loop_cnt = record_loop
            print('wait plc trigger io timeout', ', status=', plc_io)
        else :
            print('trigger signal matched.', ', status=', plc_io)
            if ( trigger_on_delay_time > 0 ):
                print('trigger delay --',trigger_on_delay_time)
                time.sleep(trigger_on_delay_time)
    
    
    resample=0
    while record_loop_cnt < record_loop:
        startTime=time.time()
        print('Start logging',datetime.datetime.now().strftime("    %Y-%m-%d %H:%M:%S"), time.perf_counter())
        os.system("taskset -cp 0 %d" %pid)
        save_flag=True
        totalResult=[]
        audioResult=dict()
                
        for i in range(mpu9250MaxNum):
            if(mpu9250_name[i]):
                mpu9250[i]["proc"].start_sample()
        
        for p in ADXL355:
            p.start_sample()
                
        if(IO_sample_enable):
            IO_sample_proc.start_sample()
            
        if(gy530_enable):
            gy530_proc.start_sample()
            
        if(kashi_enable):
            kashi_proc.start_sample()
            
        if(PLC_enable):
            PLC_proc.start_sample()
            
        if(minas_enable):
            for p in minas_proc:
                p.start_sample()
                
        if(audio_enable):
            for p in audio_proc:
                p.start_sample()
            
        if(polling_device_enable):
            polling_device_proc.start_sample()
            
        if(VPA308R_enable):
            for p in VPA308R_proc:
                p.start_sample()
            
        if use_buffer is False and ADS1x15_enable:
            for chip in ads1115_proc:
                chip.start_sample()
                
        if use_buffer is True and ADS1x15_enable:
            ADSresult=ads1115_proc.get_sample()
            totalResult.append(ADSresult)
            ADSresult=None
            
        offsetTime = startTime+1 #default add 1 sec
        if(PLC_enable):
            timeoutSet=record_second*1.1-(time.time()-offsetTime)
            if timeoutSet<0:
                timeoutSet=1
            PLC_proc.sub_join(timeoutSet)
            data=PLC_proc.getData()
            totalResult.append(data)
            data=None
            
        if(gy530_enable):
            timeoutSet=record_second*1.1-(time.time()-offsetTime)
            if timeoutSet<0:
                timeoutSet=1
            gy530_proc.sub_join(timeoutSet)
            data=gy530_proc.getData()
            totalResult.append(data)
            data=None
            
        if(kashi_enable):
            timeoutSet=record_second*1.1-(time.time()-offsetTime)
            if timeoutSet<0:
                timeoutSet=1
            kashi_proc.sub_join(timeoutSet)
            data=kashi_proc.getData()
            totalResult.append(data)
            data=None
            
        if(IO_sample_enable):
            timeoutSet=record_second*1.1-(time.time()-offsetTime)
            if timeoutSet<0:
                timeoutSet=1
            IO_sample_proc.sub_join(timeoutSet)
            data=IO_sample_proc.getData()
            totalResult.append(data)
            data=None
            
        if(polling_device_enable):
            timeoutSet=record_second*1.1-(time.time()-offsetTime)
            if timeoutSet<0:
                timeoutSet=1
            polling_device_proc.sub_join(timeoutSet)
            data=polling_device_proc.getData()
            totalResult.append(data)
            data=None
            
        if(VPA308R_enable):
            for p in VPA308R_proc:
                timeoutSet=record_second*1.1-(time.time()-offsetTime)
                if timeoutSet<0:
                    timeoutSet=1
                p.sub_join(timeoutSet)
                data=p.getData()
                angle_detect(p.name,data,p.sapleRate,signal_detect_threshold)
                totalResult.append(data)
                data=None
                
        if(minas_enable):
            for p in minas_proc:
                timeoutSet=record_second*1.1-(time.time()-offsetTime)
                if timeoutSet<0:
                    timeoutSet=1
                p.sub_join(timeoutSet)
                data=p.getData()
                totalResult.append(data)
                data=None
            
            
        for p in ADXL355:
            timeoutSet=record_second*1.1-(time.time()-offsetTime)
            if timeoutSet<0:
                timeoutSet=1
            print(timeoutSet)
            p.sub_join(timeoutSet)
            data=p.getData()
            angle_detect(p.name,data,p.sampleRate,signal_detect_threshold)
            totalResult.append(data)
            data=None
            
        if(audio_enable):
            for i,p in enumerate(audio_proc):
                timeoutSet=record_second*1.1-(time.time()-offsetTime)+3 #stream release time
                if timeoutSet<0:
                    timeoutSet=1
                p.sub_join(timeoutSet)
                data = p.getData()
                audioResult[data['name']]=dict()
                for k in data.keys():
                    if k=='name':
                        continue
                    audioResult[data['name']][k]=data[k]
                
                
                """
                for i,v in enumerate(data["value"]):
                    audioFFT=abs(np.fft.fft(v))
                    audioFFTLen = len(audioFFT)//2
                    audioFFT = audioFFT[:audioFFTLen]
                    audioFFT = 10*np.log(audioFFT/audioFFTLen*2)
                    freq = np.arange(audioFFTLen)
                    freq = freq/max(freq)*data["rate"]/2
                    audioFFTMaxX = freq[np.argmax(audioFFT)]
                    audioFFTMaxY = max(audioFFT)
                    
                    plt.plot(freq,audioFFT)
                    plt.title(data['name']+",ch"+str(i+1))
                    plt.ylabel("value 10log(x)")
                    plt.xlabel("freq(Hz)")
                    plt.text(audioFFTMaxX,audioFFTMaxY,"{:6.3f} Hz".format(audioFFTMaxX))
                    plt.show()
                """
                
                
                
                data=None
                
                
            
        if use_buffer is False and ADS1x15_enable:
            for chip in ads1115_proc:
                timeoutSet=record_second*1.1-(time.time()-startTime)
                if timeoutSet<0:
                    timeoutSet=1
                chip.sub_join(timeoutSet)
                data=chip.getData()
                ADSresult={}
                ADSresult['timestamp']= data["time"]
                ADSresult[chip.ADS_dict["name"]]= data["value"]
                totalResult.append(ADSresult)
                ADSresult=None
                data=None
        for i in range(mpu9250MaxNum):
            if(mpu9250_name[i]):
                timeoutSet=record_second*1.1-(time.time()-startTime)
                if timeoutSet<0:
                    timeoutSet=1
                mpu9250[i]["proc"].sub_join(timeoutSet)
                data = mpu9250[i]["proc"].getData()
                MPUresult={}
                MPUresult['timestamp']= data["time"]
                sample_time=data["time"][-1]-data["time"][0]
                #print(i,"sample_time=",sample_time)
                if sample_time<record_second*0.5:
                    save_flag=False
                    
                if ((mpu9250[i]["proc"].dataType == 2) | (mpu9250[i]["proc"].dataType == 3)) :                        
                    MPUresult['gyX_' + mpu9250_name[i]]= data["gyroX"]
                    MPUresult['gyY_' + mpu9250_name[i]] = data["gyroY"]
                    MPUresult['gyZ_' + mpu9250_name[i]] = data["gyroZ"]
                if ((mpu9250[i]["proc"].dataType == 1) | (mpu9250[i]["proc"].dataType == 3)) :
                    MPUresult['aX_' + mpu9250_name[i]] = data["accX"]
                    MPUresult['aY_' + mpu9250_name[i]] = data["accY"]
                    MPUresult['aZ_' + mpu9250_name[i]] = data["accZ"]
                    
                    angle_detect(mpu9250_name[i],MPUresult,mpu9250[i]["proc"].sampleRate,signal_detect_threshold)
                    
                totalResult.append(MPUresult)
                MPUresult=None
                data=None
                
                
        os.system("taskset -cp 0-3 %d" %pid)
        if save_flag is False:
            totalResult=None
            resample+=1
            if resample<3:
                print("MPU9250 buffer is overflow, so sample again.")
                continue
        if len(totalResult)>0 or len(audioResult)>0:
            if resample<3:
                os.system("taskset -cp 0-3 %d" %pid)
                
                alignStartTime(totalResult,audioResult)
                
                if data_merge_optmize ==1:
                    pd_result,sf=dataMatchOptmize(totalResult)
                else:
                    pd_result,sf=dataMatch(totalResult)
                    
                    
                print(time.ctime(),'sf=',sf )
                signal_key = "{}@{}@{}@".format(getDict(setting_dic,'eqp_name', 'TEST01'),getDict(setting_dic,'chamber', 'X'),getDict(setting_dic,'project_id', 0)) + time.strftime("%Y%m%d_%H%M%S", time.localtime())+ "_{}".format(sf)
                audio_key = "{}@{}@{}@".format(getDict(setting_dic,'eqp_name', 'TEST01'),getDict(setting_dic,'chamber', 'X'),getDict(setting_dic,'project_id', 0)) + time.strftime("%Y%m%d_%H%M%S", time.localtime())
                if len(totalResult)>0:
                    signal_dic[signal_key]=pd_result
                else:
                    signal_dic=dict()
                totalResult=None
                
                for k in audioResult.keys():
                    name = k
                    ch = audioResult[k]["ch"]
                    rate = audioResult[k]["rate"]
                    audioResult_dic[audio_key+"_"+name+"_"+str(ch)+"_"+str(rate)]=audioResult[k]
            else:
                print("Can's sucessfully sample, stop this process.")
        resample=0
        record_loop_cnt +=1
        
        
        """
        fig,ax1=plt.subplots(figsize=(10,5))
        ax1.set_xlabel("Time(s)")
        ax1.set_ylabel("Vol")
        
        ax1.set_xlabel("datas")
        ax1.set_ylabel("Vol")
        ax1.plot(signal_dic[signal_key]["ADS_A"],label="ADS_A",color="r")
        ax1.tick_params(axis='y',labelcolor="tab:red")
        ax2=ax1.twinx()
        ax2.set_ylabel("current (A)")
        ax2.plot(signal_dic[signal_key]["KASHI_A_dpCur"],label="KASHI_A_dpCur",color="b")
#        ax2.set_ylabel("distance (mm)")
#        ax2.plot(signal_dic[signal_key]["GY_A"],label="GY_A",color="b")
#        ax2.set_ylabel("Acc(0.01G) / Gyro(dps)")
#        ax2.plot(signal_dic[signal_key]["aX_MPU_A"],label="(type1)MPU_A accX 1K",color="b")
#        ax2.plot(signal_dic[signal_key]["aX_MPU_B"],label="(type1)MPU_B accX 1K",color="g")
        ax2.tick_params(axis='y',labelcolor="tab:blue")
        fig.tight_layout()
        ax1.legend(loc="upper right")
        ax2.legend(loc="upper right")
        plt.title("result after timestamp match")
#               plt.savefig("result after timestamp match_"+str(record_loop_cnt)+".png")
        plt.show()
        """

    if(IO_sample_enable):
        IO_sample_proc.release(10)
        
    if(gy530_enable):
        gy530_proc.release(10)
        
    if(kashi_enable):
        kashi_proc.release(10)
        
    if(PLC_enable):
        PLC_proc.release(10)
        
    if(polling_device_enable):
        polling_device_proc.release(10)
        
    for i in range(mpu9250MaxNum):
        if(mpu9250_name[i]):
            mpu9250[i]["proc"].release(10)
        
    if use_buffer is False and ADS1x15_enable:
        for chip in ads1115_proc:
            chip.release(10)
    
    if VPA308R_enable:
        for p in VPA308R_proc:
            p.release(10)
            
    for p in ADXL355:
        p.release(10)
        
    if(audio_enable):
        for p in audio_proc:
            p.release(10)
        
    if(minas_enable):
        for p in minas_proc:
            p.release(10)
            
    return signal_dic,audioResult_dic
 
def processing(setting_dic, 
               sensor_dic, 
               ads1115_dic, 
               mpu9250_dic, 
               gy530_dic={}, 
               kashiyama_dic={}, 
               PLC_config={},
               IO_sample_config={},
               polling_device_config={},
               VPA308R_config={},
               audio_config={},
               ADXL355_config={},
               minas_config={}):
    print("** ** ** start sensor, version:",__version__)
    global CPU_CORE_NUM
    CPU_CORE_NUM=3
    pid=os.getpid()
    print("Sensor processing pid is",pid)
    os.system("taskset -cp 0 %d" %(pid)) #main processing is cpu core 3
    
    
    #global home_path
    #global data_path
    signal_dic = {}
    audioResult_dic={}
    print('data_path=',phm_func.data_path)
    
    #print('data_path f=',phm_func.data_path)
    log_path = phm_func.data_path + '/Sensor'
    print('sensor log path=',log_path)
    save_data = int(sensor_dic['save_data'])
       
#    if not key_chk(setting_dic):
#        return signal_dic
    
    #print('---')   
    signal_dic,audioResult_dic = get_value(setting_dic, 
                           sensor_dic, 
                           ads1115_dic, 
                           mpu9250_dic, 
                           gy530_dic, 
                           kashiyama_dic,
                           PLC_config,
                           IO_sample_config,
                           polling_device_config,
                           VPA308R_config,
                           audio_config,
                           ADXL355_config,
                           minas_config)
    #print([signal_dic,audioResult_dic])
    
#    try:
#        signal_dic = get_value(setting_dic, sensor_dic, ads1115_dic, mpu9250_dic, gy530_dic, kashiyama_dic)
#    except Exception as e:
#        print(e)
#        print("End the sample processing")
#        return {}
        
    #save data
    if save_data:
        #free memory 200MB
        if shutil.disk_usage('/').free//(2**20) < 200:
            files = glob.glob(log_path + '/*.csv')
            files.sort(key=os.path.getmtime)
               
            for csv_file in files:
                os.remove(csv_file)
                   
                if shutil.disk_usage('/').free//(2**20) > 200:
                    break
 
        if not os.path.exists(log_path):
            os.mkdir(log_path)
                               
        for data_key in signal_dic:
            print('Sensor Data_key=',data_key, ' log_path=', log_path)
            signal_dic[data_key].to_csv(log_path + '/' + data_key + '.csv', index=False)
        
        if len(audioResult_dic)>0:
            import wave
            for data_key in audioResult_dic:
                print('Audio Data_key=',data_key, ' log_path=', log_path)
                wf=wave.open(log_path + '/' + data_key + '.wav','wb')
                wf.setnchannels(audioResult_dic[data_key]['ch'])
                wf.setsampwidth(audioResult_dic[data_key]['size'])
                wf.setframerate(audioResult_dic[data_key]['rate'])
                wf.writeframes(audioResult_dic[data_key]['value'].T.reshape(-1))
                #print("@@@ test",data_key,audioResult_dic[data_key]['value'].T.reshape(-1).shape
                #,audioResult_dic[data_key]['value'].shape)
                wf.close()
    
    os.system("taskset -cp 0-3 %d" %(pid))
    return signal_dic,audioResult_dic


def getSection(config,name):
    try:
        ret=config.items(name)
        return ret
    except:
        return {}
    
if __name__ == "__main__":
    pid=os.getpid()
    os.system("taskset -cp 0-3 %d" %(pid))
#    os.system("renice -n -20 -p %d" %(pid))
    #import phm_func as phm_func
    print('home_path=',phm_func.home_path)
    #phm_func.check_directory_of_phm_data()
    #print('home_path=',phm_func.home_path)
    config_path = "../config.ini"
    setting_config = {}
    sensor_config = {}
    ads1115_config = {}
    mpu9250_config = {}
    gy530_config = {}
    kashiyama_config = {}
    PLC_config = {}
    IO_sample_config={}
    polling_device_config={}
    VPA308R_config={}
    audio_config={}
    ADXL355_config={}
    minas_config={}
    
    config = configparser.ConfigParser()
    config.read(config_path)
#    print('home_path=',phm_func.home_path)
    #setting
    items = getSection(config,'setting')
    for item in items:
        setting_config[item[0]] = item[1]
   
    #sensor
    items = getSection(config,'sensor')
    for item in items:
        sensor_config[item[0]] = item[1]
   
    #ads1115
    items = getSection(config,'ads1115')
    for item in items:
        ads1115_config[item[0]] = item[1]
       
    #mpu9250
    items = getSection(config,'mpu9250')
    for item in items:
        mpu9250_config[item[0]] = item[1]
        
    #gy530
    items = getSection(config,'gy530')
    for item in items:
        gy530_config[item[0]] = item[1]
        
    #kashiyama
    items = getSection(config,'kashiyama')
    for item in items:
        kashiyama_config[item[0]] = item[1]
        
    #minas
    items = getSection(config,'minas')
    for item in items:
        minas_config[item[0]] = item[1]
        
    #plc
    items = getSection(config,'PLC')
    for item in items:
        PLC_config[item[0]] = item[1]
        
    #I/O sample
    items = getSection(config,'IO_sample')
    for item in items:
        IO_sample_config[item[0]] = item[1]
        
    #polling_device_config
    items = getSection(config,'polling_device')
    for item in items:
        polling_device_config[item[0]] = item[1]
        
    #VPA308R_config
    items = getSection(config,'VPA308R')
    for item in items:
        VPA308R_config[item[0]] = item[1]
        
    #audio_config
    items = getSection(config,'audio')
    for item in items:
        audio_config[item[0]] = item[1]
        
    #ADXL355_config
    items = getSection(config,'ADXL355')
    for item in items:
        ADXL355_config[item[0]] = item[1]
       
    print('Start --->', time.ctime())
   
#    print('setting: ',setting_config)
#    print('sensor: ',sensor_config)
    #print('mpu9250: ',mpu9250_config)try:
#    connection = manager.connect("I2Cx")
    
    signal_dic = processing(setting_config,
                            sensor_config,
                            ads1115_config,
                            mpu9250_config,
                            gy530_config,
                            kashiyama_config,
                            PLC_config,
                            IO_sample_config,
                            polling_device_config,
                            VPA308R_config,
                            audio_config,
                            ADXL355_config,
                            minas_config)
#    try:
#        signal_dic = processing(setting_config, sensor_config, ads1115_config, mpu9250_config)
#    except Exception as e:
#        print(repr(e))
#   
#    print('Endt --->', time.ctime())
