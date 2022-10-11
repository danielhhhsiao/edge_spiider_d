#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 21 11:41:57 2021

@author: etao
"""


from Library.sample import sample,_oldSamplingPath
from Library.segmentation import segmentation
from Library.upload import upload
from Library.tool import loadConfig, getDictItem, writeConfig, printErr,conponerObj, dataObj2drawList, drawList, getRamPercent,testPrintStructure,mainProgramStates,savePKL,keepTime,alineObj,testStatusUpload
import time
import os
import gc
import copy
import subprocess
import numpy as np
from datetime import datetime

_maxTestSec=600
_orinQueueProcTime = 3 #sec
_workCheckPeriod = _orinQueueProcTime #sec
_minQueueProcTime = 0.5 #sec
_minQueueProcTimeForSeg = _orinQueueProcTime #sec
_minFixSampleTime = 2 #sec
_maxFixSampleTime = 5 #sec
_orinDeviceConfigPath = '/home/pi/default/original_device.ini'
_deviceConfigPath = '/home/pi/default/device.ini'
_systemConfigPath = '/home/pi/program/system.ini'
_workConfigPath = '/home/pi/program/work.ini'
_defaultSystemConfigPath = '/home/pi/default/system.ini'
_defaultWorkConfigPath = '/home/pi/default/work.ini'
_defaultServerPath = '/home/pi/server'
_defaultSensorTestName = 'sampleResult'
_defaultSegTestName = 'segResult'
_deviceConfig = "d"
_systemConfig = "s"
_workConfig = "w"

def updateConfigPath():
    global _deviceConfigPath
    global _systemConfigPath
    global _workConfigPath
    global _defaultSystemConfigPath
    global _defaultWorkConfigPath
    global _defaultServerPath
    
    configDict = loadConfig(_deviceConfigPath)
    _systemConfigPath = configDict['environment']['home_dir'] + '/system.ini'
    _workConfigPath = configDict['environment']['home_dir'] + '/work.ini'
    _defaultSystemConfigPath = configDict['environment']['default_dir'] + '/system.ini'
    _defaultWorkConfigPath = configDict['environment']['default_dir'] + '/work.ini'
    _defaultServerPath = configDict['environment']['server_dir']
    
def checkAndPipeData(sampleProc,segmentationProc,uploadProc,testFlag=False,testRawData=[],testSegData=[]):
    testT=time.time()
    while not sampleProc.queue.empty():
        sampleData=sampleProc.queue.get(False)
        if segmentationProc.is_alive():
            segmentationProc.put(sampleData)
        if testFlag:
            testRawData.append(sampleData)
        del sampleData
        time.sleep(0.01)
    gc.collect()
    
    testT=time.time()
    while not segmentationProc.reQueue.empty():
        segmentationData=segmentationProc.reQueue.get(False)
        #uploadProc.put(segmentationData["data"],segmentationData["name"],False)
        #testPrintStructure(segmentationData["data"])
        if uploadProc.is_alive():
            uploadProc.put(segmentationData["data"],segmentationData["name"],segmentationData["type"])
        del segmentationData
        time.sleep(0.01)
    gc.collect()
        
    if testFlag:
        while not segmentationProc.drawQueue.empty():
            segmentationData=segmentationProc.drawQueue.get(False)
            testSegData.append(segmentationData)
            del segmentationData
            time.sleep(0.01)
    gc.collect()

_mainHeartbeatLastTime = 0
def mainHeartbeat():
    global _mainHeartbeatLastTime
    #print("###### ### ### ### mainHeartbeat",time.time()-_mainHeartbeatLastTime)
    if time.time()-_mainHeartbeatLastTime < 2.7:
        return
    mainProgramStates.send(mainProgramStates._MainHeartbeat)
    #print("###### ### ### ### mainHeartbeat excute")
    _mainHeartbeatLastTime=time.time()
    
if __name__ == "__main__":
    
    #subprocess.run(["cp",_orinDeviceConfigPath,_deviceConfigPath])
    gc.enable()
    _orinDeviceConfigPath
    print("gc:",gc.isenabled())
    while True:
        workCheckLastTime=time.time()
        mainHeartbeat()
        
        deviceConfig = loadConfig(_deviceConfig)
        systemConfig = loadConfig(_systemConfig)
        workConfig = loadConfig(_workConfig)
        
        #workEnable == 1, The meaning is set device to work
        #testEnable == 1, The meaning is set device to test
        workEnable = getDictItem(systemConfig,"work","enable","0")
        testEnable = getDictItem(systemConfig,"sensor_test","enable","0")
        testStatus = getDictItem(deviceConfig,"environment","sensor_test_state","0")
        exhibition = getDictItem(deviceConfig,"environment","exhibition","0")
        testTime = getDictItem(systemConfig,"sensor_test","maxsec","0")
        testTime = float(testTime)
        exhibition = int(exhibition)
        if exhibition==1:
            _minQueueProcTimeForSeg = _minQueueProcTime
            #_workCheckPeriod = _minQueueProcTime
        else:
            _minQueueProcTimeForSeg = _orinQueueProcTime
            #_workCheckPeriod = _orinQueueProcTime
        
        #print("before proc:",getRamPercent())
        #start main work or test
        #print("check workEnable/testEnable:",workEnable,testEnable)
        if(workEnable == "1" or (testEnable != "0" and testStatus=="0" and testTime>=1)):
            if getDictItem(deviceConfig,"environment","simulator","0")=="0":
                simulator=0
            elif getDictItem(deviceConfig,"environment","simulator_delay","0")=="0":
                simulator=1
            else:
                simulator=2
            print("simulator mode:",simulator)
            
            #setting status ----------------------------------------------
            testRawData=[]
            testSegData=[]
            testFlag=False
            if workEnable == "1":
                writeConfig(_deviceConfig,"environment","work_task_state","1")
                workTime = -1
            if (testEnable != "0" and testStatus=="0" and testTime>=1):
                if simulator>0:
                    workTime=-1
                else:
                    workTime = testTime
                testFlag=True
                
            #init processing ----------------------------------------------
            if (testEnable != "0"):
                testStatusUpload("1")
            if testEnable=="2":#use old sampling data
                sampleProc = sample(workConfig,_minQueueProcTime,simulator,True)
            else:
                sampleProc = sample(workConfig,_minQueueProcTime,simulator,False)
            if sampleProc.prognosis:
                minFixSampleTime=_maxFixSampleTime
            else:
                minFixSampleTime=_minFixSampleTime
            sampleProc.start()
            while not sampleProc.ready():
                time.sleep(0.1)
            
            if testEnable=="2":#use old sampling data
                segmentationProc=segmentation(workConfig,_minQueueProcTimeForSeg,testFlag,testEnable,_maxTestSec,exhibition)
            else:
                segmentationProc=segmentation(workConfig,_minQueueProcTimeForSeg,testFlag,testEnable,workTime,exhibition)
                
            uploadProc = upload(workConfig,systemConfig,_minQueueProcTime,testFlag)
            
            #start processing ----------------------------------------------
            uploadProc.start()
            segmentationProc.start()
            time.sleep(0.1)
            os.system("taskset -cp 0-2 %d" %sampleProc.getPid())
            os.system("taskset -cp 0-2 %d" %uploadProc.getPid())
            os.system("taskset -cp 0-2 %d" %segmentationProc.getPid())
            sampleProc.startSample()
            
            
                
            #working loop ----------------------------------------------
            startTime = time.time()
            nowTime = startTime
            workStatuesUpdateTime = startTime
            simulatorMaxEmpty = 4
            print("minFixSampleTime",workTime + minFixSampleTime)
            while workTime==-1 or nowTime-startTime<workTime + minFixSampleTime:
                #check and pipe data
                checkAndPipeData(sampleProc,
                    segmentationProc,
                    uploadProc,
                    testFlag,
                    testRawData,
                    testSegData)
                
                
                nowTime = time.time()
                if (testEnable != "0"):
                    testStatusUpload("2",str(round(min(nowTime-startTime,workTime)/workTime*100,1)))
                
                if nowTime-workStatuesUpdateTime>=_workCheckPeriod :
                    mainHeartbeat()
                    workStatuesUpdateTime=nowTime
                    if workEnable == "1":# refresh status
                        systemConfig = loadConfig(_systemConfig)
                        if getDictItem(systemConfig,"work","enable","0")=="0":
                            break
                    
                if simulator>0:
                    if sampleProc.queue.empty():
                        simulatorMaxEmpty = simulatorMaxEmpty-1
                    else:
                        simulatorMaxEmpty = 4
                        
                    if simulatorMaxEmpty<=0:
                        break
                    # force end the processing
                time.sleep(0.5)
                
            #release all processing ----------------------------------------------
            testStatusUpload("3")
            sampleProc.release(mainHeartbeat)
            checkAndPipeData(sampleProc,
                segmentationProc,
                uploadProc,
                testFlag,
                testRawData,
                testSegData)
            testStatusUpload("4")
            segmentationProc.release(mainHeartbeat)
            checkAndPipeData(sampleProc,
                segmentationProc,
                uploadProc,
                testFlag,
                testRawData,
                testSegData)
                
            testStatusUpload("5")
            uploadProc.release(mainHeartbeat)
            
            del sampleProc
            del segmentationProc
            del uploadProc
            gc.collect()
            
            picCount=0
            if testFlag:
                conponerResult=object
                dataList=object
                if(len(testRawData)>0):
                    conponerResult = conponerObj(testRawData,{})
                    conponerResult = alineObj(conponerResult)
                    np.set_printoptions(precision=None,threshold=None,edgeitems=None,suppress=None)
                    #print(conponerResult)
                    # for test:
                    #timeArr = conponerResult["usb"][1]["time"]
                    #timeArr = timeArr[1:]-timeArr[:-1]
                    #print("---sample interval---")
                    #print("len:",len(timeArr))
                    #print("mean:",np.mean(timeArr))
                    #print("max:",np.max(timeArr))
                    #print("min:",np.min(timeArr))
                    
                    if testEnable!="2": # save new data and picture
                        keepTime(conponerResult,workTime)
                        savePKL(conponerResult,_oldSamplingPath)
                        dataList = dataObj2drawList(conponerResult,workTime)
                        drawList(_defaultServerPath+"/example/"+_defaultSensorTestName,dataList,"6",mainHeartbeat) #"6" is drawwing sensor 
                    picCount=picCount+1
                if(len(testSegData)>0):
                    drawList(_defaultServerPath+"/example/"+_defaultSegTestName,testSegData,"7",mainHeartbeat) #"7" is drawwing segmemtation 
                    picCount=picCount+1
                
                del conponerResult
                del dataList
                del testRawData
                del testSegData
                writeConfig(_deviceConfig,"environment","sensor_test_output",str(picCount))
                writeConfig(_deviceConfig,"environment","sensor_test_state","1")
                
                
            if workEnable == "1":
                writeConfig(_deviceConfig,"environment","work_task_state","0")
        
            gc.collect()
            print("finish sample:",getRamPercent())
        elif getDictItem(deviceConfig,"environment","work_task_state","0") == "1" and workEnable=="0":
            writeConfig(_deviceConfig,"environment","work_task_state","0")
            
        sleepTime=_workCheckPeriod-(time.time()-workCheckLastTime)
        if sleepTime>0.1:
            time.sleep(sleepTime)
        
        
