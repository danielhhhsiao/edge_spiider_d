#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 21 11:41:57 2021

@author: etao
"""


import multiprocessing
import time
import os
import numpy as np
import ftplib
import pickle
from io import BytesIO
from datetime import datetime
import psutil
import VibrationHub


class vibHubProc(multiprocessing.Process):
    def __init__(self,spi_ch=-1,Fs=1000):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("class create")
        self.Fs=Fs
        self.useHub=False
        self.real=False
        if spi_ch >=0 and spi_ch<=4:
            self.useHub=True
             
    
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.queue.qsize()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
        
        
        if self.useHub:
            self.vib = VibrationHub.VibHub(spi_ch)
            print("CheckSlave:",self.vib.CheckSlave())
            self.real=self.vib.CheckSlave()
            self.vib.ScanSensor()
            print("Sansor Enable:",self.vib.enable)
            self.vib.CheckSlave()
            
            
            self.vib.SelectAllSensor([True,True,True,True,True,True])
            self.vib.SetScale(0,2)
            self.vib.SetScale(1,2)
            self.vib.SetScale(2,2)
            self.vib.SetScale(3,2)
            self.vib.SetScale(4,2)
            self.vib.SetScale(5,2)
            self.vib.SetFs(self.Fs)

    
    def stopSample(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
        
            
    def run(self):
        self.states["pid"]=os.getpid()
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        nowTime=time.time()
        # count=0
        if self.useHub :
            self.vib.StartSample()
            while not self.states["release"]:
                if self.real:
                    dataLen=self.vib.GetBufferLen()
                    readLen=int(int((dataLen)//36)*36)
                else:
                    lastTime=time.time()
                    readLen=36*int(self.Fs*(lastTime-nowTime))
                    nowTime=lastTime
                if(readLen>0):
                    data=np.array(self.vib.GetBuffer(readLen),dtype=np.uint8)
                    self.queue.put(data)
                time.sleep(0.01)
            self.vib.StartSample()
        else:
            while not self.states["release"]:
                if time.time()-nowTime>0.01: #10ms
                    lastTime=time.time()
                    length=36*int(self.Fs*(lastTime-nowTime))
                    data=np.zeros(length,dtype=np.uint8)
                    #count=count+length
                    
                    nowTime=lastTime
                    self.queue.put(data)
                    #print(time.time(),length,self.queue.qsize())
                else:
                    time.sleep(0.001)
            
           
    def value_convert(self,arr,V_off=0,scale=0,offset=0):
        return (arr-V_off)*scale+offset
    
    def release(self):
        self.stopSample()
        if self.is_alive():
            self.join()
        self.exit.set()
   
def getEvir():
    cpuUsage=psutil.cpu_percent()
    cpuClock=psutil.cpu_freq().current
    info = psutil.virtual_memory()
    memory_using = info.percent
    
    diskinfo = psutil.disk_usage("/")
    disk_free=round(diskinfo.free/(1024*1024*1024),3)
    cpu_temp=-1
    device_infor=psutil.sensors_temperatures()
    if("cpu-thermal" in device_infor.keys()):
        cpu_temp = device_infor["cpu-thermal"][0].current
    if("cpu_thermal" in device_infor.keys()):
        cpu_temp = device_infor["cpu_thermal"][0].current
        
    return cpuUsage,cpuClock,cpu_temp,memory_using,disk_free


if __name__ == "__main__":
    FTP_HOST = "192.168.0.137"
    FTP_USER = "etao"
    FTP_PASS = "19960709"


    
    busyPercent=0.5
    testKeepTime=3600
    sampleSec=20
    Fs=4000
    oneTime=36//2 #1data = 2byte
    condition=sampleSec*Fs*oneTime
    
    index = 0
    buffer=np.zeros(10000000,dtype=np.float32)
    
    # os.system("taskset -cp 3 %d" %(os.getpid()))
    
    recode=dict()
    recode['recodeTime']=[]
    recode['recodeTimestamp']=[]
    recode['cpuUsage']=[]
    recode['cpuClock']=[]
    recode['cpuTemp']=[]
    recode['memoryUsage']=[]
    recode['diskFreeG']=[]
    recode['queueSize']=[]
    recode['uploadUsageTime']=[]
    
    ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
    ftp.encoding = "utf-8"
        
    now = datetime.now() # current date and time
    timeStr2 = now.strftime("%Y/%m/%d %H:%M:%S")
    cpuUsage,cpuClock,cpu_temp,memory_using,disk_free=getEvir()
    recode['recodeTime'].append(timeStr2)
    recode['recodeTimestamp'].append(now.timestamp())
    recode['cpuUsage'].append(cpuUsage)
    recode['cpuClock'].append(cpuClock)
    recode['cpuTemp'].append(cpu_temp)
    recode['memoryUsage'].append(memory_using)
    recode['diskFreeG'].append(disk_free)
    recode['queueSize'].append(0)
    recode['uploadUsageTime'].append(0)
    
    vib = vibHubProc(0,Fs)
    vib.start()
    testStartTime=time.time()
    
    while time.time()-testStartTime<testKeepTime:
        
        while index < condition:
            if not vib.queue.empty() :
                data=vib.queue.get(False)
                data=data[0::2]*256+data[1::2]
                buffer[index:index+len(data)]=data
                index=index+len(data)
                #print(index,"/",condition,"(queue=",vib.queue.qsize())
            else:
                time.sleep(0.1)
        print("queue size:",vib.queue.qsize())
        raw = np.array(buffer[:condition],dtype=np.float32)
        if index>condition:
            buffer[0:index-condition]=buffer[condition:index]
        print("index=",index)
        index=index-condition
        
        
        print("busy simulator")
        busyStartTime=time.time()
        justVar=np.ones(100)
        while time.time()-busyStartTime<sampleSec*busyPercent:
            justVar=justVar+1
            justVar=justVar-1
        print("busy finish")
        
        
        #save array to binary in memory
        raw=raw.reshape([-1,18])
        temp = BytesIO()
        #np.savetxt(temp, raw, delimiter=",")
        pickle.dump(raw, temp)
        temp.seek(0)
        now = datetime.now() # current date and time
        timeStr = now.strftime("%Y_%m_%d_%H_%M_%S")
        fileName="test_"+timeStr+".pkl"
        
        print("upload")
        #upload memory data
        uploadTime=time.time()
        # ftp.storbinary(f"STOR test.csv", temp)
        ftp.storbinary("STOR "+fileName, temp)
        uploadUsageTime=time.time()-uploadTime
        print("uploaded use time:",uploadUsageTime)
        print("test time:",time.time()-testStartTime,"/",testKeepTime)
        
        now = datetime.now() # current date and time
        timeStr2 = now.strftime("%Y/%m/%d %H:%M:%S")
        cpuUsage,cpuClock,cpu_temp,memory_using,disk_free=getEvir()
        recode['recodeTime'].append(timeStr2)
        recode['recodeTimestamp'].append(now.timestamp())
        recode['cpuUsage'].append(cpuUsage)
        recode['cpuClock'].append(cpuClock)
        recode['cpuTemp'].append(cpu_temp)
        recode['memoryUsage'].append(memory_using)
        recode['diskFreeG'].append(disk_free)
        recode['queueSize'].append(vib.queue.qsize())
        recode['uploadUsageTime'].append(uploadUsageTime)
    
    print("Finish all")
    vib.release()
    
    temp = BytesIO()
    CSV ="\n".join([k+','+','.join(list(map(str, v))) for k,v in recode.items()]) 
    temp.write(bytearray(CSV, "utf8"))
    
    temp.seek(0)
    fileName="test_recode_"+timeStr+".csv"
    ftp.storbinary("STOR "+fileName, temp)
    
    # with open('/Users/etao/Desktop/FTPtest/test_2021_05_24_15_06_27.pkl','rb') as f:
    #     x = pickle.load(f)
    #     print(x.shape)
        
        
        
        
        
        
        
        
        
        
        
        