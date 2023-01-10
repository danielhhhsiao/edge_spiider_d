import multiprocessing
from Library.tool import getDictItem, printErr, str2intArr, str2floatArr, stamp2dateArr,mainProgramStates,openPKL,testPrintStructure
from Library.VibrationHub import VibHub
from Library.ADCHub import ADCHub
from Library.SpiSlaveScan import scanSlave
import os
import gc
import time
import datetime
import numpy as np
import pandas as pd
import VL53L0X
import RPi.GPIO as GPIO
from os import listdir
from serial.tools import list_ports
import serial
import struct
import math
import json
import alsaaudio 
import pyaudio
import copy
import threading


_oldSamplingPath = "oldSampling.pkl"
_maxSerialNum = 2
_maxVibHubNum = 4
_maxADCHubNum = 4

def serialNum2Port(number):
    defaultUSBlocation = ["1-1.6",
                        "1-1.2"]
    if(number>=len(defaultUSBlocation)):
        return None
    ports = list(list_ports.comports())
    for port in ports:
        print(port.location, port.device)
        if defaultUSBlocation[number]==port.location:
            return port.device
    return None
    
def location2Port(location):
    ports = list(list_ports.comports())
    for port in ports:
        print("location2Port",location,port.location,port.device)
        if location==port.location:
            return port.device
    return None
    
def port2Location(name):
    ports = list(list_ports.comports())
    for port in ports:
        print("port2Location",port.location,port.device)
        if name==port.device:
            return port.location
    return None
            

class sample(multiprocessing.Process):
    def __init__(self,param=dict(),minProcTime=0.01,simulator=0,oldData=False):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        
        print("sample class create")
        
        maxUSBLen=4
        self.minProcTime = minProcTime
        self.checkProcTime = 3
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["start"]=False
        self.states["release"]=False
        self.states["pid"]=-1
        self.states["ready"]=False
        self.oldData = oldData
        self.simulator = False
        self.simulatorDelay = False
        
        self.prognosis=False
        self.audioProc=[]
        self.progProc=[]
        self.vibProc=[]
        self.adcProc=[]
        self.modbusProc=[]
        self.gpioEnable = False
        self.disProcName = ""
        self.gpioName = ["","","",""]
        
        
        if oldData:
            return #end the init
            
        if simulator>0:
            self.simulator = True
        if simulator>1:
            self.simulatorDelay = True
    
        # create prognosis processing --------------------------------
        vibLocation = getDictItem(param,"prognosis","location",",")
        vibLocation = vibLocation.split(",")
        vibFs = getDictItem(param,"prognosis","sample_rate","1000,1000")
        vibFs = str2intArr(vibFs.split(","))
        vibScale = getDictItem(param,"prognosis","level","4,4")
        vibScale = str2intArr(vibScale.split(","))
        vibName = getDictItem(param,"prognosis","name",",")
        vibName = vibName.split(",")
        vibSensor = getDictItem(param,"prognosis","mode",",")
        vibSensor = vibSensor.split(",")
        
        vibMinLen = min([len(vibLocation),len(vibFs),len(vibScale),len(vibName),len(vibSensor)])
        vibLocation = vibLocation[:vibMinLen]
        vibFs = vibFs[:vibMinLen]
        vibScale = vibScale[:vibMinLen]
        vibName = vibName[:vibMinLen]
        vibSensor = vibSensor[:vibMinLen]
                 
        #update maxUSBLen
        maxUSBLen = max(maxUSBLen,vibMinLen)
        
        if len(vibName)==vibMinLen:
            for i in range(vibMinLen):
                if vibName[i]!="":
                    vibProcD = dict()
                    if vibSensor[i]=="VPA30816":
                        vibLocation[i] = vibLocation[i]+":1.0"
                    if vibLocation[i]=="":
                        vibProcD["port"] = serialNum2Port(i)
                    else:
                        vibProcD["port"] = location2Port(vibLocation[i])
                    vibProcD["vibLocation"] = vibLocation[i]
                    vibProcD["portNum"] = i
                    vibProcD["portMaxLen"]=maxUSBLen
                    vibProcD["name"]=vibName[i]
                    vibProcD["Fs"]=vibFs[i]
                    vibProcD["Scale"]=vibScale[i]
                    vibProcD["sensor"]=vibSensor[i]
                    vibProcD["minProcTime"]=minProcTime
                    
        
                    self.progProc.append(vibProcD)
                    self.prognosis=True
                    
        # create audio processing --------------------------------
        audioName = getDictItem(param,"audio","name",",").split(",")
        audio_pyaudio=pyaudio.PyAudio()
        audio_mapping=audio_process.getMapping(audio_pyaudio)
        if len(audioName)==_maxSerialNum:
            for i in range(_maxSerialNum):
                if audioName[i]!="":
                    if "usb"+str(i+1) in audio_mapping.keys():
                        audioProcD = dict()
                        audioProcD["portNum"]=i
                        audioProcD["index"]=audio_mapping["usb"+str(i+1)]
                        audioProcD["name"]=audioName[i]
                        audioProcD["minProcTime"]=minProcTime
                        audioProcD["portMaxLen"]=maxUSBLen
                        self.audioProc.append(audioProcD)
                        self.audio=True
                    else:
                        mainProgramStates.send(mainProgramStates._Err,"Audio ("+audioName[i]+") not find sensor.")
                    
        # create modbus processing --------------------------------
        modbusConnection = getDictItem(param,"modbus","connection","[]")
        modbusConnection = json.loads(modbusConnection)
        modbusSetting = getDictItem(param,"modbus","setting","[]")
        modbusSetting = json.loads(modbusSetting)
    
        for i,m in enumerate(modbusConnection):
            if len(modbusSetting)>i:
                modbusProcD = dict()
                modbusProcD["connection"]=m
                modbusProcD["setting"]=modbusSetting[i]
                modbusProcD["minProcTime"]=minProcTime
                modbusProcD["portMaxLen"]=maxUSBLen
                self.modbusProc.append(modbusProcD)
                    
        # create vibration processing --------------------------------
        vibFs = getDictItem(param,"vibration","sample_rate","1000,1000,1000,1000")
        vibFs = str2intArr(vibFs.split(","))
        for i in range(_maxVibHubNum):
            nameData = getDictItem(param,"vibration","hub"+str(i+1)+"_name",",,,,,")
            if len(nameData.split(","))==6 and nameData!=",,,,,":
                vibProcD = dict()
                vibProcD["bus"]=i
                vibProcD["name"]=nameData.split(",")
                vibProcD["Fs"]=vibFs[i]
                Scale=getDictItem(param,"vibration","hub"+str(i+1)+"_level","4,4,4,4,4,4")
                vibProcD["Scale"]=str2intArr(Scale.split(","))
                vibProcD["minProcTime"]=minProcTime
                self.vibProc.append(vibProcD)
               
        # create analog processing --------------------------------
        adcFs = getDictItem(param,"analog","sample_rate","1000,1000,1000,1000")
        adcFs = str2intArr(adcFs.split(","))
        for i in range(_maxADCHubNum):
            nameData = getDictItem(param,"analog","hub"+str(i+1)+"_name",",,,,,,,")
            nameType = getDictItem(param,"analog","hub"+str(i+1)+"_type","d,d,d,d,d,d,d,d")
            adcMode = getDictItem(param,"analog","hub"+str(i+1)+"_mode","0,0,0,0,0,0,0,0")
            adcLevel = getDictItem(param,"analog","hub"+str(i+1)+"_level","1,1,1,1,1,1,1,1")
            adcMax = getDictItem(param,"analog","hub"+str(i+1)+"_max","0,0,0,0,0,0,0,0")
            adcMin = getDictItem(param,"analog","hub"+str(i+1)+"_min","0,0,0,0,0,0,0,0")
            adcUnit = getDictItem(param,"analog","hub"+str(i+1)+"_unit","V,V,V,V,V,V,V,V")
            adcBias = getDictItem(param,"analog","hub"+str(i+1)+"_bias","0,0,0,0,0,0,0,0")
            if len(nameData.split(","))==8 and nameData!=",,,,,,,":
                adcProcD = dict()
                adcProcD["bus"]=i
                adcProcD["name"]=nameData.split(",")
                adcProcD["Fs"]=adcFs[i]
                adcProcD["differentail"]=nameType.split(",")
                adcProcD["mode"]=str2intArr(adcMode.split(","))
                adcProcD["gain"]=str2intArr(adcLevel.split(","))
                adcProcD["maxValue"]=str2floatArr(adcMax.split(","))
                adcProcD["minValue"]=str2floatArr(adcMin.split(","))
                adcProcD["unit"]=adcUnit.split(",")
                adcProcD["bias"]=str2floatArr(adcBias.split(","))
                adcProcD["minProcTime"]=minProcTime
                self.adcProc.append(adcProcD)
                
        # create gy530 processing --------------------------------
        self.disProcName = getDictItem(param,"distance","ch1_name","")
        self.disProcMinTime = minProcTime
            
        # create gpio processing --------------------------------
        for i in range(4):
            self.gpioName[i] = getDictItem(param,"gpio","ch"+str(i+1)+"_name","")
            if self.gpioName[i] != "":
                self.gpioEnable = True
                
                
    def startSample(self):
        self.states["start"]=True
    
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
    
    def ready(self):
        return self.states["ready"]
        
    def pipeProc(self,proc,func=None,param=None):
        errFlag = False
        count = 0
        for i,p in enumerate(proc):
            while not p.queue.empty():
                data=p.queue.get(False)
                #print(data["startTime"],data["endTime"],data["endTime"]-data["startTime"],len(data["data"]))
                dataObj = p.createDataObj(data["startTime"],data["endTime"],data["data"])
                #testPrintStructure(dataObj)
                if p.type == "VIBRATION": #keep to send vibration sensor error
                    if sum(p.sensorErrFlag)>0:
                        errFlag=True
                if len(dataObj)>0:
                    self.queue.put(dataObj)
                    count=count+1
                del dataObj
                
            if not p.is_alive() and not self.states["release"] and func!=None and param!=None: #connect error, this will restart process
                if callable(func[i]):
                    proc[i] = func[i](param[i])
                    time.sleep(1)
                    proc[i].start()
                    maxRetryCount=0
                    while proc[i].getPid()==-1 and maxRetryCount<25:
                        time.sleep(0.2)
                        maxRetryCount+=1
                    os.system("taskset -cp 3 %d" %proc[i].getPid())
                
        #print("smaple pipe count",count)
        if errFlag:
            mainProgramStates.send(mainProgramStates._Err)
          
    def create_prognosis(self,param):
        
        if param["vibLocation"]=="":
            param["port"] = serialNum2Port(param["portNum"])
        else:
            param["port"] = location2Port(param["vibLocation"])
        return prognosis(
                    param["port"],
                    param["portNum"],
                    param["portMaxLen"],
                    param["name"],
                    param["Fs"],
                    param["Scale"],
                    param["sensor"],
                    param["minProcTime"]
                )
                
    def create_vibration(self,param):
        return vibration(
                    param["bus"],
                    param["name"],
                    param["Fs"],
                    param["Scale"],
                    param["minProcTime"]
                )
                
    def create_ADC(self,param):
        return ADC_process(
                    param["bus"],
                    param["name"],
                    param["Fs"],
                    param["gain"],
                    param["mode"],
                    param["differentail"],
                    param["maxValue"],
                    param["minValue"],
                    param["bias"],
                    param["unit"],
                    param["minProcTime"]
                )
                
    def create_audio(self,param):
        return audio_process(
                    param["portMaxLen"],
                    param["portNum"],
                    param["index"],
                    param["name"],
                    param["minProcTime"]
                )
                
    def create_dis(self,param):
        return gy530_process(
                    param["name"],
                    param["minProcTime"]
                )
                
    def create_gpio(self,param):
        return gpio_process(
                    param["name"],
                    param["minProcTime"]
                )
                
    def create_modbus(self,param):
        return modbus_process(
                    param["portMaxLen"],
                    param["connection"],
                    param["setting"],
                    param["minProcTime"]
                )
        
    def run(self):
        self.states["pid"]=os.getpid()
        print("sample pid",self.states["pid"])
        
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        sensorProc=[]
        sensorProcCreateFunc=[]
        sensorProcParam=[]
        lowFsIndex = []
        if self.simulator:
            sensorProc.append(dataFromCSV(self.minProcTime,self.simulatorDelay))
        else:
            for param in self.progProc:
                sensorProc.append(self.create_prognosis(param))
                sensorProcCreateFunc.append(self.create_prognosis)
                sensorProcParam.append(param)
            for param in self.vibProc:
                sensorProc.append(self.create_vibration(param))
                sensorProcCreateFunc.append(self.create_vibration)
                sensorProcParam.append(param)
            for param in self.adcProc:
                sensorProc.append(self.create_ADC(param))
                sensorProcCreateFunc.append(self.create_ADC)
                sensorProcParam.append(param)
            for param in self.audioProc:
                sensorProc.append(self.create_audio(param))
                sensorProcCreateFunc.append(self.create_audio)
                sensorProcParam.append(param)
            for param in self.modbusProc:
                sensorProc.append(self.create_modbus(param))
                sensorProcCreateFunc.append(self.create_modbus)
                sensorProcParam.append(param)
                
            if self.disProcName!="":
                param = dict()
                param['name']=self.disProcName
                param['minProcTime']=self.disProcMinTime
                sensorProc.append(self.create_dis(param))
                sensorProcCreateFunc.append(self.create_dis)
                sensorProcParam.append(param)
                lowFsIndex.append(len(sensorProc)-1)
                
            if self.gpioEnable:
                param = dict()
                param['name']=self.gpioName
                param['minProcTime']=self.disProcMinTime
                sensorProc.append(self.create_gpio(param))
                sensorProcCreateFunc.append(self.create_gpio)
                sensorProcParam.append(param)
                
                lowFsIndex.append(len(sensorProc)-1)
            
        #time.sleep(1000) #for test check
        
        #wait to start
        self.states["ready"]=True
        while not self.states["start"]:
            time.sleep(0.1)
            
        for i,p in enumerate(sensorProc):
            p.start()
            
        
        time.sleep(0.1)
        for i,p in enumerate(sensorProc):
            os.system("taskset -cp 3 %d" %p.getPid())
            continue #for test
            
            #if i in lowFsIndex:
            #    os.system("taskset -cp 3 %d" %p.getPid())
            #elif len(lowFsIndex)>0:
            #    os.system("taskset -cp 0-2 %d" %p.getPid())
            #else:
            #    os.system("taskset -cp 0-3 %d" %p.getPid())
            
            
        if self.oldData:
            if os.path.isfile(_oldSamplingPath):
                dataObj = openPKL(_oldSamplingPath)
                self.queue.put(dataObj)
            else:
                print("not found old data.")
            while not self.states["release"]:
                time.sleep(1)
            return # end the run
            
        # main process queue
        updateTime = time.time()
        while not self.states["release"]:
            updateTime = time.time()
            self.pipeProc(
                sensorProc,
                sensorProcCreateFunc,
                sensorProcParam
                )
            
            sleepTime = self.checkProcTime-(time.time()-updateTime)
            #print("smaple pipe sleep time",sleepTime)
            if(sleepTime>0.1):
                time.sleep(sleepTime)
            mainProgramStates.send(mainProgramStates._SampleHeartbeat)
                
        for p in sensorProc:
            p.release()
        
        self.pipeProc(sensorProc)
        for p in sensorProc:
            del p
        gc.collect()
            
    def release(self,callback=None):
        self.stopProc()
        while self.is_alive():
            time.sleep(1)
            if callback != None:
                callback()
            #self.join()
        self.exit.set()


class vibration(multiprocessing.Process):
    def __init__(self,bus,name,Fs,Scale,minProcTime):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("Vibration class create")
             
        self.bus=bus
        self.nameStr=name
        self.Fs=Fs
        self.Scale=Scale
        self.minProcTime=minProcTime
        self.maxSamplePoint=minProcTime*self.Fs*10
        self.perSamplePoint=0
        self.enableName=[]
        self.enableType=[]
        self.enableScale=[]
        self.sensorErrFlag = []
        self.type = "VIBRATION"
        self.obj=VibHub(bus)
        self.enable = True
        
        
        hubType = scanSlave()[bus]
        if hubType!="Vibration board":
            mainProgramStates.send(mainProgramStates._Err,"The bus "+str(bus+1)+" is set to vibration, but the bus actually is "+hubType)
            self.enable = False
        else:
            realSensor = self.obj.ScanSensor()
            select=[]
            sensorType = self.obj.GetType()
            for i,n in enumerate(self.nameStr):
                if n =="":
                    select.append(False)
                elif realSensor[i] is False:
                    select.append(False)
                    mainProgramStates.send(mainProgramStates._Err,"The vibration (bus "+str(bus+1)+") channel "+str(i+1)+" ["+n+"] cannot find the sensor")
                    #self.enable = False
                else:
                    select.append(True)
                    self.sensorErrFlag.append(False)
                    self.enableType.append(sensorType[i])
                    self.enableName.append(n)
                    if sensorType[i]==2 and Scale[i]>8: #ADXL355 and G range>8G
                        self.enableScale.append(8)
                        self.obj.SetScale(i,8)
                    else:
                        self.enableScale.append(Scale[i])
                        self.obj.SetScale(i,Scale[i])
                    self.perSamplePoint=self.perSamplePoint+9 # 3 axis, 3 byte
                    
            self.obj.SelectAllSensor(select)
            self.obj.SetFs(Fs)
        
        self.bufferTotalArrSize = int(self.maxSamplePoint * self.perSamplePoint)
        self.minSamplePeriod=min(0.1,(65536/Fs/max(self.perSamplePoint,1)/10)) #1/10 buffer
        
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("vib pid",self.states["pid"])
        if not self.enable:
            while not self.states["release"]:
                mainProgramStates.send(mainProgramStates._Err) # keep states
                time.sleep(3)
            return
        bufferTotalArr=np.zeros(self.bufferTotalArrSize,dtype = np.int8)
        bufferIndex=0
        zeroCount=0
        errRecalTimeDiv=0
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        self.obj.StartSample()
        peroidTime=time.time()
        sampleTime=peroidTime
        newSampleTime=peroidTime
        overflowFlag=False
        while not self.states["release"]:
            sleepTime = self.minSamplePeriod-(time.time()-newSampleTime)
            if(sleepTime>0):
                time.sleep(sleepTime)
                
                
            
            newSampleTime=time.time()
            bufferLen = self.obj.GetBufferLen()
            
            #for overflow testing
            #while bufferLen!=65535 and not overflowFlag:
            #    newSampleTime=time.time()
            #    bufferLen = self.obj.GetBufferLen()
            #    time.sleep(0.01)
                
            if bufferLen==65535:
                mainProgramStates.send(mainProgramStates._Err,self.type+" sampling error(bus "+str(self.bus)+"). The buffer overflow.")
                return False # terminate processing
                #overflowFlag=True
            print(bufferLen)
            bufferLen = bufferLen//self.perSamplePoint*self.perSamplePoint
            if(bufferLen>0):
                bufferLen = min(bufferLen,30000)
                bufferLen = bufferLen//self.perSamplePoint*self.perSamplePoint
                bufferData = self.obj.GetBuffer(bufferLen)
                bufferTotalArr[bufferIndex:bufferIndex+bufferLen] = np.array(bufferData,dtype=np.int8)
                bufferIndex = bufferIndex+bufferLen
                if overflowFlag:
                    zeroCount=11 #keep to send error
                else:
                    zeroCount=0
            elif zeroCount<10:
                zeroCount = zeroCount+1
            elif zeroCount==10:
                zeroCount = zeroCount+1 #let zeroCount over 10, so this condition will run one times.
                mainProgramStates.send(mainProgramStates._Err,"Vibration board (bus "+str(self.bus)+") dissconnected.")
                return False # terminate processing
            elif zeroCount>10:
                errRecalTimeDiv=errRecalTimeDiv+1
                if errRecalTimeDiv>(3/self.minSamplePeriod): #sec
                    mainProgramStates.send(mainProgramStates._Err)
                    errRecalTimeDiv=0
                
                    
            
            if newSampleTime-peroidTime>=self.minProcTime :
                if bufferIndex>0:
                    bufferTotalArr = bufferTotalArr[:bufferIndex]
                    print("vib proc test",newSampleTime-peroidTime,bufferIndex/self.perSamplePoint,bufferIndex/self.perSamplePoint/(newSampleTime-peroidTime))
                    dataObj = dict()
                    dataObj["data"]=bufferTotalArr
                    dataObj["startTime"]=peroidTime
                    dataObj["endTime"]=newSampleTime
                    self.queue.put(dataObj)
                    del bufferTotalArr
                    del dataObj
                    bufferIndex=0
                    bufferTotalArr=np.zeros(self.bufferTotalArrSize,dtype = np.int8)
                peroidTime=newSampleTime
         
        if bufferIndex>0:
            bufferTotalArr = bufferTotalArr[:bufferIndex]
            dataObj = dict()
            dataObj["data"]=bufferTotalArr
            dataObj["startTime"]=peroidTime
            dataObj["endTime"]=newSampleTime
            self.queue.put(dataObj)
            del bufferTotalArr
            del dataObj
            gc.collect()
    
    def createDataObj(self,startTime,endTime,data):
        
        data = np.array(data, dtype = np.uint8)
        data = (data[0::3]*65536) + (data[1::3])*256 + data[2::3]
        data = self.obj.ConvertData(data)
        negativeIndex = (data & 0x800000) != 0
        data[negativeIndex] = (data[negativeIndex]+0xFF000000)
        #data = np.array(data,dtype=np.float32)/(32768.0)
        data = data.reshape([-1,self.perSamplePoint//3]).T
        dataLen = data.shape[1]
        timeGap = np.arange(0,dataLen+1)/(dataLen+1)*(endTime-startTime)
        timeGap = timeGap[1:]+startTime
        
        ret = dict()
        ret['bus']=[dict(),dict(),dict(),dict()]
        ret['bus'][self.bus]['type']="VIBRATION"
        ret['bus'][self.bus]['sensor']="MPU9250"
        ret['bus'][self.bus]['unit']="G"
        ret['bus'][self.bus]['fs']=self.Fs
        ret['bus'][self.bus]['scale']=dict()
        #ret['bus'][self.bus]['time'] = stamp2dateArr(timeGap,"%y/%m/%d %H:%M:%S.%f")
        ret['bus'][self.bus]['time'] = timeGap
        ret['bus'][self.bus]['data']=dict()
            
        createFlag=False
        for i,n in enumerate(self.enableName):
            if not self.sensorErrFlag[i]:
                scale = self.enableScale[i]
                ret['bus'][self.bus]['scale'][n]=scale
                x = np.array(data[i*3])*scale*self.obj.typeMappingScale[self.enableType[i]]
                y = np.array(data[i*3+1])*scale*self.obj.typeMappingScale[self.enableType[i]]
                z = np.array(data[i*3+2])*scale*self.obj.typeMappingScale[self.enableType[i]]
                if np.sum([x[-1],y[-1],z[-1]])==0:
                    if self.sensorErrFlag[i]==False: # once send
                        self.sensorErrFlag[i]=True
                        mainProgramStates.send(mainProgramStates._Err,"Vibration channel["+n+"] sensor dissconnected.")
                        self.terminate()
                        #return False # terminate processing
                else:
                    ret['bus'][self.bus]['data']["aX_"+n] = x
                    ret['bus'][self.bus]['data']["aY_"+n] = y
                    ret['bus'][self.bus]['data']["aZ_"+n] = z
                    createFlag=True
                
        if createFlag:
            return ret
        else:
            return {}
        
        
    def release(self):
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()

class modbus_process(multiprocessing.Process):
    
    def __init__(self,maxUSBLen,connection,setting,minProcTime):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("modbus class create")
        self.maxUSBLen=maxUSBLen
        
        parityMap = dict()
        parityMap["None"] = serial.PARITY_NONE
        parityMap["Even"] = serial.PARITY_EVEN
        parityMap["Odd"] = serial.PARITY_ODD
        parityMap["Mark"] = serial.PARITY_MARK
        parityMap["Space"] = serial.PARITY_SPACE
        stopbitMap = dict()
        stopbitMap["1"] = serial.STOPBITS_ONE
        stopbitMap["1.5"] = serial.STOPBITS_ONE_POINT_FIVE
        stopbitMap["2"] = serial.STOPBITS_TWO
        self.typeLenMap = dict()
        self.typeLenMap["float32"] = 4
        self.typeLenMap["int8"] = 1
        self.typeLenMap["int16"] = 2
        self.typeLenMap["int32"] = 4
        self.typeLenMap["uint8"] = 1
        self.typeLenMap["uint16"] = 2
        self.typeLenMap["uint32"] = 4
        self.typeLenMap["BCD"] = 2
        self.typeLenMap["bit8"] = 1
        self.typeLenMap["bit16"] = 2
        self.typeFunction = dict()
        self.typeFunction["float32"] = modbus_process.byte2float32
        self.typeFunction["int8"] = modbus_process.byte2int8
        self.typeFunction["int16"] = modbus_process.byte2int16
        self.typeFunction["int32"] = modbus_process.byte2int32
        self.typeFunction["uint8"] = modbus_process.byte2uint8
        self.typeFunction["uint16"] = modbus_process.byte2uint16
        self.typeFunction["uint32"] = modbus_process.byte2uint32
        self.typeFunction["BCD"] = modbus_process.byte2BCD
        self.typeFunction["bit8"] = modbus_process.byte2bit8
        self.typeFunction["bit16"] = modbus_process.byte2bit16
        self.dtypeMap = dict() 
        self.dtypeMap["float32"] = np.float32
        self.dtypeMap["int8"] = np.int32
        self.dtypeMap["int16"] = np.int64
        self.dtypeMap["int32"] = np.int64
        self.dtypeMap["uint8"] = np.int32 #unsign interger need to over the resolusion
        self.dtypeMap["uint16"] = np.int64
        self.dtypeMap["uint32"] = np.int64
        self.dtypeMap["BCD"] = np.int32
        self.dtypeMap["bit8"] = np.int8
        self.dtypeMap["bit16"] = np.int8
        
    
        
        self.usbPort=location2Port(connection["location"])
        self.portNum=connection["usb_num"]
        self.buad=connection["buad"]
        self.length=connection["length"]
        self.stopBit=stopbitMap[connection["stopbit"]]
        self.parity=parityMap[connection["parity"]]
        self.period = connection["period"]/1000
        self.oneByteTime=1/(self.buad/10) 
        print("self.oneByteTime",self.oneByteTime)
        self.transmitTime=self.oneByteTime*8 #address 1 + function code 1 + length 2 + ragister 2 + CRC 2
        self.nameArr=setting
        self.minProcTime=minProcTime
        self.type = "MODBUS"
        self.sensor="NONE"
        self.enable = True
        self.batch=[]
        self.nameAndRule=dict()
        self.maxSamplePoint = int(max(1,(1/self.period)*self.minProcTime)*5) # *5 is advoid overflow
        print("minProcTime",self.minProcTime)
        print("period",self.period)
        print("maxSamplePoint",self.maxSamplePoint)
        print("modbus",self.usbPort)
        if self.usbPort==None:
            mainProgramStates.send(mainProgramStates._Err,"The port "+str(self.portNum+1)+" cannot found Modbus eqp")
            self.enable = False
        else:
            self.port = serial.Serial(
                self.usbPort,
                self.buad,
                parity=self.parity, 
                bytesize=self.length, 
                stopbits=self.stopBit)
            if not self.port.isOpen() :
                self.port.open()
                
        byAddress = dict()
        for i,s in enumerate(setting):
            if s["address"] not in byAddress.keys():
                byAddress[s["address"]]=[]
            byAddress[s["address"]].append(s)
                    
        for k in byAddress.keys():
            byAddress[k] = sorted(byAddress[k],key=lambda d: d['register'])
            lastRegister=-5
            lastDeviceAddress = 1
            for date in byAddress[k]:
                obj = dict()
                obj["name"] = date['name']
                obj["type"] = date['type']
                obj["order"] = date['order']
                obj["ratio"] = date['ratio']
                for n in obj["name"]:
                    if n != "" and n not in self.nameAndRule.keys():
                        self.nameAndRule[n]=obj
                lastRegisterDiff = int(self.typeLenMap[date['type']]/2)
                if lastRegisterDiff == 0:
                    lastRegisterDiff = -1
                if date['register']-lastRegister!=lastRegisterDiff or lastDeviceAddress != date['address']:
                    print("11111111111111111111111111111111111111111")
                    print(date['register'],lastRegister)
                    d = dict()
                    d["address"]=date['address']
                    d["function"]=date['function']
                    d["register"]=date['register']
                    d["delay"]=date['delay']
                    d["check"]=date['check']
                    d["dataReciveByte"]= 5 #address 1 + function code 1 + length 1 + CRC 2
                    d["count"]=lastRegisterDiff
                    d["obj"]=[]
                    d["obj"].append(obj)
                    self.batch.append(d)
                    lastRegister = date['register']
                    lastDeviceAddress = date['address']
                else:
                    print("2222222222222222222222222222222222222222222222")
                    print(date['register'],lastRegister)
                    self.batch[-1]["count"] +=lastRegisterDiff
                    self.batch[-1]["delay"] = max(self.batch[-1]["delay"],date['delay'])
                    self.batch[-1]["obj"].append(obj)
                    if self.batch[-1]["count"]>= 124:#new batch
                        lastRegister=-5
                    else:
                        lastRegister = date['register']
                self.batch[-1]["dataReciveByte"] +=self.typeLenMap[date['type']] # data length
                #lastRegister = date['register']
                
            
                    
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
    @staticmethod
    def CRC_16(arr):
        key = 0xA001
        crc = 0xFFFF
        for new in arr:
            for _ in range(8):
                if (crc^new) & 1:
                    crc = (crc >> 1)^ key
                else:
                    crc >>= 1
                new>>=1
        return crc>>8 , crc&0xFF
        
    
    @staticmethod
    def orderTranslate(order,arr):
        #default is LSB
        ret = np.array(arr,dtype=np.uint8)
        if order=="MSB":
            ret = ret[::-1]
            for i in range(len(ret)):
                ret[i] = int('{:08b}'.format(ret[i])[::-1],2)
        return ret
    
    @staticmethod
    def byte2float32(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data = np.array(data[::-1],dtype=np.uint8) #serial is high byte first
        data.dtype = np.float32
        return data[0]
        
    @staticmethod
    def byte2int8(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data.dtype = np.int8
        return data[0]
        
    @staticmethod
    def byte2int16(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data = np.array(data[::-1],dtype=np.uint8) #serial is high byte first
        data.dtype = np.int16
        return data[0]
        
    @staticmethod
    def byte2int32(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data = np.array(data[::-1],dtype=np.uint8) #serial is high byte first
        data.dtype = np.int32
        return data[0]
        
    @staticmethod
    def byte2uint8(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data.dtype = np.uint8
        return data[0]
        
    @staticmethod
    def byte2uint16(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data = np.array(data[::-1],dtype=np.uint8) #serial is high byte first
        data.dtype = np.uint16
        return data[0]
        
    @staticmethod
    def byte2uint32(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data = np.array(data[::-1],dtype=np.uint8) #serial is high byte first
        data.dtype = np.uint32
        return data[0]
        
    @staticmethod
    def byte2BCD(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data = np.array(data[::-1],dtype=np.uint8) #serial is high byte first
        data.dtype = np.uint16
        try:
            ret = int(hex(data[0]).replace("0x",""),10)
        except:
            return 10000 #BCD range is 0~9999
        return ret
        
    @staticmethod
    def byte2bit8(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        bits = '{:08b}'.format(data[0])[::-1]
        ret = list(map(lambda x:int(x),bits))
        return ret
        
    @staticmethod
    def byte2bit16(order,arr):
        data = modbus_process.orderTranslate(order,arr)
        data = np.array(data[::-1],dtype=np.uint8) #serial is high byte first
        bits = ''
        for d in data:
            bits = bits+'{:08b}'.format(d)[::-1]
        ret = list(map(lambda x:int(x),bits))
        return ret
        
	
    def getModbusArr(self,slave_address,function_code,register,register_count):
        arr = [slave_address&0xFF,function_code&0xFF,register>>8,register&0xFF,register_count>>8,register_count&0xFF]
        hi,lo = modbus_process.CRC_16(arr)
        arr.append(lo)
        arr.append(hi)
        return arr
        
    def checkLen(self,dataReciveByte,arr):
        #print("checkLen",len(arr),dataReciveByte)
        return  len(arr)==dataReciveByte
        
    def checkSlave(self,slave_address,arr):
        arr = list(arr)
        if len(arr)<5:
            return False
            
        if arr[0]!=slave_address:
            return False
            
        return True
        
    def checkFuntionCode(self,function_code,arr):
        arr = list(arr)
        if len(arr)<5:
            return False
            
        if arr[1]!=function_code:
            return False
            
        return True
        
    def checkCRC(self,arr):
        arr = list(arr)
        if len(arr)<5:
            return False
            
        crc_h,crc_l = modbus_process.CRC_16(arr[:-2])
        if crc_h!= arr[-1] or crc_l!= arr[-2] :
            return False
            
        return True
        
    def getModbusArrDate(self,arr,objs):
        arr = np.array(list(arr[3:-2]))
        index = 0
        ret = dict()
        for obj in objs:
            length = self.typeLenMap[obj["type"]]
            data = arr[index:index+length]
            index = index + length
            result = self.typeFunction[obj["type"]](obj["order"],data)
            if "bit" not in obj["type"]:
                ret[obj["name"][0]] = result*obj["ratio"]
            else:
                for i,n in enumerate(obj["name"]):
                    if n !="":
                        ret[n] = result[i]
                
        #print("getModbusArrDate")
        #print(ret)
        return ret
        
            
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
        
    def createBuffer(self):
        ret = dict()
        timeArr = np.zeros(self.maxSamplePoint)
        for k in self.nameAndRule.keys():
            typeName = self.nameAndRule[k]["type"]
            if type(self.nameAndRule[k]["ratio"])!=float or "bit" in typeName:
                ret[k] = np.zeros(self.maxSamplePoint*2,dtype=self.dtypeMap[typeName])
            else:
                ret[k] = np.zeros(self.maxSamplePoint*2,dtype=np.float32)
        return ret , timeArr
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("modbus pid",self.states["pid"])
        
        peroidTime=time.time()
        sampleTime=peroidTime
        newSampleTime=peroidTime
        bufferTotalArr,timeArr = self.createBuffer()
        bufferIndex=0
        lossCount = 0
        lastData = dict()
        while not self.states["release"]:
            if not self.enable :
                mainProgramStates.send(mainProgramStates._Err) # keep states
                time.sleep(3)
                continue
            
            if(time.time()-newSampleTime<=self.period):
                sleepTime = self.period-(time.time()-newSampleTime)-0.0001
                if(sleepTime>0):
                    time.sleep(sleepTime)
                    
            newSampleTime=time.time()
            try:
                timeArr[bufferIndex] = newSampleTime
                #print("Modbus work",time.time())
                for b in self.batch:
                    useOldDate = False
                    self.port.flushOutput()
                    self.port.flushInput()
                    
                    data = self.getModbusArr(b["address"],b["function"],b["register"],b["count"])
                    print("3333333333333333333333333333333333")
                    print(data)
                    print(time.time()-newSampleTime,self.period)
                    self.port.write(data)
                    
                    #transmite time
                    time.sleep(self.transmitTime)
                    print(time.time()-newSampleTime,self.period)
                    while self.port.out_waiting>0 and time.time()-newSampleTime<self.period:
                        time.sleep(self.oneByteTime)
                    print(time.time()-newSampleTime,self.period)
                    if time.time()-newSampleTime>self.period:
                        raise Exception("transmission timeout")
                    #response + receive time
                    #time.sleep(b["delay"]/1000+self.oneByteTime*b["dataReciveByte"])
                    print(time.time()-newSampleTime,self.period)
                    while self.port.in_waiting!=b["dataReciveByte"]  and time.time()-newSampleTime<self.period:
                        time.sleep(self.oneByteTime)
                    print(time.time()-newSampleTime,self.period)
                    if time.time()-newSampleTime>self.period:
                        useOldDate = True
                        print(self.port.in_waiting,b["dataReciveByte"])
                        mainProgramStates.send(mainProgramStates._Err,"Modbus receive timeout. [slave "+str(b["address"])+",register "+str(b["register"])+" ]")
                        #raise Exception("receive timeout. in_waiting="+str(self.port.in_waiting))
                    
                    #print("dabug modbus read:",self.port.in_waiting)
                    #testTime = time.time()
                    rec = self.port.read(self.port.in_waiting)
                    
                    if not self.checkLen(b["dataReciveByte"],rec) :
                        useOldDate = True
                        #mainProgramStates.send(mainProgramStates._Err,"Modbus receive len error. [slave "+str(b["address"])+",register "+str(b["register"])+" ]")
                    elif not self.checkFuntionCode(b["function"],rec):
                        useOldDate = True
                        #mainProgramStates.send(mainProgramStates._Err,"Modbus receive function code error. [slave "+str(b["address"])+",register "+str(b["register"])+" ]")
                    elif not self.checkSlave(b["address"],rec):
                        useOldDate = True
                        #mainProgramStates.send(mainProgramStates._Err,"Modbus receive slave address error. [slave "+str(b["address"])+",register "+str(b["register"])+" ]")
                    elif not self.checkCRC(rec):
                        useOldDate = True
                        #mainProgramStates.send(mainProgramStates._Err,"Modbus receive CRC error. [slave "+str(b["address"])+",register "+str(b["register"])+" ]")
                        
                    if useOldDate: 
                        lossCount = lossCount+1
                        for k in b["obj"]:
                            for n in k["name"]:
                                if n not in lastData.keys():
                                    lastData[k]=0
                                bufferTotalArr[n][bufferIndex] = lastData[n]
                    else:
                        registerDate = self.getModbusArrDate(rec,b["obj"])
                        for k in registerDate.keys():
                            bufferTotalArr[k][bufferIndex]=registerDate[k]
                            lastData[k]=registerDate[k]
                    #print("testTime",time.time()-testTime)
                            
                bufferIndex = bufferIndex+1
                
            except Exception as e:
                errMessage = "Modbus serial port disconnected. "+str(e)
                mainProgramStates.send(mainProgramStates._Err,errMessage)
                return False # terminate processing
            
                
            if newSampleTime-peroidTime>=self.minProcTime and bufferIndex>0:
                for k in bufferTotalArr.keys():
                    bufferTotalArr[k] = bufferTotalArr[k][:bufferIndex]
                timeArr = timeArr[:bufferIndex]
                dataObj = dict()
                dataObj["data"]=bufferTotalArr
                dataObj["startTime"]=timeArr[0]
                dataObj["endTime"]=timeArr[-1]
                self.queue.put(dataObj)
                del bufferTotalArr
                del timeArr
                del dataObj
                peroidTime=newSampleTime
                bufferIndex=0
                bufferTotalArr,timeArr = self.createBuffer()
         
                
        
        if bufferIndex>0:
            for k in bufferTotalArr.keys():
                bufferTotalArr[k] = bufferTotalArr[k][:bufferIndex]
            timeArr = timeArr[:bufferIndex]
            dataObj = dict()
            dataObj["data"]=bufferTotalArr
            dataObj["startTime"]=timeArr[0]
            dataObj["endTime"]=timeArr[-1]
            self.queue.put(dataObj)
            del bufferTotalArr
            del timeArr
            del dataObj
            gc.collect()
            
        print("Modbus loss count:",lossCount)
            
    
    def createDataObj(self,startTime,endTime,data):
        firstKey = list(data.keys())[0]
        dataLen = len(data[firstKey])
        if dataLen>1:
            timeGap = np.arange(0,dataLen)/(dataLen-1)*(endTime-startTime)
            timeGap = timeGap+startTime
        else:
            timeGap = np.array([startTime])
        #print("createDataObj",dataLen,startTime,endTime,data)
        #for i in range(dataLen):
        #    print("timeGap",timeGap[i])
        if dataLen>0:
            ret = dict()
            ret['usb']=[dict() for i in range(self.maxUSBLen)]
            ret['usb'][self.portNum]['type']=self.type
            ret['usb'][self.portNum]['sensor']=self.sensor
            ret['usb'][self.portNum]['unit']="NONE"
            ret['usb'][self.portNum]['fs']=1/self.period
            ret['usb'][self.portNum]['time'] = timeGap
            ret['usb'][self.portNum]['data']=data
            
            return ret
        else:
            return {}
        
        
    def release(self):
        if self.enable:
            print("close serial port")
            self.port.close()
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()



class prognosis(multiprocessing.Process):
    def __init__(self,port,portNum,maxUSBLen,name,Fs,Scale,sensor,minProcTime):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("Prognosis class create")
        
        self.testTime=0
        self.testTimeMax=0
        self.testBufferLen=0
        self.testBufferLenMax=0
             
        self.config = dict()
        self.config["VPA308R"]                      =dict()
        self.config["VPA308R"]["defaultBaudrate"]   =921600
        self.config["VPA308R"]["oneSampleByte"]     =1544
        self.config["VPA308R"]["oneBatchSample"]    =128
        self.config["VPA308R"]["gain"]              =dict()
        self.config["VPA308R"]["gain"][2]           =0
        self.config["VPA308R"]["gain"][4]           =1
        self.config["VPA308R"]["gain"][8]           =2
        self.config["VPA308R"]["fs"]                =dict()
        self.config["VPA308R"]["fs"][4000]          =0
        self.config["VPA308R"]["fs"][2000]          =1
        self.config["VPA308R"]["fs"][1000]          =2
        self.config["VPA308R"]["fs"][500]           =3
        self.config["VPA308R"]["fs"][250]           =4
        self.config["VPA308R"]["fs"][125]           =5
        self.config["VPA308R"]["scan"]              =True
        self.config["VPA308R"]["fitst_reset"]             =False
        self.config["VPA308R"]["wait"]              =True
        self.config["VPA308R"]["br"]                =dict()
        self.config["VPA308R"]["br"][9600]          =0
        self.config["VPA308R"]["br"][19200]         =1
        self.config["VPA308R"]["br"][57600]         =2
        self.config["VPA308R"]["br"][115200]        =3
        self.config["VPA308R"]["br"][230400]        =4
        self.config["VPA308R"]["br"][256000]        =5
        self.config["VPA308R"]["br"][460800]        =6
        self.config["VPA308R"]["br"][921600]        =7
        self.config["VPA308R"]["stdCommand"]        =b'*********** FIRMWARE ***********'
             
        self.config["VPA30816"]                      =dict()
        self.config["VPA30816"]["defaultBaudrate"]   =921600*8
        self.config["VPA30816"]["oneSampleByte"]     =1544
        self.config["VPA30816"]["oneBatchSample"]    =128
        self.config["VPA30816"]["gain"]              =dict()
        self.config["VPA30816"]["gain"][2]           =0
        self.config["VPA30816"]["gain"][4]           =1
        self.config["VPA30816"]["gain"][8]           =2
        self.config["VPA30816"]["gain"][16]          =3
        self.config["VPA30816"]["fs"]                =dict()
        self.config["VPA30816"]["fs"][26667]         =0
        self.config["VPA30816"]["fs"][13333]         =1
        self.config["VPA30816"]["fs"][6667]          =2
        self.config["VPA30816"]["fs"][3333]          =3
        self.config["VPA30816"]["fs"][1667]          =4
        self.config["VPA30816"]["fs"][833]           =5
        self.config["VPA30816"]["scan"]              =False
        self.config["VPA30816"]["fitst_reset"]       =True
        self.config["VPA30816"]["wait"]              =False
        self.config["VPA30816"]["stdCommand"]        =b'*********** FIRMWARE ***********'
        
        if sensor=="":
            sensor = "VPA308R"
        self.maxUSBLen=maxUSBLen
        self.usbPort=port
        self.usbPortEnable=False
        self.nameStr=name
        self.portNum=portNum
        self.Fs=Fs
        self.realFs=Fs
        self.Scale=Scale
        self.minProcTime=minProcTime
        self.minSamplePeriod=minProcTime
        self.type = "VIBRATION_PORGNOSIS"
        self.sensor=sensor
        self.enable = True
        self.offsetRatioForTx=1/8*10/self.config[self.sensor]["defaultBaudrate"]
        
        print("prognosis",self.usbPort)
        if self.usbPort==None:
            mainProgramStates.send(mainProgramStates._Err,"The port "+str(portNum+1)+" cannot found serial port.")
            self.enable = False
        else:
            location = port2Location(self.usbPort)
            self.port = serial.Serial(self.usbPort,self.config[self.sensor]["defaultBaudrate"],parity=serial.PARITY_NONE, bytesize=8 )
            self.usbPortEnable=True
            if not self.port.isOpen() :
                self.port.open()
            #self.port.set_buffer_size(rx_size=4000000,tx_size=4096)
            #init sensor
            self.stopSample(10)
            rdata=self.get_infor()
            if(self.config[self.sensor]["stdCommand"] not in rdata):
                if self.config[self.sensor]["scan"]:
                    if self.port_scan_baud() == None :
                        mainProgramStates.send(mainProgramStates._Err,"The port "+str(portNum+1)+" sensor scan baudrate error.")
                        self.enable = False
                    elif self.port.baudrate != self.config[self.sensor]["stdCommand"] :
                        self.set_sensor_baud(self.config[self.sensor]["defaultBaudrate"])
                        rdata=self.get_infor()
                        if(self.config[self.sensor]["stdCommand"] not in rdata):
                            mainProgramStates.send(mainProgramStates._Err,"The port "+str(portNum+1)+" sensor baudrate setting error.")
                            self.enable = False
                else:
                    mainProgramStates.send(mainProgramStates._Err,"The port "+str(portNum+1)+" cannot found sensor")
                    self.enable = False
                    
            if self.enable:
                if self.Fs in self.config[self.sensor]["fs"].keys():
                    self.set_fs(self.Fs)
                else:
                    mainProgramStates.send(mainProgramStates._Err,"The port "+str(portNum+1)+" sensor Fs setting error.")
                    self.enable = False
                if self.Scale in self.config[self.sensor]["gain"].keys():
                    self.set_gain(self.Scale)
                else:
                    mainProgramStates.send(mainProgramStates._Err,"The port "+str(portNum+1)+" sensor gain setting error.")
                    self.enable = False
                self.set_bias('X',0)
                self.set_bias('Y',0)
                self.set_bias('Z',0)
                self.set_bias('T',0)
                self.set_hPassOff()
                self.set_raw()
            
                if self.config[self.sensor]["fitst_reset"] and False:
                    time.sleep(0.2) 
                    self.port.write(b'AT$RESET'+bytes([0x0D]))
                    print("reset porgnosis")
                    while self.port.out_waiting>0 :
                        time.sleep(0.2)
                    self.port.close()
                    time.sleep(2)
                    notFoundCount = 0
                    while True:
                        try:
                            self.usbPort = location2Port(location)
                            if not self.usbPort:
                                notFoundCount = notFoundCount+1
                            else:
                                self.port = serial.Serial(self.usbPort,self.config[self.sensor]["defaultBaudrate"],parity=serial.PARITY_NONE, bytesize=8 )
                                if not self.port.isOpen() :
                                    self.port.open()
                                self.stopSample(10)
                                rdata=self.get_infor()
                                if(self.config[self.sensor]["stdCommand"] not in rdata):
                                    notFoundCount = notFoundCount+1
                                else:
                                    print(rdata.decode("utf-8"))
                                    break
                            if notFoundCount>10: #2.5sec
                                mainProgramStates.send(mainProgramStates._Err,"The port "+str(portNum+1)+" cannot found sensor")
                                self.enable = False
                                break
                        except Exception as e:
                            pass
                        time.sleep(0.25)
                else:
                    rdata=self.get_infor()
                    print(rdata.decode("utf-8"))
                    
        self.minSamplePeriod = min(self.config[self.sensor]["oneBatchSample"]/self.Fs,0.001)
        #print("prognosis",self.portNum,self.minSamplePeriod)
        self.bufferTotalArrSize = int((self.minProcTime*self.Fs)*3)*2 #3axis
        
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
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
        baud_value = list(self.config[self.sensor]["br"].keys())
        for i in range(len(baud_value)):
            print("Scan baud",baud_value[i])
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
            print("\tResult:",rdata)
            if(self.config[self.sensor]["stdCommand"] in rdata):
                return baud_value[i]
        #mainProgramStates.send(mainProgramStates._Err,"Prognosis snesor (port "+str(self.portNum+1)+") is not found")        
        return None
                            
               
    def set_sensor_baud(self,baud_param):
        command = self.config[self.sensor]["br"][baud_param]
        
        self.stopSample()
        time.sleep(1)  
        self.port.write(bytes([0x0D]))
        time.sleep(0.2)
        self.port.write(b'AT$BAUD'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        
        time.sleep(0.2)
        self.port.write(b'AT$RESET'+bytes([0x0D]))
        time.sleep(5) 
        
        self.port.baudrate=baud_param
        self.stopSample()
        
        
    def set_fs(self,fs):
        command = self.config[self.sensor]["fs"][fs]
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$ODR'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        #print('VPA308R ['+self.name+'] Setting fs to %d' %fs)
        
    def set_hPassOff(self):
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$HIPASSOFF' +bytes([0x0D]))
        time.sleep(0.2)
        #print('VPA308R ['+self.name+'] Setting fs to %d' %fs)
        
        
    def set_gain(self,gain):
        command = self.config[self.sensor]["gain"][gain]
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$GRAN'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        #print('VPA308R ['+self.name+'] Setting gain to %d G' %gain)
        
        
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
                 
                            
            
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
        
    def getBuffer(self,arr):
        L = self.port.in_waiting
        bufferStartTime=time.time()
        #print("c=",self.portNum,",b=",L,len(arr))
        if L>0:
            arr = arr+self.port.read(L)
            
        if onlyBuffer:
            return arr
            
        serialBufferLen = len(arr)
        bufferStartTime -= serialBufferLen*self.offsetRatioForTx
        bufferStartTime -= math.ceil(serialBufferLen/self.config[self.sensor]["oneSampleByte"])*self.config[self.sensor]["oneBatchSample"]/self.realFs 
        bufferStartTime -= 0.013
        return arr,bufferStartTime
        
    def getBufferThread(self):
        while not self.stopThread:
            L = self.port.in_waiting
            nowTime = time.time()
            
            if L>0:
                self.lock.acquire()
                self.serialBuffer = self.serialBuffer+self.port.read(L)
                self.serialBufferStartTime = nowTime
                self.lock.release()
                
            
            # for testing
            if self.testTime!=0 and nowTime-self.testTime>self.testTimeMax:
                self.testTimeMax = nowTime-self.testTime
                print("####################################prognosis port:",str(self.portNum+1),"max time=",self.testTimeMax)
            if  L > self.testBufferLenMax:
                self.testBufferLenMax = L
                print("####################################prognosis port:",str(self.portNum+1),"max Len=",self.testBufferLenMax)
            self.testTime=nowTime
            #-------------------
            
            endTime=time.time()
            sleepTime = 0.01-(endTime-nowTime)
            if sleepTime>0 :
                time.sleep(sleepTime)
                
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("prognosis pid",self.states["pid"])
        if not self.enable:
            while not self.states["release"]:
                mainProgramStates.send(mainProgramStates._Err) # keep states
                time.sleep(3)
            return
        self.serialBuffer=bytearray()
        self.serialBufferStartTime=0
        bufferTotalArr=np.zeros(self.bufferTotalArrSize,dtype = np.float)
        lastIndex = -1
        currentIndex = 1
        bufferIndex=0
        zeroCount=0
        freshFsCount=0
        oneSampleByte = self.config[self.sensor]["oneBatchSample"]*3
        stdArr = list(range(oneSampleByte))
        errRecalTimeDiv=0
        offsetTime=self.config[self.sensor]["oneBatchSample"]/self.Fs+self.config[self.sensor]["oneSampleByte"]*self.offsetRatioForTx+0.01
        
        self.stopThread=False
        self.lock = threading.Lock()
        t = threading.Thread(target=self.getBufferThread)
        try:
        #if True:
            self.port.flushOutput()
            self.port.flushInput()
            if not self.config[self.sensor]["fitst_reset"]:
                self.port.write(b'AT$RESET'+bytes([0x0D])) #reset and start sample
            else:
                self.port.write(b'AT$RS'+bytes([0x0D])) #start sample
            testTime=time.time()
            while self.port.in_waiting==0 and not self.states["release"]:
                time.sleep(0.01) #start sample
            print("reset time:",time.time()-testTime,self.port.in_waiting)
            t.start()
            #serialBuffer,serialBufferStartTime = self.getBuffer(serialBuffer)
            
            # os.system("taskset -cp 2 %d" %(os.getpid()))
            peroidTime=time.time()-offsetTime
            sampleTime=peroidTime
            newSampleTime=peroidTime
            sensorStart=peroidTime
            sensorEnd=peroidTime
            freshFsStart=peroidTime
            
            debug=b''
            
            #serialBuffer,serialBufferStartTime = self.getBuffer(serialBuffer)
            while not self.states["release"]:
                if self.config[self.sensor]["wait"]:
                    sleepTime = self.minSamplePeriod-(time.time()-newSampleTime)
                    if(sleepTime>0):
                        time.sleep(sleepTime)
                else:
                    time.sleep(0.001)
                newSampleTime=time.time()
                
                if zeroCount<400:
                    if self.port.in_waiting==0:
                        zeroCount = zeroCount+1
                    else:
                        zeroCount = 0
                elif zeroCount==400:
                    zeroCount = zeroCount+1 #let zeroCount over 10, so this condition will run one times.
                    mainProgramStates.send(mainProgramStates._Err,"Prognosis snesor (port "+str(self.portNum+1)+") dissconnected.")
                    return False # terminate processing
                elif zeroCount>400:
                    errRecalTimeDiv=errRecalTimeDiv+1
                    if errRecalTimeDiv>(3/self.minSamplePeriod): #sec
                        mainProgramStates.send(mainProgramStates._Err)
                        errRecalTimeDiv=0
                
                
                #serialBuffer,serialBufferStartTime = self.getBuffer(serialBuffer)
                while(len(self.serialBuffer) >= self.config[self.sensor]["oneSampleByte"]
                    and bufferIndex+oneSampleByte<= self.bufferTotalArrSize
                    and zeroCount==0
                    and not self.states["release"]):
                    
                    self.lock.acquire()
                    dataStartTime = self.serialBufferStartTime
                    serialBufferLen=len(self.serialBuffer)
                    if(serialBufferLen>10000):
                        print("serialBufferLen",serialBufferLen)
                    self.lock.release()
                    dataStartTime -= serialBufferLen*self.offsetRatioForTx
                    dataStartTime -= math.ceil(serialBufferLen/self.config[self.sensor]["oneSampleByte"])*self.config[self.sensor]["oneBatchSample"]/self.realFs 
                    dataStartTime -= 0.013
                    
                    self.lock.acquire()
                    data = self.serialBuffer[:self.config[self.sensor]["oneSampleByte"]]
                    self.serialBuffer = self.serialBuffer[self.config[self.sensor]["oneSampleByte"]:]
                    self.lock.release()
                    
                    if data[0:3]!=b'AT3':
                        zeroCount=401
                        mainProgramStates.send(mainProgramStates._Err,"Prognosis snesor (port "+str(self.portNum+1)+") communication value error.")
                        self.stopThread=True
                        t.join()   
                        return False # terminate processing
                    else:
                        floatData = list(map(lambda x:struct.unpack('f',data[4+x*4:8+x*4])[0],stdArr))
                        bufferTotalArr[bufferIndex:bufferIndex+oneSampleByte] = floatData
                        if bufferIndex==0:
                            sensorStart=max(dataStartTime,sensorEnd)
                        bufferIndex=bufferIndex+oneSampleByte
                        freshFsCount = freshFsCount+self.config[self.sensor]["oneBatchSample"]
                        #print("Fs",realFs,bufferIndex/3.0/realFs,time.time())
                        currentIndex = data[3]
                        diffIndex = abs(currentIndex-lastIndex)
                        if (diffIndex != 1 and diffIndex!=255):
                            print("index error(port "+str(self.portNum+1)+")",currentIndex,lastIndex,data[0:10],debug)
                            zeroCount=401
                            mainProgramStates.send(mainProgramStates._Err,"Prognosis snesor (port "+str(self.portNum+1)+") communication index error.")
                            self.stopThread=True
                            t.join()   
                            return False # terminate processing
                        lastIndex=currentIndex
                        debug=data[0:10] #record last data
                    
                if freshFsCount/self.Fs>3:
                    #freshFsEnd = time.time()
                    freshFsEnd = dataStartTime
                    newFs = freshFsCount/(freshFsEnd-freshFsStart)
                    self.realFs = self.realFs*0.9+newFs*0.1
                    print("Prognosis snesor (port "+str(self.portNum+1)+") Fs=",(freshFsEnd-freshFsStart),freshFsCount,newFs,self.realFs)
                    freshFsCount=0
                    freshFsStart=freshFsEnd
                
                        
                if newSampleTime-peroidTime>=self.minProcTime :
                    if bufferIndex>0:
                        bufferTotalArr = bufferTotalArr[:bufferIndex]
                        sensorEnd = sensorStart+ (bufferIndex/3)/self.realFs
                        #print("vib proc test",newSampleTime-peroidTime,bufferIndex/self.perSamplePoint,bufferIndex/self.perSamplePoint/(newSampleTime-peroidTime))
                        dataObj = dict()
                        dataObj["data"]=bufferTotalArr
                        dataObj["startTime"]=sensorStart
                        dataObj["endTime"]=sensorEnd
                        #sensorStart=sensorEnd
                        self.queue.put(dataObj)
                        del bufferTotalArr
                        del dataObj
                        bufferIndex=0
                        bufferTotalArr=np.zeros(self.bufferTotalArrSize,dtype = np.float)
                    peroidTime=newSampleTime
                
        
        except Exception as e:
        #if False:
            mainProgramStates.send(mainProgramStates._Err,"Prognosis sensor ("+self.nameStr+") connect error."+str(e))
            time.sleep(3)
            return False # terminate processing
            #while not self.states["release"]:
            #    time.sleep(3)
            #    mainProgramStates.send(mainProgramStates._Err)
        
        self.stopThread=True
        t.join()        
        
        if bufferIndex>0:
            bufferTotalArr = bufferTotalArr[:bufferIndex]
            sensorEnd = sensorStart+ (bufferIndex/3)/self.realFs
            dataObj = dict()
            dataObj["data"]=bufferTotalArr
            dataObj["startTime"]=sensorStart
            dataObj["endTime"]=sensorEnd
            print("bufferIndex",bufferIndex,sensorEnd,sensorStart,sensorEnd-sensorStart)
            self.queue.put(dataObj)
            del bufferTotalArr
            del dataObj
            gc.collect()
    
    def createDataObj(self,startTime,endTime,data):
        data = data.reshape([-1,3]).T
        data = data/1000.0
        dataLen = data.shape[1]
        timeGap = np.arange(0,dataLen+1)/(dataLen+1)*(endTime-startTime)
        timeGap = timeGap[1:]+startTime
        #print(startTime,endTime,(endTime-startTime))
        if dataLen>0:
            ret = dict()
            ret['usb']=[dict() for i in range(self.maxUSBLen)]
            ret['usb'][self.portNum]['type']="VIBRATION"
            ret['usb'][self.portNum]['sensor']=self.sensor
            ret['usb'][self.portNum]['unit']="G"
            ret['usb'][self.portNum]['fs']=self.Fs
            #ret['bus'][self.bus]['time'] = stamp2dateArr(timeGap,"%y/%m/%d %H:%M:%S.%f")
            ret['usb'][self.portNum]['time'] = timeGap
            ret['usb'][self.portNum]['scale']=dict()
            ret['usb'][self.portNum]['scale'][self.nameStr]=self.Scale
            ret['usb'][self.portNum]['data']=dict()
            x = np.array(data[0])
            y = np.array(data[1])
            z = np.array(data[2])
            ret['usb'][self.portNum]['data']["aX_"+self.nameStr] = x
            ret['usb'][self.portNum]['data']["aY_"+self.nameStr] = y
            ret['usb'][self.portNum]['data']["aZ_"+self.nameStr] = z
            return ret
        else:
            return {}
        
        
    def release(self):
        if self.usbPortEnable:
            print("close serial port")
            self.port.close()
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()



class audio_process(multiprocessing.Process):
    def __init__(self,maxUSBLen,portNum,device_index,name,minProcTime):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("Audio class create",name,device_index)
        self.maxUSBLen=maxUSBLen
             
        self.FORMAT = pyaudio.paInt16 #or using paFloat32 
        self.INPUT_FRAMES_PER_BLOCK = 4096
        
        self.name = name
        self.device_index=device_index
        self.channel=1
        self.rate = 44100
        self.portNum=portNum
        
        self.minProcTime=minProcTime
        self.type = "AUDIO"
        self.sensor="MICROPHONE"
        self.enable = True
        
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
    
    @staticmethod
    def getMapping(pa):
        print("Audio sampling getOffset")
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
        
    def creatStream(self,pa,device_index):
        return pa.open(format = self.FORMAT,
              channels = self.channel,
              rate = self.rate,
              input = True,
              start=False,
              input_device_index = device_index,
              frames_per_buffer = self.INPUT_FRAMES_PER_BLOCK)
              
            
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("prognosis pid",self.states["pid"])
        maxCount=int(self.rate*self.channel*self.minProcTime*1.2)
        bufferBatch = self.INPUT_FRAMES_PER_BLOCK*self.channel
            
        pa = pyaudio.PyAudio()
        print("Audio sampling processing [",self.name,"] creatStream device_index is",self.device_index)
        try:
            stream = self.creatStream(pa,self.device_index)
            stream.start_stream()
        except Exception as e:
            mainProgramStates.send(mainProgramStates._Err,"Audio ("+self.name+") connect error.")
            while not self.states["release"]:
                time.sleep(3)
                mainProgramStates.send(mainProgramStates._Err)
                
            
        
        # os.system("taskset -cp 2 %d" %(os.getpid()
        
        peroidTime=time.time()
        sampleTime=peroidTime
        startTime=peroidTime
        bufferSize=0
        bufferLastSize=0
        bufferFreezenCount=0
        bufferFreezenCountLimit=10
        while not self.states["release"]:
            bufferArr=np.zeros(maxCount,dtype=np.int16)
            index=0
            
            while(time.time()-peroidTime<self.minProcTime and index+bufferBatch<maxCount):
                bufferSize = stream.get_read_available()
                if bufferSize>self.INPUT_FRAMES_PER_BLOCK:
                    data = stream.read(self.INPUT_FRAMES_PER_BLOCK , exception_on_overflow = False)
                    sampleTime=time.time()
                    bufferArr[index:index+bufferBatch]=np.frombuffer(data,dtype = np.int16)
                    index+=bufferBatch
                else:
                    time.sleep(0.01)
                
                if bufferSize==bufferLastSize:
                    bufferFreezenCount=bufferFreezenCount+1
                else:
                    bufferFreezenCount=0
                bufferLastSize=bufferSize
                    
            if bufferFreezenCount>bufferFreezenCountLimit:
                index=0
                mainProgramStates.send(mainProgramStates._Err,"Audio ("+self.name+") disconnected!")
                time.sleep(30)
                return False # terminate processing
                #while not self.states["release"]:
                #    time.sleep(3)
                #    mainProgramStates.send(mainProgramStates._Err)
                
            if index>0:
                bufferArr = bufferArr[:index]
                dataObj = dict()
                dataObj["data"]=bufferArr
                dataObj["startTime"]=peroidTime
                dataObj["endTime"]=sampleTime
                peroidTime=sampleTime
                self.queue.put(dataObj)
                del bufferArr
                del dataObj
            #serialBuffer = self.getBuffer(serialBuffer)))
        
        try:
            print("keep",time.time()-startTime)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            pass
            
    
    def createDataObj(self,startTime,endTime,data):
        dataLen = len(data)
        timeGap = np.arange(0,dataLen+1)/(dataLen+1)*(endTime-startTime)
        timeGap = timeGap[1:]+startTime
        #print(startTime,endTime,(endTime-startTime))
        if dataLen>0:
            ret = dict()
            ret['usb']=[dict() for i in range(self.maxUSBLen)]
            ret['usb'][self.portNum]['type']="AUDIO"
            ret['usb'][self.portNum]['sensor']=self.sensor
            ret['usb'][self.portNum]['unit']="raw"
            ret['usb'][self.portNum]['fs']=self.rate
            #ret['bus'][self.bus]['time'] = stamp2dateArr(timeGap,"%y/%m/%d %H:%M:%S.%f")
            ret['usb'][self.portNum]['time'] = timeGap
            ret['usb'][self.portNum]['data']=dict()
            ret['usb'][self.portNum]['data'][self.name] = data
            return ret
        else:
            return {}
        
        
    def release(self):
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()


class gy530_process(multiprocessing.Process):
    def __init__(self,name,minProcTime):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("gy530 class create")
             
        self.nameStr=name
        self.Fs=30
        self.Period=1/self.Fs
        self.type="distance"
        
        tof = VL53L0X.VL53L0X(i2c_bus=1,i2c_address=0x29)
        tof.open()
        tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE)
        if tof.get_distance()==-1:
            self.enable=False
            mainProgramStates.send(mainProgramStates._Err,"Distance sensor disconnected. ")
        else:
            self.enable=True
        self.chip=tof
        self.minProcTime=minProcTime
        self.maxSamplePoint=int(minProcTime*self.Fs*10)
        
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
            
    def run(self):
        errMessage=""
        errFlag=False
        self.states["pid"]=os.getpid()
        print("gy530 pid",self.states["pid"])
        bufferTotalArr=np.zeros(self.maxSamplePoint)
        bufferIndex=0
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        
        peroidTime=time.time()
        sampleTime=peroidTime
        newSampleTime=peroidTime
        while not self.states["release"]:
            if not self.enable :
                mainProgramStates.send(mainProgramStates._Err) # keep states
                time.sleep(3)
                continue
                
            if(time.time()-newSampleTime<=self.Period):
                sleepTime = self.Period-(time.time()-newSampleTime)-0.001
                if(sleepTime>0):
                    time.sleep(sleepTime)
            
            #print("distan",time.time()-newSampleTime)
            newSampleTime=time.time()
            try:
                bufferTotalArr[bufferIndex]=self.chip.get_distance()
                if bufferTotalArr[bufferIndex]==-1:
                    if errFlag is False:
                        errFlag=True
                        errMessage="Distance sensor error. Disconnected"
                        self.enable=False
                    else:
                        errMessage=""
                else:
                    errFlag=False
                
            except Exception as e:
                bufferTotalArr[bufferIndex]=-1
                if errFlag is False:
                    errFlag=True
                    errMessage="Distance sensor error. "+str(e)
                else:
                    errMessage=""
            
            if errFlag and errMessage!="":
                mainProgramStates.send(mainProgramStates._Err,errMessage)
                return False # terminate processing
                
            bufferIndex=bufferIndex+1
                
            if newSampleTime-peroidTime>=self.minProcTime and bufferIndex>0:
                bufferTotalArr = bufferTotalArr[:bufferIndex]
                dataObj = dict()
                dataObj["data"]=bufferTotalArr
                dataObj["startTime"]=peroidTime
                dataObj["endTime"]=newSampleTime
                #print("dis Fs:",bufferIndex/(newSampleTime-peroidTime))
                self.queue.put(dataObj)
                del bufferTotalArr
                del dataObj
                peroidTime=newSampleTime
                bufferIndex=0
                bufferTotalArr=np.zeros(self.maxSamplePoint)
         
                
        if bufferIndex>0:
            bufferTotalArr = bufferTotalArr[:bufferIndex]
            dataObj = dict()
            dataObj["data"]=bufferTotalArr
            dataObj["startTime"]=peroidTime
            dataObj["endTime"]=newSampleTime
            self.queue.put(dataObj)
            del bufferTotalArr
            del dataObj
            gc.collect()
    
    def createDataObj(self,startTime,endTime,data):
        dataLen = len(data)
        timeGap = np.arange(0,dataLen)/dataLen*(endTime-startTime)
        timeGap = timeGap+startTime
        
        ret = dict()
        ret['distance']=dict()
        ret['distance']['sensor']="GY530"
        ret['distance']['unit']="mm"
        ret['distance']['fs']=self.Fs
        ret['distance']['time'] = timeGap
        ret['distance']['data']=dict()
        data[data>1200] = 1200
        ret['distance']['data'][self.nameStr]=data
        return ret
        
        
    def release(self):
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()




class gpio_process(multiprocessing.Process):
    def __init__(self,nameList,minProcTime):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("gpio class create")
             
        self.Fs=20
        self.Period=1/self.Fs
        
        pin=[
            6,
            22,
            23,
            4
            ]
        self.type="gpio"
        self.enablePin=[]
        self.enableName=[]
        GPIO.setwarnings(False)
        if GPIO.getmode()==-1 or GPIO.getmode()==None:
            GPIO.setmode(GPIO.BCM)
        for index,name in enumerate(nameList):
            if name != "":
                self.enablePin.append(pin[index])
                self.enableName.append(name)
                GPIO.setup(pin[index], GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        self.minProcTime=minProcTime
        self.maxSamplePoint=int(minProcTime*self.Fs*10)
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("gpio pid",self.states["pid"])
        bufferTotalArr=np.zeros((len(self.enablePin),self.maxSamplePoint),dtype=np.int8)
        bufferIndex=0
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        
        peroidTime=time.time()
        sampleTime=peroidTime
        newSampleTime=peroidTime
        while not self.states["release"]:
            
            if(time.time()-newSampleTime<=self.Period):
                sleepTime = self.Period-(time.time()-newSampleTime)-0.001
                if(sleepTime>0):
                    time.sleep(sleepTime)
            
            #print("gpio",time.time()-newSampleTime)
            newSampleTime=time.time()
            for index,pin in enumerate(self.enablePin):
                bufferTotalArr[index][bufferIndex]=GPIO.input(pin)
            bufferIndex=bufferIndex+1
                
                
                
            if newSampleTime-peroidTime>=self.minProcTime and bufferIndex>0:
                bufferTotalArr = bufferTotalArr[:,:bufferIndex]
                dataObj = dict()
                dataObj["data"]=bufferTotalArr
                dataObj["startTime"]=peroidTime
                dataObj["endTime"]=newSampleTime
                self.queue.put(dataObj)
                del bufferTotalArr
                del dataObj
                #print("GPIO Fs:",bufferIndex/(newSampleTime-peroidTime),bufferIndex)
                peroidTime=newSampleTime
                bufferIndex=0
                #gc.collect()
                bufferTotalArr=np.zeros((len(self.enablePin),self.maxSamplePoint),dtype=np.int8)
         
                
        if bufferIndex>0:
            bufferTotalArr = bufferTotalArr[:,:bufferIndex]
            dataObj = dict()
            dataObj["data"]=bufferTotalArr
            dataObj["startTime"]=peroidTime
            dataObj["endTime"]=newSampleTime
            self.queue.put(dataObj)
            del bufferTotalArr
            del dataObj
            gc.collect()
    
    def createDataObj(self,startTime,endTime,data):
        dataLen = data.shape[1]
        timeGap = np.arange(0,dataLen)/dataLen*(endTime-startTime)
        timeGap = timeGap+startTime
        
        ret = dict()
        ret['Digital']=dict()
        ret['Digital']['unit']="mm"
        ret['Digital']['fs']=self.Fs
        ret['Digital']['time'] = timeGap
        ret['Digital']['data']=dict()
        for index,name in enumerate(self.enableName):
            ret['Digital']['data'][name]=data[index]
        return ret
        
        
    def release(self):
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()


class ADC_process(multiprocessing.Process):
    def __init__(self,bus,name,Fs,gain,mode,differentail,maxValue,minValue,bias,unit,minProcTime):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("ADC class create")
        '''
        mode mapping
        0: voltage
        1: current
        2: CTL-6-S32-8F-CL
        3: CTL-10-CLS
        4: CTL-16-CLS
        5: CTL-22-CLF
        6: CTL-24-CLSF
        7: CTL-24-CLS
        8: CTL-24-CLF
        9: CTL-36-CLS
        '''
        turn = [ # map to mode
            1,
            1,
            1,
            800,
            3000,
            3000,
            2000,
            3000,
            2000,
            3000,
            2000
        ]
        sensor = [ # map to mode
            "Not use",
            "Not use",
            "4-20mA",
            "CTL-6-S32-8F-CL",
            "CTL-10-CLS",
            "CTL-16-CLS",
            "CTL-22-CLF",
            "CTL-24-CLSF",
            "CTL-24-CLS",
            "CTL-24-CLF",
            "CTL-36-CLS"
        ]
        differentailMap={
            'd':"defferentail",
            's':"single-ended"
        }
        volGainMap={
            1:1,
            2:1,
            3:2,
            4:2,
            5:2,
            6:8
        }
        volMaxMap={
            6:1.5,
            5:3.3,
            4:5.0,
            3:6.0,
            2:10.0,
            2:10.0,
            1:12.0
        }
        curGainMap={
            1:1,
            2:2,
            3:8,
            4:1,
            5:2,
            6:8
        }
        curMaxMap=[
            [0.00025,0.001,0.002,0.025,0.100,0.200],
            [0.02,0.02,0.02,0.02,0.02,0.02],
            [0.2,0.75,1.5,15,15,15],
            [0.7,2.8,5.6,80,80,80],
            [0.7,2.8,5.6,75,120,120],
            [0.5,1.9,3.8,50,120,120],
            [0.7,2.8,5.6,75,200,200],
            [0.5,1.9,3.8,50,200,300],
            [0.7,2.8,5.6,75,300,360],
            [0.5,1.9,3.8,50,200,400]
        ]
        curMinMapDiff=[
            [-0.00025,-0.001,-0.002,-0.025,-0.100,-0.200],
            [0.004,0.004,0.004,0.004,0.004,0.004],
            [-0.2,-0.75,-1.5,-15,-15,-15],
            [-0.7,-2.8,-5.6,-80,-80,-80],
            [-0.7,-2.8,-5.6,-75,-120,-120],
            [-0.5,-1.9,-3.8,-50,-120,-120],
            [-0.7,-2.8,-5.6,-75,-200,-200],
            [-0.5,-1.9,-3.8,-50,-200,-300],
            [-0.7,-2.8,-5.6,-75,-300,-360],
            [-0.5,-1.9,-3.8,-50,-200,-400]
        ]
        curMinMapSignal=[
            [0,0,0,0,0,0],
            [0.004,0.004,0.004,0.004,0.004,0.004],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0],
            [0,0,0,0,0,0]
        ]
        curMaxMapIndex = [
            [3,2,1,6,5,4],
            [6,6,6,6,6,6],
            [3,2,1,4,4,4],
            [3,2,1,6,4,4],
            [3,2,1,6,4,4],
            [3,2,1,6,4,4],
            [3,2,1,6,4,4],
            [3,2,1,6,5,4],
            [3,2,1,6,5,4],
            [3,2,1,6,5,4]
        ]
        
        
        interR = [940,9.53]
        shunt = 46.4/(46.4+255.0)
        #shunt = 43/(43+240)
        
        self.bus=bus
        self.nameStr=name
        self.Fs=Fs
        self.gain=gain
        self.mode=mode
        self.type="CURRENT"
        self.minProcTime=minProcTime
        self.maxSamplePoint=minProcTime*self.Fs*10
        self.perSamplePoint=0
        self.enableName=[]
        self.enableTransfer=[]
        self.enableSensor=[]
        self.enableGain=[]
        self.enableCircuit=[]
        self.enableBias=[]
        self.enableRealBias=[]
        self.enableUnit=[]
        self.enableMaxValue=[]
        self.enableMinValue=[]
        
        self.obj=ADCHub(bus)
        self.enable = True
        hubType = scanSlave()[bus]
        if hubType!="Voltage board" and mode[0]==0:
            mainProgramStates.send(mainProgramStates._Err,"The bus "+str(bus+1)+" is set to voltage, but the bus actually is "+hubType)
            self.enable = False
        elif hubType!="Current board" and mode[0]!=0:
            mainProgramStates.send(mainProgramStates._Err,"The bus "+str(bus+1)+" is set to current, but the bus actually is "+hubType)
            self.enable = False
            
            
            
        if self.enable:
            select=[]
            for i,n in enumerate(self.nameStr):
                if n =="":
                    select.append(False)
                else:
                    if hubType=="Voltage board":
                        realGain=volGainMap[gain[i]]
                    else:
                        realGain=curGainMap[gain[i]]
                    self.enableName.append(n)
                    self.enableSensor.append(sensor[mode[i]])
                    self.enableGain.append(realGain)
                    self.enableCircuit.append(differentailMap[differentail[i]])
                    self.enableTransfer.append(turn[mode[i]])
                    
                    
                    print(i)
                    if mode[i]==0:
                        sampleMax = volMaxMap[gain[i]]
                        if differentail[i] == "s":
                            sampleMin=0
                        else:
                            sampleMin=sampleMax*-1
                    else:
                        gainIndex = curMaxMapIndex[mode[i]-1].index(gain[i])
                        sampleMax = curMaxMap[mode[i]-1][gainIndex]
                        if differentail[i] == "s":
                            sampleMin=curMinMapSignal[mode[i]-1][gainIndex]
                        else:
                            sampleMin=curMinMapDiff[mode[i]-1][gainIndex]
                    
                        #print("XXXXXXX",mode[i]-1,gain[i],gainIndex,sampleMax,sampleMin)
                    
                    if maxValue[i]>minValue[i]:
                        self.enableMaxValue.append(maxValue[i])
                        self.enableMinValue.append(minValue[i])
                    else:
                        self.enableMaxValue.append(sampleMax)
                        self.enableMinValue.append(sampleMin)
                        
                    self.enableBias.append(bias[i])
                    self.enableRealBias.append(bias[i])
                    self.enableUnit.append(unit[i])
                    
                    self.enableTransfer[-1] /= 32768.0
                    self.enableTransfer[-1] *= 2.4
                    self.enableTransfer[-1] /= realGain
                    
                    if mode[i]==0:
                        self.type="VOLTAGE"
                        self.enableTransfer[-1] /= shunt
                    else:
                        if gain[i]>3:
                            self.enableTransfer[-1] /= interR[1]
                        else:
                            self.enableTransfer[-1] /= interR[0]
                    
                    #print("XXXXXXX",self.enableTransfer[-1])
                    unitGain = (self.enableMaxValue[-1]-self.enableMinValue[-1])/(sampleMax-sampleMin)
                    #print("XXXXXXX",unitGain,self.enableMaxValue[-1],self.enableMinValue[-1],sampleMax,sampleMin)
                    self.enableTransfer[-1]*=unitGain
                    #print("XXXXXXX",self.enableTransfer[-1])
                    #print("XXXXXXX",self.enableRealBias[-1])
                    self.enableRealBias[-1]+=(self.enableMaxValue[-1]+self.enableMinValue[-1])*0.5-(sampleMax+sampleMin)*0.5*unitGain
                    #print("XXXXXXX",(self.enableMaxValue[-1]+self.enableMinValue[-1])*0.5,(sampleMax+sampleMin)*0.5*unitGain,self.enableRealBias[-1])
                    #if(mode[i]==2): #4-20mA bias setting
                    #    self.enableRealBias[-1]+= -0.004*unitGain
                    #print("XXXXXXX",(unitGain,self.enableRealBias[-1]))
                    select.append(True)
                    self.obj.SetScale(i,realGain,False)
                    #print("realgain:",i,realGain)
                    self.perSamplePoint=self.perSamplePoint+2 # 2 byte
            
            self.obj.SelectAllSensor(select)
            print("ADC fs:",Fs)
            print("ADC enableTransfer:",self.enableTransfer)
            self.obj.SetFs(Fs)
        
        self.bufferTotalArrSize = int(self.maxSamplePoint * self.perSamplePoint)
        self.minSamplePeriod=min(0.1,(65536/Fs/max(self.perSamplePoint,1)/10)) #1/10 buffer
        
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("adc pid",self.states["pid"])
        if not self.enable:
            while not self.states["release"]:
                mainProgramStates.send(mainProgramStates._Err) # keep states
                time.sleep(3)
            return
        bufferTotalArr=np.zeros(self.bufferTotalArrSize,dtype = np.uint8)
        bufferIndex=0
        zeroCount=0
        errRecalTimeDiv=0
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        self.obj.StartSample()
        peroidTime=time.time()
        sampleTime=peroidTime
        newSampleTime=peroidTime
        overflowFlag=False
        while not self.states["release"]:
            sleepTime = self.minSamplePeriod-(time.time()-newSampleTime)
            if(sleepTime>0):
                time.sleep(sleepTime)
                
                
            newSampleTime=time.time()
            bufferLen = self.obj.GetBufferLen()
            
            #for overflow testing
            #while bufferLen!=65535 and not overflowFlag:
            #    newSampleTime=time.time()
            #    bufferLen = self.obj.GetBufferLen()
            #    time.sleep(0.01)
            
            if bufferLen==65535:
                mainProgramStates.send(mainProgramStates._Err,self.type+" sampling error(bus "+str(self.bus)+"). The buffer overflow.")
                return False # terminate processing
                #overflowFlag=True
            
            
            bufferLen = bufferLen//self.perSamplePoint*self.perSamplePoint
            if(bufferLen>0):
                bufferData = self.obj.GetBuffer(bufferLen)
                bufferTotalArr[bufferIndex:bufferIndex+bufferLen] = bufferData
                bufferIndex = bufferIndex+bufferLen
                if overflowFlag:
                    zeroCount=11 #keep to send error
                else:
                    zeroCount=0
            elif zeroCount<10:
                zeroCount = zeroCount+1
            elif zeroCount==10:
                zeroCount = zeroCount+1 #let zeroCount over 10, so this condition will run one times.
                mainProgramStates.send(mainProgramStates._Err,self.type+" board (bus "+str(self.bus)+") dissconnected.")
                return False # terminate processing
            elif zeroCount>10:
                errRecalTimeDiv=errRecalTimeDiv+1
                if errRecalTimeDiv>(3/self.minSamplePeriod): #sec
                    #print("3/self.minSamplePeriod",3/self.minSamplePeriod)
                    mainProgramStates.send(mainProgramStates._Err)
                    errRecalTimeDiv=0
                
            if newSampleTime-peroidTime>=self.minProcTime :
                if bufferIndex>0:
                    bufferTotalArr = bufferTotalArr[:bufferIndex]
                    dataObj = dict()
                    dataObj["data"]=bufferTotalArr
                    dataObj["startTime"]=peroidTime
                    dataObj["endTime"]=newSampleTime
                    print("ADC proc test",newSampleTime-peroidTime,bufferIndex/self.perSamplePoint,bufferIndex/self.perSamplePoint/(newSampleTime-peroidTime))
                    self.queue.put(dataObj)
                    del bufferTotalArr
                    del dataObj
                    bufferIndex=0
                    bufferTotalArr=np.zeros(self.bufferTotalArrSize,dtype = np.uint8)
                peroidTime=newSampleTime
         
        if bufferIndex>0:
            bufferTotalArr = bufferTotalArr[:bufferIndex]
            dataObj = dict()
            dataObj["data"]=bufferTotalArr
            dataObj["startTime"]=peroidTime
            dataObj["endTime"]=newSampleTime
            self.queue.put(dataObj)
            del bufferTotalArr
            del dataObj
            gc.collect()
    0
    def createDataObj(self,startTime,endTime,data):
        data = data[0::2]*256+data[1::2]
        data = self.obj.ConvertData(data)
        data = np.array(data,dtype=np.float32)
        data = data.reshape([-1,self.perSamplePoint//2]).T
        dataLen = data.shape[1]
        timeGap = np.arange(0,dataLen)/dataLen*(endTime-startTime)
        timeGap = timeGap+startTime
        
        ret = dict()
        ret['bus']=[dict(),dict(),dict(),dict()]
        ret['bus'][self.bus]['type']=self.type
        ret['bus'][self.bus]['fs']=self.Fs
        ret['bus'][self.bus]['time'] = timeGap
        ret['bus'][self.bus]['sensor']=dict()
        ret['bus'][self.bus]['gain']=dict()
        ret['bus'][self.bus]['circuit']=dict()
        ret['bus'][self.bus]['data']=dict()
        ret['bus'][self.bus]['unit']=dict()
        ret['bus'][self.bus]['maxValue']=dict()
        ret['bus'][self.bus]['minValue']=dict()
        ret['bus'][self.bus]['bias']=dict()
            
        for i,n in enumerate(self.enableName):
            ret['bus'][self.bus]['sensor'][n]=self.enableSensor[i]
            ret['bus'][self.bus]['gain'][n]=self.enableGain[i]
            ret['bus'][self.bus]['circuit'][n]=self.enableCircuit[i]
            ret['bus'][self.bus]['data'][n] = np.array(data[i])*self.enableTransfer[i]+self.enableRealBias[i]
            if ret['bus'][self.bus]['circuit'][n]=="single-ended":
                zeroIndex = ret['bus'][self.bus]['data'][n]<0
                ret['bus'][self.bus]['data'][n][zeroIndex]=0
            ret['bus'][self.bus]['unit'][n]=self.enableUnit[i]
            ret['bus'][self.bus]['maxValue'][n]=self.enableMaxValue[i]
            ret['bus'][self.bus]['minValue'][n]=self.enableMinValue[i]
            ret['bus'][self.bus]['bias'][n]=self.enableBias[i]
        return ret
        
    def release(self):
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()


class dataFromCSV(multiprocessing.Process):
    def __init__(self,minProcTime,simulaotrDelay=False):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("Simulator class create")
        
        self.type='SIMULATOR'
        self.minProcTime=minProcTime
        self.Fs=0
        self.bus=0
        self.enableName=[]
        
        self.simulaotrDelay=simulaotrDelay
        
        rootPath = '/home/pi/program/simulator'
        self.data = None
        files = listdir(rootPath)
        for f in files:
            if f[-4:]==".csv" or  f[-4:]==".CSV":
                df = pd.read_csv(rootPath+"/"+f)
                if 'datetime' in df.columns:
                    isPHM_v3 = True
                    try:
                        datetime.datetime.strptime(df['datetime'].values[0],"%Y-%m-%d %H:%M:%S").timetuple()
                    except :
                        isPHM_v3 = False
                        
                    print("data is PHM_v3?",isPHM_v3)
                    if isPHM_v3:
                        realSec = pd.unique(df['datetime'])
                        df = df.drop(df.loc[df['datetime'] == realSec[0]].index)     #remove not complete sec at head
                        df = df.drop(df.loc[df['datetime'] == realSec[-1]].index)    #remove not complete sec at fial
                        realSec = pd.unique(df['datetime'])
                        self.Fs = len(df['datetime'])/len(realSec)
                        startTime = time.mktime(datetime.datetime.strptime(df['datetime'].values[0],"%Y-%m-%d %H:%M:%S").timetuple())
                    else:
                        startTime = time.mktime(datetime.datetime.strptime(df['datetime'].values[0],"%Y-%m-%d %H:%M").timetuple())
                        self.Fs = 1000
                        
                    df['datetime'] = startTime+np.arange(len(df['datetime']))/self.Fs
                    self.data = df
                    self.enableName = list(df.columns)
                    self.enableName.remove('datetime')
                    print("Simulator file:",rootPath+"/"+f)
                    print("columns:",self.enableName)
                    break
        
        if self.data is None:
            printErr("Simulator class create is error. Not found file or format error.")
        
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
    
    def stopProc(self):
        self.states["release"]=True
    
    def getPid(self):
        return self.states["pid"]
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("file pid",self.states["pid"])
        
        startTime = time.time()
        lastTime = startTime
        nowTime = startTime
        baseTime = self.data['datetime'].values[0]
        while not self.states["release"]:
            
            if self.simulaotrDelay:
                nowTime = time.time()
                if nowTime-lastTime >=self.minProcTime:
                    dataObj = dict()
                    dataObj["startTime"]=baseTime+lastTime-startTime
                    dataObj["endTime"]=baseTime+nowTime-startTime
                    dataObj["data"]=self.data.loc[(self.data['datetime']>=dataObj["startTime"]) & (self.data['datetime']<dataObj["endTime"])]
                    if(len(dataObj["data"])==0):
                        break
                    print("Simulator proc test",dataObj["startTime"],dataObj["endTime"],len(dataObj["data"]),len(dataObj["data"])/(nowTime-lastTime))
                    self.queue.put(dataObj)
                    lastTime=nowTime
                else:
                    time.sleep(0.05)
            else:
                nowTime+=self.minProcTime
                dataObj = dict()
                dataObj["startTime"]=baseTime+lastTime-startTime
                dataObj["endTime"]=baseTime+nowTime-startTime
                dataObj["data"]=self.data.loc[(self.data['datetime']>=dataObj["startTime"]) & (self.data['datetime']<dataObj["endTime"])]
                if(len(dataObj["data"])==0):
                    break
                print("Simulator proc test",dataObj["startTime"],dataObj["endTime"],len(dataObj["data"]),len(dataObj["data"])/(nowTime-lastTime))
                self.queue.put(dataObj)
                lastTime=nowTime
            
        print("Simulator done")
    
    def createDataObj(self,startTime,endTime,data):
        dataLen = data.shape[0]
        timeGap = np.arange(0,dataLen)/dataLen*(endTime-startTime)
        timeGap = timeGap+startTime
        
        ret = dict()
        ret['bus']=[dict(),dict(),dict(),dict()]
        ret['bus'][self.bus]['type']=self.type
        ret['bus'][self.bus]['fs']=self.Fs
        ret['bus'][self.bus]['time'] = timeGap
        ret['bus'][self.bus]['sensor']=dict()
        ret['bus'][self.bus]['gain']=dict()
        ret['bus'][self.bus]['circuit']=dict()
        ret['bus'][self.bus]['data']=dict()
        ret['bus'][self.bus]['unit']=dict()
        ret['bus'][self.bus]['maxValue']=dict()
        ret['bus'][self.bus]['minValue']=dict()
        ret['bus'][self.bus]['bias']=dict()
            
        for i,n in enumerate(self.enableName):
            ret['bus'][self.bus]['sensor'][n]="Simulator"
            ret['bus'][self.bus]['gain'][n]=1
            ret['bus'][self.bus]['circuit'][n]="Differential"
            ret['bus'][self.bus]['data'][n] = np.array(data[n].values)
            ret['bus'][self.bus]['unit'][n]="None"
            ret['bus'][self.bus]['maxValue'][n]=1
            ret['bus'][self.bus]['minValue'][n]=-1
            ret['bus'][self.bus]['bias'][n]=0
        return ret
        
    def release(self):
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()
