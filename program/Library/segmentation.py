import multiprocessing
import os
import time
import os
import gc
import json
import copy
import numpy as np
import pandas as pd
from sys import getsizeof
from scipy.signal import spectrogram, find_peaks
from datetime import datetime
from Library.tool import getDictItem, conponerObj, printErr, keepChannelName, searchChannelKey, testPrintStructure,dataObj2drawList,dataObj2pd,mainProgramStates,alineObj,isSPIIDER

if isSPIIDER():
    from service.feature_engineer_service import get_feature_engineer
    import service
    from os import listdir
    from os.path import isdir, isfile, join
    #pd.set_option("display.max_rows",None,"display.max_columns",None)

import sys
np.set_printoptions(threshold=sys.maxsize)

class segmentation(multiprocessing.Process):
    def __init__(self,param=dict(),minProcTime=0.01,testFlag=False,testType="0",workTime=-1,exhibition=0):
        multiprocessing.Process.__init__(self)
        print("segmentation class create")
        
        self.exit = multiprocessing.Event()
        manager=multiprocessing.Manager()
        self.queue=manager.Queue()
        self.reQueue=manager.Queue()
        self.drawQueue=manager.Queue()
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
        

        if isSPIIDER():
            file_name_list = [file_name for file_name in listdir(service.config_path) if
                              '.json' in file_name and isfile(join(service.config_path, file_name))]
            print(file_name_list)
            service.config_dict={}
            for file_name in file_name_list:
                file_path = join(service.config_path, file_name)
                with open(file_path, 'r') as reader:
                    temp = json.loads(reader.read())
                    if 'project_id' not in temp or not temp['project_id']:
                        raise Exception('Config file ({0}) project id not find.'.format(file_path))
                    if temp['project_id'] in service.config_dict:
                        raise Exception('Config file ({0}) project id ({1}) duplicate.'.format(file_path, temp['project_id']))

                    service.config_dict[temp['project_id']] = temp 
            print(service.config_dict.keys())
        
                       
        self.test = testFlag
        self.testType = testType
        self.minProcTime = minProcTime
        self.exhibition = exhibition
        self.maxRuleLen = 16
        self.param = []
        self.filterByColumn = dict() #search rule index by column
        self.filterByRule = [] #search column by rule index
        for i in range(1,self.maxRuleLen+1):
            sectionName = "segmentation_"+str(i)
            data = dict()
            ruleType = int(getDictItem(param,sectionName,"type","0"))
            if(ruleType==4):
                ruleType=1
            ruleName = getDictItem(param,sectionName,"name","")
            ruleUnit = getDictItem(param,sectionName,"unit","")
            ruleSubunit = getDictItem(param,sectionName,"sub_unit","")
            if ruleType !=0 and ruleName!="":
                data["type"]= ruleType
                data["name"]= "@".join([ruleName,ruleUnit,ruleSubunit])
                data["basis_column"]= getDictItem(param,sectionName,"basis_column","")
                data["target_column"]= getDictItem(param,sectionName,"target_column","").split(",")
                data["ignore_time"]= float(getDictItem(param,sectionName,"ignore_time","0"))
                data["operation_reverse"]= int(getDictItem(param,sectionName,"operation_reverse","0"))
                data["operation_rising_falling"]= int(getDictItem(param,sectionName,"operation_rising_falling","0"))
                data["operation_count"]= float(getDictItem(param,sectionName,"operation_count","1"))
                data["operation_filter"]= float(getDictItem(param,sectionName,"operation_filter","0"))
                data["sub_operation_count"]= float(getDictItem(param,sectionName,"sub_operation_count","0"))
                data["operation_threshold"]= float(getDictItem(param,sectionName,"operation_threshold","1"))
                data["operation_shift"]= float(getDictItem(param,sectionName,"operation_shift","0"))
                data["padding"]= float(getDictItem(param,sectionName,"padding","0"))
                data["certain_freq"]= int(getDictItem(param,sectionName,"certain_freq","0"))
                data["upload_seg"]= int(getDictItem(param,sectionName,"upload_seg","0"))
                data["upload_extraction"]= int(getDictItem(param,sectionName,"upload_extraction","0"))
                data["operation_trigger_threshold"]= float(getDictItem(param,sectionName,"operation_trigger_threshold","0"))
                data["trigger_column"]= getDictItem(param,sectionName,"trigger_column","")
                data["trigger_shift"]= float(getDictItem(param,sectionName,"trigger_shift","0"))
                data["workTime"]= workTime
                data["extraction_project"]= getDictItem(param,sectionName,"extraction_project","0")
                data["smart_grid"]= int(getDictItem(param,sectionName,"smart_grid","0"))
                data["use_filter_exception"]= int(getDictItem(param,sectionName,"use_filter_exception","0"))
                if data["extraction_project"]=="":
                    data["extraction_project"]=0
                else:
                    data["extraction_project"] = int(data["extraction_project"])
                
                filterColumn = []
                if data["basis_column"]!="":
                    filterColumn.append(data["basis_column"])
                if data["operation_rising_falling"]!=0:
                    if data["trigger_column"]!="" and data["trigger_column"] not in filterColumn:
                        filterColumn.append(data["trigger_column"])
                for c in data["target_column"]:
                    if c !="" and c not in filterColumn:
                        filterColumn.append(c)
                self.filterByRule.append(filterColumn)
                data["focusColumn"]= filterColumn
                self.param.append(data)
                
                selfParamIndex = len(self.param)-1
                for c in filterColumn:
                    if c in self.filterByColumn.keys():
                        self.filterByColumn[c].append(selfParamIndex) #append rule index on param list
                    else:
                        self.filterByColumn[c]=[selfParamIndex]
                        
        self.TDMA = False
        self.TDMA_period = 0
        TDMA_period = int(getDictItem(param,"tdma","period","0"))
        
        if TDMA_period >=60 and len(self.param)>1 and not self.test:
            self.TDMA_period=TDMA_period
            self.TDMA=True
            
        print("self.filterByColumn",self.filterByColumn)
        print("self.filterByRule",self.filterByRule)
        print("self.minProcTime",self.minProcTime)
        
    def stopProc(self):
        self.states["release"]=True
    
    def put(self,data):
        self.queue.put(data)
    
    def getPid(self):
        return self.states["pid"]
        
    def checkAndPipeData(self,ruleProc):
        
        bufferList = []
        
        
        pTimes = self.queue.qsize()
        for _ in range(pTimes):
        #while not self.queue.empty(): 
            data=self.queue.get(False)
            bufferList.append(data)
            del data
            time.sleep(0.01)
        #print("**seg checkAndPipeData",len(bufferList))
            
        if len(bufferList)>0:
            obj = conponerObj(bufferList,{})
            
            """
            for i,c in enumerate(self.filterByRule):
                pipeData = keepChannelName(obj,c)
                if len(pipeData)>0:
                    ruleProc[i].put(pipeData)
                    del pipeData
            """
            
            for p in ruleProc:
                if p.is_alive():
                    pipeData = keepChannelName(obj,p.param["focusColumn"])
                    if len(pipeData)>0:
                        p.put(pipeData)
                        del pipeData
            
            del obj
        
        for p in ruleProc:
            try:
                while not p.reQueue.empty(): 
                    data=p.reQueue.get(False)
                    self.reQueue.put(data)
                    del data
                    time.sleep(0.01)
                while not p.drawQueue.empty(): 
                    data=p.drawQueue.get(False)
                    self.drawQueue.put(data)
                    del data
                    time.sleep(0.01)
            except Exception as e:
                mainProgramStates.send(mainProgramStates._Err,"Segmentation pipe error. "+str(e))
        gc.collect()
            
    def run(self):
        self.states["pid"]=os.getpid()
        print("Seg pid",self.states["pid"])
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        paramLen = len(self.param)
        TDMA_index = 0
        TDMA_startTime = 0
        ruleProc = []
        time.sleep(self.minProcTime) #wait taskset
        
        if self.TDMA :
            ruleProc.append(segRule(self.param[TDMA_index],self.minProcTime,self.test,self.testType,self.exhibition))
            ruleProc[0].start()
            TDMA_index = (TDMA_index+1)%paramLen
        else:
            for p in self.param:
                ruleProc.append(segRule(p,self.minProcTime,self.test,self.testType,self.exhibition))
                ruleProc[-1].start()
        
        
        startTime=time.time()
        endTime=startTime
        while not self.states["release"]:
            startTime=time.time()
            self.checkAndPipeData(ruleProc)
                #working
            if self.TDMA :
                if time.time()-TDMA_startTime>self.TDMA_period:
                    print("Kill Rule:", ruleProc[0].param["name"])
                    while ruleProc[0].is_alive():
                        ruleProc[0].terminate()
                        time.sleep(0.5)
                    print("Change Rule from", ruleProc[0].param["name"],"to",self.param[TDMA_index]["name"])
                    ruleProc[0] = segRule(self.param[TDMA_index],self.minProcTime,self.test,self.testType,self.exhibition)
                    ruleProc[0].start()
                    gc.collect()
                    TDMA_index = (TDMA_index+1)%paramLen
                    TDMA_startTime=time.time()
                    
            endTime=time.time()
            sleepTime=self.minProcTime-(endTime-startTime)
            #print("Seg sleep",sleepTime)
            if sleepTime>0:
                time.sleep(sleepTime)
                
        self.checkAndPipeData(ruleProc)

        for p in ruleProc:
            p.release()
            self.checkAndPipeData(ruleProc)
    
    def release(self,callback=None):
        self.stopProc()
        while self.is_alive():
            time.sleep(1)
            if callback != None:
                callback()
            #self.join()
        self.exit.set()


class segRule(multiprocessing.Process):
    def __init__(self,param=dict(),minProcTime=0.01,test=False,testType="0",exhibition=0):
        multiprocessing.Process.__init__(self)
        print("Rule class create")
        
        self.minProcTime = minProcTime
        self.exit = multiprocessing.Event()
        manager=multiprocessing.Manager()
        self.queue=manager.Queue() #get raw data
        self.reQueue=manager.Queue()   #return seg. result
        self.drawQueue=manager.Queue() #return draw list
        self.states=manager.dict()
        self.states["release"]=False
        self.states["pid"]=-1
        self.FEerr = False
        self.mean = 0
        self.meanCount = 0
        
        self.param = param
        self.testType = testType
        dataMaxLen = max(self.param["operation_count"],self.param["sub_operation_count"],self.param["operation_filter"])
        self.keepTimeLen = dataMaxLen*2 + abs(self.param["operation_shift"]) + abs(+self.param["trigger_shift"])+self.param["operation_count"]
        self.allowDataLen = dataMaxLen + abs(self.param["operation_shift"]) + abs(+self.param["trigger_shift"])
        
        self.test = test
        self.testStartTime = 0
        
        if(self.param["type"] == 5):
            self.minProcTime = min(max(minProcTime, self.param["operation_count"]),
                                   max(self.param["sub_operation_count"], 10),
                                   max(self.param["operation_filter"], 10)
                                   )
        else:
            self.minProcTime = min(minProcTime, 
                                   self.param["operation_count"],
                                   max(self.param["sub_operation_count"], 10),
                                   max(self.param["operation_filter"], 10)
                                   )
        if self.test:
            self.minProcTime = min(self.minProcTime,3)
        if(exhibition!=0):
            self.minProcTime=0.5
        print("rule keepTimeLen/allowDataLen/minProcTime",self.keepTimeLen,self.allowDataLen,self.minProcTime)
        
    def updateMean(self,v):
        self.mean = (self.mean*self.meanCount+sum(v))/(self.meanCount+len(v))
        self.meanCount +=len(v)
        
    def stopProc(self):
        self.states["release"]=True
    
    def put(self,data):
        self.queue.put(data)
        
    def getPid(self):
        return self.states["pid"]
        
    def getFirstTime(self,obj):
        focusColumn = self.param["focusColumn"]
        ret = []
        
        for column in focusColumn:
            keys = searchChannelKey(obj,column)
            if len(keys)==2:
                targetObj = obj[keys[0]][keys[1]]
            elif len(keys)==1:
                targetObj = obj[keys[0]]
            else:
                continue
            ret.append(targetObj["time"][0])
        return ret
        
    def getLastTime(self,obj):
        focusColumn = self.param["focusColumn"]
        ret = []
        #testPrintStructure(obj)
        for column in focusColumn:
            keys = searchChannelKey(obj,column)
            #print(obj)
            #print(keys)
            if len(keys)==2:
                targetObj = obj[keys[0]][keys[1]]
            elif len(keys)==1:
                targetObj = obj[keys[0]]
            else:
                continue
                
            #print(targetObj)
            ret.append(targetObj["time"][-1])
        return ret
        
    def includeTarger(self,obj):
        focusColumn = self.param["focusColumn"]
        for column in focusColumn:
            keys = searchChannelKey(obj,column)
            if len(keys)!=1 and len(keys)!=2:
                print("includeTarger",self.param["name"],column)
                return False
        return True
        
        
    def dataLenCheck(self,obj):
        targetTime = self.allowDataLen 
        focusColumn = self.param["focusColumn"]
        checkPoint = dict()
        checkPoint["startTime"] = []
        checkPoint["timeLen"] = []
        
        for column in focusColumn:
            keys = searchChannelKey(obj,column)
            if len(keys)==2:
                targetObj = obj[keys[0]][keys[1]]
            elif len(keys)==1:
                targetObj = obj[keys[0]]
            else:
                continue
            checkPoint["startTime"].append(targetObj["time"][0])
            checkPoint["timeLen"].append(len(targetObj["time"])/float(targetObj["fs"]))
            #use standard time to avoid NTP effict
        
        #print("dataLenCheck",checkPoint)
        if len(checkPoint["startTime"])==0:
            return False
            
        timeInterval = max(checkPoint["startTime"])-min(checkPoint["startTime"])
        if min(checkPoint["timeLen"]-timeInterval) >=targetTime: 
            return True
        return False
        
    #return dict[column][list index][start/end index]
    def segByNormal(self,obj):
        target_column = self.param["target_column"]
        startTimeList = []
        FsList = []
        
        for column in target_column:
            keys = searchChannelKey(obj,column)
            if len(keys)==2:
                targetObj = obj[keys[0]][keys[1]]
            elif len(keys)==1:
                targetObj = obj[keys[0]]
            else:
                continue
            startTimeList.append(targetObj["time"][0])
            FsList.append(targetObj["fs"])
            
        
        if len(startTimeList)>0:
            #startTime = max(startTimeList)#use final start point to be main start point
            startTime = startTimeList[np.argmin(FsList)]#use min Fs to be target
            endTime = startTime+self.param["operation_count"]
        else:
            return {}
            
        ret = dict()
        return self.cutAllColumnByTime(obj,target_column,[],startTime,endTime,ret)
     
    def segByRawFilter(self, obj):
        
        # editor: Kasper at 08:00:00 01/09/2023
        # Function Describition: 
        #     A segmentation rule which is designed for user-friendly parameter setting.
        #     The input signal will be filterd by the filter_threshold to exclude the signal noise,
        #     then a rolling sum process will be excuted on the filtered signal to obtain the
        #     cutting start/end points by diff and thus forms multiple temporal segments. 
        #     Finally, the official segments will be confirmed by 4 checking rules to avoid overlap or 
        #     unwanted segmentations.
        
        focusColumn = self.param["focusColumn"]
        basis_column = self.param["basis_column"]
        keys = searchChannelKey(obj,basis_column)
        if len(keys)==2:
            targetObj = obj[keys[0]][keys[1]]
        elif len(keys)==1:
            targetObj = obj[keys[0]]
        else:
            return {}
        
        filter_threshold = self.param['operation_threshold']
        fs = targetObj['fs']
        motion_time = self.param['operation_filter']
        operation_filter = int(self.param['operation_filter'] * fs)
        capture_time = self.param['sub_operation_count']
        num_filter = (int(motion_time * fs * 0.95), int(motion_time * fs * 1.05))
        shift_len = int(capture_time * fs * 0.5)
        shift_len_half = int(shift_len/2)
        window_size = int(self.param['operation_count'] * fs)
        
        isExceptionRange=False
        enable_filter = True
        if operation_filter == 0:
            enable_filter=False
            operation_filter = int(shift_len * 2)
        
        data_pd = pd.DataFrame()
        data_pd[basis_column] = targetObj["data"][basis_column]
        data_filtered = np.where(data_pd[basis_column]<filter_threshold, 0, data_pd[basis_column])
        data_rolling = pd.DataFrame(data_filtered).rolling(window_size).sum().dropna()
        rolling_sum_arr = np.array(data_rolling).ravel()
        rolling_sum_arr = np.where(rolling_sum_arr < 1e-06, 0, rolling_sum_arr)
        zero_value_idx = np.argwhere(rolling_sum_arr==0).ravel()
        
        if len(zero_value_idx) < len(rolling_sum_arr)*0.05:
            msg = "[WARNING] The rolling results have few zero value, try to 'INCREASE' the 'Filter Threshold'"
            print(msg)
            return {}
        elif len(zero_value_idx) == len(rolling_sum_arr):
            msg = "[WARNING] The rolling results are all zero value, try to 'DECREASE' the 'Filter Threshold'"
            print(msg)
            return {}
        
        diff_idx = np.diff(np.where(rolling_sum_arr > 0, 1, rolling_sum_arr)).astype(np.int)
        cut_index_arr, cut_index_val = list(data_rolling.index[1:][diff_idx!=0]-1), list(diff_idx[diff_idx!=0])
        for i in range(len(cut_index_arr)):
             if cut_index_val[i] == -1:
                 cut_index_arr[i] -= window_size
        
        print("****** cut_index_arr ******:\n", cut_index_arr)
        print("****** cut_index_val ******:\n", cut_index_val)

        """
        start_points, end_points = list(rolling_sum.index[1:][diff_idx==1]-1), list(rolling_sum.index[1:][diff_idx==-1]-1)
        if start_points == [] or end_points == []:
            msg = "[INFO] This signal has no complete motion."
            print(msg)
            return {}
        if start_points[0] > end_points[0]:
            start_points = [0] + start_points
        if len(start_points) < len(end_points):
            start_points = [0] + start_points
        elif len(start_points) > len(end_points)
            end_points.append(len(data)-1)
    
        start_points, end_points = np.array(start_points), np.array(end_points)
        seg_len = end_points - start_points
        
        pass_seg_idx = np.argwhere((seg_len>=num_filter[0]) & (seg_len<=num_filter[1])).ravel()
        if np.size(pass_seg_idx) == 0:
            msg = "[WARNING] No pass segment, try to tune the 'Motion Time'"
            return {}
            
        pass_start_points, pass_end_points = start_points[pass_seg_idx], end_points[pass_seg_idx]
        official_mid_seg_idx = np.array((pass_start_points + pass_end_points)/2, dtype=int)
        official_start_seg_idx, official_end_seg_idx = official_mid_seg_idx - shift_len, official_mid_seg_idx + shift_len
        temp_start_seg_idx, temp_end_seg_idx = np.concatenate([official_start_seg_idx, [len(data_filtered)]]), np.concatenate([[0], official_end_seg_idx])
        
        # Check whether official segments have overlaps with themself
        rule_1 = np.size(np.where(temp_start_seg_idx[1:-1] - temp_end_seg_idx[1:-1] < 0)) == 0
        if not rule_1:
            overlap_idx = np.argwhere(temp_start_seg_idx - temp_end_seg_idx < 0).ravel(0)
            overlap_points = [(temp_start_seg_idx[i], temp_end_seg_idx[i]) for i in overlap_idx]
            msg = "[WARNING] The 'Capture Time' is too long so the captured signal may contain redundant signal, try to 'DECREASE' the 'Capture Time'"
            print(msg)
            return {}
        
        # Check whethere official segments have overlaps with temp segments
        next_start_point_idx = []
        for i in pass_seg_idx + 1:
            if i < len(start_points):
                next_start_point_idx.append(i)
        next_end_point_idx = []
        for i in pass_seg_idx - 1:
            if i >= 0:
                next_end_point_idx.append(i)
        
        if len(next_start_point_idx) != len(official_end_seg_idx):
            next_start_point = np.concatenate([start_points[next_start_point_idx], [len(data_filtered)]])
        else:
            next_start_point = start_points[next_start_point_idx]
        
        if len(next_end_point_idx) != len(official_start_seg_idx):
            next_start_point = np.concatenate([[len(data_filtered)], end_points[next_end_point_idx]])
        else:
            next_start_point = end_points[next_end_point_idx]
            
        rule_2 = np.size(np.where(official_end_seg_idx - next_start_point > 0)) == 0
        rule_3 = np.size(np.where(official_start_seg_idx - next_end_point < 0)) == 0
        if not (rule_2 and rule_3):
            overlap_idx = np.argwhere(official_end_seg_idx - next_start_point < 0).ravel()
            overlap_points = [(official_end_seg_idx[i], next_start_point[i]) for i in overlap_idx]
            overlap_idx = np.argwhere(official_start_seg_idx - next_end_point < 0).ravel()
            overlap_points += [(official_start_seg_idx[i], next_end_point[i]) for i in overlap_idx]
            msg = "[WARNING] The 'Capture Time' is too long so the captured signal may contain redundant signal, try to 'DECREASE' the 'Capture Time'"
            print(msg)
            return {}
            
        rule_4 = np.size(np.where(pass_start_points - official_start_seg_idx < 0)) == 0
        if not rule_4:
            overlap_idx = np.argwhere(pass_start_points - official_start_seg_idx < 0).ravel()
            overlap_points = [(pass_start_points[i], official_start_seg_idx[i]) for i in overlap_idx]
            msg = "[WARNING] The 'Motion Time' is too long so the captured signal may contain redundant signal, try to 'DECREASE' the 'Capture Time'"
            print(msg)
            return {}
        
        """
        
        ind_o = 0
        cut_s = 0
        overlap_s = 0
        startIndex=-1
        for j, ind, value in zip(range(len(cut_index_arr)), cut_index_arr, cut_index_val):
            if ind_o == 0 or (ind - ind_o) > operation_filter*0.05:
                if value == 1:  # means this point is cut start point
                    cut_s = ind
                else:
                    if ind_o == 0:
                        overlap_s = ind  # means this point is the first point and is down, which value = -1
                    if cut_s > window_size:  # cut start point index larger than 1 window size 
                        #排除突波
                        cut_len = ind - cut_s   # temp segment length
                        print("****** judge ******\n:",cut_s,ind,cut_len,operation_filter * 0.95)
                        if cut_len > (operation_filter*0.05):
                            if enable_filter:
                                if cut_len < (operation_filter * 0.95) or cut_len > (operation_filter * 1.05):  # segment too short or long
                                    if cut_len < (operation_filter*0.95) and self.param["use_filter_exception"] == 1:
                                        isExceptionRange=True  # whether need to save the short segment data
                                    else:
                                        continue
                            
                            print("****** isExceptionRange ******: ", isExceptionRange)
                            startIndex = int(cut_s)
                            endIndex = int(ind)
                            midIndex = int((startIndex+endIndex)/2)
                            print(f"****** startIndex:{startIndex}/endIndex:{endIndex}/midIndex:{midIndex} ******")

                            """
                            if isExceptionRange:
                                startIndex = int(cut_s)
                                endIndex = int(ind)
                                #print('ExceptionRange startIndex',startIndex,':',endIndex,':',cut_len)
                            else:
                                startIndex = int(cut_s)
                                endIndex = int(ind)
                                #print('startIndex',startIndex,':',cut_len)
                            """
            
                            if startIndex != -1:  # means this segment is needed to be segmented
                                ret = dict()
                                if isExceptionRange:
                                    #print(self.param["name"],"point",startIndex-operation_quarter , endIndex-operation_quarter,len(targetObj["time"]))
                                    if midIndex-shift_len_half >= 0 and midIndex+shift_len_half <= len(targetObj["time"]):
                                        startTime = targetObj["time"][midIndex-shift_len_half]
                                        endTime = targetObj["time"][midIndex+shift_len_half]
                                        print(f"****** midIndex-shift_len_half:{midIndex-shift_len_half}\nmidIndex+shift_len_half:{midIndex+shift_len_half}\n ******")

                                        overlap_startTime, overlap_endTime = [], []
                                        if midIndex-shift_len_half < overlap_s:
                                            overlap_startTime.append(targetObj["time"][midIndex-shift_len_half])
                                            overlap_endTime.append(targetObj["time"][overlap_s])
                                        if j != len(cut_index_arr)-1: 
                                            if midIndex+shift_len_half > cut_index_arr[j+1]:
                                                overlap_startTime.append(targetObj["time"][cut_index_arr[j+1]])
                                                overlap_endTime.append(targetObj["time"][midIndex+shift_len_half])
                                        print(f"****** startTime:{startTime}\nendTime:{endTime}\noverlap_startTime:{overlap_startTime}\n/overlap_endTime:{overlap_endTime} ******")

                                        return self.cutAllColumnByTime(obj,focusColumn,[],startTime,endTime,ret,overlap_startTime,overlap_endTime) 
                                else:
                                    #print(self.param["name"],"point",startIndex-final_operation_half , startIndex+final_operation_half,len(targetObj["time"]))
                                    if midIndex-shift_len >= 0 and midIndex+shift_len <= len(targetObj["time"]):  # to check whether the startIndex(which will be the final segment's middle points) forward 1 and backward 1 half capture length will exceed the input signal 
                                        startTime = targetObj["time"][midIndex-shift_len]
                                        endTime = targetObj["time"][midIndex+shift_len]
                                        print(f"****** midIndex-shift_len:{midIndex-shift_len}\nmidIndex+shift_len:{midIndex+shift_len}\n ******")

                                        overlap_startTime, overlap_endTime = [], []
                                        if midIndex-shift_len < overlap_s:
                                            overlap_startTime.append(targetObj["time"][midIndex-shift_len])
                                            overlap_endTime.append(targetObj["time"][overlap_s])
                                        if j != len(cut_index_arr)-1: 
                                            if midIndex+shift_len > cut_index_arr[j+1]:
                                                overlap_startTime.append(targetObj["time"][cut_index_arr[j+1]])
                                                overlap_endTime.append(targetObj["time"][midIndex+shift_len])
                                        print(f"****** startTime:{startTime}\nendTime:{endTime}\noverlap_startTime:{overlap_startTime}\noverlap_endTime:{overlap_endTime}\n******")

                                        
                                        return self.cutAllColumnByTime(obj,focusColumn,[],startTime,endTime,ret,overlap_startTime,overlap_endTime) 
            ind_o = ind
        
        
        
        return {}
    
    def segByStrength(self,obj):
        focusColumn = self.param["focusColumn"]
        basis_column = self.param["basis_column"]
        keys = searchChannelKey(obj,basis_column)
        if len(keys)==2:
            targetObj = obj[keys[0]][keys[1]]
        elif len(keys)==1:
            targetObj = obj[keys[0]]
        else:
            return {}
            
        segmentation_dic = {}
        operation_reverse = self.param['operation_reverse']
        operation_threshold = self.param['operation_threshold']
       
        fs = targetObj['fs']
       
        operation_count = self.param['operation_count'] * fs *2
        sub_operation_count = self.param['sub_operation_count'] * fs
        operation_half = int(operation_count / 2)
        operation_quarter = int(operation_count / 4)
        operation_filter = self.param['operation_filter'] * fs
        operation_shift = self.param['operation_shift'] * fs
       
        isExceptionRange=False
        enable_filter = True
        if operation_filter == 0:
            enable_filter=False
            operation_filter = operation_count
           
        if sub_operation_count == 0:
            sub_operation_count = operation_filter
           
        final_operation_half = int(sub_operation_count / 2)
       
        #data_pd = data_value[100:1000]
        data_pd = pd.DataFrame()
        data_pd[basis_column] = targetObj["data"][basis_column]

        #mode
        #mode = data_pd[basis_column].mode()[0]
        self.updateMean(data_pd[basis_column])
        mode = self.mean
        #abs
        data_abs = (data_pd[basis_column] - mode).abs()
        #rolling
        #data_rolling = data_abs.rolling(operation_half).mean() * 1000
        
        data_rolling = data_abs.rolling(operation_half).sum()  # v2
        #data_rolling = np.sum(rolling_window(data_abs,operation_half),axis=1)  # spiider optimiz
       
        #reverse
        if operation_reverse:
            data_rolling = (data_rolling * (-1)) + (operation_threshold * 2)
        #print("data_rolling",data_rolling)
        #cut_threshold
        cut_threshold = (data_rolling >= operation_threshold)*1
        
        if self.test and False:
            minTime = min(targetObj["time"])
            rollingIndex = data_rolling.isnull()==False
            draw=dict()
            draw['title'] = "Rule("+self.param["name"]+")Result rolling"
            draw['data'] = dict()
            draw['data']['input_item'] = targetObj["data"][basis_column]
            draw['time'] = targetObj["time"]-minTime
            draw['timeR'] = targetObj["time"][rollingIndex]-minTime
            draw['dataR'] = dict()
            draw['dataR']['Strength value'] = data_rolling.dropna()
            draw['dataR']['rolling threshold'] = np.ones(len(draw['timeR']))*operation_threshold
            if type(targetObj["unit"])==dict:
                draw['unit']=targetObj["unit"][basis_column]
            else:
                draw['unit']=targetObj["unit"]
            self.drawQueue.put(draw)
       
        #平移相減
        cut_index = cut_threshold.diff(periods = 1)
        #testing_start_time = time.time()
        main_index = (cut_index != 0)
        cut_index_arr = np.array(cut_index.index)[main_index][1:] # use [1:0] to dropna
        cut_index_val = np.array(cut_index)[main_index][1:]#use [1:0] to dropna
        #print("key point time",time.time()-testing_start_time)
        #cut_index = cut_index[cut_index != 0].dropna()
        
        #取擷取中心點
        ind_o = 0
        cut_s = 0
        startIndex=-1
        for ind,value in zip(cut_index_arr,cut_index_val):
        #for ind,value in cut_index.items():
            if ind_o == 0 or (ind - ind_o) > operation_filter*0.05:
                if value == 1:
                    cut_s = ind
                else:
                    if cut_s > operation_half:
                        #排除突波
                        cut_len = ind - cut_s
                        #print("judge",cut_s,ind,cut_len,operation_filter * 0.95)
                        if cut_len > (operation_filter*0.05):
                            if enable_filter:
                                if cut_len < (operation_filter * 0.95) or cut_len > (operation_filter * 1.05):
                                    if cut_len < (operation_filter*0.95) and self.param["use_filter_exception"] == 1:
                                        isExceptionRange=True
                                    else:
                                        continue
                            if isExceptionRange:
                                startIndex = int(cut_s)
                                endIndex = int(ind)
                                #print('ExceptionRange startIndex',startIndex,':',endIndex,':',cut_len)
                                
                            else:
                                startIndex = int(cut_s + operation_shift)
                                #print('startIndex',startIndex,':',cut_len)
            
            
                            if startIndex!=-1:
                                ret = dict()
                                if isExceptionRange:
                                    #print(self.param["name"],"point",startIndex-operation_quarter , endIndex-operation_quarter,len(targetObj["time"]))
                                    if startIndex-operation_quarter >= 0 and endIndex-operation_quarter <= len(targetObj["time"]):
                                        startTime=targetObj["time"][startIndex-operation_quarter]
                                        endTime=targetObj["time"][endIndex-operation_quarter]
                                        return self.cutAllColumnByTime(obj,focusColumn,[],startTime,endTime,ret) 
                                else:
                                    #print(self.param["name"],"point",startIndex-final_operation_half , startIndex+final_operation_half,len(targetObj["time"]))
                                    if startIndex-final_operation_half >= 0 and startIndex+final_operation_half <= len(targetObj["time"]):
                                        startTime=targetObj["time"][startIndex-final_operation_half]
                                        endTime=targetObj["time"][startIndex+final_operation_half]
                                        return self.cutAllColumnByTime(obj,focusColumn,[],startTime,endTime,ret) 
                                
            ind_o = ind
                
        return {}
        
    def segByFreq(self,obj,testResult=[]):
        focusColumn = self.param["focusColumn"]
        basis_column = self.param["basis_column"]
        keys = searchChannelKey(obj,basis_column)
        if len(keys)==2:
            targetObj = obj[keys[0]][keys[1]]
        elif len(keys)==1:
            targetObj = obj[keys[0]]
        else:
            return {}
        
        segmentation_dic = {}
        operation_reverse = int(self.param['operation_reverse'])
        operation_threshold = float(self.param['operation_threshold'])
       
        height = 4 #float(config_dic['height'])
        padding = self.param['padding']
        sig_threshold = 0 #1.5 #float(config_dic['sig_threshold'])
        sx_energy_threshold = 0 #0.01 #float(config_dic['sx_energy_threshold'])
        certain_freq = self.param['certain_freq']
   
        fs = targetObj['fs']
       
        operation_count = self.param['operation_count'] * fs *2
        sub_operation_count = self.param['sub_operation_count'] * fs
        operation_half = int(operation_count / 2)
        operation_quarter = int(operation_count / 4)
        operation_filter = self.param['operation_filter'] * fs
        operation_shift = self.param['operation_shift'] * fs
        
        
       
        enable_filter = True
        if operation_filter == 0:
            enable_filter=False
            operation_filter = operation_count
           
        if sub_operation_count == 0:
            sub_operation_count = operation_filter
           
        time_range = int(sub_operation_count / 2)
           
        final_operation_half = int(sub_operation_count / 2)
       
        temp_dic = {}
       
        #data_pd = data_value[100:1000]
        data_pd = pd.DataFrame()
        data_pd[basis_column] = targetObj["data"][basis_column]
        
        self.updateMean(data_pd[basis_column])
        mode = self.mean
        #abs
        data_abs = (data_pd[basis_column] - mode).abs()
        #rolling
        #data_rolling = data_abs.rolling(operation_half).mean() * 1000
        data_rolling = data_abs.rolling(operation_half).sum()  # v2
       
        #reverse
        if operation_reverse:
            data_rolling = (data_rolling * (-1)) + (operation_threshold * 2)
       
                
        #cut_threshold
        cut_threshold = (data_rolling.iloc[:] >= operation_threshold)*1
       
       
        #平移相減
        cut_index = cut_threshold.diff(periods = 1)
        main_index = (cut_index != 0)
        cut_index_arr = np.array(cut_index.index)[main_index][1:] # use [1:0] to dropna
        cut_index_val = np.array(cut_index)[main_index][1:]#use [1:0] to dropna
        #cut_index = cut_index[cut_index != 0].dropna()
        
        #取擷取中心點
        ind_o = 0
        cut_s = 0
        cut_ary = []
        filter_cnt = 0
       
        for ind,value in zip(cut_index_arr,cut_index_val):
        #for ind,value in cut_index.items():
            #print(ind,value,ind_o,ind-ind_o,operation_filter*0.1)
            if ind_o == 0 or (ind - ind_o) > operation_filter*0.1:
                #print("pass",value,operation_half)
                if value == 1:
                    cut_s = ind
                else:
                    if cut_s > operation_half:
                        #排除突波
                        cut_len = ind - cut_s
                        #print("debug****",ind,cut_s,cut_len,(operation_filter*0.95) , (operation_filter*1.05))
                        if cut_len > operation_quarter:
                            if enable_filter:
                                #if cut_len < (operation_filter-padding*fs) or cut_len > (operation_filter+padding*fs):
                                if cut_len < (operation_filter*0.95) or cut_len > (operation_filter*1.05):
                                    continue
                               
                            filter_cnt += 1
                            #print('cut_len_',filter_cnt,':',cut_len)
                            cut_ary.append(
                            {
                                "s":int(cut_s) + operation_shift,
                                "e":int(ind) + operation_shift
                            })
            ind_o = ind
           
        #print(self.param["name"],'cut_ary:',cut_ary)
   
        #segmentation   
        last_index = 0
        segmentation_cnt = 0
        startIndex=-1
        for cut_obj in cut_ary:
            index = cut_obj["s"]
            if last_index == 0 or (last_index + operation_filter) < index:
                #cut_s = index - final_operation_half
                #cut_e = index + final_operation_half
                cut_s = cut_obj["s"]
                cut_e = cut_obj["e"]
                #print("cut_s",cut_s,cut_e,len(data_pd))
                if cut_s >= 0 and cut_e <= len(data_pd):
                    last_index = index
                    save_data = data_pd.loc[int(cut_s):int(cut_e)]
                    signal = save_data[basis_column]
                    if self.test:
                        testResult.append({"data":copy.deepcopy(signal),"time":targetObj["time"][int(cut_s)]})
                    if len(signal)<=int(fs/5):
                        continue
                    idx,peak_freq,f_range = self.seg_using_STFT_freq(signal, fs, operation_count//8, height, sig_threshold, time_range, sx_energy_threshold, certain_freq)
                    #print(self.param["name"],"stft:",idx,peak_freq,f_range)
                    if idx != None:
                        if idx[0] >= 0 and idx[1] < len(data_pd):
                            startIndex = idx[0]
                            stopIndex = idx[1]
                            break

        if startIndex!=-1:
            ret = dict()
            #print(self.param["name"],"point",startIndex , stopIndex,len(targetObj["time"]))
            if startIndex >= 0 and stopIndex <= len(targetObj["time"]):
                startTime=targetObj["time"][startIndex]
                endTime=targetObj["time"][stopIndex]
                return self.cutAllColumnByTime(obj,focusColumn,[],startTime,endTime,ret)
        return {}

    def short_time_fourier_transform(self, X, fs, nperseg, noverlap):
        X = X.values.ravel() # ravel將資料格式從1D陣列(n,1)轉換成扁平陣列(n,)
        f, t, Sx = spectrogram(X, fs=fs, window = 'hamming', nperseg=nperseg, noverlap = noverlap) # 短時距傅立葉轉換
        return f, t, np.abs(Sx)
     
    def get_max_freq(self, signal, fs,full=True):
        nperseg = int(fs//5)
        if full:
            noverlap = nperseg-1
        else:
            noverlap = int(nperseg*0.9)
           
        print("signal",len(signal))
        print("nperseg",nperseg)
        print("noverlap",noverlap)
        f, t, Sx = self.short_time_fourier_transform(signal, fs, nperseg, noverlap)
        Sx[np.isnan(Sx)] = 0
        Sx[Sx<=np.mean(Sx)] = 0
        f_max_idx = np.argmax(Sx, axis = 0)
        return t,f,f_max_idx,Sx
        
    def seg_using_STFT_freq(self, signal, fs, distance, height, sig_threshold, time_range, sx_energy_threshold, certain_freq):
        nperseg = int(fs//5)
        noverlap = nperseg-1
        f, t, Sx = self.short_time_fourier_transform(signal, fs, nperseg, noverlap)
        Sx[np.isnan(Sx)] = 0
        Sx[Sx<=np.mean(Sx)] = 0
        #V0
        #    f_max_idx = np.argmax(Sx, axis = 0)
        #    f_max = f[f_max_idx]
        #    f_max = np.append([0],f_max) # prevent find peak error
        #    f_max = np.append(f_max,[0]) # prevent find peak error
        #    peak_idx = find_peaks(f_max, distance = distance, height = height)[0]
        #    peak_idx = peak_idx-1
        #    f_peaks = f_max[peak_idx]
        #    if np.max(Sx[:, peak_idx[0]]) > sx_energy_threshold:
        #        if np.max(signal.abs()) > sig_threshold:
        #            #thres_freq = int(f_peaks[0])*thres
        #            f_range = pd.Series(f_max[int(max(peak_idx[0]-time_range,0)):int(min(peak_idx[0]+time_range,len(f_max)))])
        #            #idx = f_range[f_range > thres_freq].index
        #            start_idx = int(signal.index[0]+peak_idx[0] - time_range)
        #            stop_idx = int(signal.index[0]+peak_idx[0] + time_range)
        #            if certain_freq == 0 or int(f_peaks[0])==certain_freq:
        #                return [start_idx,stop_idx],int(f_peaks[0]),f_range
        #            else:
        #                return None,int(f_peaks[0]),f_range
        #    return None,int(f_peaks[0]),None

        #f_max_idx = np.argmax(Sx, axis = 0)
        #f_max = f[f_max_idx].astype(int)
        #freq_counts = pd.Series(f_max).value_counts()
        #f_peaks = int(freq_counts.index[0])
        #if f_peaks == 0:
        #    f_peaks = int(freq_counts.index[1])
        #equal_start_idx = int(t[f_max == f_peaks][0]*fs)
        #equal_end_idx = int(t[f_max == f_peaks][-1]*fs)
        #peak_idx = int((equal_start_idx+equal_end_idx)//2) 
        # 
        #f_range = pd.Series(f_max[int(max(peak_idx-time_range,0)):int(min(peak_idx+time_range,len(f_max)))])
        #start_idx = int(signal.index[0]+peak_idx - time_range)
        #stop_idx = int(signal.index[0]+peak_idx + time_range)
        #if certain_freq == 0 or int(f_peaks)==certain_freq:
        #    return [start_idx,stop_idx],int(f_peaks),f_range
        #else:
        #    return None,int(f_peaks),f_range
            
        
        resol=5
        shift = int(np.floor(fs//resol))
        f_max_idx = np.argmax(Sx, axis = 0)
        f_max = np.floor(f[f_max_idx]).astype(int)
        f_max_diff_abs = f_max[shift*2:]-f_max[:-shift*2] # V2.1
        f_max_diff_abs[np.abs(f_max_diff_abs)>10*resol]=0 # V2.1
        acc_mid = pd.Series(f_max_diff_abs).idxmax()+shift # V2.1
        dec_mid = pd.Series(f_max_diff_abs).idxmin()+shift # V2.1
        freq_counts = pd.Series(f_max)[acc_mid:dec_mid].value_counts() # V2.1
        f_peaks = int(freq_counts.index[0])
        #print("new stft##########################","Acc F=",f_max[acc_mid],", Dec F=",f_max[dec_mid],", best F=",int(f_peaks))
        if f_peaks == 0:
            f_peaks = int(freq_counts.index[1])
        equal_start_idx = int(t[f_max == f_peaks][0]*fs)
        equal_end_idx = int(t[f_max == f_peaks][-1]*fs)
        peak_idx = int((equal_start_idx+equal_end_idx)//2) 
        f_range = pd.Series(f_max[int(max(peak_idx-time_range,0)):int(min(peak_idx+time_range,len(f_max)))])
        start_idx = int(signal.index[0]+peak_idx - time_range)
        stop_idx = int(signal.index[0]+peak_idx + time_range)
        if certain_freq == 0 or int(f_peaks)==certain_freq:
            return [start_idx,stop_idx],int(f_peaks),f_range
        else:
            return None,int(f_peaks),f_range

    def seg_using_STFT_freq_old(self, signal, fs, distance, height, sig_threshold, time_range, sx_energy_threshold, certain_freq):
        
        t,f,f_max_idx,Sx=self.get_max_freq(signal, fs,full=True)
        f_max = f[f_max_idx]
        f_max = np.append([0],f_max) # prevent find peak error
        f_max = np.append(f_max,[0]) # prevent find peak error
        peak_idx = find_peaks(f_max, distance = distance, height = height)[0]
        peak_idx = peak_idx-1
        f_peaks = f_max[peak_idx]
        #print("flag A",peak_idx[0],sx_energy_threshold,np.max(Sx[:, peak_idx[0]]))
        if np.max(Sx[:, peak_idx[0]]) > sx_energy_threshold:
            #print("flag B",sig_threshold,np.max(signal.abs()))
            if np.max(signal.abs()) > sig_threshold:
                #print("flag C")
                #thres_freq = int(f_peaks[0])*thres
                f_range = pd.Series(f_max[int(max(peak_idx[0]-time_range,0)):int(min(peak_idx[0]+time_range,len(f_max)))])
                #idx = f_range[f_range > thres_freq].index
                if certain_freq == 0 or certain_freq in f_peaks:
                    if certain_freq == 0:
                        f_index = 0
                    else:
                        f_index = list(f_peaks).index(certain_freq)
                    start_idx = int(signal.index[f_index]+peak_idx[f_index] - time_range)
                    stop_idx = int(signal.index[f_index]+peak_idx[f_index] + time_range)
                    #print("flag D")
                    return [start_idx,stop_idx],int(f_peaks[f_index]),f_range
                else:
                    #print("flag E")
                    return None,int(f_peaks[0]),f_range
        return None,int(f_peaks[0]),None

    def cutAllColumnByTime(self,obj,focusColumn,ignore_column,startTime,endTime,ret,ovelap_startTime=[],overlap_endTime=[]):
        for column in focusColumn:
            if column in ignore_column:
                continue
            keys = searchChannelKey(obj,column)
            if len(keys)==2:
                targetObj = obj[keys[0]][keys[1]]
            elif len(keys)==1:
                targetObj = obj[keys[0]]
            else:
                return {}
                
            ret[column] = []
            point = dict()            
            startIndex = np.argwhere(targetObj["time"] >= startTime)
            endIndex = np.argwhere(targetObj["time"] >= endTime)
            
            
            if len(startIndex)>0 and len(endIndex)>0:
                point["start"] = startIndex[0][0]
                point["startTime"] = targetObj["time"][startIndex[0][0]]
                point["end"] = endIndex[0][0]
                point["endTime"] = targetObj["time"][endIndex[0][0]]
                # Kasper add for segByRawFilter at 2023/01/13 10:00:00
                if len(ovelap_startTime)>0 and len(overlap_endTime)>0:
                    overlap_startIndex = []
                    overlap_endIndex = []
                    for i in range(len(ovelap_startTime)):
                        overlap_startIndex.append(np.argwhere(targetObj["time"] >= ovelap_startTime[i])[0][0])
                        overlap_endIndex.append(np.argwhere(targetObj["time"] >= overlap_endTime[i])[0][0])
                    point["overlap_start"] = overlap_startIndex
                    point["overlap_startTime"] = targetObj["time"][overlap_startIndex]
                    point["overlap_end"] = overlap_endIndex
                    point["overlap_endTime"] = targetObj["time"][overlap_endIndex]
                ret[column].append(point)
            else:
                return {}
            
        return ret
      
    # 2023/01/10 16:00:00 Kasper: Add one elif for segByRawFilter if self.param["type"] == 5
    def getCutIndex(self,obj,testResult):
        if(self.param["type"] == 1):
            return self.segByNormal(obj)
        elif(self.param["type"] == 2):
            return self.segByStrength(obj)
        elif(self.param["type"] == 3):
            return self.segByFreq(obj,testResult)
        elif(self.param["type"] == 5):
            return self.segByRawFilter(obj)
        else:
            return []
            
        
    def getResultObjList(self,obj,index):
        ret = []
        if len(index)==0:
            return ret
        firstKey=list(index.keys())[0]
        if len(index[firstKey])==0:
            return ret
            
        cutIndexLen = len(index[firstKey])
        for i in range(cutIndexLen):
            subObj = copy.deepcopy(obj)
            fastTime=index[firstKey][i]["endTime"]
            for key in index.keys():
                #print('self.param["target_column"]',self.param["target_column"])
                if key not in self.param["target_column"]:
                    keyList = searchChannelKey(subObj,key)
                    if len(keyList)==2:
                        del subObj[keyList[0]][keyList[1]]
                    elif len(keyList)==1:
                        del subObj[keyList[0]]
                    continue
                startIndex = index[key][i]["start"]
                endIndex = index[key][i]["end"]
                fastTime = min(fastTime,index[key][i]["endTime"])
                keyList = searchChannelKey(subObj,key)
                if len(keyList)==2:
                    targetObj = subObj[keyList[0]][keyList[1]]
                elif len(keyList)==1:
                    targetObj = subObj[keyList[0]]
                else:
                    continue
                targetObj["data"][key] = targetObj["data"][key][startIndex:endIndex]
                standardTimeArrLen=len(targetObj["data"][key])
                fs = targetObj["fs"]
                ps = 1/float(fs)
                standardTime = np.arange(standardTimeArrLen)/standardTimeArrLen
                standardTime = standardTime*standardTimeArrLen*ps+index[key][i]["startTime"]
                targetObj["time"] = standardTime
            
            mainObj = dict()
            mainObj["type"] = "seg"
            mainObj["name"] = self.param["name"]
            mainObj["data"] = subObj
            
            ret.append(mainObj)
            
        return ret
        
    def getSmartGridFormat(self,obj):
        iotData = dict()
        iotData["IOT_ID"]=dict()
        iotData["Value"]=dict()
        iotData["Report_Time"]=dict()
        target_column = self.param["target_column"]
        index = 0
        for column in target_column:
            keys = searchChannelKey(obj,column)
            if len(keys)==2:
                targetObj = obj[keys[0]][keys[1]]
            elif len(keys)==1:
                targetObj = obj[keys[0]]
            else:
                continue
                
            if "type" not in targetObj.keys():
                continue
                
            if targetObj["type"]!="CURRENT" and  targetObj["type"]!="VOLTAGE":
                continue
                
            iotData["IOT_ID"][str(index)] = column
            iotData["Report_Time"][str(index)] = datetime.fromtimestamp(targetObj["time"][0]).strftime("%Y-%m-%d %H:%M:%S")
                
            if targetObj["type"]=="CURRENT":
                #print("MQTT using RMS")
                iotData["Value"][str(index)] = np.sqrt(np.mean(np.square(targetObj["data"][column])))
            else:
                #print("MQTT using mean")
                iotData["Value"][str(index)] = np.mean(targetObj["data"][column])
            index=index+1
        #print("MQTT:")
        #print("Data type:",targetObj["type"])
        #print(iotData)
        
        ret = dict()
        ret["type"] = "mqtt"
        ret["name"] = self.param["name"]
        ret["data"] = iotData
        
        if index>0:
            return ret
        else:
            return None
        
    def removeFinishData(self,obj,index):
        focusColumn = self.param["focusColumn"]
        keepSomeData = False
        if len(index)==0:
            keepSomeData = True
        else:
            minFs=9999999
            for column in index.keys():
                keyList = searchChannelKey(obj,column)
                if len(keyList)==2:
                    targetObj = obj[keyList[0]][keyList[1]]
                elif len(keyList)==1:
                    targetObj = obj[keyList[0]]
                else:
                    continue
                if targetObj["fs"]<minFs:
                    minFs=targetObj["fs"]
                    firstKey=column
            #firstKey=list(index.keys())[0]
            if len(index[firstKey])==0:
                keepSomeData = True
        
        if keepSomeData:
            targetTime = self.keepTimeLen
            for column in focusColumn:
                keyList = searchChannelKey(obj,column)
                if len(keyList)==2:
                    targetObj = obj[keyList[0]][keyList[1]]
                elif len(keyList)==1:
                    targetObj = obj[keyList[0]]
                else:
                    continue
                finalTime = targetObj["time"][-1]-targetTime
                keepCount = sum((targetObj["time"]>=finalTime)*1)
                targetObj["time"] = targetObj["time"][-keepCount:]
                targetObj["data"][column] = targetObj["data"][column][-keepCount:]
        else:
            for column in focusColumn:
                keyList = searchChannelKey(obj,column)
                if len(keyList)==2:
                    targetObj = obj[keyList[0]][keyList[1]]
                elif len(keyList)==1:
                    targetObj = obj[keyList[0]]
                else:
                    continue
                finalTime = index[firstKey][-1]["endTime"]
                keepCount = sum((targetObj["time"]>=finalTime)*1)
                targetObj["time"] = targetObj["time"][-keepCount:]
                targetObj["data"][column] = targetObj["data"][column][-keepCount:]
        
    def removeIdelData(self,obj,targetTime):
        focusColumn = self.param["focusColumn"]
        for column in focusColumn:
            keyList = searchChannelKey(obj,column)
            if len(keyList)==2:
                targetObj = obj[keyList[0]][keyList[1]]
            elif len(keyList)==1:
                targetObj = obj[keyList[0]]
            else:
                continue
            keepCount = sum((targetObj["time"]>=targetTime)*1)
            if keepCount==0:
                targetObj["time"] = targetObj["time"][-1:]
                targetObj["data"][column] = targetObj["data"][column][-1:]
            else:
                targetObj["time"] = targetObj["time"][-keepCount:]
                targetObj["data"][column] = targetObj["data"][column][-keepCount:]
                
    def removeExceptData(self,obj):
        focusColumn = self.param["focusColumn"]
        for column in focusColumn:
            keyList = searchChannelKey(obj,column)
            if len(keyList)==2:
                targetObj = obj[keyList[0]][keyList[1]]
            elif len(keyList)==1:
                targetObj = obj[keyList[0]]
            else:
                continue
            diff = np.array(targetObj["time"])[1:]-np.array(targetObj["time"])[:-1]
            if len(diff) > 0 and max(diff)>1: #inteval > 1 sec
                obj={} #reset
                return True
        return False
                
                
    def removeBeforeTrigger(self,obj): #return True == have tp wait more
        if self.param["operation_rising_falling"]==0:
            #print(self.param["name"],"operation_rising_falling",self.param["operation_rising_falling"])
            return False #end function
            
        triggerColumn = self.param["trigger_column"]
        threshold = self.param["operation_trigger_threshold"]
        trigger_shift = self.param["trigger_shift"]
        protectTime=0.1
        
        keyList = searchChannelKey(obj,triggerColumn)
        if len(keyList)==2:
            targetObj = obj[keyList[0]][keyList[1]]
        elif len(keyList)==1:
            targetObj = obj[keyList[0]]
        else:
            #print(self.param["name"],"keyList",keyList,self.param["trigger_column"])
            return False #end function
            
        diff = ((targetObj["data"][triggerColumn]-threshold)>0)*1
        diff = diff[:-1]-diff[1:] #1 is falling, -1 is rising
        
        if self.param["operation_rising_falling"]==1: #rising
            startIndex = np.argwhere(diff==-1)
        elif self.param["operation_rising_falling"]==2: #falling
            startIndex = np.argwhere(diff==1)
            
        if len(startIndex)>0 :
            #print(self.param["name"],"startIndex",startIndex)
            for point in startIndex:
                p = point[0]
                if targetObj["time"][p]+trigger_shift < min(targetObj["time"]):
                    #print(self.param["name"],"p",p,":",targetObj["time"][p],"< min",min(targetObj["time"]))
                    continue
                elif targetObj["time"][p]+trigger_shift > max(targetObj["time"]):
                    #print(self.param["name"],"p",p,":",targetObj["time"][p],"> max",max(targetObj["time"]))
                    keepTime = targetObj["time"][p]+ min(0,trigger_shift)-protectTime
                    self.removeIdelData(obj,keepTime)
                    return True #not enought, so don't trigger
                elif max(targetObj["time"])-(targetObj["time"][p]+trigger_shift) < self.allowDataLen:
                    keepTime = targetObj["time"][p]+ min(0,trigger_shift)-protectTime
                    #print(self.param["name"],"p",p,":",max(targetObj["time"])-(targetObj["time"][p]+trigger_shift),"allow",self.allowDataLen,"keepTime",keepTime)
                    #print(self.param["name"],max(targetObj["time"]),(targetObj["time"][p]+trigger_shift),max(targetObj["time"])-(targetObj["time"][p]+trigger_shift))
                    self.removeIdelData(obj,keepTime)
                    #print(self.param["name"],min(targetObj["time"]))
                    
                    return True #not enought, so don't trigger
                else:
                    testTime = targetObj["time"][p]
                    startTime = targetObj["time"][p]+trigger_shift
                    self.removeIdelData(obj,startTime)
                    #print(self.param["name"],"OK",p,testTime,startTime,min(targetObj["time"]),max(targetObj["time"])-min(targetObj["time"]),"allow",self.allowDataLen)
                    return False
            return True #not enought, so don't trigger
        else: #not get trigger, remove and keep shift length
            self.removeIdelData(obj,max(targetObj["time"])+trigger_shift-protectTime)
            return True #end function
            
    def busGarbageClean(self,obj):
        focusColumn = self.param["focusColumn"]
        for column in focusColumn:
            keyList = searchChannelKey(obj,column)
            if len(keyList)==2:
                targetObj = obj[keyList[0]][keyList[1]]
            else:
                continue
            
            # only check bus
            if keyList[0] != "bus":
                continue
                
            if len(targetObj['data'][column]) != len(targetObj['time']):
                del targetObj['data'][column]
            
            if len(targetObj['data'])==0:
                targetObj={}
                targetObj['type']="NONE"
                
            
            
    def checkAndPipeData(self,dataBuffer,targetIdelTime,testRaw,testResult,testFreqData):
        queueList = []
        
        testT=time.time()
        while not self.queue.empty(): 
            data=self.queue.get(False)
            queueList.append(data)
            del data
            time.sleep(0.01)
        #print("***rule checkAndPipeData****",len(queueList),time.time()-testT)
            
        if len(queueList)>0:
            if self.test:
                copyQueueList = copy.deepcopy(queueList)
                conponerObj(copyQueueList,testRaw)
                del copyQueueList
            conponerObj(queueList,dataBuffer)
        
        if getsizeof(dataBuffer)>100000000: #100MB protect
            dataBuffer={}
            gc.collect()
        
        self.busGarbageClean(dataBuffer)
        
        removeAct = self.removeExceptData(dataBuffer)
        if removeAct:
            targetIdelTime = time.time() #force defind idle time to now
            
        self.removeIdelData(dataBuffer,targetIdelTime)
        
        if self.param["operation_rising_falling"]!=0:
            #if self.dataLenCheck(dataBuffer):
            #    self.removeBeforeTrigger(dataBuffer)
            
            if self.removeBeforeTrigger(dataBuffer):
                # have to wait more data
                print(self.param["name"],"wait more")
                return targetIdelTime
        if self.dataLenCheck(dataBuffer):
            cutIndex = self.getCutIndex(dataBuffer,testFreqData)
            print(self.param["name"],"getCutIndex",cutIndex)
            #if len(cutIndex)==0 or True:
                #print("dataBuffer:")
                #testPrintStructure(dataBuffer)
                #print("")
            if len(cutIndex)>0:
                firstKey = list(cutIndex.keys())[0]
                maxTime = cutIndex[firstKey][-1]["endTime"]
                for ci in cutIndex.keys():
                    maxTime=max(maxTime,cutIndex[ci][-1]["endTime"])
                targetIdelTime = maxTime + self.param["ignore_time"]
                resultList = self.getResultObjList(dataBuffer,cutIndex)
                
                
                if self.test and self.testStartTime==0:
                    self.testStartTime = min(self.getFirstTime(testRaw))+self.param["workTime"]
                    #print("testStartTime",self.testStartTime,min(self.getFirstTime(testRaw)),self.param["workTime"])
                    
                if len(resultList)>0:
                    mainProgramStates.send(mainProgramStates._SegHeartbeat)
                for i,r in enumerate(resultList):
                    if not self.includeTarger(r["data"]):
                        continue
                    if self.test and self.testType!="2":
                        maxCutTime=0
                        for ci in cutIndex.keys():
                            maxCutTime=max(maxCutTime,cutIndex[ci][i]["endTime"])
                        #print("DEBUG",self.getLastTime(r["data"]), maxCutTime,self.testStartTime)
                        if  max(self.getLastTime(r["data"]))> self.testStartTime or maxCutTime > self.testStartTime:
                            print("continue")
                            continue
                    print(self.param["name"],"seg. put data!")
                    self.reQueue.put(r)
                    if self.param["smart_grid"]!=0:
                        SGF = self.getSmartGridFormat(r["data"])
                        if SGF is not None:
                            self.reQueue.put(SGF)
                    #print(self.param["extraction_project"], self.FEerr , self.param["upload_extraction"])
                    if isSPIIDER() and self.param["extraction_project"]>0 and not self.FEerr and self.param["upload_extraction"]==1:
                        data = dict()
                        try:
                            df_data = dataObj2pd(r["data"])
                            oneSeg_df =get_feature_engineer(self.param["extraction_project"], df_data)
                            data["name"] = r["name"]
                            data["type"] = "FE"
                            data["data"] = dict()
                            data["data"]["value"] = oneSeg_df.to_dict()
                            data["data"]["time"] = df_data["datetime"].values[0]
                            self.reQueue.put(data)
                            print(self.param["name"],"FE put data!")
                            #print(str(data)[:1000])
                            del data
                            del oneSeg_df
                        except Exception as e:
                            self.FEerr = True
                            printErr("Rule("+self.param["name"]+"), project ID ("+str(self.param["extraction_project"])+") err: "+str(e))
                            
                    
                if self.test:
                    for k in cutIndex.keys():
                        d = copy.deepcopy(cutIndex[k])
                        if k not in testResult.keys():
                            testResult[k]=d
                        else:
                            testResult[k]=testResult[k]+d
                    
            self.removeFinishData(dataBuffer,cutIndex)
        else:
            self.removeFinishData(dataBuffer,{}) #force clear
                
        #testPrintStructure(dataBuffer)
        return targetIdelTime
            
        
    def run(self):
        self.states["pid"]=os.getpid()
        print("Rule pid",self.states["pid"])
        # os.system("taskset -cp 2 %d" %(os.getpid()))
        
        dataBuffer = dict()
        
        startTime=time.time()
        endTime=startTime
        testRaw={}
        testResult={}
        testFreqData=[]
        targetIdelTime=0
        while not self.states["release"]:
            startTime=time.time()
            targetIdelTime= self.checkAndPipeData(
                dataBuffer,
                targetIdelTime,
                testRaw,
                testResult,
                testFreqData
                )
            endTime=time.time()
            sleepTime=self.minProcTime-(endTime-startTime)
            print("rule sleep/target",sleepTime,targetIdelTime)
            if sleepTime>0:
                time.sleep(sleepTime)
            
        #do onec and get buffer
        targetIdelTime= self.checkAndPipeData(
            dataBuffer,
            targetIdelTime,
            testRaw,
            testResult,
            testFreqData)
           
        #check buffer already not enought
        lastTargetIdelTime = 0
        while self.dataLenCheck(dataBuffer) and lastTargetIdelTime!=targetIdelTime:
            print("lastTargetIdelTime",lastTargetIdelTime)
            lastTargetIdelTime=targetIdelTime
            targetIdelTime = self.checkAndPipeData(
                dataBuffer,
                targetIdelTime,
                testRaw,
                testResult,
                testFreqData)
        
        if self.test:
            maxSec=9999999
            if self.param["workTime"]>0:
                maxSec=self.param["workTime"]
            testRaw=alineObj(testRaw,maxSec)
            if self.param["type"] == 2 or self.param["type"] == 3:
                print("draw rolling.")
                basis_column = self.param["basis_column"]
                keys = searchChannelKey(testRaw,basis_column)
                targetObj = None
                if len(keys)==2:
                    targetObj = copy.deepcopy(testRaw[keys[0]][keys[1]])
                elif len(keys)==1:
                    targetObj = copy.deepcopy(testRaw[keys[0]])
                    
                if targetObj != None:
                    print("process start.")
                    operation_count = float(self.param['operation_count']) * targetObj['fs']*2
                    operation_threshold=float(self.param['operation_threshold'])
                    operation_half = int(operation_count / 2)
                    data_pd = pd.DataFrame()
                    data_pd[basis_column] = targetObj["data"][basis_column]
                    
                    print("upload mean.")
                    self.updateMean(data_pd[basis_column])
                    mode = self.mean
                    data_abs = (data_pd[basis_column] - mode).abs()
                    print("rolling sum start.")
                    data_rolling = data_abs.rolling(operation_half).sum()  # v2
                    
                    print("data process.")
                    minTime = min(targetObj["time"])
                    print("data process. (isnull)")
                    rollingIndex = data_rolling.isnull()==False
                    draw=dict()
                    draw['title'] = "Rule("+self.param["name"]+")Result rolling"
                    draw['data'] = dict()
                    draw['data']['input_item'] = targetObj["data"][basis_column]
                    draw['time'] = targetObj["time"]-minTime
                    draw['timeR'] = targetObj["time"][rollingIndex]-minTime
                    if self.param["type"] == 3:
                        draw['timeR'] = draw['timeR']+self.param["operation_shift"]
                        
                    draw['dataR'] = dict()
                    print("data process. (dropna)")
                    draw['dataR']['Strength value'] = data_rolling.dropna()
                    draw['dataR']['threshold'] = np.ones(len(draw['timeR'])) *operation_threshold
                    draw['dataRtext'] = "Strength"
                    
                    print("get rolling.")
                    #cut_threshold
                    cut_threshold = (draw['dataR']['Strength value'] >= operation_threshold)*1
                    #平移相減
                    cut_index = cut_threshold.diff(periods = 1)
                    main_index = (cut_index != 0)
                    cut_index_arr = np.array(cut_index.index)[main_index][1:] # use [1:0] to dropna
                    cut_index_val = np.array(cut_index)[main_index][1:]#use [1:0] to dropna
                    
                    draw['textR'] = []
                    draw['textTag'] = []
                    textP = dict()
                    #for p in list(cut_index.index):
                    for i,p in enumerate(cut_index_arr):
                        if len(textP)>0 and cut_index_val[i]==-1:
                            textT = dict()
                            textT['x'] = (textP['x']+draw['time'][p])/2
                            textT['y'] = operation_threshold
                            textT['d'] = "{:6.2f}s".format(abs(textP['x']-draw['time'][p]))
                            textT['r'] = draw['time'][p]
                            textT['l'] = textP['x']
                            if self.param["type"] == 3:
                                textT['x'] = textT['x']+self.param["operation_shift"]/2
                                textT['r'] = textT['r']+self.param["operation_shift"]
                            draw['textTag'].append(textT)
                        textP = dict()
                        textP['x'] = draw['time'][p]
                        if self.param["type"] == 3:
                            textP['x'] = textP['x']+self.param["operation_shift"]
                        textP['y'] = operation_threshold
                        textP['d'] = "{:6.2f}s".format(draw['time'][p])
                        draw['textR'].append(textP)
                    
                    #print(draw['textR'])
                        
                    
                    if type(targetObj["unit"])==dict:
                        draw['unit']=targetObj["unit"][basis_column]
                    else:
                        draw['unit']=targetObj["unit"]
                    self.drawQueue.put(draw)
            
            if self.param["type"] == 3:
                print("draw stft.")
                basis_column = self.param["basis_column"]
                keys = searchChannelKey(testRaw,basis_column)
                targetObj = None
                if len(keys)==2:
                    targetObj = copy.deepcopy(testRaw[keys[0]][keys[1]])
                elif len(keys)==1:
                    targetObj = copy.deepcopy(testRaw[keys[0]])
                    
                if targetObj != None:
                    minTime = min(targetObj["time"])
                    timeR = np.array([])
                    dataR = np.array([])
                    textR = []
                    
                    for d in testFreqData:
                        print("testFreqData",len(d['data']),d['time'])
                        if len(d['data'])<=int(targetObj['fs']/5):
                            continue
                        t,f,f_id,Sx = self.get_max_freq(d['data'],targetObj['fs'],full=True)
                        
                        halfTimeInterval = abs(t[1]-t[0])
                        timeR = np.append(timeR,[t[0]+d['time']-minTime-halfTimeInterval])
                        print("halfTimeInterval",halfTimeInterval,timeR[-1])
                        dataR = np.append(dataR,[0])
                            
                        timeR = np.append(timeR,t+d['time']-minTime)
                        dataR = np.append(dataR,f[f_id])
                        
                        timeR = np.append(timeR,[t[-1]+d['time']-minTime+halfTimeInterval])
                        dataR = np.append(dataR,[0])
                            
                        resol=5
                        shift = int(np.floor(targetObj['fs']//resol))
                        f_max_idx = np.argmax(Sx, axis = 0)
                        f_max = np.floor(f[f_max_idx]).astype(int)
                        f_max_diff_abs = f_max[shift*2:]-f_max[:-shift*2] # V2.1
                        f_max_diff_abs[np.abs(f_max_diff_abs)>10*resol]=0 # V2.1
                        acc_mid = pd.Series(f_max_diff_abs).idxmax()+shift # V2.1
                        dec_mid = pd.Series(f_max_diff_abs).idxmin()+shift # V2.1
                        freq_counts = pd.Series(f_max)[acc_mid:dec_mid].value_counts() # V2.1
                        f_peaks = int(freq_counts.index[0])
                        if f_peaks == 0:
                            f_peaks = int(freq_counts.index[1])
                        equal_start = t[f_max == f_peaks][0]
                        equal_end = t[f_max == f_peaks][-1]
                        peak_idx = (equal_start+equal_end)/2 +d['time']-minTime
                        
                        
                        textP = dict()
                        textP['x'] = peak_idx
                        textP['y'] = f_peaks
                        textP['d'] = "{:6.1f}Hz".format(f_peaks)
                        textR.append(textP)
                        print(textP)
                        
                    draw=dict()
                    draw['title'] = "Rule("+self.param["name"]+")Result rolling"
                    draw['data'] = dict()
                    draw['data']['input_item'] = targetObj["data"][basis_column]
                    draw['time'] = targetObj["time"]-minTime
                    draw['timeR'] = timeR
                    draw['dataR'] = dict()
                    draw['dataR']['Main Freq.'] = dataR
                    draw['dataRtext'] = "Frequency(Hz)"
                    if type(targetObj["unit"])==dict:
                        draw['unit']=targetObj["unit"][basis_column]
                    else:
                        draw['unit']=targetObj["unit"]
                    draw['textR']=textR
                        
                        
                    
                    self.drawQueue.put(draw)
            
            # 2023/01/10 16:00:00 Kasper: Add for segByRawFilter
            if self.param["type"] == 5:
                
                print("draw rolling.")
                basis_column = self.param["basis_column"]
                keys = searchChannelKey(testRaw,basis_column)
                targetObj = None
                if len(keys)==2:
                    targetObj = copy.deepcopy(testRaw[keys[0]][keys[1]])
                elif len(keys)==1:
                    targetObj = copy.deepcopy(testRaw[keys[0]])
                    
                if targetObj != None:
                    print("process start.")
                
                    filter_threshold = self.param['operation_threshold']
                    fs = targetObj['fs']
                    motion_time = self.param['operation_filter']
                    capture_time = self.param['sub_operation_count']
                    num_filter = (int(motion_time * fs * 0.95), int(motion_time * fs * 1.05))
                    
                    shift_len = int(capture_time * fs * 0.5)
                    window_ratio = self.param['operation_count']
                    window_size = int(fs*window_ratio)
                    overlap_points = []
                    msg = ""
                    
                    data_pd = pd.DataFrame()
                    data_pd[basis_column] = targetObj["data"][basis_column]
                    data_filtered = np.where(data_pd[basis_column]<filter_threshold, 0, data_pd[basis_column])
                    rolling_sum = pd.DataFrame(data_filtered).rolling(window_size).sum().dropna()
                    rolling_sum_arr = np.array(rolling_sum).ravel()
                    rolling_sum_arr = np.where(rolling_sum_arr < 1e-06, 0, rolling_sum_arr)
                    zero_value_idx = np.array(rolling_sum.index)[np.argwhere(rolling_sum_arr==0).ravel()]
                    
                    #print("****** data_filtered ******:\n", data_filtered.ravel()[3000:9000])
                    print("****** rolling_sum ******:\n", rolling_sum)

                    #print("****** rolling_sum_arr ******:\n", rolling_sum_arr.ravel()[3000:9000])

                    
                    if len(zero_value_idx) < len(rolling_sum_arr)*0.05:
                        msg = "\n[Warning] The rolling results have few zero value, try to 'INCREASE' the Filter Threshold"
                    elif len(zero_value_idx) == len(rolling_sum_arr):
                        msg = "\n[Warning] The rolling results are all zero value, try to 'DECREASE' the Filter Threshold"
                    
                    diff_idx = np.diff(np.where(rolling_sum_arr > 0, 1, rolling_sum_arr)).astype(np.int)
                    start_points, end_points = list(rolling_sum.index[1:][diff_idx==1]-1), list(rolling_sum.index[1:][diff_idx==-1]-1)
                    if start_points == [] or end_points == []:
                        pass
                        # msg = "\n[INFO] This signal has no complete motion."
                    else:
                        new_end_points = list(np.array(end_points)-window_size)
                        new_rolling_sum = []
                        start_idx = 0
                        for old_idx, new_idx in zip(end_points, new_end_points):
                            new_rolling_sum += np.ones(new_idx-start_idx, dtype=int).tolist()
                            new_rolling_sum += np.zeros(old_idx-new_idx, dtype=int).tolist()
                            start_idx = old_idx
                        new_rolling_sum = new_rolling_sum[window_size:]
                        new_rolling_sum += np.ones(len(rolling_sum_arr)-start_idx+window_size, dtype=int).tolist()
                        rolling_sum_arr *= new_rolling_sum
                        # rolling_sum_arr = pd.DataFrame(rolling_sum_arr)
                        # rolling_sum_arr.index = rolling_sum.index
                        
                        end_points = new_end_points
                            
                        print("****** diff_idx ******:\n", len(diff_idx[diff_idx!=0]))
                        print("****** start_points ******:\n", start_points)
                        print("****** end_points ******:\n", end_points)

                    
                        if start_points[0] > end_points[0]:
                            start_points = [0] + start_points
                        if len(start_points) < len(end_points):
                            start_points = [0] + start_points
                        elif len(start_points) > len(end_points):
                            end_points.append(len(data_pd[basis_column])-1)

                        start_points, end_points = np.array(start_points), np.array(end_points)
                        seg_len = end_points - start_points
                        print("****** seg_len ******:\n", seg_len)
                        print("****** num_filter ******:\n", num_filter)
                        pass_seg_idx = np.argwhere((seg_len>=num_filter[0]) & (seg_len<=num_filter[1])).ravel()
                        print("****** pass_seg_idx ******:\n", pass_seg_idx)

                        if np.size(pass_seg_idx) == 0:
                            msg = "\n[WARNING] No pass segment, try to tune the 'Motion Time'"
                        else:
                            pass_start_points, pass_end_points = start_points[pass_seg_idx], end_points[pass_seg_idx]
                            official_mid_seg_idx = np.array((pass_start_points + pass_end_points)/2, dtype=int)
                            official_start_seg_idx, official_end_seg_idx = official_mid_seg_idx - shift_len, official_mid_seg_idx + shift_len
                            temp_start_seg_idx, temp_end_seg_idx = np.concatenate([official_start_seg_idx, [len(data_filtered)]]), np.concatenate([[0], official_end_seg_idx])
                            
                            """ Check whether official segments have overlaps with themself """
                            rule_1 = np.size(np.where(temp_start_seg_idx[1:-1] - temp_end_seg_idx[1:-1] < 0)) == 0
                            print("****** rule_1 ******:", rule_1)
                            print("****** temp_start_seg_idx ******:", temp_start_seg_idx)
                            print("****** temp_end_seg_idx ******:", temp_end_seg_idx)
                            if not rule_1:
                                overlap_idx = np.argwhere(temp_start_seg_idx - temp_end_seg_idx < 0).ravel()
                                overlap_points = [(temp_start_seg_idx[i], temp_end_seg_idx[i]) for i in overlap_idx]
                                msg = "\n[Warning] The Capture Time is too long so the captured signal may contain redundant signal, try to 'DECREASE' the Capture Time"
                            
                            """ Check whethere official segments have overlaps with temp segments """
                            next_start_point_idx = []
                            for i in pass_seg_idx + 1:
                                if i < len(start_points):
                                    next_start_point_idx.append(i)
                            next_end_point_idx = []
                            for i in pass_seg_idx - 1:
                                if i >= 0:
                                    next_end_point_idx.append(i)
                            print("****** next_end_point_idx ******:", next_end_point_idx)
                            
                            if len(next_start_point_idx) != len(official_end_seg_idx):
                                next_start_point = np.concatenate([start_points[next_start_point_idx], [len(data_filtered)]])
                            else:
                                next_start_point = start_points[next_start_point_idx]
                            
                            if len(next_end_point_idx) != len(official_start_seg_idx):
                                next_end_point = np.concatenate([[0], end_points[next_end_point_idx]])
                            else:
                                next_end_point = end_points[next_end_point_idx]
                                
                            rule_2 = np.size(np.where(official_end_seg_idx - next_start_point > 0)) == 0
                            rule_3 = np.size(np.where(official_start_seg_idx - next_end_point < 0)) == 0
                            print("****** rule_2 ******:", rule_2)
                            print("****** rule_3 ******:", rule_3)
                            print("****** official_end_seg_idx ******:", official_end_seg_idx)
                            print("****** next_start_point ******:", next_start_point)
                            print("****** official_start_seg_idx ******:", official_start_seg_idx)
                            print("****** next_end_point ******:", next_end_point)
                            print("****** pass_start_points ******:", pass_start_points)
                            print("****** pass_end_points ******:", pass_end_points)

                            
                            if not (rule_2 and rule_3):
                                overlap_idx = np.argwhere(official_end_seg_idx - next_start_point < 0).ravel()
                                overlap_points = [(official_end_seg_idx[i], next_start_point[i]) for i in overlap_idx]
                                overlap_idx = np.argwhere(official_start_seg_idx - next_end_point < 0).ravel()
                                overlap_points += [(official_start_seg_idx[i], next_end_point[i]) for i in overlap_idx]
                                msg = "\n[Warning] The Capture Time is too long so the captured signal may contain redundant signal, try to 'DECREASE' the Capture Time"
                            
                            rule_4 = np.size(np.where(pass_start_points - official_start_seg_idx < 0)) == 0
                            if not rule_4:
                                overlap_idx = np.argwhere(pass_start_points - official_start_seg_idx < 0).ravel()
                                overlap_points = [(pass_start_points[i], official_start_seg_idx[i]) for i in overlap_idx]
                                msg = "\n[Warning] The Capture Time is too short so the captured signal may loss signal, try to 'INCREASE' the Capture Time"

                    print("data process.")
                    minTime = min(targetObj["time"])
                    print("data process. (isnull)")
                    rollingIndex = rolling_sum.isnull()==False
                        
                    # for drawing raw data information
                    draw=dict()
                    draw['title'] = "Rule("+self.param["name"]+")Result rolling" + msg
                    draw['data'] = dict()
                    draw['data']['input_item'] = targetObj["data"][basis_column]
                    draw['time'] = targetObj["time"]-minTime
                    
                    # for drawing rolling infomation
                    draw['dataR'] = dict()
                    draw['timeR'] = targetObj["time"][rolling_sum.index]-minTime
                    draw['dataR']['Strength value'] = rolling_sum_arr
                    draw['dataR']['Filter Threshold'] = np.ones(len(draw['timeR'])) * filter_threshold
                    draw['S_E points'] = np.concatenate((start_points, end_points), axis=None)/fs

                    draw['dataRtext'] = "Strength"

                    """
                    TODO: Draw the segmentation results from overall view, which can show precise overlap results
                    # for drawing ovelaping information
                    if overlap_points != []:
                        draw['ovelap'] = dict()
                        draw['ovelap']['overlap_points'] = overlap_points
                    """
                    
                    if type(targetObj["unit"])==dict:
                        draw['unit']=targetObj["unit"][basis_column]
                    else:
                        draw['unit']=targetObj["unit"]
                    self.drawQueue.put(draw)
                
            maxSec=9999999
            if self.param["workTime"]>0:
                maxSec=self.param["workTime"]
                
            name_array = self.param["name"].split("@")
            fTitle = "Rule("+name_array[0]+"@"+name_array[1]+name_array[2]+")Result "
            
            # plot segmentation result
            drawList = []
            for k in testResult.keys():  # testResult is the segmentation results, if it is empty, then it won't draw anything
                full = []  # if full is empty, then it won't plot
                overlap_full = []
                for t in testResult[k]:
                    startTime = t["startTime"]
                    endTime = t["endTime"]
                    full.append([startTime,endTime])
                    if "overlap_startTime" in t:
                        for o_sT, o_eT in zip(t["overlap_startTime"], t["overlap_endTime"]):
                            overlap_full.append([o_sT, o_eT])
                        
                obj = keepChannelName(testRaw,[k])
                
                if self.testType == "2":
                    drawList = drawList+dataObj2drawList(obj,99999999,fTitle,full,overlap_full)
                else:
                    drawList = drawList+dataObj2drawList(obj,maxSec,fTitle,full,overlap_full)
            
            for d in drawList:
                self.drawQueue.put(d)
    
    def release(self):
        self.stopProc()
        if self.is_alive():
            self.join()
        self.exit.set()
