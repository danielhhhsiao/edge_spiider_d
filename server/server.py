# -*- coding: utf-8 -*-
"""
Created on Mon May  17 09:19:26 2021

@author: EtaoWTLi

test: http://127.0.0.1:8000/api?sn=1862659
""" 

import sys
import http.server
import socketserver
import json
import configparser
import io
import os
import gc
from subprocess import Popen, PIPE, TimeoutExpired
import numpy as np
import shutil
import time
from urllib import parse
import hashlib
import base64
from datetime import datetime
import multiprocessing
import Library.ftpCheck as ftpCheck
def isSPIIDER():
    return sys.platform=="linux"

if isSPIIDER():
    import Library.SpiSlaveScan as SpiSlaveScan
    import Library.VibrationHub as VibrationHub
    _defaultWorkConfigPath = '/home/pi/default/work.ini'
    _workConfigPath = '/home/pi/program/work.ini'
else:
    import pathlib
    import shutil
    import pandas as pd
    from Library.segmentation import segmentation
    from Library.tool import dataObj2drawList, drawListMuti_proc,openPKL,createDataObjFromCSV,getDictItem
    serverPath = str(pathlib.Path(__file__).parent.absolute())
    lastServerPath = "\\".join(serverPath.split("\\")[:-1])
    _defaultWorkConfigPath = serverPath+'\\work_default.ini'
    _workConfigPath = lastServerPath+'\\work.ini'
    _dataPath = lastServerPath+'\\Data'
    _inputPath = _dataPath+'\\rawdata'
    _outputPath = _dataPath+'\\picture'

_maxSegRule = 16
_deviceConfigPath = '/home/pi/default/device.ini'
_systemConfigPath = '/home/pi/program/system.ini'
_OTAPath = '/home/pi/OTA/buffer/new.bin'
_localDataPath = '/home/pi/program/LocalSaved'
_localDataPath_T = '/home/pi/program/T_LocalSaved'
_defaultSystemConfigPath = '/home/pi/default/system.ini'
_defaultServerPath = '/home/pi/server'
_apSettingPath = "/home/pi/tool_sh/ap_setting.sh"
_staSettingPath = "/home/pi/tool_sh/wifi_connect.sh"
_staDisconnectPath = "/home/pi/tool_sh/wifi_disconnect.sh"
_staSearchPathPy = "/home/pi/tool_sh/wifi_search.py"
_staSearchPath = "/home/pi/tool_sh/wifi_search"
_ipSettingPath =  "/home/pi/tool_sh/ip_setting.sh"
_gy530AddressCheck =  "/home/pi/tool_sh/GY530check.sh"
_OTAprogramPy = '/home/pi/OTA/setup.py'
_OTAprogramCMD = '/home/pi/OTA/setup >> /home/pi/OTA/log.txt'
_OTAprogramCMDPy = 'python3 /home/pi/OTA/setup.py >> /home/pi/OTA/log.txt'
_hostname = ""

def popen_retry(cmd,timeout=None,times=-1,defualtV=""):
    #(times ==-1) will keep to try
    flag=False
    while (flag is False) and (times!=0): 
        flag , ret = popen_retry_sub(cmd,timeout,defualtV)
        times=times-1
        if times < -1:
            times = -1
    return ret
    
def popen_retry_sub(cmd,timeout,defualtV):
    p = Popen(cmd, stdout=PIPE)
    
    try:
        out = p.communicate(timeout=timeout)
    except TimeoutExpired:
        p.kill()
        return False , defualtV
    
    return True,out[0].decode("utf-8")

def HWmappping():
    bus_max_len = 4
    data = SpiSlaveScan.scanSlave()
    data = data[:bus_max_len]
    bus = []
    for index,d in enumerate(data):
        obj = dict()
        if d == "Vibration board":
            obj['name']="vib"
            vib = VibrationHub.VibHub(index)
            obj['channel']=[]
            for i in vib.ScanSensor():
                if i :
                    obj['channel'].append(1)
                else:
                    obj['channel'].append(0)
					
            
        elif d == "Voltage board":
            obj['name']="voltage"
        elif d == "Current board":
            obj['name']="current"
        else:
            obj['name']="none"	
        bus.append(obj)		
    ret = dict()
    ret["bus"] = bus
    GY530Address = popen_retry([_gy530AddressCheck],10,1,'false').replace("\n","")
    
    if GY530Address == "true":
        ret["distance"]=True
    else:
        ret["distance"]=False
    return ret
    
def getMask(data):
    mask = data.split(".")
    mask_num = 0
    for m in mask:
        bit = 128
        while bit!=0 and int(m)&bit !=0:
            mask_num=mask_num+1
            bit=bit//2 #move right
        if bit !=0: #jubge a 0
            break
    return str(mask_num)
    
def updateConfigPath():
    global _deviceConfigPath
    global _systemConfigPath
    global _workConfigPath
    global _defaultSystemConfigPath
    global _defaultWorkConfigPath
    global _defaultServerPath
    global _hostname
    global _localDataPath
    global _localDataPath_T
    
    configDict = readConfig(_deviceConfigPath)._sections
    _systemConfigPath = configDict['environment']['home_dir'] + '/system.ini'
    _workConfigPath = configDict['environment']['home_dir'] + '/work.ini'
    _defaultSystemConfigPath = configDict['environment']['default_dir'] + '/system.ini'
    _defaultWorkConfigPath = configDict['environment']['default_dir'] + '/work.ini'
    _localDataPath = configDict['environment']['home_dir'] + '/LocalSaved'
    _localDataPath_T = configDict['environment']['home_dir'] + '/T_LocalSaved'
    _defaultServerPath = configDict['environment']['server_dir']
    process = Popen(['hostname'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    _hostname=str(stdout,"utf-8")
    
def checkWorkEnable():
    if not isSPIIDER():
        return False
    global _deviceConfigPath
    configDict = readConfig(_deviceConfigPath)._sections
    if configDict['environment']['work_task_state']=="1":
        return True
    return False
    
def replaceConfig(path,data):
    config = readConfig(path)
    configDict = config._sections
    for section in data.keys():
        if section in configDict.keys():
            for key in data[section].keys():
                if key in configDict[section].keys():
                    configDict[section][key]=data[section][key]
                    
    if isSPIIDER():
        with open(path+"_ub", 'w') as configfile:
            config.write(configfile)
        #popen_retry(["rm",path],10,1)
        popen_retry(["cp",path+"_ub",path],10,1)
    else:
        with open(path, 'w') as configfile:
            config.write(configfile)
    
    
def readConfig(path):
    global _defaultWorkConfigPath
    useBackup = False
    if not os.path.isfile(path):
        useBackup=True
    elif os.path.getsize(path) < 100:
        useBackup=True
        
    if isSPIIDER():
        if useBackup and os.path.isfile(path+"_ub") and os.path.getsize(path+"_ub") > 100:
            print("Use backup",path+"_ub")
            popen_retry(["cp",path+"_ub",path],10,1)
    else:
        if useBackup and os.path.isfile(_defaultWorkConfigPath) and os.path.getsize(_defaultWorkConfigPath) > 100:
            print("Use backup",_defaultWorkConfigPath)
            shutil.copyfile(_defaultWorkConfigPath,path)
                
        
    config = configparser.ConfigParser()
    config.read(path)
    return config
    
def _API_systemTime(method,path,data={}):
    global _systemConfigPath
    global _defaultSystemConfigPath
    
    print(method)
    if(method=="PUT"):
        data = json.loads(data)
        flag=False
        configDict = readConfig(_defaultSystemConfigPath)._sections
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        if "time" in data.keys():
            popen_retry([ "sudo" ,"date" ,"-s" ,data["time"]["value"]],10,3)
            popen_retry([ "sudo" ,"hwclock" ,"--set" ,"--date" ,data["time"]["value"]],10,3)
        
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
     
    
        
def _API_systemConfig(method,path,data={}):
    global _systemConfigPath
    global _defaultSystemConfigPath
    
    print(method)
    if(method=="GET"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        if isSPIIDER():
            configDict = readConfig(_systemConfigPath)._sections
            ret["data"]=configDict
        else:
            ret["data"]=dict()
            ret["data"]["sensor_test"]=dict()
            ret["data"]["sensor_test"]["enable"]=simulatorP.workCheck()
            ret["data"]["work"]=dict()
            ret["data"]["work"]["enable"]="0"
            ret["data"]["language"]=dict()
            ret["data"]["language"]["value"]="english"
            
            
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    elif(method=="PUT"):
        data = json.loads(data)
        flag=False
        configDict = readConfig(_defaultSystemConfigPath)._sections
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        """
        for section in configDict.keys():
            if section in data.keys():
                flag=True
                for key in configDict[section].keys():
                    if key not in data[section].keys():
                        ret["state"]=402
                        ret["msg"]="key error. Please add key "+key+" in "+section+" section."
                        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        if flag is False:
            ret["state"]=401
            ret["msg"]="Not any section in requite body. Please use section: "+(",").join(list(configDict.keys()))
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        """
        
        # relace old setting
        replaceConfig(_systemConfigPath,data)
            
        if "ap" in data.keys():
            popen_retry([ _apSettingPath ,data["ap"]["name"] , data["ap"]["passwd"]],10,3)
            
        if "ntp" in data.keys():
            popen_retry([ "sudo" ,"ntpdate" ,"-u" ,data["ntp"]["ip"]],10,3)
            
        if "ftpTest" in data.keys():
            ret["ftp_test"] = popen_retry([ "python3" ,"/home/pi/server/Library/ftpCheck.py" , data["ftpTest"]["ip"], data["ftpTest"]["name"], data["ftpTest"]["pwd"]],10,3)
           
        if "mqttTest" in data.keys():
            ret["mqtt_test"] = popen_retry([ "python3" ,"/home/pi/server/Library/mqttCheck.py" , data["mqttTest"]["ip"], data["mqttTest"]["port"], data["mqttTest"]["name"], data["mqttTest"]["pwd"]],10,4)
        
        networkUpdate = False
        eth0ip = "--"
        eth0gw = "--"
        eth0fresh = "--"
        eth1ip = "--"
        eth1gw = "--"
        eth1fresh = "--"
        wlan0ip = "--"
        wlan0gw = "--"
        wlan0fresh = "--"
        
        configDict = readConfig(_systemConfigPath)._sections
        if configDict["lan"]["mask"]!="..." :
            eth0ip = configDict["lan"]["ip"]+"/"+getMask(configDict["lan"]["mask"])
            eth0gw = configDict["lan"]["getway"]
        if configDict["lan2"]["mask"]!="..." :
            eth1ip = configDict["lan2"]["ip"]+"/"+getMask(configDict["lan2"]["mask"])
            eth1gw = configDict["lan2"]["getway"]
        if configDict["wifi"]["mask"]!="..." :
            wlan0ip = configDict["wifi"]["ip"]+"/"+getMask(configDict["wifi"]["mask"])
            wlan0gw = configDict["wifi"]["getway"]
        
        
        if "lan" in data.keys():
            if data["lan"]["ip"]!="..." and data["lan"]["mask"]!="..." and  data["lan"]["getway"]!="..." :
                eth0ip = data["lan"]["ip"]+"/"+getMask(data["lan"]["mask"])
                eth0gw = data["lan"]["getway"]
            eth0fresh = "1"
            networkUpdate=True
                
        if "lan2" in data.keys():
            if data["lan2"]["ip"]!="..." and data["lan2"]["mask"]!="..." and  data["lan2"]["getway"]!="..." :
                eth1ip = data["lan2"]["ip"]+"/"+getMask(data["lan2"]["mask"])
                eth1gw = data["lan2"]["getway"]
            eth1fresh = "1"
            networkUpdate=True
                
        if "wifi" in data.keys():
            if data["wifi"]["ip"]!="..." and data["wifi"]["mask"]!="..." and  data["wifi"]["getway"]!="..." :
                wlan0ip = data["wifi"]["ip"]+"/"+getMask(data["wifi"]["mask"])
                wlan0gw = data["wifi"]["getway"]
            wlan0fresh = "1"
            networkUpdate=True
        print(configDict)
        print(" ".join([
                "sudo" ,
                _ipSettingPath ,
                eth0ip,
                eth0gw,
                eth0fresh,
                eth1ip,
                eth1gw,
                eth1fresh,
                wlan0ip,
                wlan0gw,
                wlan0fresh
                ]))
        if networkUpdate:
            popen_retry([
                "sudo" ,
                _ipSettingPath ,
                eth0ip,
                eth0gw,
                eth0fresh,
                eth1ip,
                eth1gw,
                eth1fresh,
                wlan0ip,
                wlan0gw,
                wlan0fresh
                ],10,3)
        
        
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    
def _API_sensorConfig(method,path,data={}):
    global _workConfigPath
    global _defaultWorkConfigPath
    
    #print(method)
    if(method=="GET"):
        configDict = readConfig(_workConfigPath)._sections
        for i in range(_maxSegRule):
            if("segmentation_"+str(i+1) in configDict.keys()):
                del configDict["segmentation_"+str(i+1)]
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=configDict
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    elif(method=="PUT"):
        data = json.loads(data)
        #check work states:
        if checkWorkEnable():
            ret = dict()
            ret["state"]=501
            ret["msg"]="Work already enable."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            
        
        # use defualt data to check body json data
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        """
        configDict = readConfig(_defaultWorkConfigPath)._sections
        for i in range(_maxSegRule):
            if("segmentation_"+str(i+1) in configDict.keys()):
                del configDict["segmentation_"+str(i+1)]
        for section in configDict.keys():
            if section not in data.keys():
                ret["state"]=401
                ret["msg"]="section error. Please add section "+section+"."
                return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            else:
                for key in configDict[section].keys():
                    if key not in data[section].keys():
                        ret["state"]=402
                        ret["msg"]="key error. Please add key "+key+" in "+section+" section."
                        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        """
        
        # relace old setting
        replaceConfig(_workConfigPath,data)
        
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    
def _API_segConfig(method,path,data={}):
    global _workConfigPath
    global _defaultWorkConfigPath
    global _deviceConfigPath
    
    #print(method)
    if(method=="GET"):
        configDict = readConfig(_workConfigPath)._sections
        retDict=dict()
        for i in range(_maxSegRule):
            if("segmentation_"+str(i+1) in configDict.keys()):
                retDict["segmentation_"+str(i+1)] = configDict["segmentation_"+str(i+1)]
        retDict["tdma"] = configDict["tdma"]
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=retDict
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    elif(method=="PUT"):
        data = json.loads(data)
        #check work states:
        if checkWorkEnable():
            ret = dict()
            ret["state"]=501
            ret["msg"]="Work already enable."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        # use defualt data to check body json data
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        configDict = readConfig(_defaultWorkConfigPath)._sections
        for i in range(_maxSegRule):
            section = "segmentation_"+str(i+1)
            if section not in data.keys():
                ret["state"]=401
                ret["msg"]="section error. Please add section "+section+"."
                return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            else:
                for key in configDict[section].keys():
                    if key not in data[section].keys():
                        ret["state"]=402
                        ret["msg"]="key error. Please add key "+key+" in "+section+" section."
                        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
                        
        
        if isSPIIDER():#write FE config
            configRootDict = readConfig(_deviceConfigPath)._sections
            path = configRootDict['environment']['home_dir']
            shutil.rmtree(path+"/configs/")
            os.mkdir(path+"/configs/")
            for i in range(_maxSegRule):
                section = "segmentation_"+str(i+1)
                if data[section]["fe_json"]!="" and  data[section]["extraction_project"]!="" :
                    timeStr = datetime.fromtimestamp(time.time()).strftime("%y%m%d_%H%M%S")
                    files = open(path+"/configs/project_"+str(data[section]["extraction_project"])+"_feature_engineering_info_"+timeStr+".json","w")
                    files.write(data[section]["fe_json"])
                    files.close()
                    
            
        # relace old setting
        replaceConfig(_workConfigPath,data)
        
        #future work
        #add download project id
        
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    
def _API_heartbeat(method,path,data=""):
    global _deviceConfigPath
    global _localDataPath
    global _localDataPath_T
    global _hostname
    #print(method)
    if(method=="GET"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=dict()
        ret["data"]['environment']=dict()
        ret["data"]['environment']['spiider']=isSPIIDER()
        ret["data"]['environment']['server_connect']='0'
        
        
        ret["data"]['environment']['timestamp']=time.time()
        
        if isSPIIDER():
            configDict = readConfig(_deviceConfigPath)._sections
            working = False
            connection = False
            if configDict['environment']['work_task_state']=="1":
                working=True
            if configDict['environment']['server_connect']=="1":
                connection=True
            if not working and connection:
                ret["data"]['environment']['server_connect']='1'
            if     working and connection:
                ret["data"]['environment']['server_connect']='2'
            if not working and not connection:
                ret["data"]['environment']['server_connect']='3'
            if     working and not connection:
                ret["data"]['environment']['server_connect']='4'
                
            _,_,files = next(os.walk(_localDataPath))
            _,_,files_T = next(os.walk(_localDataPath_T))
            ret["data"]['environment']['localCount']=str(len(files)+len(files_T))
            ret["data"]['environment']['hostname']=_hostname
            ret["data"]['environment']['upload_queue']=max(int(configDict['environment']['upload_queue']),0)
            ret["data"]['environment']['time_status']=configDict['environment']['time_status']
            ret["data"]['environment']['time_api']=configDict['environment']['time_api']
            ret["data"]['environment']['time_ftp']=configDict['environment']['time_ftp']
            ret["data"]['environment']['time_mqtt']=configDict['environment']['time_mqtt']
            ret["data"]['environment']['st1_err_msg']=configDict['environment']['st1_err_msg']
            ret["data"]['environment']['st2_err_msg']=configDict['environment']['st2_err_msg']
            ret["data"]['environment']['version']=configDict['environment']['version']
        else:
            ret["data"]['environment']['localCount']="0"
            ret["data"]['environment']['upload_queue']="0"
            ret["data"]['environment']['hostname']="not_SPIIDER"
            ret["data"]['environment']['server_connect']='5'
            ret["data"]['environment']['time_status']="--"
            ret["data"]['environment']['time_api']="--"
            ret["data"]['environment']['time_ftp']="--"
            ret["data"]['environment']['time_mqtt']="--"
            ret["data"]['environment']['st1_err_msg']="--"
            ret["data"]['environment']['st2_err_msg']="--"
            
        
        if("all" not in data.keys()):
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")

        wlanIP = "--"
        macID = "--"
        eth0IP = "--"
        eth0MAC = "--"
        eth1IP = "--"
        eth1MAC = "--"
        
        if os.path.isfile('/sys/class/net/wlan0/address'):
            macF = open('/sys/class/net/wlan0/address','r')
            macID = macF.read()
            macID = macID.replace("\n","")
            process = Popen(['ip', 'address'], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            IPcmd = str(stdout,"utf-8").split("wlan0")
            
            if len(IPcmd)>=3 and "inet" in IPcmd[1]:
                wlanIP=IPcmd[1].split("inet ")[-1]
                wlanIP=wlanIP.split(" ")[0]
        
        if os.path.isfile('/sys/class/net/eth0/address'):
            macF = open('/sys/class/net/eth0/address','r')
            eth0MAC = macF.read()
            eth0MAC = eth0MAC.replace("\n","")
            process = Popen(['ip', 'address'], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            IPcmd = str(stdout,"utf-8").split("eth0")
            
            if len(IPcmd)>=3 and "inet" in IPcmd[1]:
                eth0IP=IPcmd[1].split("inet ")[-1]
                eth0IP=eth0IP.split(" ")[0]
        
        if os.path.isfile('/sys/class/net/eth1/address'):
            macF = open('/sys/class/net/eth1/address','r')
            eth1MAC = macF.read()
            eth1MAC = eth1MAC.replace("\n","")
            process = Popen(['ip', 'address'], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            IPcmd = str(stdout,"utf-8").split("eth1")
            
            if len(IPcmd)>=3 and "inet" in IPcmd[1]:
                eth1IP=IPcmd[1].split("inet ")[-1]
                eth1IP=eth1IP.split(" ")[0]
        
                
                
        ret["data"]['environment']['wlanMac']=macID
        ret["data"]['environment']['wlanIp']=wlanIP
        ret["data"]['environment']['eth0Mac']=eth0MAC
        ret["data"]['environment']['eth0Ip']=eth0IP
        ret["data"]['environment']['eth1Mac']=eth1MAC
        ret["data"]['environment']['eth1Ip']=eth1IP
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    
def _API_workFile(method,path,data=""):
    global _workConfigPath
    
    #print(method)
    if(method=="GET"):
        f = open(_workConfigPath, 'r')
        data = f.read()
        f.close()
        return False,bytes(data, "utf8")
    elif(method=="POST"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        buf = io.StringIO(data.decode("utf-8"))
        config = configparser.ConfigParser()
        config.read_file(buf)
        configDict = config._sections
        
        """
        # use defualt data to check body json data
        defConfigDict = readConfig(_defaultWorkConfigPath)._sections
        for section in defConfigDict.keys():
            if section not in configDict.keys():
                ret["state"]=401
                ret["msg"]="section error."
                return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            else:
                for key in defConfigDict[section].keys():
                    if key not in configDict[section].keys():
                        ret["state"]=402
                        ret["msg"]="key error."
                        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        """
        
        configRootDict = readConfig(_deviceConfigPath)._sections
        path = configRootDict['environment']['home_dir']
        shutil.rmtree(path+"/configs/")
        os.mkdir(path+"/configs/")
        for i in range(_maxSegRule):
            section = "segmentation_"+str(i+1)
            if section not in configDict.keys():
                continue
            if configDict[section]["fe_json"]!="" and  configDict[section]["extraction_project"]!="" :
                timeStr = datetime.fromtimestamp(time.time()).strftime("%y%m%d_%H%M%S")
                files = open(path+"/configs/project_"+str(configDict[section]["extraction_project"])+"_feature_engineering_info_"+timeStr+".json","w")
                files.write(configDict[section]["fe_json"])
                files.close()
        
        replaceConfig(_workConfigPath,configDict)
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
def _API_systemConfigFile(method,path,data=""):
    global _systemConfigPath
    
    #print(method)
    if(method=="GET"):
        buf = io.StringIO()
        defConfig = readConfig(_systemConfigPath)
        defConfigDict = defConfig._sections
        del defConfigDict['pin']
        del defConfigDict['ap']
        del defConfigDict['work']
        del defConfigDict['sensor_test']
        del defConfigDict['seg_test']
        
        defConfig.write(buf)
        data = buf.getvalue()
        
        
        #f = open(_systemConfigPath, 'r')
        #data = f.read()
        #f.close()
        return False,bytes(data, "utf8")
    elif(method=="POST"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        buf = io.StringIO(data.decode("utf-8"))
        config = configparser.ConfigParser()
        config.read_file(buf)
        configDict = config._sections
        
        # use defualt data to check body json data
        """
        defConfigDict = readConfig(_defaultSystemConfigPath)._sections
        
        del defConfigDict['pin']
        del defConfigDict['ap']
        del defConfigDict['work']
        del defConfigDict['sensor_test']
        del defConfigDict['seg_test']
        for section in defConfigDict.keys():
            if section not in configDict.keys():
                ret["state"]=401
                ret["msg"]="section error."
                return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            else:
                for key in defConfigDict[section].keys():
                    if key not in configDict[section].keys():
                        ret["state"]=402
                        ret["msg"]="key error."
                        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        """
        if 'pin' in configDict.keys():
            del configDict['pin']
        if 'ap' in configDict.keys():
            del configDict['ap']
        if 'work' in configDict.keys():
            del configDict['work']
        if 'sensor_test' in configDict.keys():
            del configDict['sensor_test']
        if 'seg_test' in configDict.keys():
            del configDict['seg_test']
        replaceConfig(_systemConfigPath,configDict)
        
        eth0ip = "--"
        eth0gw = "--"
        eth0fresh = "1"
        eth1ip = "--"
        eth1gw = "--"
        eth1fresh = "1"
        wlan0ip = "--"
        wlan0gw = "--"
        wlan0fresh = "1"
        
        if configDict["lan"]["ip"]!="..." and configDict["lan"]["mask"]!="..." and configDict["lan"]["getway"]!="...":
            eth0ip = configDict["lan"]["ip"]+"/"+getMask(configDict["lan"]["mask"])
            eth0gw = configDict["lan"]["getway"]
        if configDict["lan2"]["ip"]!="..." and configDict["lan2"]["mask"]!="..." and configDict["lan2"]["getway"]!="...":
            eth1ip = configDict["lan2"]["ip"]+"/"+getMask(configDict["lan2"]["mask"])
            eth1gw = configDict["lan2"]["getway"]
        if configDict["wifi"]["ip"]!="..." and configDict["wifi"]["mask"]!="..." and configDict["wifi"]["getway"]!="...":
            wlan0ip = configDict["wifi"]["ip"]+"/"+getMask(configDict["wifi"]["mask"])
            wlan0gw = configDict["wifi"]["getway"]
        
        print(" ".join([
                "sudo" ,
                _ipSettingPath ,
                eth0ip,
                eth0gw,
                eth0fresh,
                eth1ip,
                eth1gw,
                eth1fresh,
                wlan0ip,
                wlan0gw,
                wlan0fresh
                ]))
        popen_retry([
            "sudo" ,
            _ipSettingPath ,
            eth0ip,
            eth0gw,
            eth0fresh,
            eth1ip,
            eth1gw,
            eth1fresh,
            wlan0ip,
            wlan0gw,
            wlan0fresh
            ],10,3)
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
def _API_wifiControl(method,path,data={}):
    global _systemConfigPath
    if(method=="GET"):
        
        #future work
        # f = open("testConfig/wifiSimulat.json", 'r')
        # data = f.read()
        # data = json.loads(data)
        # f.close()
        
        if os.path.isfile(_staSearchPathPy):
            wifiOut = popen_retry(["python3",_staSearchPathPy],10,1,'{"wifi":[]}')
        else:
            wifiOut = popen_retry([_staSearchPath],10,1,'{"wifi":[]}')
        wifiOut = json.loads(wifiOut)
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=wifiOut
        
        
        
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    elif(method=="PUT"):
        data = json.loads(data)
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        if "wifi" in data.keys():
            if "ssid" in data["wifi"].keys() and "passwd" in data["wifi"].keys() :
                replaceConfig(_systemConfigPath,data)
                #future work
                
            else:
                ret["state"]=402
                ret["msg"]="item error."
                return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        else:
            ret["state"]=401
            ret["msg"]="section error."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            
        
        if "wifi" in data.keys():
            if data["wifi"]["passwd"]!="":
                popen_retry([ _staSettingPath ,data["wifi"]["ssid"] , data["wifi"]["passwd"]],15,3)
            else:
                popen_retry([ _staSettingPath ,data["wifi"]["ssid"] ],15,3)
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    elif(method=="DELETE"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        data=dict()
        data['wifi']=dict()
        data['wifi']["ssid"]=""
        data['wifi']["passwd"]=""
        
        replaceConfig(_systemConfigPath,data)
        #future work
        
        #print(json.dumps(ret, separators=(',', ':')))
        popen_retry([ _staDisconnectPath],15,3)
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    

def _API_sensorlist(method,path,data={}):
    #print(method)
    if(method=="GET"):
        if checkWorkEnable():
            ret = dict()
            ret["state"]=501
            ret["msg"]="Work already enable."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        #future work
        #f = open("testConfig/busSimulat.json", 'r')
        #data = f.read()
        #data = json.loads(data)
        #f.close()
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=HWmappping()
            
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
_API_sensorTest_num = 1
_API_sensorTest_n = 0
_API_sensorTest_m = 1
def _API_sensorTest(method,path,data={}):
    global _deviceConfigPath
    global _systemConfigPath
    global _API_sensorTest_num
    global _API_sensorTest_n
    global _API_sensorTest_m
    global simulatorP
    #print(method)
    if(method=="GET"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=dict()
        ret["data"]['environment']=dict()
        ret["data"]['var']=dict()
        
        if isSPIIDER():
            ret["data"]['var']['num']=_API_sensorTest_num
            ret["data"]['var']['n']=_API_sensorTest_n
            ret["data"]['var']['m']=_API_sensorTest_m
            configDict = readConfig(_deviceConfigPath)._sections
            ret["data"]['environment']['sensor_test_state']=configDict['environment']['sensor_test_state']
            ret["data"]['environment']['sensor_test_output']=configDict['environment']['sensor_test_output']
            ret["data"]['environment']['upload_ftp_seg_csv']=configDict['environment']['upload_ftp_seg_csv']
            ret["data"]['environment']['upload_ftp_fe_csv']=configDict['environment']['upload_ftp_fe_csv']
            ret["data"]['environment']['upload_ftp_seg_pkl']=configDict['environment']['upload_ftp_seg_pkl']
            ret["data"]['environment']['upload_ftp_fe_pkl']=configDict['environment']['upload_ftp_fe_pkl']
            ret["data"]['environment']['upload_api_seg']=configDict['environment']['upload_api_seg']
            ret["data"]['environment']['upload_api_fe']=configDict['environment']['upload_api_fe']
            ret["data"]['environment']['upload_mqtt']=configDict['environment']['upload_mqtt']
            if(_API_sensorTest_num=="5"): #upload
                #_,_,files = next(os.walk(_localDataPath))
                _,_,files_T = next(os.walk(_localDataPath_T))
                ret["data"]['var']['n'] = str(len(files_T)+max(int(configDict['environment']['upload_queue']),0))
        else:
            ret["data"]['var']['num']=simulatorP.sensorTest_num()
            ret["data"]['var']['n']=simulatorP.sensorTest_n()
            ret["data"]['var']['m']=simulatorP.sensorTest_m()
            ret["data"]['environment']['sensor_test_state']=simulatorP.workCheck()
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
    elif(method=="PUT"):
        data = json.loads(data)
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        if "sensor_test" in data.keys():
            if isSPIIDER():
                if "enable" in data["sensor_test"].keys() and "maxsec" in data["sensor_test"].keys() :
                    if checkWorkEnable():
                        ret = dict()
                        ret["state"]=501
                        ret["msg"]="Work already enable."
                        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
                    replaceConfig(_systemConfigPath,data)
                    #reset test status
                    resetDict = dict()
                    resetDict['environment'] = dict()
                    resetDict['environment']['sensor_test_state']="0"
                    replaceConfig(_deviceConfigPath,resetDict)
                    _API_sensorTest_num = 1
                    _API_sensorTest_n = 0
                    _API_sensorTest_m = 1
                else:
                    ret["state"]=402
                    ret["msg"]="item error."
                    return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            else:
                if "enable" in data["sensor_test"].keys():
                    if simulatorP.workCheck() !="0":
                        ret = dict()
                        ret["state"]=501
                        ret["msg"]="Test already enable."
                        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
                    if data["sensor_test"]["enable"]=="1":
                        _API_sensorTest_num = 1
                        _API_sensorTest_n = 0
                        _API_sensorTest_m = 1
                        simulatorP.setConfig(readConfig(_workConfigPath)._sections)
                        simulatorP.startTransfer()
                    return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
                else:
                    ret["state"]=402
                    ret["msg"]="item error."
                    return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
                
        elif "num" in data.keys() and "n" in data.keys() and "m" in data.keys() :
            _API_sensorTest_num = data["num"]
            _API_sensorTest_n = data["n"]
            _API_sensorTest_m = data["m"]
        else:
            ret["state"]=401
            ret["msg"]="section error."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    
def _API_segTest(method,path,data={}):
    global _deviceConfigPath
    global _systemConfigPath
    #print(method)
    if(method=="GET"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=dict()
        ret["data"]['environment']=dict()
        
        configDict = readConfig(_deviceConfigPath)._sections
        ret["data"]['environment']['seg_test_state']=configDict['environment']['seg_test_state']
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
    elif(method=="PUT"):
        data = json.loads(data)
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        if "seg_test" in data.keys():
            if "enable" in data["seg_test"].keys() :
                #print(data)
                replaceConfig(_systemConfigPath,data)
            else:
                ret["state"]=402
                ret["msg"]="item error."
                return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        else:
            ret["state"]=401
            ret["msg"]="section error."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    
def _API_workEnable(method,path,data={}):
    global _systemConfigPath
    
    #print(method)
    if(method=="GET"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=dict()
        ret["data"]['environment']=dict()
        ret["data"]['environment']['work_task_state']='0'
        if checkWorkEnable():
            ret["data"]['environment']['work_task_state']='1'
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    elif(method=="PUT"):
        data = json.loads(data)
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        if "work" in data.keys():
            if "enable" in data['work'].keys():
                if data['work']['enable']=="0" or data['work']['enable']=="1":
                    replaceConfig(_systemConfigPath,data)
                else:
                    ret["state"]=403
                    ret["msg"]="value error. That can use string '0' or '1'."
            else:
                ret["state"]=402
                ret["msg"]="key error. Please add enable key."
        else:
            ret["state"]=401
            ret["msg"]="Not 'work' section in requite body."
           
        # relace old setting
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")

def _API_pin(method,path,data=""):
    global _systemConfigPath
    global _hostname
    
    #print(method)
    if(method=="POST"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        configDict = readConfig(_systemConfigPath)._sections
        
        data = json.loads(data)
        #print(data)
        if configDict["pin"]["pwd"]!=data["pin"]["pwd"]:
                ret["state"]=501
                ret["msg"]="password wrror."
                return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        
        #print(json.dumps(ret, separators=(',', ':')))
        process = Popen(['hostname'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        ret["hostname"]=_hostname
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")


def _API_systemOTA(method,path,data=b'',md5=""):
    global _deviceConfigPath
    global _OTAPath
    
    #print(method)
    if(method=="POST"):
        m = hashlib.md5()
        print(type(data))
        _md5 = hashlib.md5(data).hexdigest()
        if _md5 != md5:
            ret = dict()
            ret["state"]=501
            ret["msg"]="File error"
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        data_b = base64.decodebytes(data)
        with open(_OTAPath, 'wb') as f:
            f.write(data_b)
            
        #reset device
        if os.path.isfile(_OTAprogramPy):
            os.popen("("+_OTAprogramCMDPy+")&")
        else:
            os.popen("("+_OTAprogramCMD+")&")
        
        replaceConfig(_deviceConfigPath,{"environment":{"ota_status":"1"}})
        replaceConfig(_deviceConfigPath,{"environment":{"ota_msg":"--"}})
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    elif(method=="PUT"):
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=dict()
        replaceConfig(_deviceConfigPath,{"environment":{"ota_status":"0"}})
        replaceConfig(_deviceConfigPath,{"environment":{"ota_msg":"--"}})
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    elif(method=="GET"):
        configDict = readConfig(_deviceConfigPath)._sections
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=dict()
        ret["data"]["code"] = configDict["environment"]["ota_status"];
        ret["data"]["msg"] = configDict["environment"]["ota_msg"];
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")


def _API_systemClear(method,path,data=""):
    global _localDataPath
    global _localDataPath_T
    if(method=="GET"):
        _,_,files = next(os.walk(_localDataPath))
        _,_,files_T = next(os.walk(_localDataPath_T))
        for f in files:
            print("remove",os.path.join(_localDataPath,f))
            os.remove(os.path.join(_localDataPath,f))
        for f in files_T:
            print("remove",os.path.join(_localDataPath_T,f))
            os.remove(os.path.join(_localDataPath_T,f))
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")


def _API_systemClearMem(method,path,data=""):
    global _deviceConfigPath
    if(method=="GET"):
        replaceConfig(_deviceConfigPath,{"environment":{"upload_queue":"-1"}})
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")

def _API_systemReboot(method,path,data=""):
    global _deviceConfigPath
    if(method=="PUT"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        os.popen("(sleep 5 ; sudo reboot -nf )&")
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
def _API_featureExtraction(method,path,data=""):
    #print(method)
    if(method=="GET"):
        #future work
        f = open("testConfig/FEProjectSimulat.json", 'r')
        data = f.read()
        data = json.loads(data)
        f.close()
        
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        ret["data"]=data
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
    

def _API_read(method,path,data={}):
    global _deviceConfigPath
    global _systemConfigPath
    global _workConfigPath
    
    #print(method)
    if(method=="GET"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        # t = target file path
        #    value {"d" / "s" / "w"} is { "device" / "system" / "work" }
        # s = config section
        # i = config item of section
        # v = config value of item
        
        if("t" not in data.keys()):
            ret["state"]=501
            ret["msg"]="parameter key wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            
        if data["t"]=="d":
            path = _deviceConfigPath
        elif data["t"]=="s":
            path = _systemConfigPath
        elif data["t"]=="w":
            path = _workConfigPath
        else:
            ret["state"]=502
            ret["msg"]="parameter target path wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            
        configDict = readConfig(path)._sections
        
        if("s" not in data.keys()
            or "i" not in data.keys()):
            ret["data"]=configDict
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        
        if data["s"] not in configDict.keys():
            ret["state"]=503
            ret["msg"]="parameter section wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        if data["i"] not in configDict[data["s"]].keys():
            ret["state"]=504
            ret["msg"]="parameter item wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        ret["data"]=configDict[data["s"]][data["i"]]
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")


def _API_write(method,path,data={}):
    global _deviceConfigPath
    global _systemConfigPath
    global _workConfigPath
    
    #print(method)
    if(method=="GET"):
        ret = dict()
        ret["state"]=200
        ret["msg"]="susessful"
        
        # t = target file path
        #    value {"d" / "s" / "w"} is { "device" / "system" / "work" }
        # s = config section
        # i = config item of section
        # v = config value of item
        
        if("t" not in data.keys()
            or "s" not in data.keys()
            or "i" not in data.keys()
            or "v" not in data.keys()):
            ret["state"]=501
            ret["msg"]="parameter key wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            
        if data["t"]=="d":
            path = _deviceConfigPath
        elif data["t"]=="s":
            path = _systemConfigPath
        elif data["t"]=="w":
            path = _workConfigPath
        else:
            ret["state"]=502
            ret["msg"]="parameter target path wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
            
        config = readConfig(path)
        configDict = config._sections
        
        if data["s"] not in configDict.keys():
            ret["state"]=503
            ret["msg"]="parameter section wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        if data["i"] not in configDict[data["s"]].keys():
            ret["state"]=504
            ret["msg"]="parameter item wrror."
            return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
        configDict[data["s"]][data["i"]]=data["v"]
        
        with open(path+"_ub", 'w') as configfile:
            config.write(configfile)
        popen_retry(["cp",path+"_ub",path],10,1)
        
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")
        
    else:
        ret = dict()
        ret["state"]=500
        ret["msg"]="method error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        return True,bytes(json.dumps(ret, separators=(',', ':')), "utf8")


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def setup(self):
        http.server.SimpleHTTPRequestHandler.setup(self)
        self.request.settimeout(10)
        
    def address_string(self):
        return self.client_address[0]
    
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Cache-Control", "immutable")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    def _set_headersJson(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    def _set_headersFile(self):
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        
    def _404_page(self):
        self.path = '404error.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
    def do_GET(self):
        print("do_GET",self.path,time.time())
        global mapPath
        global apiFunction
        global _defaultServerPath
        parameters = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
         
        self.path = self.path.split("?")[0]
        if(self.path.find(".js")!=-1 or 
           self.path.find(".css")!=-1 or 
           self.path.find(".png")!=-1 or 
           self.path.find(".svg")!=-1):
            #self.path = _defaultServerPath+self.path
            print(self.path)
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        elif(self.path in mapPath.keys() ):
            self.path = mapPath[self.path]
            print(self.path)
            #print("End time",time.time())
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif(self.path in apiFunction.keys() ):
            useJSON,data=apiFunction[self.path]("GET",self.path,parameters)
            if useJSON:
                self._set_headersJson()
            else:
                self._set_headersFile()
            self.wfile.write(data)
            #print("End time",time.time())
        else:
            self._404_page()
            #print("End time",time.time())
    def do_POST(self):
        print("do_POST",self.path,time.time())
        if(self.path in apiFunction.keys() ):
            jsonDateLen = int(self.headers['Content-Length'])
            if jsonDateLen>0:
                jsonData = self.rfile.read(jsonDateLen)
                if "md5" in self.headers.keys():
                    useJSON,data=apiFunction[self.path]("POST",self.path,jsonData,self.headers['md5'])
                else:
                    useJSON,data=apiFunction[self.path]("POST",self.path,jsonData)
            else:
                useJSON,data=apiFunction[self.path]("POST",self.path)
                
            if useJSON:
                self._set_headersJson()
            else:
                self._set_headersFile()
            self.wfile.write(data)
            #print("End time",time.time())
            return
        elif  self.path.find('/api') == -1:
            #print("End time",time.time())
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        ret = dict()
        ret["state"]=400
        ret["msg"]="API path error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        #print("End time",time.time())
        return bytes(json.dumps(ret, separators=(',', ':')), "utf8")

    def do_PUT(self):
        print("do_PUT",self.path,time.time())
        if(self.path in apiFunction.keys() ):
            jsonDateLen = int(self.headers['Content-Length'])
            if jsonDateLen>0:
                jsonData = self.rfile.read(jsonDateLen)
                useJSON,data=apiFunction[self.path]("PUT",self.path,jsonData)
            else:
                useJSON,data=apiFunction[self.path]("PUT",self.path)
                
            if useJSON:
                self._set_headersJson()
            else:
                self._set_headersFile()
            self.wfile.write(data)
            #print("End time",time.time())
            return
        elif  self.path.find('/api') == -1:
            #print("End time",time.time())
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        ret = dict()
        ret["state"]=400
        ret["msg"]="API path error"
        
        print(json.dumps(ret, separators=(',', ':')))
        #print("End time",time.time())
        return bytes(json.dumps(ret, separators=(',', ':')), "utf8")

    def do_DELETE(self):
        print("do_DELETE",self.path,time.time())
        if(self.path in apiFunction.keys() ):
            useJSON,data=apiFunction[self.path]("DELETE",self.path)
                
            if useJSON:
                self._set_headersJson()
            else:
                self._set_headersFile()
            self.wfile.write(data)
            print("End time",time.time())
            return
        elif  self.path.find('/api') == -1:
            print("End time",time.time())
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        ret = dict()
        ret["state"]=400
        ret["msg"]="API path error"
        
        #print(json.dumps(ret, separators=(',', ':')))
        #print("End time",time.time())
        return bytes(json.dumps(ret, separators=(',', ':')), "utf8")
# Create an object of the above class
        

class simulator(multiprocessing.Process):
    def __init__(self,inputPath,outputPath):
        global _maxSegRule
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        
        
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.states=manager.dict()
        self.states["start"]=False
        self.states["work"]=False
        self.states["sensorTest_num"]=""
        self.states["sensorTest_n"]=""
        self.states["sensorTest_m"]=""
        self.states["config"]=""
        
        self.inputPath = inputPath
        self.outputPath = outputPath
        
        self.cpu_count = multiprocessing.cpu_count()
        self.maxSegRule = _maxSegRule
                
        
    def sensorTest_num(self):
        return self.states["sensorTest_num"]
        
    def sensorTest_n(self):
        return self.states["sensorTest_n"]
        
    def sensorTest_m(self):
        return self.states["sensorTest_m"]
        
    def workCheck(self):
        if self.states["work"]:
            return "1"
        else:
            return "0"
        
    def startTransfer(self):
        self.states["start"]=True
        
    def setConfig(self,config):
        self.states["config"]=config
        
    def multiProc(self,targetP,maxProc,filePath,config,fileType):
        total = len(filePath)
        finish = [False for i in range(total)]
        doProcess = [False for i in range(total)]
        process = [None for i in range(total)]
        self.states["sensorTest_m"]=str(total)
        self.states["sensorTest_n"]=str(sum(finish))
        
        while sum(finish)!=total:
            for i,f in enumerate(filePath):
                if doProcess[i]==True:
                    if not process[i].is_alive():
                        process[i].release()
                        finish[i]=True
                        doProcess[i]=False
                        self.states["sensorTest_n"]=str(sum(finish))
                elif sum(doProcess)<maxProc and finish[i]==False:
                    p = f.replace(".","_")
                    p = p[len(self.inputPath):]
                    p = self.outputPath+"\\"+p
                    process[i] = targetP(config,fileType[i],f,p)
                    process[i].start()
                    doProcess[i]=True
                    
            time.sleep(0.1)
            
    def run(self):
        print("simulator class run")
        
        while True:
            while not self.states["start"]:
                time.sleep(0.2)
            self.states["work"] = True
            
            
            
            fileType = []
            filePath = []
            for root, dirs, files in os.walk(self.inputPath):
                for f in files:
                    fullpath = os.path.join(root, f)
                    if f.split(".")[-1].lower()=="csv":
                        fileType.append("csv")
                    elif f.split(".")[-1].lower()=="pkl":
                        fileType.append("pkl")
                    else:
                        continue
                    filePath.append(fullpath)
                    d = root[len(self.inputPath):].split("\\")
                    for i,p in enumerate(d):
                        #print(self.outputPath+"\\".join(d[:i+1]))
                        if p != "" and not os.path.isdir(self.outputPath+"\\".join(d[:i+1])):
                            os.makedirs(self.outputPath+"\\".join(d[:i+1]))
            #print(csv)
            #print(pkl)
            
            
            seg_count = 0
            for i in range(1,self.maxSegRule+1):
                sectionName = "segmentation_"+str(i)
                ruleType = int(getDictItem(self.states["config"],sectionName,"type","0"))
                ruleName = getDictItem(self.states["config"],sectionName,"name","")
                if ruleType !=0 and ruleName!="":
                    seg_count = seg_count + 1
            
            seg_maxP = self.cpu_count*2
            seg_maxP = int(max(1,seg_maxP/seg_count))
            
            self.states["sensorTest_num"]="6"
            self.multiProc(simulatorSensor,self.cpu_count,filePath,self.states["config"],fileType)
            
            self.states["sensorTest_num"]="7"
            self.multiProc(simulatorSeg,seg_maxP,filePath,self.states["config"],fileType)
                
            self.states["work"] = False
            self.states["start"]=False
            gc.collect()
            


class simulatorSensor(multiprocessing.Process):
    def __init__(self,config,fileType,inputPath,outputPath):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        
        self.config = config
        self.inputPath = inputPath
        self.outputPath = outputPath+"_sensor"
        self.fileType = fileType
        
    def run(self):
        print("simulator sensor class run")
        if os.path.isfile(self.outputPath+".png"):
            return
            
        if self.fileType=="csv":
            data = createDataObjFromCSV(self.inputPath)
        else:
            data = openPKL(self.inputPath)
            
        if data != False:
            data = dataObj2drawList(data)
            process = drawListMuti_proc(self.outputPath,data)
            process.start()
            process.release()
            
    def release(self):
        while self.is_alive():
            time.sleep(1)
        self.exit.set()
        
class simulatorSeg(multiprocessing.Process):
    def __init__(self,config,fileType,inputPath,outputPath):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        
        self.config = config
        self.inputPath = inputPath
        self.outputPath = outputPath+"_seg"
        self.fileType = fileType
        
    def run(self):
        print("simulator seg class run")
        if self.fileType=="csv":
            data = createDataObjFromCSV(self.inputPath)
        else:
            data = openPKL(self.inputPath)
            
        segmentationProc=segmentation(self.config,0.1,True,"2",999999999)
        segmentationProc.start()
        segmentationProc.put(data)
        while not segmentationProc.queue.empty():
            time.sleep(0.1)
        segmentationProc.release()
        while not segmentationProc.reQueue.empty():
            segmentationProc.reQueue.get(False)
            #release momery
        segResult = []
        while not segmentationProc.drawQueue.empty():
            segResult.append(segmentationProc.drawQueue.get(False))
        if len(segResult)>0:
            process = drawListMuti_proc(self.outputPath,segResult)
            process.start()
            process.release()
            
    def release(self):
        while self.is_alive():
            time.sleep(1)
        self.exit.set()
if __name__ == "__main__":
    if isSPIIDER():
        print("Start!")
        updateConfigPath()
    
        mapPath=dict()
        mapPath['']="home.html"
        mapPath['/']="home.html"
        mapPath['/home']="home.html"
        mapPath['/fromFile']="fromFile.html"
        mapPath['/sample']="sample.html"
        mapPath['/system']="system.html"
        mapPath['/login']="login.html"
        mapPath['/status']="status.html"
        mapPath['/network']="network.html"
        mapPath['/wifi']="wifi.html"
        
        apiFunction=dict()
        apiFunction['/api/sensor/config']=_API_sensorConfig
        apiFunction['/api/sensor/list']=_API_sensorlist
        apiFunction['/api/sensor/test']=_API_sensorTest
        apiFunction['/api/segmentation/config']=_API_segConfig
        apiFunction['/api/segmentation/test']=_API_segTest
        apiFunction['/api/work/file']=_API_workFile
        apiFunction['/api/work/state']=_API_workEnable
        apiFunction['/api/system/config']=_API_systemConfig
        apiFunction['/api/system/file']=_API_systemConfigFile
        apiFunction['/api/system/time']=_API_systemTime
        apiFunction['/api/system/ota']=_API_systemOTA
        apiFunction['/api/system/clear/local']=_API_systemClear
        apiFunction['/api/system/clear/mem']=_API_systemClearMem
        apiFunction['/api/system/boot/reboot']=_API_systemReboot
        apiFunction['/api/wifi']=_API_wifiControl
        apiFunction['/api/device/heartbeat']=_API_heartbeat
        apiFunction['/api/server/featureExtraction']=_API_featureExtraction
        apiFunction['/api/pin']=_API_pin
        apiFunction['/api/read']=_API_read
        apiFunction['/api/write']=_API_write
        
        PORT = 80
        
    else:
        multiprocessing.freeze_support()
        print("Please wait to open server.")
        mapPath=dict()
        mapPath['']="sample.html"
        mapPath['/']="sample.html"
        mapPath['/home']="sample.html"
        mapPath['/sample']="sample.html"
        
        apiFunction=dict()
        apiFunction['/api/sensor/config']=_API_sensorConfig
        apiFunction['/api/segmentation/config']=_API_segConfig
        apiFunction['/api/device/heartbeat']=_API_heartbeat
        apiFunction['/api/system/config']=_API_systemConfig
        apiFunction['/api/sensor/test']=_API_sensorTest
        
        PORT = 8081
        if not os.path.isdir(_dataPath):
            os.makedirs(_dataPath)
        if not os.path.isdir(_inputPath):
            os.makedirs(_inputPath)
        if not os.path.isdir(_outputPath):
            os.makedirs(_outputPath)
        simulatorP = simulator(_inputPath,_outputPath)
        simulatorP.start()
        time.sleep(3)
    
    handler_object = MyHttpRequestHandler
    my_server = socketserver.TCPServer(("", PORT), handler_object)
    print("Please brower for http://127.0.0.1:"+str(PORT))
    my_server.serve_forever()
