#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: alan
"""
import os
import time
import sys
import psutil
import re
from datetime import datetime
import configparser
import socket
import requests
import glob
import json
import Library.SpiSlaveScan as SpiSlaveScan
import Library.VibrationHub as VibrationHub
import Library.ADCHub as ADCHub
import RPi.GPIO as GPIO

def script(cmd):
	log = True
	p = os.popen(cmd)
	t = p.read()
	if log:
		print(t)
	p.close()
	
def reset():
	ST2_pin = 13
	reverse = True
	time.sleep(1)
	#reset config
	print("reset config")
	script("rm /home/pi/default/device.ini_ub")
	script("rm /home/pi/program/system.ini_ub")
	script("rm /home/pi/program/work.ini_ub")
	script("cp /home/pi/default/original_device.ini /home/pi/default/device.ini ")
	script("cp /home/pi/default/system.ini /home/pi/program/system.ini ")
	script("cp /home/pi/default/work.ini /home/pi/program/work.ini ")
	
	#clear file
	print("clear file")
	script("rm /home/pi/program/LocalSaved/*")
	
	#reset wifi connection information
	print("reset wifi connection information")
	script("/home/pi/tool_sh/wifi_disconnect.sh")
	
	#clear static network IP setting
	print("clear static network IP setting")
	script("/home/pi/tool_sh/ip_setting.sh -- -- -- -- -- -- -- -- --")
	
	#reset AP setting
	print("reset AP setting")
	script("hostname raspberry")
	
	time.sleep(1)
	
	GPIO.output(ST2_pin,0^reverse)
	script("/bin/hostAP_check.sh >> /home/pi/Desktop/test.txt")
	script("(sleep 2 ; shutdown -r 0 )&")

def shutdown():
	script("(sleep 1 ; shutdown -h 0 )&")
	
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
#Static info
def getAPSSID():
	path = '/home/pi/default/system.ini'
	config = configparser.ConfigParser()
	config.read(path)
	sys_dic = config._sections
	if 'ap' in sys_dic.keys():
		if 'name' in sys_dic['ap'].keys():
			return sys_dic['ap']['name']
	return None

def getWifiSSID():
	return str(os.popen("iwgetid -r").readline().strip())
	
def getAPMac():
	try:
		string = str(os.popen("iwconfig wlan0 | grep Access | tr -d ' ' ").readline().strip())
		split_str = string.split(":",3)
		return split_str[3]
	except:
		return ""
		
def getWifiIP():
	try:
		string = str(os.popen("ip addr show wlan0 | grep 'inet\s' | awk \'{ print $2 }\'").readline().strip())
		split_str=string.split("/",1)
		return split_str[0]
	except:
		return ""
		
def getLanMac():
	try:
		string = str(os.popen("ifconfig eth0 | grep dc").readline().strip())
		split_str = string.split(":",1)
		split_str = split_str[1].split(" ",1)
		return split_str[0]
	except:
		return ""

def getLanIP():
	try:
		string = str(os.popen("ifconfig eth0 | grep inet").readline().strip())
		split_str = string.split(" ",2)
		return split_str[1]
	except:
		return ""
		
def getLan2Mac():
	try:
		string = str(os.popen("ifconfig eth1 | grep dc").readline().strip())
		split_str = string.split(":",1)
		split_str = split_str[1].split(" ",1)
		return split_str[0]
	except:
		return ""

def getLan2IP():
	try:
		string = str(os.popen("ifconfig eth1 | grep inet").readline().strip())
		split_str = string.split(" ",2)
		return split_str[1]
	except:
		return ""
	
def getTotalROM():
	return (round(psutil.disk_usage('/').total / (2**30),3))
	
def getTotalRAM():
	return (round(psutil.virtual_memory().total/(2**30),3))
	
#Recognize
def getMacID():
	try:
		mac = open('/sys/class/net/wlan0/address').read().strip()
	except:
		mac = "00:00:00:00:00:00"
	return mac
#Environment status
def getCPUTemperature():
	try:
		res = os.popen('vcgencmd measure_temp').readline().strip()
		return float(res.replace("temp=","").replace("'C",""))
	except:
		return 0
	
def getCPULoad():
	try:
		return float(psutil.cpu_percent())
	except:
		return 0

def getRamPercent():
	return psutil.virtual_memory()[3] / psutil.virtual_memory()[0] * 100

def getRomPercent():
	return psutil.disk_usage('/').percent
		
def getSignal():
	try:
		pid = str(os.popen('/home/pi/tool_sh/eeprom -r 1').readline().strip())
	except:
		pid = ''
	try:
		if pid != '':
			sig = str(os.popen("wpa_cli SIGNAL_POLL | grep RSSI | tr -d ' ' | cut -d'=' -f2").readline().strip())
		else:
			sig = str(os.popen("iwconfig wlan0 | grep Signal | tr -d ' ' | cut -d'=' -f3").readline().strip())
		split_str = sig.split("d")
		return float(split_str[0])
	except:
		return 0
def getQuality():
	try:
		string = str(os.popen("iwconfig wlan0 | grep Quality").readline().strip())
		split_str = string.split(" ",2)
		str_t = split_str[1].split("=",2)
		split_str = str_t[1].split("/",2)
		Qulity = (str)((int)(split_str[0])/(int)(split_str[1])*100)+'%'
		return Qulity
	except:
		return ''
def getApStatus(chk):
	try:
		if chk == 1:
			string = str(os.popen("iwconfig wlan1 | grep ESSID").readline().strip())
			if string != "":
				apConns = str(os.popen("iw dev wlan1 station dump | grep Station").readline().strip())
				if apConns != "":
					return 2
				return 1
			else:
				return 0
		else:
			string = str(os.popen("iwconfig ap0 | grep Tx-Power").readline().strip())
			if string != "":
				apConns = str(os.popen("iw dev ap0 station dump | grep Station").readline().strip())
				if apConns != "":
					return 2
				return 1
			else:
				return 0
	except:
		return 0
		
#Device work status	
def getBootTime():
	uptime = os.popen('uptime').readline()
	chunks = re.split(r"[ ,]+",uptime)
	uptime = chunks[3].split(":")
	return_time = ''
	if len(uptime) == 1:
		return_time = str(int(uptime[0]))
	elif len(uptime) == 2:
		return_time = str(int(uptime[0])*60 + int(uptime[1]))
	return return_time

def getDeviceTime():
	date = datetime.now()
	timeStr = date.strftime("%Y-%m-%d %H:%M:%S")
	return timeStr
	
def getruleType(workDict, Name):
	ruleType = []
	ruleFs = []
	hub_mode = ',,,,,,,'
	hub_name = ',,,,,,,'
	str_Name_split = Name.split(',')
	vibHeader = ['aX_','aY_','aZ_']
	#print(len(str_Name_split))
	for n in range(len(str_Name_split)):
		hasFindMode = False
		if str_Name_split[n][0:3] in vibHeader:
			inputName = str_Name_split[n][3:]
		else:
			inputName = str_Name_split[n]
		print(inputName)
		#analog
		mode_Type = ["votage","current"]
		modeTypeCur = 0
		hub_sample_rate = getDictItem(workDict,'analog','sample_rate',',,,')
		str_sampleRate_split = hub_sample_rate.split(',')
		for i in range(4):
			hubModeOption = "hub" + str(i+1) + "_mode"
			hubNameOption = "hub" + str(i+1) + "_name"
			hub_mode = getDictItem(workDict,'analog',hubModeOption,',,,,,,,')
			hub_name = getDictItem(workDict,'analog',hubNameOption,',,,,,,,')
			if(hub_name != ',,,,,,,'):
				str_name_split = hub_name.split(',')
				str_mode_split = hub_mode.split(',')
				for j in range(len(str_name_split)):
					if (str_name_split[j] != '') and (str_name_split[j] == inputName):
						if(int(str_mode_split[j]) != 0):
							modeTypeCur = 1
						else:
							modeTypeCur = 0
						ruleType.append(mode_Type[modeTypeCur])
						ruleFs.append(int(str_sampleRate_split[i]))
						hasFindMode = True
						break
		if hasFindMode == False:
			#Vibration
			hub_sample_rate = getDictItem(workDict,'vibration','sample_rate',',,,')
			str_sampleRate_split = hub_sample_rate.split(',')
			for i in range(4):
				hubNameOption = "hub" + str(i+1) + "_name"
				hub_name = getDictItem(workDict,'vibration',hubNameOption,',,,,,')
				if(hub_name != ',,,,,'):
					str_split = hub_name.split(',')
					for j in range(len(str_split)):
						if (str_split[j] != '') and (str_split[j] == inputName):
							ruleType.append('vibration')
							ruleFs.append(int(str_sampleRate_split[i]))
							hasFindMode = True
							break
			if hasFindMode == False:
				#Distance
				for i in range(1):
					chNameOption = "ch" + str(i+1) + "_name"
					ch_name = getDictItem(workDict,'distance',chNameOption,'')
					if(ch_name != '') and (ch_name == inputName):
						ruleType.append('distance')
						ruleFs.append(30)
						hasFindMode = True
						break
				if hasFindMode == False:
					#prognosis
					hub_sample_rate = getDictItem(workDict,'prognosis','sample_rate',',')
					str_sampleRate_split = hub_sample_rate.split(',')
					hub_name = getDictItem(workDict,'prognosis','name',',')
					if(hub_name != ','):
						str_split = hub_name.split(',')
						for j in range(len(str_split)):
							if (str_split[j] != '') and (str_split[j] == inputName):
								ruleType.append('prognosis')
								ruleFs.append(int(str_sampleRate_split[i]))
								hasFindMode = True
								break
					if hasFindMode == False:
						#audio
						hub_name = getDictItem(workDict,'audio','name',',')
						if(hub_name != ','):
							str_split = hub_name.split(',')
							for j in range(len(str_split)):
								if (str_split[j] != '') and (str_split[j] == inputName):
									ruleType.append('audio')
									ruleFs.append(44100)
									hasFindMode = True
									break
						if hasFindMode == False:
							#gpio
							for i in range(4):
								chNameOption = "ch" + str(i+1) + "_name"
								ch_name = getDictItem(workDict,'gpio',chNameOption,'')
								if(ch_name != '') and (ch_name == inputName):
									ruleType.append('digital input')
									ruleFs.append(20)
									break
	return ruleType, ruleFs
	
def getBoardVersion():
	data = SpiSlaveScan.scanSlave()
	data = data[:4]
	bus = []
	boardVersion = []
	boardType = []

	for index,d in enumerate(data):
		obj = dict()
		if d == "Vibration board":
			boardType.append("Vibration")
			vib = VibrationHub.VibHub(index)
			boardVersion.append(vib.GetFWVersion())
		elif d == "Voltage board":
			boardType.append("Voltage")
			adc = ADCHub.ADCHub(index)
			boardVersion.append(adc.GetFWVersion())
		elif d == "Current board":
			boardType.append("Current")
			adc = ADCHub.ADCHub(index)
			boardVersion.append(adc.GetFWVersion())
		else:
			boardType.append("")
			boardVersion.append("")
	return boardVersion, boardType
	
def staticInfoTrans(boardVersion, boardType):
	payload_dict = dict()
	payload_dict.setdefault('trxName','basic')
	payload_dict.setdefault('id',getMacID())
	payload_dict.setdefault('apSSID',getAPSSID())
	payload_dict.setdefault('apMac',getAPMac())
	payload_dict.setdefault('wifiName',getWifiSSID())
	payload_dict.setdefault('wifiMac',getMacID())
	payload_dict.setdefault('ipAddress',getWifiIP())
	payload_dict.setdefault('lan1Mac',getLanMac())
	payload_dict.setdefault('lan1IP',getLanIP())
	payload_dict.setdefault('lan2Mac',getLan2Mac())
	payload_dict.setdefault('lan2IP',getLan2IP())
	payload_dict.setdefault('totalROM',getTotalROM())
	payload_dict.setdefault('totalRAM',getTotalRAM())
	payload_dict.setdefault('deviceTime',getDeviceTime())
	d = [requests.get('http://127.0.0.1/api/work/file'),requests.get('http://127.0.0.1/api/system/file')]
	config = configparser.ConfigParser()
	config.read(d[1].text)
	payload_dict.setdefault('sysConfig',d[1].text)
	payload_dict.setdefault('workConfig',d[0].text)
	
	configDict = loadConfig("d")
	print(configDict)
	workDict = loadConfig("w")
	print(workDict)
	#ruleName/ruleType
	ruleName = []
	ruleType = []
	ruleType_name = ["","normal","time","freq","normal"]
	for key in workDict.keys():
		if 'type' in workDict[key].keys():
			if workDict[key]['type'] != '0':
				if workDict[key]['name'] != '':
					ruleName.append(workDict[key]['name']+'@'+getDictItem(workDict,key,'unit','')+'@'+getDictItem(workDict,key,'subunit',''))
					ruleType.append(ruleType_name[int(workDict[key]['type'])])
	#ruleBasicName/ruleOutputName
	ruleBasicName = []
	ruleOutputName = []		
	
	ruleBasicType = []
	ruleOutputType = []
	
	ruleBasicFs = []
	ruleOutputFs = []
	
	segCount = 0
	while(1):
		segCount+=1
		segStr = "segmentation_" + str(segCount)
		segType = getDictItem(workDict,segStr,"type","-1")
		if(segType == "-1"):
			break
		if(segType != "0"):
			basicName = getDictItem(workDict,segStr,'basis_column','')
			outputName = getDictItem(workDict,segStr,'target_column','')
			ruleBasicName.append(basicName)
			ruleOutputName.append(outputName)
			if basicName == '':
				ruleBasicType.append('')
				ruleBasicFs.append('')
			else:
				outType, outFs = getruleType(workDict,basicName)
				ruleBasicType.append(outType)
				ruleBasicFs.append(outFs)
				
			if outputName == '':
				ruleOutputType.append('')
				ruleOutputFs.append('')
			else:
				outType, outFs = getruleType(workDict,outputName)
				ruleOutputType.append(outType)
				ruleOutputFs.append(outFs)

	
	payload_dict.setdefault('ruleName',ruleName)
	payload_dict.setdefault('ruleType',ruleType)
	payload_dict.setdefault('ruleBasicName',ruleBasicName)
	payload_dict.setdefault('ruleOutputName',ruleOutputName)
	payload_dict.setdefault('ruleBasicType',ruleBasicType)
	payload_dict.setdefault('ruleOutputType',ruleOutputType)
	payload_dict.setdefault('ruleBasicFs',ruleBasicFs)
	payload_dict.setdefault('ruleOutputFs',ruleOutputFs)
	
	version = configDict['environment']['version']
	payload_dict.setdefault('programVersion','D'+version)
	

	payload_dict.setdefault('boardVersion',boardVersion)
	payload_dict.setdefault('boardType',boardType)
	
	return payload_dict
	
def dynamicInfoTrans(startWorkTime,uploadStatus,ST1,ST2,message,Seg,FE):
	#time.sleep(1)
	payload_dict = dict()
	payload_dict.setdefault('trxName','period')
	payload_dict.setdefault('id',getMacID())
	payload_dict.setdefault('cpuTemp',getCPUTemperature())
	payload_dict.setdefault('cpuUsage',getCPULoad())
	payload_dict.setdefault('memoryUsage',getRamPercent())
	payload_dict.setdefault('ROMUsage',getRomPercent())
	payload_dict.setdefault('wifiStrength',getSignal())
	#payload_dict.setdefault('keepBootTime',getBootTime())
	#payload_dict.setdefault('keepWorkTime',str(int(time.time()-startWorkTime)))
	#
	#payload_dict.setdefault('uploadStatus',uploadStatus)
	#localfile check
	FTP_count = 0
	API_count = 0
	MQTT_count = 0
	configDict = loadConfig("d")
	test_flag = configDict['environment']['sensor_test_state']
	program_path = configDict['environment']['home_dir']
	if test_flag == '1':
		path_dir = program_path + "/T_LocalSaved/"
		Upload_label_startCount = len(path_dir)
	elif test_flag == '0':
		path_dir = program_path + "/LocalSaved/"
		Upload_label_startCount = len(path_dir)
		
	if(glob.glob(path_dir+'*') != []):
		for f in glob.glob(path_dir+'*'):
			first_file = f
			Upload_label = str(first_file[Upload_label_startCount:Upload_label_startCount+2])
			if (Upload_label == "F_"):
				FTP_count += 1
			elif (Upload_label == "A_"):
				API_count += 1
			elif (Upload_label == "M_"):
				MQTT_count += 1
	
	payload_dict.setdefault('locationFileCountForAPI',API_count)
	payload_dict.setdefault('locationFileCountForFTP',FTP_count)
	payload_dict.setdefault('locationFileCountForMQTT',MQTT_count)
	payload_dict.setdefault('segCount',Seg)
	payload_dict.setdefault('featureCount',FE)
	
	ST1_label = ["non-work","idle","sample","seg.","sensor error"]
	ST2_label = ["non-network","empty","successful","fail","RAM alarm"]
	ST1_shift = ST1+1
	ST2_shift = ST2+1
	payload_dict.setdefault('ST1',ST1_label[ST1_shift])
	payload_dict.setdefault('ST2',ST2_label[ST2_shift])
	payload_dict.setdefault('message',message)
	payload_dict.setdefault('deviceTime',getDeviceTime())

	return payload_dict
	
#For Auo
proxy_server_index=0
proxy_testTime="YYYY-MM-DD"
proxy_server_list=["http://10.97.4.1:8080",
				   "http://10.37.9.111:8080",
				   "http://10.88.95.1:8080",
				   "http://10.22.10.134:8080",
				   "http://10.84.66.6:8080",
				   "http://10.31.10.188:8080",
				   "http://10.34.128.199:8080",
				   "http://10.34.129.100:8080"]

proxy_search_record_path="proxy_search_record"
proxy_list={}
proxy_list["10.88"]="http://10.88.95.1:8080"
proxy_list["10.31"]="http://10.31.10.188:8080"
proxy_list["10.21"]="http://10.22.10.134:8080"
proxy_list["10.1"]="http://10.22.10.134:8080"
proxy_list["10.98"]="http://10.97.4.1:8080"
proxy_list["10.37"]="http://10.37.9.111:8080"
proxy_list["10.84"]="http://10.84.66.6:8080"
proxy_list["10.34"]={}
proxy_list["10.34"]["83"]="http://10.34.128.199:8080"
proxy_list["10.34"]["116"]="http://10.34.129.100:8080"
proxy_list["10.34"]["117"]="http://10.34.129.100:8080"
proxy_list_ex=["10.34"]
proxy_success_flag = False

def creat_config(A,B):
	global proxy_search_record_path
	config = configparser.ConfigParser()
	config.add_section("record")
	config.set("record","proxy_server_index",A)
	config.set("record","proxy_testtime",B)
	config.write(open(proxy_search_record_path,"w"))
	
def getDict(dic,key, default=None):
	val=dic.get(key, default)
	if val=="":
		return default
	return val 

def IoTInfoTrans(Seg,FE):
	configDict = loadConfig('d')
	workDict = loadConfig('w')
	systemDict = loadConfig('s')
	#sampling rate
	samplingRate_list = []

	#columnsName/columnsType
	columnsName = ''
	#analog
	hub_name = []
	sampling_rate_string = getDictItem(workDict,'analog','sample_rate','0')
	split_sampling = sampling_rate_string.split(",")
	sampling_rate_int = [int(i) for i in split_sampling]
	max_sampling_rate = max(sampling_rate_int)
	hub_name.append(getDictItem(workDict,'analog','hub1_name',',,,,,'))
	hub_name.append(getDictItem(workDict,'analog','hub2_name',',,,,,'))
	hub_name.append(getDictItem(workDict,'analog','hub3_name',',,,,,'))
	hub_name.append(getDictItem(workDict,'analog','hub4_name',',,,,,'))
	for i in range(4):
		if(hub_name[i] != ',,,,,,,'):
			str_name_split = hub_name[i].split(',')
			for j in range(len(str_name_split)):
				if str_name_split[j] != '':
					columnsName=columnsName+str_name_split[j]+','
	#vibration
	hub_name = []
	sampling_rate_string = getDictItem(workDict,'vibration','sample_rate','0')
	split_sampling = sampling_rate_string.split(",")
	sampling_rate_int = [int(i) for i in split_sampling]
	max_sampling_rate = max(max(sampling_rate_int),max_sampling_rate)
	hub_name.append(getDictItem(workDict,'vibration','hub1_name',',,,,,'))
	hub_name.append(getDictItem(workDict,'vibration','hub2_name',',,,,,'))
	hub_name.append(getDictItem(workDict,'vibration','hub3_name',',,,,,'))
	hub_name.append(getDictItem(workDict,'vibration','hub4_name',',,,,,'))
	for i in range(4):
		if(hub_name[i] != ',,,,,'):
			str_split = hub_name[i].split(',')
			for j in range(len(str_split)):
				if str_split[j] != '':
					columnsName=columnsName+str_split[j]+','
					
	#distance
	ch_name = getDictItem(workDict,'distance','ch1_name','')
	if(ch_name != ''):
		columnsName=columnsName+ch_name+','
	#digital
	ch_name = []
	ch_name.append(getDictItem(workDict,'gpio','ch1_name',''))
	ch_name.append(getDictItem(workDict,'gpio','ch2_name',''))
	ch_name.append(getDictItem(workDict,'gpio','ch3_name',''))
	ch_name.append(getDictItem(workDict,'gpio','ch4_name',''))
	for i in range(4):
		if(ch_name[i] != ''):
			columnsName=columnsName+ch_name[i]+','
	
	diskinfo = psutil.disk_usage("/")
	disk_used=round(diskinfo.used/(1024*1024*1024),3)
	disk_free=round(diskinfo.free/(1024*1024*1024),3)
	payload_dict = dict()
	payload_dict.setdefault('wifiMac',getMacID())
	payload_dict.setdefault('apMac',getAPMac())
	payload_dict.setdefault('eqpId',getDictItem(systemDict,'ap','name','Unknown'))
	payload_dict.setdefault('programStatus',1)
	version = configDict['environment']['version']
	payload_dict.setdefault('programVersion','D'+version)
	payload_dict.setdefault('loopIndex',1)
	payload_dict.setdefault('realSamplingRate',max_sampling_rate)
	payload_dict.setdefault('recordSecond','0')
	payload_dict.setdefault('sensorList',columnsName)
	payload_dict.setdefault('segCount',Seg)
	payload_dict.setdefault('featureCount',FE)
	payload_dict.setdefault('cpuTemp',float(getCPUTemperature()))
	payload_dict.setdefault('memoryUsage',float(getRamPercent()))
	payload_dict.setdefault('diskUsedG',float(disk_used))
	payload_dict.setdefault('diskFreeG',float(disk_free))
	payload_dict.setdefault('wifiName',getWifiSSID())
	payload_dict.setdefault('wifiQuality',getQuality())
	payload_dict.setdefault('wifiStregth',getSignal())
	payload_dict.setdefault('ipAddress',getWifiIP())
	print(payload_dict)
	API_URL = getDictItem(systemDict,"server","ip","")
	API_PROXY = getDictItem(systemDict,"server","proxy","")
	if API_URL == "":
		API_URL = "http://10.88.19.70:8080/api/CIotPhmdevices/updateStatus";
	auoUploadFlag = IoTRequire(payload_dict,API_URL,API_PROXY,True)
	
	return auoUploadFlag

def getMappingProxy():
	global proxy_list
	global proxy_list_ex
	ip_str=getWifiIP().split(".")
	ip_str_judge=".".join(ip_str[:2])
	if ip_str_judge in proxy_list.keys():
		if ip_str_judge in proxy_list_ex:
			if ip_str[2] in proxy_list[ip_str_judge].keys():
				proxy_mapping=proxy_list[ip_str_judge][ip_str[2]]
		else:
			proxy_mapping=proxy_list[ip_str_judge]
	else:
		proxy_mapping = ""
	return proxy_mapping
			

def IoTRequire(data,url,proxy,first=False):
	global proxy_server_index
	global proxy_server_list
	global proxy_search_record_path
	global proxy_list
	global proxy_list_ex
	global proxy_testTime
	global proxy_success_flag
	nowTimeString=datetime.strftime(datetime.now(),"%Y-%m-%d")
	use_mapping=False
	uploadFlag = False
	proxy_mapping=""
	if proxy == "":
		if first:
			ip_str=data["ipAddress"].split(".")
			ip_str_judge=".".join(ip_str[:2])
			if ip_str_judge in proxy_list.keys():
				if ip_str_judge in proxy_list_ex:
					if ip_str[2] in proxy_list[ip_str_judge].keys():
						proxy_mapping=proxy_list[ip_str_judge][ip_str[2]]
						use_mapping=True
				else:
					proxy_mapping=proxy_list[ip_str_judge]
					use_mapping=True
					
		j_data=json.dumps(data,separators=(',',':'))

		if use_mapping==False:
			if os.path.isfile(proxy_search_record_path):
				config = configparser.ConfigParser()
				config.read(proxy_search_record_path)
				config_dict=dict()
				try:
					config_list=config.items("record")
					for config_list_data in config_list:
						config_dict[config_list_data[0]]=config_list_data[1]
					proxy_testTime=getDict(config_dict,"proxy_testtime","YYYY-MM-DD")
					proxy_server_index=int(getDict(config_dict,"proxy_server_index",0))
				except:
					proxy_testTime="YYYY-MM-DD"
					proxy_server_index=0
					creat_config(str(proxy_server_index),proxy_testTime)
				
				#proxy_server_flag=True
				#proxy_server_index=0
				#proxy_testTime="YYYY-MM-DD"
			else:
				proxy_testTime="YYYY-MM-DD"
				proxy_server_index=0
				creat_config(str(proxy_server_index),proxy_testTime)

			#proxy_server_index>=len(proxy_server_list) meaning is already search
			if proxy_server_index>=len(proxy_server_list) and nowTimeString!=proxy_testTime:
				proxy_server_index=0
			proxy_testTime=nowTimeString #one day check one time
	else:
		use_mapping = True
		proxy_mapping = proxy
	try:
		workFlag = True
		if use_mapping:
			print("use proxy mapping:",proxy_mapping)
			proxy_path=proxy_mapping
		elif proxy_server_index<len(proxy_server_list):
			print("use list test:",proxy_server_list[proxy_server_index])
			proxy_path=proxy_server_list[proxy_server_index]
		else:
			workFlag=False

		if workFlag:
			if url[0:5] == "https":
				rsp=requests.request("POST",
					#"http://10.88.26.149:8081/api/CIotPhmdevices/updateStatus", #test
					#"http://myiot:8080/api/CIotPhmdevices/updateStatus", #iot platform dns
					url, #iot platform ip
					headers={"Content-Type":"application/json"},
					proxies={"https":proxy_path},
					data=j_data,
					timeout = 15)
			else:
				rsp=requests.request("POST",
					#"http://10.88.26.149:8081/api/CIotPhmdevices/updateStatus", #test
					#"http://myiot:8080/api/CIotPhmdevices/updateStatus", #iot platform dns
					url, #iot platform ip
					headers={"Content-Type":"application/json"},
					proxies={"http":proxy_path},
					data=j_data,
					timeout = 15)
			#return_code = rsp.text[8:11]
			print("iot api status(",rsp.status_code,"):",rsp.text)
			print("iot api proxy:",proxy_path)
			
			if(rsp.status_code == 200):
				writeConfig('d','environment','time_status',time.time())
				proxy_success_flag = True
			uploadFlag = True
			
		
	except requests.exceptions.RequestException as e:
		if (str(e).find("Cannot connect to proxy")>=0 or str(e).find("timed out")>=0) and use_mapping==False and proxy_success_flag==False:
			if proxy_server_index<len(proxy_server_list):
				proxy_server_index=proxy_server_index+1
				creat_config(str(proxy_server_index),proxy_testTime)
				if(proxy_server_index<len(proxy_server_list)):
					IoTRequire(data,url)
				else:
					print("Not match proxy")
					proxy_testTime=nowTimeString
		else:
			print("IoT API error:",e)
			print("JSON data:",j_data)
		
	except Exception as e: 
		print("IoT API error",e)
		print("JSON data:",j_data)
			
	if use_mapping==False:
		creat_config(str(proxy_server_index),proxy_testTime)
	
	return uploadFlag
