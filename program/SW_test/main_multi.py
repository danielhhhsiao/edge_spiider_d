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
                time.sleep(0.05)
            self.vib.StartSample()
        else:
            while not self.states["release"]:
                if time.time()-nowTime>0.05: #10ms
                    lastTime=time.time()
                    length=36*int(self.Fs*(lastTime-nowTime))
                    data=np.zeros(length,dtype=np.uint8)
                    #count=count+length
                    
                    nowTime=lastTime
                    self.queue.put(data)
                    #print(time.time(),length,self.queue.qsize())
                else:
                    time.sleep(0.01)
            
           
    
    def release(self):
        self.stopSample()
        if self.is_alive():
            self.join()
        self.exit.set()

class FTPProc(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        FTP_HOST = "192.168.0.137"
        FTP_USER = "etao"
        FTP_PASS = "19960709"

        self.ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        self.ftp.encoding = "utf-8"
        
        manager=multiprocessing.Manager()
        self.queueData=manager.Queue()
        self.queueName=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
        

    
    def stop(self):
        self.states["release"]=True
    
    def put(self,data,name):
        self.queueData.put(data)
        self.queueName.put(name)
    
    def getPid(self):
        return self.states["pid"]
        
            
    def run(self):
        self.states["pid"]=os.getpid()
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        while not self.states["release"]:
            if self.queueData.empty()==False and self.queueName.empty()==False : 
                
                data=self.queueData.get()
                name=self.queueName.get()
                #upload memory data
                self.ftp.storbinary("STOR "+name, data)
                
            else:
                time.sleep(0.1)
            
           
    def release(self):
        self.stop()
        if self.is_alive():
            self.join()
        self.exit.set()
   
   
class busyProc(multiprocessing.Process):
    def __init__(self,sec):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.sec=sec
        self.ftp=FTPProc()
        self.ftp.start()
        manager=multiprocessing.Manager()
        self.queueData=manager.Queue()
        self.queueName=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
        print("busy time:",self.sec)

    
    def stop(self):
        self.states["release"]=True
    
    def put(self,data,name):
        self.queueData.put(data)
        self.queueName.put(name)
    
    def getPid(self):
        return self.states["pid"]
        
            
    def run(self):
        self.states["pid"]=os.getpid()
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        while not self.states["release"]:
            if self.queueData.empty()==False and self.queueName.empty()==False : 
                
                data=self.queueData.get()
                name=self.queueName.get()
                print("busy simulator",time.time())
                busyStartTime=time.time()
                justVar=np.ones(100)
                while time.time()-busyStartTime<self.sec:
                    justVar=justVar+1
                    justVar=justVar-1
                print("busy finish",time.time())
                
                self.ftp.put(data, name)
                
            else:
                time.sleep(0.1)
            
        while not self.ftp.queueName.empty():
            time.sleep(1)
        

    
    def release(self):
        self.stop()
        if self.is_alive():
            self.join()
        self.exit.set() 
        self.ftp.stop()
        self.ftp.release()
        
        
class recodeProc(multiprocessing.Process):
    def __init__(self,period):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        FTP_HOST = "192.168.0.137"
        FTP_USER = "etao"
        FTP_PASS = "19960709"

        self.ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        self.ftp.encoding = "utf-8"
        
        self.period=period
        
        manager=multiprocessing.Manager()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
        

        self.recode=dict()
        self.recode['recodeTime']=[]
        self.recode['recodeTimestamp']=[]
        self.recode['cpuUsage']=[]
        self.recode['cpuClock']=[]
        self.recode['cpuTemp']=[]
        self.recode['memoryUsage']=[]
        self.recode['diskFreeG']=[]
    
    def getEvir(self):
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
    
    def stop(self):
        self.states["release"]=True
    
    def put(self,data,name):
        self.queueData.put(data)
        self.queueName.put(name)
    
    def getPid(self):
        return self.states["pid"]
        
            
    def run(self):
        self.states["pid"]=os.getpid()
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        lastTime=time.time()
        while not self.states["release"]:
            if time.time()-lastTime>self.period : 
                lastTime=time.time()
                
                now = datetime.now() # current date and time
                timeStr2 = now.strftime("%Y/%m/%d %H:%M:%S")
                cpuUsage,cpuClock,cpu_temp,memory_using,disk_free=self.getEvir()
                self.recode['recodeTime'].append(timeStr2)
                self.recode['recodeTimestamp'].append(now.timestamp())
                self.recode['cpuUsage'].append(cpuUsage)
                self.recode['cpuClock'].append(cpuClock)
                self.recode['cpuTemp'].append(cpu_temp)
                self.recode['memoryUsage'].append(memory_using)
                self.recode['diskFreeG'].append(disk_free)
            else:
                time.sleep(self.period /10)
                
        temp = BytesIO()
        CSV ="\n".join([k+','+','.join(list(map(str, v))) for k,v in self.recode.items()]) 
        temp.write(bytearray(CSV, "utf8"))
        
        now = datetime.now() # current date and time
        timeStr = now.strftime("%Y_%m_%d_%H_%M_%S")
        temp.seek(0)
        fileName="test_recode_"+timeStr+".csv"
        self.ftp.storbinary("STOR "+fileName, temp)
            

    
    def release(self):
        self.stop()
        if self.is_alive():
            self.join()
        self.exit.set() 
   


if __name__ == "__main__":
    channel=4
    busyPercent=0.8
    testKeepTime=10
    sampleSec=3
    Fs=4000
    oneTime=36//2 #1data = 2byte
    condition=sampleSec*Fs*oneTime
    recodePeriod=1.0
    
    
    index = []
    buffer=[]
    for i in range(channel):
        index.append(0)
        buffer.append(np.zeros(10000000,dtype=np.float32))
    
    # os.system("taskset -cp 3 %d" %(os.getpid()))
    
    
    vib=[]
    for i in range(channel):
        vib.append(vibHubProc(i,Fs))
        
    busy=busyProc(sampleSec*busyPercent)
    recode=recodeProc(recodePeriod)
    busy.start()
    recode.start()
    
    for i in range(channel):
        vib[i].start()
    testStartTime=time.time()
    
    while time.time()-testStartTime<testKeepTime:
        
        while( index[0] < condition or 
              index[1] < condition or 
              index[2] < condition or 
              index[3] < condition):
            for i in range(channel):
                if not vib[i].queue.empty() and index[i] < condition:
                    data=vib[i].queue.get(False)
                    data=data[0::2]*256+data[1::2]
                    buffer[i][index[i]:index[i]+len(data)]=data
                    index[i]=index[i]+len(data)
                    #print(index,"/",condition,"(queue=",vib.queue.qsize())
            time.sleep(0.01)
                
        raw=[]
        for i in range(channel):
            print(i,"queue size:",vib[i].queue.qsize())
            raw.append(np.array(buffer[i][:condition],dtype=np.float32).reshape([-1,18]))
            if index[i]>condition:
                buffer[i][0:index[i]-condition]=buffer[i][condition:index[i]]
            print("index=",index[i])
            index[i]=index[i]-condition
        
        
        #save array to binary in memory
        raw=np.array(raw)
        temp = BytesIO()
        #np.savetxt(temp, raw, delimiter=",")
        pickle.dump(raw, temp)
        temp.seek(0)
        
        now = datetime.now() # current date and time
        timeStr = now.strftime("%Y_%m_%d_%H_%M_%S")
        fileName="test_"+timeStr+".pkl"
        busy.put(temp, fileName)
        
        print(time.time()-testStartTime,"/",testKeepTime)
    
    print("Finish all")
    
    for i in range(channel):
        vib[i].stopSample()
    for i in range(channel):
        vib[i].release()
    
    
    
    while not busy.queueName.empty():
        time.sleep(1)
    busy.stop()
    busy.release()
    
    recode.stop()
    recode.release()
    
    
    # with open('/Users/etao/Desktop/FTPtest/test_2021_05_25_12_04_28.pkl','rb') as f:
    #     x = pickle.load(f)
    #     print(x.shape)
        
        
        
        
        
        
        
        
        
        
        
        