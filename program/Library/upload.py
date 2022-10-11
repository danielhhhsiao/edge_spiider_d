import multiprocessing
import ftplib
from io import BytesIO, StringIO
from sys import getsizeof
import os
import glob
import random
import time
import requests
import pickle
import numpy as np
from datetime import datetime
import pandas as pd
import gzip
from Library.tool import ledStatusUpload, dataObjTrans_FE, dataObj2pd, transFormatUpload, loadConfig, getDictItem, conponerObj, printErr, keepChannelName, searchChannelKey, testPrintStructure,dataObj2drawList,getRamPercent,getRamFree,getRomPercent,getRomFree,writeConfig
import paho.mqtt.client as mqtt
import json
import gc
import psutil

class npEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
            
        return json.JSONEncoder.default(self,obj)

class upload(multiprocessing.Process):
    def __init__(self,param=dict(),param2=dict(),minProcTime=0.01,testFlag=True):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        print("upload class create")
        
        #Get program path info.
        self.configDict = loadConfig("d")
        self.programPath = getDictItem(self.configDict,'environment','home_dir',"/home/pi/program")
        
        #upload choose
        self.API_Enable = int(getDictItem(param2,"server","type","0"))
        self.FTP_Mode = int(getDictItem(param2,"ftp","type","0"))
        self.FTP_HOST = getDictItem(param2,"ftp","ip","")
        self.FTP_PROXY = getDictItem(param2,"ftp","proxy","")
        self.FTP_USER = getDictItem(param2,"ftp","name","")
        self.FTP_PASS = getDictItem(param2,"ftp","pwd","")
        self.FTP_Enable = 0
        #FTP params
        if (self.FTP_Mode != 0):
            self.FTP_Enable = 1
            #if ini doesn't have IP
            if(self.FTP_HOST == ""):
                self.FTP_Enable = 0
        #API params
        if (self.API_Enable != 0):
            self.API_URL = getDictItem(param2,"server","ip","")
            self.API_PROXY = getDictItem(param2,"server","proxy","")
            #if ini doesn't have URL
            if (self.API_URL == ""):
                self.API_Enable = 0

        #self.API_URL = "http://114.32.85.251:1082/edgedata/segment"
        #self.API_URL = "http://114.32.85.251:1082/edgedata/"
        
        #mqtt params
        self.MQTT_URL = getDictItem(param2,"mqtt","ip","")
        self.MQTT_PORT = getDictItem(param2,"mqtt","port","")
        self.MQTT_TOPIC = getDictItem(param2,"mqtt","topic","")
        self.MQTT_NAME = getDictItem(param2,"mqtt","name","")
        self.MQTT_PSWD = getDictItem(param2,"mqtt","passwd","")
        
        
        #Type
        self.type_std = ['seg','FE','mqtt']
        
        #Local saved param
        self.local_saved_flag = False           #Ram detect to saved in local
        self.local_upload_flag = False          #Check the upload process for local upload or not
        self.local_upload_error_flag = False    #When local upload is success, remove the local file.
        
        #config
        self.workini=param
        self.sysini=param2
        
        #share data in porcess
        manager=multiprocessing.Manager()
        self.queueData=manager.Queue()
        self.queueName=manager.Queue()
        self.queueType=manager.Queue()
        self.minProcTime=minProcTime
        
        self.ruleIgnore = {}
        
        self.states=manager.dict()
        self.states["data_List_Flag"] = False
        self.states["pid"]=False
        self.states["release"]=False
        self.states["Seg_queue_data_count"] = 0
        self.states["FE_queue_data_count"] = 0
        self.states["MQTT_queue_data_count"] = 0
        self.states["FTPUploadSuccess"] = 0
        self.states["APIUploadSuccess"] = 0
        self.states["MQTTUploadSuccess"] = 0
        
        #upload config flag
        self.states["upload_config_flag"] = False
        self.states["config_First_Flag"] = False
        
        #Use for calculate upload timeout
        self.upload_speed_std = 100000
        
        #Test or Work mode
        self.testFlag = testFlag
        
        #Const timeout
        self.const_Timeout = 5
        
        #RAM/ROM limit
        if (psutil.virtual_memory()[0] / (1024 ** 2)) < 1024:
            self.ramAlarm = 64
            self.ramLimit = 128
        else:
            self.ramAlarm = 128
            self.ramLimit = 256
        self.romLimit = 512
        
    def stopProc(self):
        self.states["release"]=True
    
    def put(self,data,name,Type):
        self.queueData.put(data)
        self.queueName.put(name)
        self.queueType.put(Type)
        
    def getPid(self):
        return self.states["pid"]
    
    def data_process(self):
        if not self.queueData.empty():
            queue_size = range(self.queueData.qsize())
            self.listdata.extend([self.queueData.get() for x in queue_size])
            self.listname.extend([self.queueName.get() for x in queue_size])
            self.listtype.extend([self.queueType.get() for x in queue_size])
        print("list size:",len(self.listdata))            
        data = self.listdata.pop(0)
        name = self.listname.pop(0)
        Type = self.listtype.pop(0)
        if name not in self.ruleIgnore:
            self.ruleIgnore[name] = 0
        #---------------------------------------------------#       
        #config
        sysini=self.sysini
        workini=self.workini
        #Check the upload error occur in main process?
        uploadF_error_flag = False 
        uploadA_error_flag = False
        #Return the API/FTP/MQTT process alive or not
        uploadF_alive_flag = False
        uploadA_alive_flag = False
        uploadM_alive_flag = False
        #timeout params
        FTP_upload_timeout = self.const_Timeout
        API_upload_timeout = self.const_Timeout
        MQTT_upload_timeout = self.const_Timeout
        break_flag = 0
        print(Type+" queue input.")
        if Type != self.type_std[2]:
            #Get the interval params to determine interval or not
            Seg_upload = 0
            FE_upload = 0
            Seg_interval = 0
            for key in workini.keys():
                ruleName = "@".join([
                    getDictItem(workini,key,"name",""),
                    getDictItem(workini,key,"unit",""),
                    getDictItem(workini,key,"sub_unit","")
                    ])
                if name in ruleName:
                    Seg_upload = int(getDictItem(workini,key,"upload_seg","0"))
                    Seg_interval = int(getDictItem(workini,key,"upload_interval","0"))
                    FE_upload = int(getDictItem(workini,key,"upload_extraction","0"))
            #------------------upload seg/FE count-------------#
            if(Seg_upload == 1) and (FE_upload == 1):
                if Type == self.type_std[0]:
                    if((self.ruleIgnore[name]%(Seg_interval+1)) == 0):
                        print("Data rule:",name)
                        print("Interval upload")
                        self.ruleIgnore[name] = 1
                        ledStatusUpload(3,0,"")
                    else:
                        print("Data rule:",name)
                        print("Interval skip : %d, not upload"%self.ruleIgnore[name])
                        self.ruleIgnore[name]+=1
                        break_flag = 1
                else:
                  ledStatusUpload(3,1,"")  
            else:
                if Type == self.type_std[0]:
                   ledStatusUpload(3,0,"")
                else:
                  ledStatusUpload(3,1,"")   
                self.ruleIgnore[name] = 1
            #Check the seq data need to upload or not
            if(Seg_upload == 0):
                if Type == self.type_std[0]:
                    print("Seg upload = 0, not upload")
                    break_flag = 1
                elif (FE_upload==0):
                    print("FE upload = 0, not upload")
                    break_flag = 1
        else:
            if self.MQTT_URL == '':
                break_flag = 1
                print("MQTT does not setting.")
                ledStatusUpload(2,2,"MQTT params does not setting.")
            else:
                print("MQTT upload.")
            
        
        if break_flag == 0:
            path_dir = self.programPath+'/T_LocalSaved/'
            if not self.testFlag:
                path_dir = self.programPath+'/LocalSaved/'
            #---------------------------------------------------#
            start = time.time()
            upload_payload, sampling_time, file_name = transFormatUpload(data,workini,name,Type)
            if Type == self.type_std[0]:
                sampling_time = datetime.fromtimestamp(sampling_time)
            end = time.time()
            print("TransFormat cost time : " + str(end-start))
            #--------------------RAM Detect---------------------#
            if(getRamFree() < self.ramLimit):
                self.local_saved_flag = True
            elif (getRamFree() > self.ramLimit+64):
                self.local_saved_flag = False
            #-----------------------------------upload Region-------------------------------------#
            self.local_upload_flag = False
            #--------------------FTP upload---------------------#
            if (Type != self.type_std[2]):
                if (self.FTP_Enable != 0):
                    try:
                        self.FTP_upload_Proc = FTP_upload(path_dir, self.FTP_HOST, self.FTP_USER, self.FTP_PASS, self.FTP_Mode,\
                        data,name,Type,sampling_time,file_name,self.local_upload_flag,self.states["upload_config_flag"])
                        self.FTP_upload_Proc.start()
                        temp = BytesIO()
                        pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                        FTP_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                    except Exception as e:
                        ledStatusUpload(2,2,"FTP - "+str(e))
                        uploadF_error_flag = True
                        print(e)
                        print("FTP Upload Error, Saved in local")
                        data.setdefault('file_name',file_name)
                        data.setdefault(name,Type)
                        if Type == self.type_std[0]:
                            timeStr = sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "Seg_"+timeStr
                        elif Type == self.type_std[1]:
                            timeStr = datetime.strptime(sampling_time,"%Y/%m/%d %H:%M:%S")
                            timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "FE_"+timeStr
                        fileName="LocalSaved_"+timeStr+"_"+name+".pkl"
                        if(getRomFree() < self.romLimit):
                            if(glob.glob(path_dir+'*') != []):
                                first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                                os.remove(first_file)
                        pickle.dump(data,open(path_dir+"F_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                #--------------------API upload---------------------#
                if (self.API_Enable != 0):
                    try:
                        #Seg
                        if Type == self.type_std[0]:
                            if self.API_URL[-1] != '/':
                                api_url = self.API_URL + "/segment"
                            else:
                                api_url = self.API_URL + "segment"
                        #FE
                        else:
                            if self.API_URL[-1] != '/':
                                api_url = self.API_URL + "/feature"
                            else:
                                api_url = self.API_URL + "feature"
                        self.API_upload_Proc = API_upload(path_dir,api_url,self.API_PROXY,upload_payload,data,name,Type,sampling_time,self.local_upload_flag)
                        self.API_upload_Proc.start()
                        temp = BytesIO()
                        pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                        API_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                    except Exception as e:
                        ledStatusUpload(2,2,"API - "+str(e))
                        uploadA_error_flag = True
                        print(e)
                        print("API Upload Error, Saved in local")
                        data.setdefault(name,Type)
                        if Type == self.type_std[0]:
                            timeStr = sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "Seg_"+timeStr
                        elif Type == self.type_std[1]:
                            timeStr = datetime.strptime(sampling_time,"%Y/%m/%d %H:%M:%S")
                            timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "FE_"+timeStr
                        fileName="LocalSaved_"+timeStr+"_"+name+".pkl"
                        if(getRomFree() < self.romLimit):
                            if(glob.glob(path_dir+'*') != []):
                                first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                                os.remove(first_file)
                        pickle.dump(data,open(path_dir+"A_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
            #--------------------MQTT upload---------------------#
            else:
                try:
                    mqtt_url = self.MQTT_URL
                    self.MQTT_upload_Proc = MQTT_upload(path_dir,name,self.MQTT_URL,self.MQTT_PORT,self.MQTT_TOPIC,self.MQTT_NAME,self.MQTT_PSWD,data,self.local_upload_flag)
                    self.MQTT_upload_Proc.start()
                    temp = BytesIO()
                    pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                    MQTT_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                except Exception as e:
                    ledStatusUpload(2,2,"MQTT - "+str(e))
                    uploadM_error_flag = True
                    print(e)
                    print("MQTT Upload Error, Saved in local")
                    timeStr = data["Report_Time"]["0"]
                    timeStr = datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S")
                    timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                    fileName="LocalSaved_"+timeStr+"_"+name+".pkl"
                    if(getRomFree() < self.romLimit):
                        if(glob.glob(path_dir+'*') != []):
                            first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                            os.remove(first_file)
                    pickle.dump(data,open(path_dir+"M_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
            #--------------------------------upload Region End-------------------------------------#
            #--------------------Saved on local---------------------#    
            list_count = len(self.listdata)
            if (self.local_saved_flag) and (list_count != 0):   #RAM detect result
                print("RAM in heavy status, Saved in local")
                list_count = int((list_count + (list_count%2))/2)
                saved_data = [self.listdata.pop(x) for x in range(list_count)]
                saved_name = [self.listname.pop(x) for x in range(list_count)]
                saved_type = [self.listtype.pop(x) for x in range(list_count)]
                while(len(saved_data) != 0):
                    data_ram=saved_data.pop(0)
                    name_ram=saved_name.pop(0)
                    Type_ram=saved_type.pop(0)
                    
                    upload_payload_ram, sampling_time_ram, file_name_ram = transFormatUpload(data_ram,workini,name_ram,Type_ram)
                    #--------------------ROM Detect---------------------#
                    if(getRomFree() < self.romLimit):
                        if(glob.glob(path_dir+'*') != []):
                            first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                            os.remove(first_file)
                    #--------------------Saved in Local----------------#        
                    if Type_ram != self.type_std[2]:
                        if Type_ram == self.type_std[0]:
                            sampling_time_ram = datetime.fromtimestamp(sampling_time_ram)
                            timeStr = sampling_time_ram.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "Seg_"+timeStr
                        elif Type_ram == self.type_std[1]:
                            timeStr = datetime.strptime(sampling_time_ram,"%Y/%m/%d %H:%M:%S")
                            timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "FE_"+timeStr
                        fileName="LocalSaved_"+timeStr+"_"+name_ram+".pkl"
                        if (self.FTP_Enable != 0):
                            data_ram.setdefault('file_name',file_name_ram)
                            data_ram.setdefault(name_ram,Type_ram)
                            pickle.dump(data_ram,open(path_dir+"F_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                            print("RAM protection. Saved file : " + "F_" + fileName)
                        if (self.API_Enable != 0):
                            data_ram.setdefault(name_ram,Type_ram)
                            pickle.dump(data_ram,open(path_dir+"A_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                            print("RAM protection. Saved file : " + "A_" + fileName)
                    else:
                        timeStr = data_ram["Report_Time"]["0"]
                        timeStr = datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S")
                        #timeStr = datetime.strptime(timeStr,"%y/%m/%d %H:%M:%S")
                        timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                        fileName="LocalSaved_"+timeStr+"_"+name_ram+".pkl"
                        pickle.dump(data_ram,open(path_dir+"M_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                        print("RAM protection. Saved file : " + "M_" + fileName)
                    
                    #the stored file        
                    if Type_ram == self.type_std[0]:
                        self.states["Seg_queue_data_count"] += 1
                    elif Type_ram == self.type_std[1]:
                        self.states["FE_queue_data_count"] += 1
                    elif Type_ram == self.type_std[2]:
                        self.states["MQTT_queue_data_count"] += 1
            #---------------------release------------------------#
            if Type != self.type_std[2]:
                if(self.FTP_Enable != 0):
                    uploadF_alive_flag = self.FTP_upload_Proc.is_alive()
                if(self.API_Enable != 0):
                    uploadA_alive_flag = self.API_upload_Proc.is_alive()
            else:
                uploadM_alive_flag = self.MQTT_upload_Proc.is_alive()
                
        if(len(self.listdata) > 0):
            self.states["data_List_Flag"] = True
        else:
            self.states["data_List_Flag"] = False
        return uploadF_alive_flag, uploadA_alive_flag, uploadM_alive_flag, FTP_upload_timeout, API_upload_timeout, MQTT_upload_timeout, uploadF_error_flag, uploadA_error_flag, data, name, Type, break_flag
        
    def run(self):
        sysini=self.sysini
        workini=self.workini
        self.states["pid"]=os.getpid()
        
        dataprocess_break_flag = 0
        self.local_upload_flag = False
        localfile_process_flag = False
        uploadF_error_flag = True 
        uploadA_error_flag = True
        uploadM_error_flag = True
        uploadF_alive_flag = False
        uploadA_alive_flag = False
        uploadM_alive_flag = False
        
        self.listdata = []
        self.listname = []
        self.listtype = []
        
        startTime=time.time()
        endTime=startTime
        Ram_predetect_time = 0
        intervalCounter = {}
        uploadF_pretime = 0
        uploadA_pretime = 0
        uploadM_pretime = 0
        sampling_time = 0
        #return upload success/failed count params
        havebeen_upload_flag = False
        t_F_S_csv_s = 0
        t_F_S_csv_f = 0
        t_F_S_pkl_s = 0
        t_F_S_pkl_f = 0
        t_F_F_csv_s = 0
        t_F_F_csv_f = 0
        t_F_F_pkl_s = 0
        t_F_F_pkl_f = 0
        t_A_S_s = 0
        t_A_S_f = 0
        t_A_F_s = 0
        t_A_F_f = 0
        F_Seg_uploadcsv_success = 0
        F_Seg_uploadcsv_failed = 0
        F_Seg_uploadpkl_success = 0
        F_Seg_uploadpkl_failed = 0
        F_FE_uploadcsv_success = 0
        F_FE_uploadcsv_failed = 0
        F_FE_uploadpkl_success = 0
        F_FE_uploadpkl_failed = 0
        A_Seg_upload_success = 0
        A_Seg_upload_failed = 0
        A_FE_upload_success = 0
        A_FE_upload_failed = 0
        MQTT_upload_success = 0
        MQTT_upload_failed = 0
        
        #rule check flag
        rule_check_flag = False
        #Removed the test local file
        path_dir = self.programPath+'/T_LocalSaved/'
        Upload_label_startCount = len(path_dir)
        
        try:
            if(glob.glob(path_dir+'*') != []):
                for f in glob.glob(path_dir+'*'):
                    first_file = f
                    os.remove(first_file)
                    print("Remove Test Local file: " + first_file)
        except Exception as e:
            print(e) 
        
        if not self.testFlag:
            path_dir = self.programPath+'/LocalSaved/'
            Upload_label_startCount = len(path_dir)
        if not os.path.isdir(path_dir):
            os.makedirs(path_dir)
        
        """
        if(self.FTP_HOST != ""):
            self.states["config_First_Flag"] = True
            self.FTP_upload_Proc = FTP_upload(path_dir,self.FTP_HOST,self.FTP_USER,self.FTP_PASS,self.FTP_Mode,'','','','','','',self.states["upload_config_flag"])
            self.FTP_upload_Proc.start()
            uploadF_alive_flag = True
            FTP_upload_timeout = 5
            upload_pretime = time.time()
        """
        
        while not self.states["release"] or self.queueData.empty()==False or uploadF_alive_flag or uploadA_alive_flag or uploadM_alive_flag or localfile_process_flag or havebeen_upload_flag or self.states["data_List_Flag"]:
            try:
                #----------RAM Detect-----------#
                Ram_detect_time = time.time()
                if(Ram_detect_time - Ram_predetect_time > 2):
                    Ram_predetect_time = Ram_detect_time
                    print(self.queueData.empty(),uploadF_alive_flag,uploadA_alive_flag,uploadM_alive_flag,localfile_process_flag,self.states["data_List_Flag"])
                    print("ListSize: %d" %len(self.listdata))
                    deviceConfig = loadConfig("d")
                    if(getDictItem(deviceConfig,'environment','upload_queue',"0") == "-1"):
                        self.listdata.clear()
                        self.listname.clear()
                        self.listtype.clear()
                        self.states["data_List_Flag"] = False
                    writeConfig('d','environment','upload_queue',len(self.listdata)) 
                    if(getRamFree() < self.ramLimit + self.ramAlarm):
                        ledStatusUpload(2,3,"RAM")
                #------------------------------#
                minProcT=self.minProcTime
                #---------upload proc. alive?----------#
                if uploadF_alive_flag == True:
                    uploadF_alive_flag = self.FTP_upload_Proc.is_alive()
                    if uploadF_alive_flag:
                        if (time.time() - uploadF_pretime) > FTP_upload_timeout:
                            print("FTP timeout, terminate.",FTP_upload_timeout)
                            self.FTP_upload_Proc.terminate()
                            uploadF_alive_flag = False
                            ledStatusUpload(2,2,"FTP Timeout.")
                            if not self.FTP_upload_Proc.get_upload_error_flag():
                                if not localfile_process_flag:
                                    #---------------saved in local when timeout------------#
                                    upload_payload, sampling_time, file_name = transFormatUpload(data,workini,name,Type)
                                    data.setdefault('file_name',file_name)
                                    data.setdefault(name,Type)
                                    if Type == self.type_std[0]:
                                        sampling_time = datetime.fromtimestamp(sampling_time)
                                        timeStr = sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                                        timeStr = "Seg_"+timeStr
                                    elif Type == self.type_std[1]:
                                        timeStr = datetime.strptime(sampling_time,"%Y/%m/%d %H:%M:%S")
                                        timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                                        timeStr = "FE_"+timeStr
                                    fileName="LocalSaved_"+timeStr+"_"+name+".pkl"
                                    if(getRomFree() < self.romLimit):
                                        if(glob.glob(path_dir+'*') != []):
                                            first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                                            os.remove(first_file)
                                    print("Timeout. FTP upload failed. Saved file : "  + "F_" +  fileName)
                                    pickle.dump(data,open(path_dir+"F_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                                    del upload_payload
                                    #del data

                elif uploadA_alive_flag == True:
                    uploadA_alive_flag = self.API_upload_Proc.is_alive()
                    if uploadA_alive_flag:
                        if (time.time() - uploadA_pretime) > API_upload_timeout:
                            print("API timeout, terminate.",API_upload_timeout)
                            self.API_upload_Proc.terminate()
                            uploadA_alive_flag = False
                            ledStatusUpload(2,2,"API Timeout.")
                            if not self.API_upload_Proc.get_upload_error_flag():
                                if not localfile_process_flag:
                                    #---------------saved in local when timeout------------#
                                    upload_payload, sampling_time, file_name = transFormatUpload(data,workini,name,Type)
                                    data.setdefault(name,Type)
                                    if Type == self.type_std[0]:
                                        sampling_time = datetime.fromtimestamp(sampling_time)
                                        timeStr = sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                                        timeStr = "Seg_"+timeStr
                                    elif Type == self.type_std[1]:
                                        timeStr = datetime.strptime(sampling_time,"%Y/%m/%d %H:%M:%S")
                                        timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                                        timeStr = "FE_"+timeStr
                                    fileName="LocalSaved_"+timeStr+"_"+name+".pkl"
                                    if(getRomFree() < self.romLimit):
                                        if(glob.glob(path_dir+'*') != []):
                                            first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                                            os.remove(first_file)
                                    print("Timeout.API upload failed. Saved file : "  + "F_" +  fileName)
                                    pickle.dump(data,open(path_dir+"A_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                                    del upload_payload
                                    #del data
                elif uploadM_alive_flag == True:
                    uploadM_alive_flag = self.MQTT_upload_Proc.is_alive()
                    if uploadM_alive_flag:
                        if (time.time() - uploadM_pretime) > MQTT_upload_timeout:
                            print("MQTT timeout, terminate.",MQTT_upload_timeout)
                            self.MQTT_upload_Proc.terminate()
                            uploadM_alive_flag = False
                            ledStatusUpload(2,2,"MQTT Timeout.")
                            if not self.MQTT_upload_Proc.get_upload_error_flag():
                                if not localfile_process_flag:
                                    timeStr = data["Report_Time"]["0"]
                                    timeStr = datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S")
                                    timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                                    fileName="LocalSaved_"+timeStr+"_"+name+".pkl"
                                    if(getRomFree() < self.romLimit):
                                        if(glob.glob(path_dir+'*') != []):
                                            first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                                            os.remove(first_file)
                                    print("Timeout.MQTT upload failed. Saved file : " + "M_"+ fileName)
                                    pickle.dump(data,open(path_dir+"M_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                else:
                    if localfile_process_flag == True:
                        localfile_process_flag = False
                        if(Upload_label == "F_") and (uploadF_error_flag == False):
                            self.local_upload_error_flag |= self.FTP_upload_Proc.get_upload_error_flag()
                        elif(Upload_label == "A_") and (uploadA_error_flag == False):
                            self.local_upload_error_flag |= self.API_upload_Proc.get_upload_error_flag()
                        elif(Upload_label == "M_") and (uploadM_error_flag == False):
                            self.local_upload_error_flag |= self.MQTT_upload_Proc.get_upload_error_flag()
                        if not self.local_upload_error_flag:
                            os.remove(first_file)
                            print("Local upload success, Remove Local " + first_file)
                        else:
                            print("Local upload Error - " + first_file + ", file reserved.")
                    #return upload count process
                    if (havebeen_upload_flag):
                        if self.FTP_Enable != 0 and Type != self.type_std[2]:
                            self.states["upload_config_flag"] = self.FTP_upload_Proc.get_upload_config_flag()
                        if not self.local_upload_flag:
                            if (Type != self.type_std[2]):
                                if(self.FTP_Enable != 0):
                                    if not uploadF_error_flag:
                                        t_F_S_csv_s,t_F_S_csv_f,t_F_F_csv_s,t_F_F_csv_f,\
                                        t_F_S_pkl_s,t_F_S_pkl_f,t_F_F_pkl_s,t_F_F_pkl_f =self.FTP_upload_Proc.get_upload_count()
                                        F_Seg_uploadcsv_success += t_F_S_csv_s
                                        F_Seg_uploadcsv_failed += t_F_S_csv_f
                                        F_FE_uploadcsv_success += t_F_F_csv_s
                                        F_FE_uploadcsv_failed += t_F_F_csv_f
                                        F_Seg_uploadpkl_success += t_F_S_pkl_s
                                        F_Seg_uploadpkl_failed += t_F_S_pkl_f
                                        F_FE_uploadpkl_success += t_F_F_pkl_s
                                        F_FE_uploadpkl_failed += t_F_F_pkl_f
                                if(self.API_Enable != 0):
                                    if not uploadA_error_flag:
                                        t_A_S_s,t_A_S_f,t_A_F_s,t_A_F_f=self.API_upload_Proc.get_upload_count()
                                        A_Seg_upload_success+=t_A_S_s
                                        A_FE_upload_success+=t_A_F_s
                            else:
                                uploadM_error_flag = self.MQTT_upload_Proc.get_upload_error_flag()
                                if not uploadM_error_flag:
                                    MQTT_upload_success+=self.MQTT_upload_Proc.get_upload_count()
                        else:
                            if(Upload_label == "F_") and (uploadF_error_flag == False):
                                t_F_S_csv_s,t_F_S_csv_f,t_F_F_csv_s,t_F_F_csv_f,\
                                t_F_S_pkl_s,t_F_S_pkl_f,t_F_F_pkl_s,t_F_F_pkl_f =self.FTP_upload_Proc.get_upload_count()
                                F_Seg_uploadcsv_success += t_F_S_csv_s
                                F_FE_uploadcsv_success += t_F_F_csv_s
                                F_Seg_uploadpkl_success += t_F_S_pkl_s
                                F_FE_uploadpkl_success += t_F_F_pkl_s
                            elif(Upload_label == "A_") and (uploadA_error_flag == False):
                                t_A_S_s,t_A_S_f,t_A_F_s,t_A_F_f=self.API_upload_Proc.get_upload_count()
                                A_Seg_upload_success+=t_A_S_s
                                A_FE_upload_success+=t_A_F_s
                            elif(Upload_label == "M_") and (uploadM_error_flag == False):
                                MQTT_upload_success+=self.MQTT_upload_Proc.get_upload_count()
                        havebeen_upload_flag = False
                    
                    #if done current job and upload have been release, break loop.
                    if self.states["release"] and self.queueData.empty() and self.states["data_List_Flag"]==False:
                        print("Work done, break while_loop.")
                        break
                    
                    #Check queue have data ?        
                    if not self.queueData.empty() or (self.states["data_List_Flag"]):
                        uploadF_alive_flag, uploadA_alive_flag, uploadM_alive_flag, FTP_upload_timeout, API_upload_timeout, MQTT_upload_timeout, uploadF_error_flag, uploadA_error_flag, data, name, Type, dataprocess_break_flag= self.data_process()
                        uploadF_pretime = time.time()
                        uploadA_pretime = time.time()
                        uploadM_pretime = time.time()
                        if(dataprocess_break_flag == 0):
                            if Type == self.type_std[0]:
                                self.states["Seg_queue_data_count"] += 1
                                havebeen_upload_flag = True
                            elif Type == self.type_std[1]:
                                self.states["FE_queue_data_count"] += 1
                                havebeen_upload_flag = True
                            elif Type == self.type_std[2]:
                                self.states["MQTT_queue_data_count"] += 1
                                havebeen_upload_flag = True
                            self.local_upload_flag = False
                            print(FTP_upload_timeout,API_upload_timeout,MQTT_upload_timeout)
                            
                    #-----------upload local data when idle--------------#
                    else:
                        if(glob.glob(path_dir+'*') != []):
                            first_file = random.choice(glob.glob(path_dir+'*'))
                            if(os.path.getsize(first_file) == 0):
                                print(first_file,"0 bytes data, remove it.")
                                os.remove(first_file)
                            try:
                                Upload_label = str(first_file[Upload_label_startCount:Upload_label_startCount+2])
                                self.local_upload_flag = True
                                self.local_upload_error_flag = False
                                print("Upload local data when idle")
                                if Upload_label != 'M_':
                                    data = pickle.load(open(first_file,'rb'))
                                    for key in data.keys():
                                        name_key = key
                                    name = name_key
                                    Type = data[name_key]
                                    del data[name_key]
                                    #rule check
                                    rule_check_flag = False
                                    for key in workini.keys():
                                        ruleName = "@".join([
                                            getDictItem(workini,key,"name",""),
                                            getDictItem(workini,key,"unit",""),
                                            getDictItem(workini,key,"sub_unit","")
                                            ])
                                        if name in ruleName:
                                            rule_check_flag = True
                                    if not rule_check_flag:
                                        print(first_file,"not found rule, removed.")
                                        os.remove(first_file)
                                        continue
                                    #--------------------FTP upload---------------------#
                                    if (Upload_label == "F_"):
                                        try:
                                            file_name = data['file_name']
                                            del data['file_name']
                                            upload_payload, sampling_time, file_name = transFormatUpload(data,self.workini,name,Type)
                                            if Type == self.type_std[0]:
                                                sampling_time = datetime.fromtimestamp(sampling_time)
                                            uploadF_pretime = time.time()
                                            self.FTP_upload_Proc = FTP_upload(path_dir,self.FTP_HOST,self.FTP_USER,self.FTP_PASS,self.FTP_Mode,data,name,Type,sampling_time,file_name,self.local_upload_flag,self.states["upload_config_flag"])
                                            self.FTP_upload_Proc.start()
                                            uploadF_error_flag = False
                                            temp = BytesIO()
                                            pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                                            FTP_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                                            del temp
                                        except Exception as e:
                                            print(e)
                                            uploadF_error_flag = True
                                            self.local_upload_error_flag = True
                                            ledStatusUpload(2,2,"FTP - "+str(e))
                                    #--------------------API upload---------------------#
                                    elif (Upload_label == "A_"):
                                        try:
                                            upload_payload, sampling_time, file_name = transFormatUpload(data,self.workini,name,Type)
                                            #Seg
                                            if Type == self.type_std[0]:
                                                sampling_time = datetime.fromtimestamp(sampling_time)
                                                if self.API_URL[-1] != '/':
                                                    api_url = self.API_URL + "/segment"
                                                else:
                                                    api_url = self.API_URL + "segment"
                                            #FE
                                            else:
                                                if self.API_URL[-1] != '/':
                                                    api_url = self.API_URL + "/feature"
                                                else:
                                                    api_url = self.API_URL + "feature"
                                            uploadA_pretime = time.time()
                                            self.API_upload_Proc = API_upload(path_dir,api_url,self.API_PROXY,upload_payload,data,name,Type,sampling_time,self.local_upload_flag)
                                            self.API_upload_Proc.start()
                                            uploadA_error_flag = False
                                            temp = BytesIO()
                                            pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                                            API_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                                            del temp
                                        except Exception as e:
                                            print(e)
                                            uploadA_error_flag = True
                                            self.local_upload_error_flag = True
                                            ledStatusUpload(2,2,"API - "+str(e))
                                #--------------------MQTT upload---------------------#
                                else:
                                    try:
                                        data = pickle.load(open(first_file,'rb'))
                                        mqtt_url = self.MQTT_URL
                                        uploadM_pretime = time.time()
                                        self.MQTT_upload_Proc = MQTT_upload(path_dir,name,self.MQTT_URL,self.MQTT_PORT,self.MQTT_TOPIC,self.MQTT_NAME,self.MQTT_PSWD,data,self.local_upload_flag)
                                        self.MQTT_upload_Proc.start()
                                        uploadM_error_flag = False
                                        temp = BytesIO()
                                        pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                                        MQTT_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                                        del temp
                                    except Exception as e:
                                        print(e)
                                        uploadM_error_flag = True
                                        self.local_upload_error_flag = True
                                        ledStatusUpload(2,2,"MQTT - "+str(e))
                                #------------------Release-------------------------#
                                havebeen_upload_flag = True
                                if(Upload_label == "F_") and (uploadF_error_flag == False):
                                    uploadF_alive_flag = self.FTP_upload_Proc.is_alive()
                                    localfile_process_flag = True
                                elif(Upload_label == "A_") and (uploadA_error_flag == False):
                                    uploadA_alive_flag = self.API_upload_Proc.is_alive()
                                    localfile_process_flag = True
                                elif(Upload_label == "M_") and (uploadM_error_flag == False):
                                    uploadM_alive_flag = self.MQTT_upload_Proc.is_alive()
                                    localfile_process_flag = True
                            except Exception as e:
                                print(e)
                endTime=time.time()
                if endTime-startTime<minProcT:
                    time.sleep(minProcT-(endTime-startTime))
                gc.collect()
            except Exception as e:
                errTime = datetime.strftime(datetime.now(),'%Y_%m_%d_%H_%M_%S')
                pickle.dump(data,open("/home/pi/program/Err_" + errTime,'wb'),protocol=pickle.HIGHEST_PROTOCOL)

        #upload local data
        if(glob.glob(path_dir+'*') != []):
            #upload all files in local
            print("upload all files in local")
            for f in glob.glob(path_dir+'*'):
                first_file = f
                if(os.path.getsize(first_file) == 0):
                    print(first_file,"0 bytes data, remove it.")
                    os.remove(first_file)
                try:
                    Upload_label = str(first_file[Upload_label_startCount:Upload_label_startCount+2])
                    self.local_upload_flag = True
                    self.local_upload_error_flag = False
                    if Upload_label != "M_":
                        data = pickle.load(open(first_file,'rb'))
                        for key in data.keys():
                            name_key = key
                        name = name_key
                        Type = data[name_key]
                        del data[name_key]
                        #rule check
                        rule_check_flag = False
                        for key in workini.keys():
                            ruleName = "@".join([
                                getDictItem(workini,key,"name",""),
                                getDictItem(workini,key,"unit",""),
                                getDictItem(workini,key,"sub_unit","")
                                ])
                            if name in ruleName:
                                rule_check_flag = True
                        if not rule_check_flag:
                            print(first_file,"not found rule, removed.")
                            os.remove(first_file)
                            continue
                        #--------------------FTP upload---------------------#
                        if (Upload_label == "F_"):
                            try:
                                file_name = data['file_name']
                                del data['file_name']
                                uploadF_error_flag = False
                                upload_payload, sampling_time, file_name = transFormatUpload(data,self.workini,name,Type)
                                if Type == self.type_std[0]:
                                    sampling_time = datetime.fromtimestamp(sampling_time)
                                uploadF_pretime = time.time()
                                FTP_upload_Proc = FTP_upload(path_dir,self.FTP_HOST,self.FTP_USER,self.FTP_PASS,self.FTP_Mode,data,name,Type,sampling_time,file_name,self.local_upload_flag,self.states["upload_config_flag"])
                                FTP_upload_Proc.start()
                                temp = BytesIO()
                                pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                                FTP_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                                del data
                                del temp
                                del upload_payload
                            except Exception as e:
                                ledStatusUpload(2,2,"FTP - "+str(e))
                                print(e)
                                uploadF_error_flag = True
                                self.local_upload_error_flag = True
                        
                        #--------------------API upload---------------------#
                        if (Upload_label == "A_"):
                            try:
                                uploadA_error_flag = False
                                upload_payload, sampling_time, file_name = transFormatUpload(data,self.workini,name,Type)
                                #Seg
                                if Type == self.type_std[0]:
                                    sampling_time = datetime.fromtimestamp(sampling_time)
                                    if self.API_URL[-1] != '/':
                                        api_url = self.API_URL + "/segment"
                                    else:
                                        api_url = self.API_URL + "segment"
                                #FE
                                else:
                                    if self.API_URL[-1] != '/':
                                        api_url = self.API_URL + "/feature"
                                    else:
                                        api_url = self.API_URL + "feature"
                                uploadA_pretime = time.time()
                                API_upload_Proc = API_upload(path_dir,api_url,self.API_PROXY,upload_payload,data,name,Type,sampling_time,self.local_upload_flag)
                                API_upload_Proc.start()
                                temp = BytesIO()
                                pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                                API_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                                del data
                                del temp
                                del upload_payload
                            except Exception as e:
                                ledStatusUpload(2,2,"API - "+str(e))
                                print(e)
                                uploadA_error_flag = True
                                self.local_upload_error_flag = True
                    #--------------------MQTT upload---------------------#
                    else:
                        try:
                            uploadM_error_flag = False
                            data = pickle.load(open(first_file,'rb'))
                            mqtt_url = self.MQTT_URL
                            uploadM_pretime = time.time()
                            MQTT_upload_Proc = MQTT_upload(path_dir,name,self.MQTT_URL,self.MQTT_PORT,self.MQTT_TOPIC,self.MQTT_NAME,self.MQTT_PSWD,data,self.local_upload_flag)
                            MQTT_upload_Proc.start()
                            temp = BytesIO()
                            pickle.dump(data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                            MQTT_upload_timeout = temp.getbuffer().nbytes*8 / self.upload_speed_std + self.const_Timeout
                            del data
                            del temp
                        except Exception as e:
                            print(e)
                            uploadM_error_flag = True
                            self.local_upload_error_flag = True
                            ledStatusUpload(2,2,"MQTT - "+str(e))
                    #------------------Release-------------------------#
                    if(Upload_label == "F_") and (uploadF_error_flag == False):
                        while(FTP_upload_Proc.is_alive()):
                            if (time.time() - uploadF_pretime) > FTP_upload_timeout:
                                print("FTP timeout, terminate.",FTP_upload_timeout)
                                FTP_upload_Proc.terminate()
                                self.local_upload_error_flag = True
                                ledStatusUpload(2,2,"FTP timeout.")
                                break
                            time.sleep(0.5)
                        if not self.local_upload_error_flag:
                            self.states["upload_config_flag"] = FTP_upload_Proc.get_upload_config_flag()
                            t_F_S_csv_s,t_F_S_csv_f,t_F_F_csv_s,t_F_F_csv_f,\
                            t_F_S_pkl_s,t_F_S_pkl_f,t_F_F_pkl_s,t_F_F_pkl_f =FTP_upload_Proc.get_upload_count()
                            F_Seg_uploadcsv_success += t_F_S_csv_s
                            F_Seg_uploadcsv_failed += t_F_S_csv_f
                            F_FE_uploadcsv_success += t_F_F_csv_s
                            F_FE_uploadcsv_failed += t_F_F_csv_f
                            F_Seg_uploadpkl_success += t_F_S_pkl_s
                            F_Seg_uploadpkl_failed += t_F_S_pkl_f
                            F_FE_uploadpkl_success += t_F_F_pkl_s
                            F_FE_uploadpkl_failed += t_F_F_pkl_f
                        self.local_upload_error_flag |= FTP_upload_Proc.get_upload_error_flag()
                    elif(Upload_label == "A_") and (uploadA_error_flag == False):
                        while(API_upload_Proc.is_alive()):
                            if (time.time() - uploadA_pretime) > API_upload_timeout:
                                print("API timeout, terminate.",API_upload_timeout)
                                API_upload_Proc.terminate()
                                self.local_upload_error_flag = True
                                ledStatusUpload(2,2,"API timeout.")
                                break
                                
                            time.sleep(0.5)
                        if not self.local_upload_error_flag:
                            t_A_S_s,t_A_S_f,t_A_F_s,t_A_F_f=API_upload_Proc.get_upload_count()
                            A_Seg_upload_success+=t_A_S_s
                            A_FE_upload_success+=t_A_F_s
                        self.local_upload_error_flag |= API_upload_Proc.get_upload_error_flag()
                    elif(Upload_label == "M_") and (uploadM_error_flag == False):
                        while(MQTT_upload_Proc.is_alive()):
                            if (time.time() - uploadM_pretime) > MQTT_upload_timeout:
                                print("MQTT timeout, terminate.",MQTT_upload_timeout)
                                MQTT_upload_Proc.terminate()
                                self.local_upload_error_flag = True
                                ledStatusUpload(2,2,"MQTT timeout.")
                                break
                            time.sleep(0.5)
                        if not self.local_upload_error_flag:
                            MQTT_upload_success+=MQTT_upload_Proc.get_upload_count()
                        self.local_upload_error_flag |= MQTT_upload_Proc.get_upload_error_flag()
                        
                    if not self.local_upload_error_flag:
                        os.remove(first_file)
                        print("Local upload success, Remove Local " + first_file)
                    else:
                        print("Local upload Error - " + first_file + ", file reserved.")
                    
                    gc.collect()
                except Exception as e:
                    print(e)
                    
        if self.testFlag :
            if (self.FTP_Mode == 1) or (self.FTP_Mode == 3) :
                F_Seg_uploadcsv_failed = self.states["Seg_queue_data_count"] - F_Seg_uploadcsv_success
                F_FE_uploadcsv_failed = self.states["FE_queue_data_count"] - F_FE_uploadcsv_success
            if (self.FTP_Mode == 2) or (self.FTP_Mode == 3):
                F_Seg_uploadpkl_failed = self.states["Seg_queue_data_count"] - F_Seg_uploadpkl_success
                F_FE_uploadpkl_failed = self.states["FE_queue_data_count"] - F_FE_uploadpkl_success
            if (self.API_Enable):
                A_Seg_upload_failed = self.states["Seg_queue_data_count"] - A_Seg_upload_success           
                A_FE_upload_failed = self.states["FE_queue_data_count"] - A_FE_upload_success
            MQTT_upload_failed = self.states["MQTT_queue_data_count"] - MQTT_upload_success
            
            if self.FTP_Enable != 0:
                print("FTP upload count:",F_Seg_uploadcsv_success,F_Seg_uploadcsv_failed,F_FE_uploadcsv_success,F_FE_uploadcsv_failed,\
                F_Seg_uploadpkl_success,F_Seg_uploadpkl_failed,F_FE_uploadpkl_success,F_FE_uploadpkl_failed,self.states["Seg_queue_data_count"],self.states["FE_queue_data_count"])
            else:
                print("FTP not upload")
            if self.API_Enable != 0:
                print("API upload count:",A_Seg_upload_success,A_Seg_upload_failed,A_FE_upload_success,A_FE_upload_failed,self.states["Seg_queue_data_count"],self.states["FE_queue_data_count"])
            else:
                print("API not upload")
            if self.states["MQTT_queue_data_count"] > 0:
                print("MQTT upload count:",MQTT_upload_success,MQTT_upload_failed,self.states["MQTT_queue_data_count"])
            else:
                print("MQTT not upload")
                
            writeConfig("d","environment","upload_ftp_seg_csv","{:d}/{:d}".format(F_Seg_uploadcsv_success,F_Seg_uploadcsv_success+F_Seg_uploadcsv_failed))
            writeConfig("d","environment","upload_ftp_fe_csv","{:d}/{:d}".format(F_FE_uploadcsv_success,F_FE_uploadcsv_success+F_FE_uploadcsv_failed))
            writeConfig("d","environment","upload_ftp_seg_pkl","{:d}/{:d}".format(F_Seg_uploadpkl_success,F_Seg_uploadpkl_success+F_Seg_uploadpkl_failed))
            writeConfig("d","environment","upload_ftp_fe_pkl","{:d}/{:d}".format(F_FE_uploadpkl_success,F_FE_uploadpkl_success+F_FE_uploadpkl_failed))
            writeConfig("d","environment","upload_api_seg","{:d}/{:d}".format(A_Seg_upload_success,A_Seg_upload_success+A_Seg_upload_failed))
            writeConfig("d","environment","upload_api_fe","{:d}/{:d}".format(A_FE_upload_success,A_FE_upload_success+A_FE_upload_failed))
            writeConfig("d","environment","upload_mqtt","{:d}/{:d}".format(MQTT_upload_success,MQTT_upload_success+MQTT_upload_failed))
            
            
    def release(self,callback=None):
        self.stopProc()
        while self.is_alive():
            time.sleep(1)
            if callback != None:
                callback()
            #self.join()
        self.exit.set()

class FTP_upload(multiprocessing.Process):
    def __init__(self,path,host,userid,pswd,mode,data,name,Type,sampling_time,file_name,localdata_flag,upload_config_flag):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        #FTP Params
        self.path = path
        self.host = host
        self.userid = userid
        self.pswd = pswd
        self.FTP_Mode = mode
        self.data = data
        self.name = name
        try:
            splitName = name.split("@",2)
            self.FTPToolID = splitName[0]
            self.FTPnamePath = splitName[0]+"_"+splitName[1]+splitName[2]
        except:
            self.FTPToolID = "Unknown"
            self.FTPnamePath = "Unknown"
        
        self.Type = Type
        self.type_std = ['seg','FE','mqtt']
        self.sampling_time = sampling_time
        self.file_name = file_name
        self.local_upload_flag = localdata_flag
        manager=multiprocessing.Manager()
        self.states=manager.dict()
        self.states["config_flag"] = upload_config_flag
        #except flag
        self.states["local_uploadF_error_flag"]=False
        #ROM limit
        self.romLimit = 512
        #Upload status count
        self.states["Seg_uploadcsv_success"]=0
        self.states["Seg_uploadcsv_failed"]=0
        self.states["FE_uploadcsv_success"]=0
        self.states["FE_uploadcsv_failed"]=0
        self.states["Seg_uploadpkl_success"]=0
        self.states["Seg_uploadpkl_failed"]=0
        self.states["FE_uploadpkl_success"]=0
        self.states["FE_uploadpkl_failed"]=0
        print("FTP upload create")
        del data
        gc.collect()
    
    def get_upload_config_flag(self):
        return self.states["config_flag"]
    
    def get_upload_error_flag(self):
        return self.states["local_uploadF_error_flag"]
        
    def get_upload_count(self):
        return self.states["Seg_uploadcsv_success"],self.states["Seg_uploadcsv_failed"],self.states["FE_uploadcsv_success"],self.states["FE_uploadcsv_failed"],\
        self.states["Seg_uploadpkl_success"],self.states["Seg_uploadpkl_failed"],self.states["FE_uploadpkl_success"],self.states["FE_uploadpkl_failed"]
    
    def cd_dir(self,path):
        if path != "":
            try:
                self.ftp.cwd("/"+path)
                print("found ftp folder.")
            except:
                self.cd_dir("/".join(path.split("/")[:-1]))
                self.ftp.mkd("/"+path)
                self.ftp.cwd("/"+path)
                print("Not found ftp folder, create " + path)
    
        
    def run(self):
        try:
            path_dir = self.path
            self.ftp = ftplib.FTP(self.host, self.userid, self.pswd)
            if self.userid == '':
                self.ftp.login()
            self.ftp.encoding = "utf-8"
            if self.data != '':
                #CSV mode
                if (self.FTP_Mode == 1) or (self.FTP_Mode == 3):
                    temp1 = StringIO()
                    if self.Type == self.type_std[0]:
                        pd_data = dataObj2pd(self.data)
                    elif self.Type == self.type_std[1]:
                        pd_data = dataObjTrans_FE(self.data)
                    pd_data.to_csv(temp1,index=False,encoding='utf-8')
                    temp1.seek(0)
                    temp = BytesIO(temp1.read().encode('utf8'))
                    temp.seek(0)
                    #now = datetime.now() # current date and time
                    if self.Type == self.type_std[0]:
                        path = "Segmentation/" + self.FTPnamePath + "/" + self.sampling_time.strftime("%Y") + "/" + self.sampling_time.strftime("%m%d")
                        timeStr = self.sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                        timeStr = "Seg_"+timeStr
                    elif self.Type == self.type_std[1]:
                        timeStr = datetime.strptime(self.sampling_time,"%Y/%m/%d %H:%M:%S")
                        path = "Extraction/" + self.FTPnamePath + "/" + timeStr.strftime("%Y") + "/" + timeStr.strftime("%m%d")
                        timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                        timeStr = "FE_"+timeStr
                    fileName=self.file_name+".csv"
                    self.cd_dir(path)
                    #self.ftp.storbinary("STOR "+fileName, temp)
                    self.ftp.storbinary("STOR "+ '/' +path + '/' + fileName, temp)
                    self.states["local_uploadF_error_flag"]=False
                    print("FTP Mode1 upload success." + fileName)
                    if self.Type == self.type_std[0]:
                        self.states["Seg_uploadcsv_success"]+=1
                    elif self.Type == self.type_std[1]:
                        self.states["FE_uploadcsv_success"]+=1
                    ledStatusUpload(2,1,"")
                    writeConfig('d','environment','time_ftp',time.time())
                    del temp
                    del temp1
                #pickle mode
                if (self.FTP_Mode == 2) or (self.FTP_Mode == 3):
                    temp = BytesIO()
                    pickle.dump(self.data,temp,protocol=pickle.HIGHEST_PROTOCOL)
                    temp.seek(0)
                    #now = datetime.now() # current date and time
                    if self.Type == self.type_std[0]:
                        path = "Segmentation/" + self.FTPnamePath + "/" + self.sampling_time.strftime("%Y") + "/" + self.sampling_time.strftime("%m%d")
                        timeStr = self.sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                        timeStr = "Seg_"+timeStr
                    elif self.Type == self.type_std[1]:
                        timeStr = datetime.strptime(self.sampling_time,"%Y/%m/%d %H:%M:%S")
                        path = "Extraction/" + self.FTPnamePath + "/" + timeStr.strftime("%Y") + "/" + timeStr.strftime("%m%d")
                        timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                        timeStr = "FE_"+timeStr
                    fileName=self.file_name+".pkl"
                    self.cd_dir(path)
                    #self.ftp.storbinary("STOR "+fileName, temp)
                    self.ftp.storbinary("STOR "+ '/' +path + '/' + fileName, temp)
                    self.states["local_uploadF_error_flag"]=False
                    print("FTP Mode2 upload success." + fileName)
                    if self.Type == self.type_std[0]:
                        self.states["Seg_uploadpkl_success"]+=1
                    elif self.Type == self.type_std[1]:
                        self.states["FE_uploadpkl_success"]+=1
                    ledStatusUpload(2,1,"")
                    writeConfig('d','environment','time_ftp',time.time())
                    del temp
            #config upload flag    
            if not self.states["config_flag"]:
                try:
                    d = [requests.get('http://127.0.0.1/api/work/file'),requests.get('http://127.0.0.1/api/system/file')]
                    
                    path = "Raspberry_Detail/" + self.FTPToolID
                    self.cd_dir(path)
                    fileName = ['work.ini','system.ini']
                    for i in range(2):
                        temp1 = StringIO(d[i].text)
                        temp1.seek(0)
                        temp = BytesIO(temp1.read().encode('utf8'))
                        temp.seek(0)
                        if path_dir == self.path+'/T_LocalSaved/':
                            fname = fileName[i]
                        else:
                            fname = datetime.now().strftime("%Y_%m_%d_%H_%M_%S-") + fileName[i]
                        self.ftp.storbinary("STOR "+ '/' +path + '/' + fname, temp)
                        print(fname,", Saved in FTP.")
                    self.states["config_flag"] = True
                    writeConfig('d','environment','time_ftp',time.time())
                    del temp
                    del temp1
                except Exception as e:
                    print(e)
        #Error -> saved in local / put queue
        except Exception as e:
            ledStatusUpload(2,2,"FTP - "+str(e))
            print(e)
            self.states["local_uploadF_error_flag"] = True
            if self.Type == self.type_std[0]:
                if (self.FTP_Mode == 1) or (self.FTP_Mode == 3):
                    self.states["Seg_uploadcsv_failed"]+=1
                if (self.FTP_Mode == 2) or (self.FTP_Mode == 3):
                    self.states["Seg_uploadpkl_failed"]+=1
            elif self.Type == self.type_std[1]:
                if (self.FTP_Mode == 1) or (self.FTP_Mode == 3):
                    self.states["FE_uploadcsv_failed"]+=1
                if (self.FTP_Mode == 2) or (self.FTP_Mode == 3):
                    self.states["FE_uploadpkl_failed"]+=1        
            
            if(self.local_upload_flag == False):
                #now = datetime.now() # current date and time
                self.data.setdefault('file_name',self.file_name)
                self.data.setdefault(self.name,self.Type)
                if self.Type == self.type_std[0]:
                    timeStr = self.sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                    timeStr = "Seg_"+timeStr
                elif self.Type == self.type_std[1]:
                    timeStr = datetime.strptime(self.sampling_time,"%Y/%m/%d %H:%M:%S")
                    timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                    timeStr = "FE_"+timeStr
                fileName="LocalSaved_"+timeStr+"_"+self.name+".pkl"
                if(getRomFree() < self.romLimit):
                    if(glob.glob(path_dir+'*') != []):
                        first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                        os.remove(first_file)
                print("In-FTP upload failed. Saved file : " + "F_" + fileName)
                pickle.dump(self.data,open(path_dir+"F_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
        del self.data
        gc.collect()
    def release(self):
        if self.is_alive():
            self.join()
        self.exit.set()
        
class API_upload(multiprocessing.Process):
    def __init__(self,path,url,proxy,up_format,data,name,Type,sampling_time,localdata_flag):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        #API params
        self.path = path
        self.url = url
        self.proxy = proxy
        self.upload_data = up_format
        self.data = data
        self.name = name
        self.Type = Type
        self.type_std = ['seg','FE','mqtt']
        self.sampling_time = sampling_time
        self.local_upload_flag = localdata_flag
        #ROM limit
        self.romLimit = 512
        #upload status count
        manager=multiprocessing.Manager()
        self.states=manager.dict()
        self.states["local_uploadA_error_flag"]=False
        self.states["Seg_upload_success"]=0
        self.states["Seg_upload_failed"]=0
        self.states["FE_upload_success"]=0
        self.states["FE_upload_failed"]=0
        print("API upload create")
        del up_format
        del data
        gc.collect()
        
    def get_upload_error_flag(self):
        return self.states["local_uploadA_error_flag"]
        
    def get_upload_count(self):
        return self.states["Seg_upload_success"],self.states["Seg_upload_failed"],self.states["FE_upload_success"],self.states["FE_upload_failed"]
        
    def run(self):
        try:
            path_dir = self.path
            error_count = 0
            #API upload
            #print(self.upload_data)
            if self.proxy == '':
                d = requests.post(url=self.url,json=self.upload_data)
            elif self.url[0:5] == 'https':
                d = requests.post(url=self.url,proxies={"https":self.proxy},json=self.upload_data)
            else:
                d = requests.post(url=self.url,proxies={"http":self.proxy},json=self.upload_data)
            #return_code = d.text[8:11]
            print("API upload return code : " + str(d.status_code))
            if(d.status_code != 200):
                ledStatusUpload(2,2,"API - " + str(d.text))
                if(d.status_code != 500):
                    while(error_count <=3):
                        if self.proxy == '':
                            d = requests.post(url=self.url,json=self.upload_data)
                        elif self.url[0:5] == 'https':
                            d = requests.post(url=self.url,proxies={"https":self.proxy},json=self.upload_data)
                        else:
                            d = requests.post(url=self.url,proxies={"http":self.proxy},json=self.upload_data)
                        #return_code = d.text[8:11]
                        print("API upload return code : " + str(d.status_code))
                        if(d.status_code == 200):
                            self.states["local_uploadA_error_flag"]=False
                            break
                        error_count+=1
                        if error_count == 3:
                            self.states["local_uploadA_error_flag"] = True
                            if(self.local_upload_flag == False):
                                self.data.setdefault(self.name,self.Type)
                                if self.Type == self.type_std[0]:
                                    timeStr = self.sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                                    timeStr = "Seg_"+timeStr
                                elif self.Type == self.type_std[1]:
                                    timeStr = datetime.strptime(self.sampling_time,"%Y/%m/%d %H:%M:%S")
                                    timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                                    timeStr = "FE_"+timeStr

                                fileName="LocalSaved_"+timeStr+"_"+self.name+".pkl"
                                if(getRomFree() < self.romLimit):
                                    if(glob.glob(path_dir+'*') != []):
                                        first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                                        os.remove(first_file)
                                print("In-API upload failed. Saved file : " + "A_"+ fileName)
                                pickle.dump(self.data,open(path_dir+"A_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                            if self.Type == self.type_std[0]:
                                self.states["Seg_upload_failed"]+=1
                            elif self.Type == self.type_std[1]:
                                self.states["FE_upload_failed"]+=1
                else:
                    self.states["local_uploadA_error_flag"] = True 
                    if(self.local_upload_flag == False):
                        self.data.setdefault(self.name,self.Type)
                        if self.Type == self.type_std[0]:
                            timeStr = self.sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "Seg_"+timeStr
                        elif self.Type == self.type_std[1]:
                            timeStr = datetime.strptime(self.sampling_time,"%Y/%m/%d %H:%M:%S")
                            timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                            timeStr = "FE_"+timeStr
                        fileName="LocalSaved_"+timeStr+"_"+self.name+".pkl"
                        if(getRomFree() < self.romLimit):
                            if(glob.glob(path_dir+'*') != []):
                                first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                                os.remove(first_file)
                        print("In-API upload failed. Saved file : " + "A_"+ fileName)
                        pickle.dump(self.data,open(path_dir+"A_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
                    if self.Type == self.type_std[0]:
                        self.states["Seg_upload_failed"]+=1
                    elif self.Type == self.type_std[1]:
                        self.states["FE_upload_failed"]+=1
            else:
                ledStatusUpload(2,1,"")
                if self.Type == self.type_std[0]:
                    self.states["Seg_upload_success"]+=1
                elif self.Type == self.type_std[1]:
                    self.states["FE_upload_success"]+=1
                self.states["local_uploadA_error_flag"]=False
                writeConfig('d','environment','time_api',time.time())
        #Error -> saved in local / put queue
        except Exception as e:
            ledStatusUpload(2,2,"API - " + str(e))
            print(e)
            self.states["local_uploadA_error_flag"] = True
            if(self.local_upload_flag == False):
                self.data.setdefault(self.name,self.Type)
                if self.Type == self.type_std[0]:
                    timeStr = self.sampling_time.strftime("%Y_%m_%d_%H_%M_%S")
                    timeStr = "Seg_"+timeStr
                elif self.Type == self.type_std[1]:
                    timeStr = datetime.strptime(self.sampling_time,"%Y/%m/%d %H:%M:%S")
                    timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                    timeStr = "FE_"+timeStr
                fileName="LocalSaved_"+timeStr+"_"+self.name+".pkl"
                if(getRomFree() < self.romLimit):
                    if(glob.glob(path_dir+'*') != []):
                        first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                        os.remove(first_file)
                print("In-API upload failed. Saved file : " + "A_"+ fileName)
                pickle.dump(self.data,open(path_dir+"A_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
            if self.Type == self.type_std[0]:
                self.states["Seg_upload_failed"]+=1
            elif self.Type == self.type_std[1]:
                self.states["FE_upload_failed"]+=1
        
        del self.data
        del self.upload_data
        gc.collect()
        
    def release(self):
        if self.is_alive():
            self.join()
        self.exit.set()
        
class MQTT_upload(multiprocessing.Process):
    def __init__(self,path,name,url,port,topic,client_id,pswd,data,localdata_flag):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.path = path
        self.name = name
        self.data = data
        self.local_upload_flag = localdata_flag
        #MQTT params
        self.mqtt_broker = url
        self.mqtt_port = int(port)
        self.mqtt_topic = topic
        self.mqtt_username = client_id
        self.mqtt_pswd = pswd
        #ROM limit
        self.romLimit = 512
        try:
            string = str(os.popen("cat /sys/class/net/wlan0/address").readline().strip())
            self.mqtt_client_id = string.replace(':','')
        except Exception as e:
            print(e)
            self.mqtt_client_id = "DAQ"
        self.timeout = 10
        manager=multiprocessing.Manager()
        self.states=manager.dict()
        self.states["publish"]=False
        self.states["local_uploadM_error_flag"]=False
        self.states["MQTT_upload_success"] = 0
        self.states["MQTT_connect_flag"] = False
        del data
        gc.collect()
    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connect to MQTT Broker.")
                self.states["MQTT_connect_flag"] = True
            else:
                print("Failed to connect.")
                self.client = -1
                self.states["MQTT_connect_flag"] = True
                ledStatusUpload(2,2,"MQTT connect failed.")
        def on_disconnect(client,userdata,rc):
            print("Disconnect to MQTT Broker.")
        def on_publish(client, userdata, mid):
            print("Publish success.")
            self.states["publish"] = True
            self.states["MQTT_upload_success"] = 1
            ledStatusUpload(2,1,"")
        try:
            self.client = mqtt.Client(str(self.mqtt_client_id))
            self.client.on_connect = on_connect
            self.client.on_disconnect = on_disconnect
            self.client.on_publish = on_publish
            if self.mqtt_username != '':
                self.client.username_pw_set(self.mqtt_username,self.mqtt_pswd)
            self.client.connect(self.mqtt_broker, self.mqtt_port)
            self.client.loop_start()
            while(self.states["MQTT_connect_flag"] == False):
                print("Wait for connect mqtt...")
                time.sleep(0.5)
            return self.client
        except Exception as e:
            ledStatusUpload(2,2,"MQTT - "+str(e))
            print(e)
            print("Connect to MQTT Error!")
            self.states["local_uploadM_error_flag"] = True
            #Saved in local while upload error
            if(self.local_upload_flag == False):
                timeStr = self.data["Report_Time"]["0"]
                timeStr = datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S")
                timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                fileName="LocalSaved_"+timeStr+"_"+self.name+".pkl"
                if(getRomFree() < self.romLimit):
                    if(glob.glob(self.path+'*') != []):
                        first_file = min(glob.glob(self.path+'*'),key=os.path.getctime)
                        os.remove(first_file)
                print("In-MQTT upload failed. Saved file : " + "M_"+ fileName)
                pickle.dump(self.data,open(self.path+"M_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
            return -1
    
    def get_upload_error_flag(self):
        return self.states["local_uploadM_error_flag"]
    
    def get_upload_count(self):
        return self.states["MQTT_upload_success"]
            
    def run(self):
        path_dir = self.path
        try:
            print("MQTT run")
            client = self.connect_mqtt()
            if client != -1:
                #self.local_upload_flag = False
                payload = json.dumps(self.data,cls=npEncoder,indent=4)
                result = client.publish(self.mqtt_topic, payload)
                publishStartT = time.time()
                status = result[0]
                if status == 0:
                    print(f"Send data to MQTT topic {self.mqtt_topic}")
                    while not self.states["publish"]:
                        time.sleep(0.1)
                    self.states["publish"] = False
                    writeConfig('d','environment','time_mqtt',publishStartT)
                else:
                    print(f"Failed to send message to topic {self.mqtt_topic}")
                    self.states["local_uploadM_error_flag"] = True
                del payload

            else:
                self.states["local_uploadM_error_flag"] = True
                
        except Exception as e:
            ledStatusUpload(2,2,"MQTT - "+str(e))
            print(e)
            self.states["local_uploadM_error_flag"] = True
            #Saved in local while upload error
            if(self.local_upload_flag == False):
                timeStr = self.data["Report_Time"]["0"]
                timeStr = datetime.strptime(timeStr,"%Y-%m-%d %H:%M:%S")
                timeStr = timeStr.strftime("%Y_%m_%d_%H_%M_%S")
                fileName="LocalSaved_"+timeStr+"_"+self.name+".pkl"
                if(getRomFree() < self.romLimit):
                    if(glob.glob(path_dir+'*') != []):
                        first_file = min(glob.glob(path_dir+'*'),key=os.path.getctime)
                        os.remove(first_file)
                print("In-MQTT upload failed. Saved file : " + "M_"+ fileName)
                pickle.dump(self.data,open(path_dir+"M_"+fileName,'wb'),protocol=pickle.HIGHEST_PROTOCOL)
        #self.client.loop_stop()
        self.client.disconnect()
        del self.data
        gc.collect()
