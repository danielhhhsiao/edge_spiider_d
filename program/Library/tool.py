#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: etao
"""
import sys
def isSPIIDER():
    return sys.platform=="linux"
           
import time
import math
import configparser
import gc
import multiprocessing
from io import BytesIO
from PIL import Image
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.ticker import LinearLocator
import numpy as np
import pickle
import json
import copy
import pandas as pd
import urllib
if isSPIIDER():
    import psutil
    import requests
    
#np.set_printoptions(precision=None,threshold=None,edgeitems=None,suppress=None)

#import matplotlib 
#matplotlib.use("qt4agg")
plt.switch_backend("AGG")
           
def savePKL(data,path):
    with open(path,'wb') as handel:
        pickle.dump(data,handel,protocol=pickle.HIGHEST_PROTOCOL)
        
def openPKL(path):
    ret = {}
    try:
        with open(path,'rb') as handel:
            ret = pickle.load(handel)
    except Exception as e:
        printErr("Error openPKL:",e)
        
    return ret

def saveTXT(data,path):
    files = open(path,"w")
    files.write(data)
    files.close()
    
def openTXT(path):
    ret = ""
    try:
        files = open(path,"r+")
        ret = files.read()
        files.close()
    except Exception as e:
        printErr("Error openTXT:",e)
        
    return ret

def rolling_window(a,window):
    a = np.array(a)
    shape = a.shape[:-1] + (a.shape[-1]-window+1,window)
    strides = a.strides+(a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a,shape=shape,strides=strides)
    
def getRamPercent():
    return psutil.virtual_memory()[3] / psutil.virtual_memory()[0] * 100

def getRamFree():
    return psutil.virtual_memory()[1] / (1024 ** 2)
    
def getRomPercent():
    return psutil.disk_usage('/').percent
    
def getRomFree():
    return psutil.disk_usage('/').free / (1024 ** 2)

def loadConfig(target):
    payload = {'t' : target}
    try:
        d = requests.get('http://127.0.0.1/api/read',params = payload)
        data = json.loads(d.text)
        if data["state"]==200:
            return data["data"]
    except:
        return {}
    return {}
    
def getDictItem(dic,section,item,default):
    if section in dic.keys():
        if item in dic[section].keys():
            return dic[section][item]
    return default

def writeConfig(target,section,item,value):
    payload = {'t' : target, 's' : section, 'i' : item, 'v' : value}
    d = requests.get('http://127.0.0.1/api/write',params = payload)
    data = json.loads(d.text)
    
    if data["state"]==200:
        return True
    return False
    
def getDictFocus(target,section,item,default):
    payload = {'t' : target, 's' : section, 'i' : item}
    d = requests.get('http://127.0.0.1/api/read',params = payload)
    data = json.loads(d.text)
    
    if data["state"]==200:
        return data["data"]
    return default
    
def printErr(*args,**kwargs):
    timeStr = datetime.fromtimestamp(time.time()).strftime("%y/%m/%d %H:%M:%S.%f")
    print("Err["+timeStr+"]",file=sys.stderr)
    print(*args,file=sys.stderr,**kwargs)
    
def stamp2dateArr(data,Dformat):
    ret = map(lambda x:datetime.fromtimestamp(x).strftime(Dformat),data)
    return np.array(list(ret))
    
def str2intArr(data):
    ret = map(lambda x:int(x),data)
    return np.array(list(ret))
    
def str2floatArr(data):
    ret = map(lambda x:float(x),data)
    return np.array(list(ret))
    
    
def dataObj2pd(dataObj):
    #dataframe param
    df_sum = pd.DataFrame()
    df_index_max = 0
    #Time cut
    last_startTime = []
    first_endTime = []
    #Digital filter
    Digital_Flag = 0
    #First dataframe flag
    First_df_flag = 0

    for key in dataObj.keys():
        if (key == "Digital"):
            last_startTime.append(min(dataObj[key]["time"]))
            first_endTime.append(max(dataObj[key]["time"]))
            df_data = pd.DataFrame(data = dataObj[key]["data"])
            df_time = pd.DataFrame(data = dataObj[key]["time"])
            df_time.columns = ['datetime']
            df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
            #First data frame?
            if(First_df_flag==0):
                First_df_flag = 1
                df_sum = df_merge
                df_index_max = df_merge.shape[0]
            else:
                if(df_index_max >= df_merge.shape[0]):
                    df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                else:
                    df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
            df_sum = df_sum.fillna(method='bfill')
            filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
            df_sum = df_sum[filt]

        elif (key == "bus"):    
            for d in dataObj["bus"]:
                if "type" in d.keys() and d["type"]!="NONE":
                    #get data name
                    last_startTime.append(min(d["time"]))
                    first_endTime.append(max(d["time"]))
                    df_data = pd.DataFrame(data = d["data"])
                    df_time = pd.DataFrame(data = d["time"])
                    df_time.columns = ['datetime']
                    df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
                    #First data frame?
                    if(First_df_flag==0):
                        First_df_flag = 1
                        df_sum = df_merge
                        df_index_max = df_merge.shape[0]
                    else:
                        if(df_index_max >= df_merge.shape[0]):
                            df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                        else:
                            df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
                    df_sum = df_sum.fillna(method='bfill')
                    filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
                    df_sum = df_sum[filt]
        
        elif (key == "usb"):    
            for d in dataObj["usb"]:
                if "type" in d.keys() and d["type"]!="NONE":
                    #get data name
                    last_startTime.append(min(d["time"]))
                    first_endTime.append(max(d["time"]))
                    df_data = pd.DataFrame(data = d["data"])
                    df_time = pd.DataFrame(data = d["time"])
                    df_time.columns = ['datetime']
                    df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
                    #First data frame?
                    if(First_df_flag==0):
                        First_df_flag = 1
                        df_sum = df_merge
                        df_index_max = df_merge.shape[0]
                    else:
                        if(df_index_max >= df_merge.shape[0]):
                            df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                        else:
                            df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
                    df_sum = df_sum.fillna(method='bfill')
                    filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
                    df_sum = df_sum[filt]
                    
        elif (key == "distance"):
            last_startTime.append(min(dataObj[key]["time"]))
            first_endTime.append(max(dataObj[key]["time"]))
            df_data = pd.DataFrame(data = dataObj[key]["data"])
            df_time = pd.DataFrame(data = dataObj[key]["time"])
            df_time.columns = ['datetime']
            df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
            #First data frame?
            if(First_df_flag==0):
                First_df_flag = 1
                df_sum = df_merge
                df_index_max = df_merge.shape[0]
            else:
                if(df_index_max >= df_merge.shape[0]):
                    df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                else:
                    df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
            df_sum = df_sum.fillna(method='bfill')
            filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
            df_sum = df_sum[filt]
            
    df_sum['datetime'] = stamp2dateArr(df_sum['datetime'] ,"%Y/%m/%d %H:%M:%S")
    return df_sum

def dataObjTrans_FE(dataObj):
    columns_name = list(dataObj["value"].keys())
    value = []
    val = []
    for key in dataObj["value"].keys():
        value.append(dataObj["value"][key][0])

    df_data = pd.DataFrame(columns = columns_name, data = [value])
    df_data.columns = [columns_name]
    dTime = datetime.strptime(dataObj["time"],"%Y/%m/%d %H:%M:%S")
    timeStr = dTime.strftime("%Y-%m-%d %H:%M:%S")
    df_data.insert(0,'datetime',timeStr)
    return df_data
        
def transFormatUpload(dataObj,work_ini,name,Type):
    type_std = ['seg','FE','mqtt']
    #payload element
    API_id = name.split('@',2)
    tool_id = API_id[0]
    chamber_id = API_id[1]+API_id[2]
    sampleRate = 0
    data_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #dataframe param
    df_sum = pd.DataFrame()
    df_index_max = 0
    #Time cut
    last_startTime = []
    first_endTime = []
    #Digital filter
    Digital_Flag = 0
    #First dataframe flag
    First_df_flag = 0
    if(Type == type_std[0]):
        for key in dataObj.keys():
            if (key == "Digital"):
                last_startTime.append(min(dataObj[key]["time"]))
                first_endTime.append(max(dataObj[key]["time"]))
                df_data = pd.DataFrame(data = dataObj[key]["data"])
                df_time = pd.DataFrame(data = dataObj[key]["time"])
                df_time.columns = ['datetime']
                df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
                #First data frame?
                if(First_df_flag==0):
                    First_df_flag = 1
                    df_sum = df_merge
                    df_index_max = df_merge.shape[0]
                else:
                    if(df_index_max >= df_merge.shape[0]):
                        df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                    else:
                        df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
                df_sum = df_sum.fillna(method='bfill')
                filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
                df_sum = df_sum[filt]

            elif (key == "bus"):    
                for d in dataObj["bus"]:
                    if "type" in d.keys() and d["type"]!="NONE":
                        #get data name
                        last_startTime.append(min(d["time"]))
                        first_endTime.append(max(d["time"]))
                        df_data = pd.DataFrame(data = d["data"])
                        df_time = pd.DataFrame(data = d["time"])
                        df_time.columns = ['datetime']
                        df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
                        #First data frame?
                        if(First_df_flag==0):
                            First_df_flag = 1
                            df_sum = df_merge
                            df_index_max = df_merge.shape[0]
                        else:
                            if(df_index_max >= df_merge.shape[0]):
                                df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                            else:
                                df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
                        df_sum = df_sum.fillna(method='bfill')
                        filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
                        df_sum = df_sum[filt]
            
            elif (key == "usb"):    
                for d in dataObj["usb"]:
                    if "type" in d.keys() and d["type"]!="NONE":
                        #get data name
                        last_startTime.append(min(d["time"]))
                        first_endTime.append(max(d["time"]))
                        df_data = pd.DataFrame(data = d["data"])
                        df_time = pd.DataFrame(data = d["time"])
                        df_time.columns = ['datetime']
                        df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
                        #First data frame?
                        if(First_df_flag==0):
                            First_df_flag = 1
                            df_sum = df_merge
                            df_index_max = df_merge.shape[0]
                        else:
                            if(df_index_max >= df_merge.shape[0]):
                                df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                            else:
                                df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
                        df_sum = df_sum.fillna(method='bfill')
                        filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
                        df_sum = df_sum[filt]
                        
            elif (key == "distance"):
                last_startTime.append(min(dataObj[key]["time"]))
                first_endTime.append(max(dataObj[key]["time"]))
                df_data = pd.DataFrame(data = dataObj[key]["data"])
                df_time = pd.DataFrame(data = dataObj[key]["time"])
                df_time.columns = ['datetime']
                df_merge = pd.merge(df_time,df_data,how='inner',left_index=True,right_index=True)
                #First data frame?
                if(First_df_flag==0):
                    First_df_flag = 1
                    df_sum = df_merge
                    df_index_max = df_merge.shape[0]
                else:
                    if(df_index_max >= df_merge.shape[0]):
                        df_sum = pd.merge_asof(df_sum,df_merge,on='datetime')
                    else:
                        df_sum = pd.merge_asof(df_merge,df_sum,on='datetime')
                df_sum = df_sum.fillna(method='bfill')
                filt = ((df_sum['datetime']>=max(last_startTime)) & (df_sum['datetime']<=min(first_endTime)))
                df_sum = df_sum[filt]
                
        if (max(df_sum['datetime'])-min(df_sum['datetime']))!=0:
            sampleRate = round(len(df_sum)/(max(df_sum['datetime'])-min(df_sum['datetime'])))
        else:
            sampleRate = 0
        df_sum['datetime'] = stamp2dateArr(df_sum['datetime'] ,"%Y-%m-%d %H:%M:%S")
        print(sampleRate)
        #df_sum = df_sum.drop(columns=['Time'])
        val = df_sum.values.tolist()
        upload_dict = {"tool_list":[{"tool_id":tool_id,"chamber":chamber_id,"data_time":data_time,\
                                     "data":{"column_names":list(df_sum.columns.values),"value":val}}]}
        print("Trans Seg upload data success.")
        
        #Filename - Toolid@chanber@0@Ymd_HMS
        sampling_time = datetime.fromtimestamp(max(last_startTime))
        timeStr = sampling_time.strftime("%Y%m%d_%H%M%S")
        filenameSeg = "@".join([tool_id, chamber_id, '0', timeStr]) + '_' + str(sampleRate) + '_01'
        return upload_dict,max(last_startTime),filenameSeg
    #FE
    elif Type == type_std[1]:
        try:
            for key in work_ini.keys():
                ruleName = "@".join([
                    getDictItem(work_ini,key,"name",""),
                    getDictItem(work_ini,key,"unit",""),
                    getDictItem(work_ini,key,"sub_unit","")
                    ])
                if name == ruleName:
                    project_id = int(getDictItem(work_ini,key,"extraction_project","0"))
            columns_name = list(dataObj["value"].keys())
            value = []
            for key in dataObj["value"].keys():
                value.append(dataObj["value"][key][0])
                
            upload_datetime = datetime.strptime(dataObj["time"],"%Y/%m/%d %H:%M:%S")
            upload_datetime = upload_datetime.strftime("%Y-%m-%d %H:%M:%S")
            upload_dict = {"tool_list":[{"project_id":project_id,"tool_id":tool_id,"chamber":chamber_id,"data_time":data_time,\
                                         "data":{"datetime":[upload_datetime],"column_names":columns_name,"value":[value]}}]}
            print("Trans FE upload data success.")
            
            #Filename - Toolid@chanber@project_id@Ymd_HMS
            sampling_time = datetime.strptime(dataObj["time"],"%Y/%m/%d %H:%M:%S")
            timeStr = sampling_time.strftime("%Y%m%d_%H%M%S")
            diffTime = round(time.time() - sampling_time.timestamp())
            filenameSeg = "@".join([tool_id, chamber_id, str(project_id), timeStr]) + "_" + str(diffTime)
            #filenameSeg = "@".join([tool_id, chamber_id, str(project_id), timeStr])
            
            return upload_dict,dataObj["time"],filenameSeg
        except Exception as e:
            print(e)
            return "","",""
            
    else:
        return "","",""
    

def ledStatusUpload(n,s,m):
    if not isSPIIDER(): 
        return
    payload = {'n' : n, 's' : s, 'm' : m}
    payload_quote = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)
    d = requests.get('http://127.0.0.1:81',params = payload_quote)
    
def testStatusUpload(num,n="",m=""):
    payload = json.dumps({'num' : num, 'n' : n, 'm' : m})
    d = requests.put('http://127.0.0.1/api/sensor/test',data = payload)
    
def alineObj(dataObj,limitTime=99999999):
    dataObj=copy.deepcopy(dataObj)
    startTime = 0
    #find time
    for sensor in dataObj.keys():
        if sensor=="bus" or  sensor=="usb":
            for d in dataObj[sensor]:
                if "type" in d.keys() and d["type"]!="NONE":
                    startTime = max(startTime,d["time"][0])
        else:
            startTime = max(startTime,dataObj[sensor]["time"][0])
            
    #not do anything
    if startTime==0: 
        return dataObj
        
    endTime = startTime+limitTime
    #cut signal at start / end
    for sensor in dataObj.keys():
        if sensor=="bus" or  sensor=="usb":
            for d in dataObj[sensor]:
                if "type" in d.keys() and d["type"]!="NONE":
                    d = cutItenByTime(d,startTime,False)
                    d = cutItenByTime(d,endTime,True)
        else:
            dataObj[sensor] = cutItenByTime(dataObj[sensor],startTime,False)
            dataObj[sensor] = cutItenByTime(dataObj[sensor],endTime,True)
            
    return dataObj
                  
    
def cutItenByTime(d,startTime,keep=False):
    maxIndex = np.argwhere(d["time"]>=startTime)
    if len(maxIndex)>0:
        maxIndex=maxIndex[0][0]
        if keep:
            d["time"]=d["time"][:maxIndex]
        else:
            d["time"]=d["time"][maxIndex:]
        for cName in d["data"].keys():
            if keep:
                d["data"][cName]=d["data"][cName][:maxIndex]
            else:
                d["data"][cName]=d["data"][cName][maxIndex:]
    return d
            
def dataObj2drawList(dataObj,maxSec=9999999,fTitle="",full=None):
    #print("\n\n dataObj2drawList ******************************")
    #testPrintStructure(dataObj)
    
    ret = []
    if maxSec==-1:
        maxSec=9999999
        
    #print("MaxSec",maxSec)
    for sensor in dataObj.keys():
        if sensor=="bus" or  sensor=="usb":
            for d in dataObj[sensor]:
                if "type" in d.keys() and d["type"]!="NONE":
                    keylist = []
                    if "scale" in d.keys():
                        keylist=list(d["scale"].keys())
                    elif "gain" in d.keys():
                        keylist=list(d["gain"].keys())
                    elif "data" in d.keys():
                        keylist=list(d["data"].keys())
                    for name in keylist: #got the name
                        if(
                            d["type"]=="VIBRATION" 
                            and "aX_"+name not in d["data"].keys()
                            and "aY_"+name not in d["data"].keys()
                            and "aZ_"+name not in d["data"].keys()
                        ):
                            continue
                        if d["type"]!="VIBRATION" and name not in d["data"].keys():
                            continue
                            
                        startTime = datetime.fromtimestamp(d["time"][0]).strftime("%y-%m-%d %H:%M:%S.%f")
                        sub = dict()
                        sub["title"] = fTitle+"Sensor("+name+") start at "+startTime
                        sub["time"] = d["time"]-min(d["time"])
                        maxIndex = np.argwhere(sub["time"]>maxSec)
                        if len(maxIndex)>0:
                            maxIndex=maxIndex[0][0]
                        else:
                            maxIndex=len(sub["time"])
                        sub["time"]=sub["time"][:maxIndex]
                        sub["data"] = dict()
                        if full != None:
                            full=full-min(d["time"])
                            sub["full"]=[]
                            for f in full:
                                if f[1]<maxSec:
                                    sub["full"].append(f)
                                else:
                                    print(name,"kipt!!",f)
                                    break
                            if len(sub["full"])==0:
                                return ret
                            
                        if "VIBRATION" in d["type"]:
                            sub["title"]="Vibration "+sub["title"]
                            if "aX_"+name in d["data"].keys():
                                sub["data"]["axis_X"] = d["data"]["aX_"+name][:maxIndex]
                            if "aY_"+name in d["data"].keys():
                                sub["data"]["axis_Y"] = d["data"]["aY_"+name][:maxIndex]
                            if "aZ_"+name in d["data"].keys():
                                sub["data"]["axis_Z"] = d["data"]["aZ_"+name][:maxIndex]
                            sub["unit"] = d["unit"]
                            ret.append(sub)
                        if d["type"]=="CURRENT":
                            sub["title"]="Current "+sub["title"]
                            sub["data"]["signal"] = d["data"][name][:maxIndex]
                            sub["unit"] = d["unit"][name]
                            ret.append(sub)
                        if d["type"]=="VOLTAGE":
                            sub["title"]="Voltage "+sub["title"]
                            sub["data"]["signal"] = d["data"][name][:maxIndex]
                            sub["unit"] = d["unit"][name]
                            ret.append(sub)
                        if d["type"]=="SIMULATOR":
                            sub["title"]="Simulator "+sub["title"]
                            sub["data"]["signal"] = d["data"][name][:maxIndex]
                            sub["unit"] = d["unit"][name]
                            ret.append(sub)
                        if d["type"]=="AUDIO":
                            sub["title"]="AUDIO "+sub["title"]
                            sub["data"]["signal"] = d["data"][name][:maxIndex]
                            sub["unit"] = d["unit"]
                            ret.append(sub)
                        if d["type"]=="MODBUS":
                            sub["title"]="MODBUS "+sub["title"]
                            sub["data"]["result"] = d["data"][name][:maxIndex]
                            sub["unit"] = d["unit"]
                            #print(sub)
                            ret.append(sub)
                            
        elif sensor=="Digital":
            startTime = datetime.fromtimestamp(dataObj[sensor]["time"][0]).strftime("%y/%m/%d %H:%M:%S.%f")
            
            timeData = dataObj[sensor]["time"]-min(dataObj[sensor]["time"])
            maxIndex = np.argwhere(timeData>maxSec)
            if len(maxIndex)>0:
                maxIndex=maxIndex[0][0]
            else:
                maxIndex=len(timeData)
            for item in dataObj[sensor]["data"].keys():
                sub = dict()
                sub["title"] = fTitle+"Digital("+item+") start at "+startTime
                sub["time"] = dataObj[sensor]["time"]-min(dataObj[sensor]["time"])
                sub["time"] = timeData[:maxIndex]
                sub["unit"] = dataObj[sensor]["unit"]
                sub["data"] = dict()
                sub["data"]["signal"] = dataObj[sensor]["data"][item][:maxIndex]
                if full != None:
                    full=full-min(dataObj[sensor]["time"])
                    sub["full"]=[]
                    for f in full:
                        if f[1]<maxSec:
                            sub["full"].append(f)
                        else:
                            print(item,"kipt!!",f)
                            break
                    if len(sub["full"])==0:
                        return ret
                ret.append(sub)
        elif sensor=="distance":
            startTime = datetime.fromtimestamp(dataObj[sensor]["time"][0]).strftime("%y/%m/%d %H:%M:%S.%f")
            sub = dict()
            sub["title"] = fTitle+"Sensor("+sensor+") start at "+startTime
            sub["time"] = dataObj[sensor]["time"]-min(dataObj[sensor]["time"])
            maxIndex = np.argwhere(sub["time"]>maxSec)
            if len(maxIndex)>0:
                maxIndex=maxIndex[0][0]
            else:
                maxIndex=len(sub["time"])
            sub["time"]=sub["time"][:maxIndex]
            sub["unit"] = dataObj[sensor]["unit"]
            sub["data"] = dict()
            if full != None:
                full=full-min(dataObj[sensor]["time"])
                sub["full"]=[]
                for f in full:
                    if f[1]<maxSec:
                        sub["full"].append(f)
                    else:
                        print(sensor,"kipt!!",f)
                        break
                if len(sub["full"])==0:
                    return ret
            for item in dataObj[sensor]["data"].keys():
                sub["data"][item]=dataObj[sensor]["data"][item][:maxIndex]
            ret.append(sub)
    return ret 
    
def conponerObj(objList,ret):
    for obj in objList:
        if type(obj)==dict:
            conponerObjRecursive(obj,ret)
    
    if "bus" in ret.keys():
        for i in range(4):
            if "type" not in ret["bus"][i].keys():
                ret["bus"][i]["type"]="NONE"
    else:
        ret["bus"]=[
            {"type":"NONE"},
            {"type":"NONE"},
            {"type":"NONE"},
            {"type":"NONE"}
            ]
#    savePKL(ret,"test_format.pkl")
#    saveTXT(str(ret),"test_format.txt")
#    print(openPKL("test_format.pkl"))
#    print(openTXT("test_format.txt"))
          
    return ret
        
def conponerObjRecursive(obj,ret={}):
    for key in obj.keys():
        if key in ret.keys():
            if type(obj[key])==dict:
                conponerObjRecursive(obj[key],ret[key])
            elif type(obj[key])==np.ndarray:
                ret[key] = np.hstack([ret[key],obj[key]])
            elif type(obj[key])==list:
                listLen = len(obj[key])
                for i in range(listLen): # have to dict
                    if type(obj[key][i])==dict:
                        #print(key,i)
                        #testPrintStructure(obj)
                        #testPrintStructure(ret)
                        conponerObjRecursive(obj[key][i],ret[key][i])
        else:
            ret[key]=copy.deepcopy(obj[key])
    
def drawList(path,data,testStatus="",callback=None):
    if callback!=None:
        callback()
    print("start drawList",getRamPercent())
    #t = drawListOnce_proc(path,data)
    t = drawListMuti_proc(path,data,testStatus,callback)
    t.start()
    t.release()
    gc.collect()
    print("end drawList",getRamPercent())
    
    
class drawListOnce_proc(multiprocessing.Process):
    def __init__(self,path,data):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.path=path
        self.data=data
        
        
    def run(self):
        size = 12
        data = self.data
        fig, ax = plt.subplots()
        fig.subplots_adjust(hspace=0.4,wspace=0.4)
        H = len(data)
        fig.set_figheight(size//4*H)
        fig.set_figwidth(size)
        for i,d in enumerate(data):
            labels=[]
            plt.subplot(H,1,i+1)
            for item in d["data"].keys():
                labels.append(item)
                plt.plot(d["time"],d["data"][item],alpha=0.8,linewidth=0.5)
                
            minData,maxData=plt.ylim()
            if "full" in d.keys():
                for f in d["full"]:
                    plt.fill_between((f[0],f[1]),minData,maxData,alpha=0.3,facecolor="gold")
                    
            plt.title(d["title"])
            plt.xlabel("Time(s)")
            plt.ylabel("Value("+d["unit"]+")")
            plt.legend(labels=labels)
        plt.tight_layout()
        fig.savefig(self.path+".png",dpi=80)
        fig.savefig(self.path+"_hight.png",dpi=400)
        #plt.show()
        fig.clf()
        fig.clear()
        plt.cla()
        plt.clf()
        plt.close("all")
        plt.close(fig)
        
        
    def release(self):
        if self.is_alive():
            self.join()
        self.exit.set()


class drawListMuti_proc(multiprocessing.Process):
    def __init__(self,path,data,testStatus="",callback=None):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.path=path
        self.data=data
        self.testStatus=testStatus
        self.callback=callback
        
    def run(self):
        imgList = []
        imgList_H = []
        size = 12
        data = self.data
        alpha=0.95
        #plt.tight_layout(h_pad=3)
        fig, ax = plt.subplots(figsize=(size,size//4))
        #fig.subplots_adjust(left=0.07,right=0.95,top=0.9,bottom=0.2)
        fig.subplots_adjust(left=0.07,right=0.92,top=0.9,bottom=0.2)
        for i,d in enumerate(data):
        
            
            if self.testStatus !="":
                testStatusUpload(self.testStatus,str(i+1),str(len(data)))
            _test_startTime=time.time()
            
            plt.grid(True,axis='both',linestyle=":",color='gray',alpha=alpha/2)
            labels=[]
            newMaxData=-999999
            newMinData=999999
            limitDataTime = 0
            for item in d["data"].keys():
                minlength = min(len(d["time"]),len(d["data"][item]))
                newMaxData = max(newMaxData,max(d["data"][item][:minlength]))
                newMinData = min(newMinData,min(d["data"][item][:minlength]))
                DataMean = d["data"][item].mean()
                newX,newY = self.downSample(np.array(d["time"][:minlength]),np.array(d["data"][item][:minlength]))
                if limitDataTime > 0:
                    limitDataTime = min(limitDataTime,d["time"][minlength-1])
                else:
                    limitDataTime = d["time"][minlength-1]
                L, = ax.plot(newX,newY,alpha=alpha,linewidth=0.5,label = item)
                #L, = ax.plot(d["time"][:minlength],d["data"][item][:minlength],alpha=alpha,linewidth=0.5,label = item)
                labels.append(L)
            axR = None
            axRmax = 0
            if "dataR" in d.keys():
                axR = ax.twinx()
                for i in range(len(labels)):
                    axR._get_lines.prop_cycler = ax._get_lines.prop_cycler
                for item in d["dataR"].keys():
                    minlength = min(len(d["timeR"]),len(d["dataR"][item]))
                    newX,newY = self.downSample(np.array(d["timeR"][:minlength]),np.array(d["dataR"][item][:minlength]))
                    L, = axR.plot(newX,newY,alpha=alpha,linewidth=0.5,label = item)
                    #L, = axR.plot(d["timeR"][:minlength],d["dataR"][item][:minlength],alpha=alpha,linewidth=0.5,label = item)
                    if(len(d["dataR"][item])>0):
                        axRmax = max(axRmax,max(d["dataR"][item]))
                    labels.append(L)
                    
                if "dataRtext" in d.keys():
                    axR.set_ylabel(d["dataRtext"])
                
            #print("limitDataTime",limitDataTime)
            minData,maxData=plt.ylim()
            centerData = (minData+maxData)/2
            dataRange = maxData-minData
            minTime,maxTime=plt.xlim()
            timeRange = maxTime-minTime
            if "full" in d.keys():
                for f in d["full"]:
                    if f[1]>limitDataTime:
                        continue
                    plt.axvline(x=f[0],alpha=alpha,color="gold")
                    if f[1]<maxTime:
                        plt.axvline(x=f[1],alpha=alpha,color="gold")
                        plt.fill_between((f[0],f[1]),minData,maxData,alpha=alpha/4,facecolor="gold")
                    else:
                        plt.fill_between((f[0],maxTime),minData,maxData,alpha=alpha/4,facecolor="gold")
                    
            if "textR" in d.keys():
                for text in d["textR"]:
                    #axR.text(text['x'],text['y'],text['d'],{"ha":"center"},fontsize=8)
                    axR.text(text['x']-timeRange/200,text['y']+dataRange/20,text['d'],fontsize=8,rotation=60)
                    axR.scatter(text['x'],text['y'],color='r',s=3)
                    axR.plot([text['x'],text['x']],[text['y'],text['y']+dataRange*3/40],color='r',linewidth=1,linestyle=':')
                    
            if "textTag" in d.keys():
                for text in d["textTag"]:
                    #t = axR.text(text['x'],text['y'],text['d'],fontsize=8,alpha=alpha/1.2,rotation=60)#,ha='center',va='center')
                    t = axR.text(text['x'],text['y'],text['d'],fontsize=8,alpha=alpha/1.2,ha='center')#,va='center')
                    #t.set_bbox(dict(facecolor='gold',edgecolor=None,boxstyle='Round,pad=0.1',alpha=alpha/4))
                    plt.fill_between((text['l'],text['r']),text['y'],text['y']+dataRange/20,alpha=alpha/4,facecolor="green")
                    
            ax.set_title(d["title"]+'  (Mean:%2f)'%DataMean)
            ax.axhline(DataMean,color="royalblue")
            sensor_name = d["title"].split('Sensor(')[1].split(') start')[0]
            #ax.text(math.ceil(max(d["time"])),DataMean,f"{sensor_name}'s Mean=%.2f"%DataMean,color="blue",horizontalalignment="right",verticalalignment="bottom")
            ax.set_xlabel("Time(s)")
            ax.set_ylabel("Value("+d["unit"]+")")
            #ax.set_xlim(0,math.ceil(max(d["time"])))  #math.ceil return the >= miniest int
            ax.set_xlim(0,math.floor(max(d["time"])))  #math.floor return the <= biggiest int
            newRange = (abs(newMaxData*1.0-newMinData*1.0)/3.0*4.0)/2.0
            newCenter = (newMaxData+newMinData)/2.0
            newMaxData = newCenter+newRange
            newMinData = newCenter-newRange
            
            ax.get_xaxis().set_major_locator(LinearLocator(numticks=21))
            ax.get_yaxis().set_major_locator(LinearLocator(numticks=9))
            if newMinData!=newMaxData:
                ax.set_ylim(newMinData,newMaxData)
            
            if axR != None:
                axR.get_yaxis().set_major_locator(LinearLocator(numticks=9))
                axR.set_ylim(0,axRmax*8/7)
            ax.legend(handles=labels,loc="upper right")
            
            stream = BytesIO()
            fig.savefig(stream,format='png',dpi=80)
            stream.seek(0)
            imgList.append(Image.open(stream))
            del stream
            gc.collect()
            
            stream = BytesIO()
            fig.savefig(stream,format='png',dpi=200)
            stream.seek(0)
            imgList_H.append(Image.open(stream))
            del stream
            gc.collect()
            
            ax.cla()
            plt.cla()
            if "dataR" in d.keys():
                axR.cla()
                fig, ax = plt.subplots(figsize=(size,size//4))
                #fig.subplots_adjust(left=0.07,right=0.95,top=0.9,bottom=0.2)
                fig.subplots_adjust(left=0.07,right=0.92,top=0.9,bottom=0.2)
            gc.collect()
            _test_endTime=time.time()
        plt.close(fig)
            
        if len(imgList)>0:
            if isSPIIDER():
                self.saveImfList(imgList,self.path+".png")
            del imgList
            gc.collect()
        if len(imgList_H)>0:
            if isSPIIDER():
                self.saveImfList(imgList_H,self.path+"_hight.png")
            else:
                self.saveImfList(imgList_H,self.path+".png")
            del imgList_H
            gc.collect()
        
        
    def downSample(self,x,y):
        #return x, y
        
        if len(x)>20000: #20k
            interval_num = 4000
            interval = int(len(y)/interval_num)
            total_num = interval*interval_num
            newY = np.reshape(np.array(y[:total_num]),(interval_num,interval))
            scale = np.arange(interval_num)*interval
            maxY = np.argmax(newY,axis=1)
            minY = np.argmin(newY,axis=1)
            index = np.arange(total_num,len(y))
            index = np.append(index,maxY+scale)
            index = np.append(index,minY+scale)
            index = np.sort(index)
            #print("Len",len(x[index]),len(x))
            return x[index],y[index]
            
        return x,y
        
        
    def saveImfList(self,imgList,path):
        number = len(imgList)
        W,H = imgList[0].size
        offset = H
        new_img = Image.new('RGB',(W,H*number))
        for i,img in enumerate(imgList):
            new_img.paste(img,(0,i*offset))
        new_img.save(path)
        
        
    def release(self):
        while self.is_alive():
            time.sleep(1)
            if self.callback != None:
                self.callback()
            #self.join()
        self.exit.set()


def keepChannelName(obj,channelList):
    flag = False
    ret = copy.deepcopy(obj)
    retKeyList=list(ret.keys())
    for key in retKeyList:
        #print("keepChannelName",key)
        if type(ret[key])==dict:
            retKeyDateListlist = list(ret[key]["data"].keys())
            for chName in retKeyDateListlist:
                if chName not in channelList:
                    #print("del",chName)
                    ret[key]["data"].pop(chName)
                else:
                    #print("keep",chName)
                    flag = True
            if len(ret[key]["data"])==0:
                ret.pop(key)
        elif type(ret[key])==list:
            for i in range(len(ret[key])):
                if "data" not in ret[key][i].keys():
                    continue
                retKeyIndexDateListlist = list(ret[key][i]["data"].keys())
                for chName in retKeyIndexDateListlist:
                    if chName not in channelList:
                        ret[key][i]["data"].pop(chName)
                        #print("del",chName)
                    else:
                        #print("keep",chName)
                        flag = True
                if len(ret[key][i]["data"])==0:
                    ret[key][i]={"type":"NONE"}
    if flag:
        return ret
    del ret 
    return {}
                
def testPrintStructure(ret):
    for i in ret.keys():
        print("key:",i,type(ret[i]))
        if type(ret[i])==list:
            for j in range(len(ret[i])):
                for k in ret[i][j].keys():
                    if type(ret[i][j][k])==dict:
                        for x in ret[i][j][k].keys():
                            if type(ret[i][j][k][x])==np.ndarray:
                                print(i,j,",key",k,",keyIn",x,ret[i][j][k][x].shape)
                        
                    else:
                        if type(ret[i][j][k])==np.ndarray:
                            print(i,j,",key",k,ret[i][j][k].shape)
                        else:
                            print(i,j,",key",k,ret[i][j][k])
        elif  type(ret[i])==dict:
            for k in ret[i].keys():
                if type(ret[i][k])==np.ndarray:
                    print(i,k,ret[i][k].shape)
                    
def keepTime(ret,maxSec):
    for i in ret.keys():
        if type(ret[i])==list:
            for j in range(len(ret[i])):
                if "time" in ret[i][j].keys():
                    removeByTime(ret[i][j],maxSec)
        elif  type(ret[i])==dict:
            if "time" in ret[i].keys():
                removeByTime(ret[i],maxSec)
                    
def removeByTime(targetObj,targetTime):
    keepCount = sum((targetObj["time"]<=min(targetObj["time"])+targetTime)*1)
    if keepCount>0:
        targetObj["time"] = targetObj["time"][:keepCount]
        for column in targetObj["data"].keys():
            targetObj["data"][column] = targetObj["data"][column][:keepCount]
            
searchChannelKeyFastRet={}
def searchChannelKey(obj,channelName):
    #if channelName in searchChannelKeyFastRet:
    #    keyPath = searchChannelKeyFastRet[channelName]
    #    if keyPath[0] in obj.keys():
    #        if len(keyPath)==2:
    #            if keyPath[1] <= len(obj[keyPath[0]]):
    #                return keyPath
    #        else:
    #            return keyPath
        
    ret = []
    for key in obj.keys():
        if type(obj[key])==dict:
            if channelName in obj[key]["data"].keys():
                ret.append(key)
                return ret
        elif type(obj[key])==list:
            for i in range(len(obj[key])):
                if "data" not in obj[key][i].keys():
                    continue
                if channelName in obj[key][i]["data"].keys():
                    ret.append(key)
                    ret.append(i)
                    searchChannelKeyFastRet[channelName]=ret
                    return ret
    return ret

class mainProgramStates(object):
    _ST1 = 1
    _MainHeartbeat = 0
    _SampleHeartbeat = 1
    _SegHeartbeat = 2
    _Err = 3
    _startTime=0
        
    @classmethod
    def debug(cls,s,m):
        if cls._startTime==0:
            cls._startTime=time.time()
        print("@@ ST1:",s,m,time.time()-cls._startTime)
    
    @classmethod
    def send(cls,s,m=""):
        ledStatusUpload(cls._ST1,s,m)
        if m !="":
            printErr(m)
        #for debug
        cls.debug(s,m)
    

def createDataObjFromCSV(filePath):
    df = pd.read_csv(filePath)
    if 'datetime' in df.columns:
        endOffset = 0
        if len(pd.unique(df['datetime']))==1:
            endOffset = 1
            
        realSec = pd.unique(df['datetime'])
        if(len(realSec)>=3):
            df = df.drop(df.loc[df['datetime'] == realSec[0]].index)     #remove not complete sec at head
            df = df.drop(df.loc[df['datetime'] == realSec[-1]].index)    #remove not complete sec at fial
        realSec = pd.unique(df['datetime'])
        Fs = len(df['datetime'])/len(realSec)
        try:
            startTime = time.mktime(datetime.strptime(df['datetime'].values[0],"%Y/%m/%d %H:%M:%S").timetuple())
            endTime = time.mktime(datetime.strptime(df['datetime'].values[-1],"%Y/%m/%d %H:%M:%S").timetuple())+endOffset
        except :
            try:
                startTime = time.mktime(datetime.strptime(df['datetime'].values[0],"%Y-%m-%d %H:%M:%S").timetuple())
                endTime = time.mktime(datetime.strptime(df['datetime'].values[-1],"%Y-%m-%d %H:%M:%S").timetuple())+endOffset
            except :
                print("time error")
                return False
                
        enableName = list(df.columns)
        enableName.remove('datetime')
    else:
        print("not datetime")
        return False
        
        
    dataLen = len(df['datetime'])
    timeGap = np.arange(0,dataLen)/dataLen*(endTime-startTime)
    timeGap = timeGap+startTime
    
    ret = dict()
    ret['bus']=[dict(),dict(),dict(),dict()]
    ret['bus'][0]['type']="SIMULATOR"
    ret['bus'][0]['fs']=Fs #just simulater
    ret['bus'][0]['time'] = timeGap
    ret['bus'][0]['sensor']=dict()
    ret['bus'][0]['gain']=dict()
    ret['bus'][0]['circuit']=dict()
    ret['bus'][0]['data']=dict()
    ret['bus'][0]['unit']=dict()
    ret['bus'][0]['maxValue']=dict()
    ret['bus'][0]['minValue']=dict()
    ret['bus'][0]['bias']=dict()
        
    for i,n in enumerate(enableName):
        ret['bus'][0]['sensor'][n]="Simulator"
        ret['bus'][0]['gain'][n]=1
        ret['bus'][0]['circuit'][n]="Differential"
        ret['bus'][0]['data'][n] = np.array(df[n].values)
        ret['bus'][0]['unit'][n]="None"
        ret['bus'][0]['maxValue'][n]=1
        ret['bus'][0]['minValue'][n]=-1
        ret['bus'][0]['bias'][n]=0
    return ret
