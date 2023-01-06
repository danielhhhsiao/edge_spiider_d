import http.server
import socketserver
import time
from datetime import datetime
import threading
import queue
import RPi.GPIO as GPIO
from urllib.parse import urlparse
from datetime import datetime
from Library.StatusServerLib import staticInfoTrans,dynamicInfoTrans,writeConfig,loadConfig,getDictItem,IoTInfoTrans,getWifiIP,getLanIP,getLan2IP,getMacID,getBoardVersion,getMappingProxy,getApStatus,reset,shutdown
import requests
import ftplib
import multiprocessing
import json
import os
import io
import gc

class LED_Control(threading.Thread):
	ST1_modeTimeStamp = [0,0,0,0]
	ST2_modeTimeStamp = [0,0,0,0]
	reverse = True
	def __init__(self,queue):
		threading.Thread.__init__(self)
		self.queue = queue
		
		self.deviceConfigPath = 'd'
		self.systemConfigPath = 's'
		self.boardVer, self.boardType = getBoardVersion()

	def run(self):
		configDict = loadConfig(self.deviceConfigPath)
		#systemConfig = loadConfig(self.systemConfigPath)

		ST1_Mode = 0
		ST2_Mode = 0
		
		ST1_Timeout = [0,0,0,0]
		ST2_Timeout = [0,0,0,0]
		
		#status upload params
		startWorkTime = time.time()
		uploadStatus = "OK"
		staticInfo_upload_flag = False
		dynamicInfo_upload_flag = False
		auoInfo_upload_mode = 0
		mainNonWorkC = 0
		ST1_status = 0
		ST2_status = 0
		pre_m = ''
		m = ''
		
		#Start API Process
		APIProc_queue_num = 0
		self.API_upload_Proc = API_status_upload()
		self.API_upload_Proc.start()
		
		#Start FTP Process
		self.FTP_upload_Proc = FTP_status_upload()
		self.FTP_upload_Proc.start()
		
		#Start LED Process
		self.LED_Blink_Proc = LED_Blink()
		self.LED_Blink_Proc.start()
		
		#bootTimeCheck
		wifiDisconnectCount = 0
		closeAPTime = 600
		closeAPFlag = False
		APOpenFlag = False
		
		#Seg/FE count
		segCount = 0
		feCount = 0
		
		#check internet status
		checkIPCount = 0
		checkIPFlag = False
		
		#Check FAB/SPIIDER
		try:
			pid = str(os.popen('/home/pi/tool_sh/eeprom -r 1').readline().strip())
		except:
			pid = ''
			
		while(1):
			if(auoInfo_upload_mode == 0):
				auoInfo_upload_mode = self.API_upload_Proc.getConnectMode()
				if (auoInfo_upload_mode != 0):
					if auoInfo_upload_mode == 2:
						print("Not Auo.")
						#boot upload static info
						json_obj = staticInfoTrans(self.boardVer,self.boardType)
						print(json_obj)
						self.API_upload_Proc.put(json_obj)
						
						#5min upload time
						dynamicStartTime = time.time()
					else:
						print("Auo.")
						auoStartTime = time.time()
					checkAPTime = time.time()	#After wifi connect, start to check closeAPTime to close AP
					closeAPFlag = True
			if(self.queue.qsize() > 0):
				query_string = self.queue.get()
				print(query_string)
				n = int(query_string[2])
				s = int(query_string[6])
				m = query_string[10:]
				#Check API queue data when not use auo upload
				if auoInfo_upload_mode == 2:
					APIProc_queue_num = self.API_upload_Proc.getQueueSize()
					#if APIProc_queue_num > 100 :
					#	if m == '':
					#		continue
					if(n == 1):
						if(s >= 0):
							mainNonWorkC = 0
						#mode timeout reset
						ST1_Timeout[s] = 0
						if m != '':
							try:
								writeConfig(self.deviceConfigPath,'environment','st1_err_msg',datetime.fromtimestamp(time.time()).strftime(" %Y-%m-%d %H:%M:%S") + ' ' + m)
							except Exception as e:
								print(e)
							dynamicInfo_upload_flag = True
						#mode change
						if(s > ST1_Mode):
							#Status 1 -> 2, 3, 4
							if (ST1_Mode == 0) and (staticInfo_upload_flag == False):
								#put ststicInfo
								json_obj = staticInfoTrans(self.boardVer,self.boardType)
								self.API_upload_Proc.put(json_obj)
								startWorkTime = time.time()
								staticInfo_upload_flag = True
							ST1_Mode = s
							self.LED_Blink_Proc.getMode(ST1_Mode,ST2_Mode)
							if ST1_Mode != 2:
								dynamicInfo_upload_flag = True
							
					elif(n == 2):
						ST2_Timeout[s] = 0
						if (m != ''):
							try:
								writeConfig(self.deviceConfigPath,'environment','st2_err_msg',datetime.fromtimestamp(time.time()).strftime(" %Y-%m-%d %H:%M:%S") + ' ' + m)
							except Exception as e:
								print(e)
							if(pre_m != m):
								dynamicInfo_upload_flag = True
								pre_m = m
							
						if(s > ST2_Mode):
							ST2_Mode = s
							if ST1_Mode == 1:
								self.LED_Blink_Proc.getMode(ST1_Mode,ST2_Mode)
							if(s == 1):
								uploadStatus = "OK"
							elif(s == 2):
								uploadStatus = "NG"
							if ST2_Mode != 1:
								dynamicInfo_upload_flag = True
					elif(n == 3):
						if(s == 0):
							segCount+=1
						elif(s == 1):
							feCount+=1
							
				else:
					if(n == 1):
						if m != '':
							try:
								writeConfig(self.deviceConfigPath,'environment','st1_err_msg',datetime.fromtimestamp(time.time()).strftime(" %Y-%m-%d %H:%M:%S") + ' ' + m)
							except Exception as e:
								print(e)
						if(s == 0):
							mainNonWorkC = 0
						#mode timeout reset
						ST1_Timeout[s] = 0
						#mode change
						if(s > ST1_Mode):
							ST1_Mode = s			
					elif(n == 2):
						if (m != '') and (pre_m != m):
							try:
								writeConfig(self.deviceConfigPath,'environment','st2_err_msg',datetime.fromtimestamp(time.time()).strftime(" %Y-%m-%d %H:%M:%S") + ' ' + m)
							except Exception as e:
								print(e)
							pre_m = m
						ST2_Timeout[s] = 0
						if(s > ST2_Mode):
							ST2_Mode = s
					elif(n == 3):
						if(s == 0):
							segCount+=1
						elif(s == 1):
							feCount+=1
					self.LED_Blink_Proc.getMode(ST1_Mode,ST2_Mode)
			time.sleep(0.1)
			checkIPCount += 1
			if checkIPCount == 100:
				checkIPCount = 0
				if (getWifiIP() == '' and getLanIP() == '' and getLan2IP() == ''):
					checkIPFlag = True
					ST2_Mode = -1
					self.LED_Blink_Proc.getMode(ST1_Mode,ST2_Mode)
				else:
					checkIPFlag = False
					if(ST2_Mode == -1):
						ST2_Mode = 0
					self.LED_Blink_Proc.getMode(ST1_Mode,ST2_Mode)
				if self.FTP_upload_Proc.ipChangedCheck() == True:
					print("IP changed, upload the static payload.")
					json_obj = staticInfoTrans(self.boardVer,self.boardType)
					self.API_upload_Proc.put(json_obj)

			for i in range(3,-1,-1):
				if(ST1_Timeout[i] == 50):
					if (ST1_Mode == i):
						if(i == 0):
							mainNonWorkC+=1
							ST1_Timeout[0] = 0
							if(mainNonWorkC == 6):
								mainNonWorkC = 0
								ST1_Mode = -1
								print("Main doesnt work.",ST1_Mode)
								m = "Main doesnt work."
								if auoInfo_upload_mode == 2:
									dynamicInfo_upload_flag = True
								writeConfig(self.deviceConfigPath,'environment','st1_err_msg',datetime.fromtimestamp(time.time()).strftime(" %Y-%m-%d %H:%M:%S") + ' ' + m)
						else:
							if i == 1:
								mainNonWorkC = 0
								ST1_Timeout[0] = 0
							if (auoInfo_upload_mode == 2) and (i != 2):
								dynamicInfo_upload_flag = True
							ST1_Mode = i-1
							#reset staticInfo upload flag
							if(ST1_Mode == 0):
								staticInfo_upload_flag = False
							print("ST1 reset mode",ST1_Mode)
							ST1_Timeout[i] = 0
							m = ''
						self.LED_Blink_Proc.getMode(ST1_Mode,ST2_Mode)
				else:
					ST1_Timeout[i] += 1
				if(ST2_Timeout[i] == 50):
					if (ST2_Mode == i) and (i != 0):
						if auoInfo_upload_mode == 2:
							if(i != 1):
								dynamicInfo_upload_flag = True
							else:
								dynamicInfo_upload_flag = False
						if(ST2_Mode == 1):
							uploadStatus = "OK"
						elif(ST2_Mode == 2):
							uploadStatus = "NG"
						ST2_Mode = i-1
						print("ST2 reset mode",ST2_Mode)
						ST2_Timeout[i] = 0
						m = ''
						self.LED_Blink_Proc.getMode(ST1_Mode,ST2_Mode)
				else:
					ST2_Timeout[i] += 1
			
			if auoInfo_upload_mode == 2:
				if (time.time() - dynamicStartTime)>300:
					dynamicInfo_upload_flag = True
				#put dynamicInfo	
				if dynamicInfo_upload_flag:
					dynamicInfo_upload_flag = False
					dynamicStartTime = time.time()
					json_obj = dynamicInfoTrans(startWorkTime,uploadStatus,ST1_Mode,ST2_Mode,m,segCount,feCount)
					print(json_obj)
					self.API_upload_Proc.put(json_obj)
			elif auoInfo_upload_mode == 1:
				if (time.time() - auoStartTime)>300:
					auoStartTime = time.time()
					tempF = IoTInfoTrans(segCount,feCount)
					configDict = loadConfig(self.deviceConfigPath)
					if tempF:
						if (getDictItem(configDict,'environment','server_connect',"0") == "0"):
							writeConfig(self.deviceConfigPath,'environment','server_connect',"1")
					else:
						if (getDictItem(configDict,'environment','server_connect',"0") == "1"):
							writeConfig(self.deviceConfigPath,'environment','server_connect',"0")
			if closeAPFlag:
				if (time.time() - checkAPTime) > closeAPTime:
					closeAPFlag = False
					#close AP
					try:
						if pid != '':
							#pass
							res = os.popen('sudo ifdown wlan1 --force').readline().strip()
						else:
							#pass
							res = os.popen('sudo ifdown ap0 --force').readline().strip()
						print("Timeup, close the AP mode.")
					except Exception as e:
						print(e)
			elif auoInfo_upload_mode != 0:
				#print("IP",getWifiIP())
				if checkIPFlag:
					#checkIPFlag = False
					if APOpenFlag == False:
						wifiDisconnectCount+=1
						if(wifiDisconnectCount == 300):
							try:
								wifiDisconnectCount = 0
								if pid != '':
									#pass
									res = os.popen('sudo ifup wlan1 --force').readline().strip()
								else:
									#pass
									res = os.popen('sudo ifup ap0 --force').readline().strip()
								print("WIFI disconnect, open the AP mode.")
								APOpenFlag = True
							except Exception as e:
								print(e)
				elif APOpenFlag:
					wifiDisconnectCount+=1
					if(wifiDisconnectCount == 100):
						print("Reconnect wifi.")
						checkAPTime = time.time()
						closeAPFlag = True
						APOpenFlag = False

class LED_Blink(multiprocessing.Process):
	def __init__(self):
		multiprocessing.Process.__init__(self)
		self.exit = multiprocessing.Event()
		#GPIO setting
		self.shutdownPin = 0
		self.resetPin = 1
		self.ST1 = 12
		self.ST2 = 13
		self.apLed = 27
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.shutdownPin,GPIO.IN)
		GPIO.setup(self.resetPin,GPIO.IN)
		GPIO.setup(self.ST1,GPIO.OUT)
		GPIO.setup(self.ST2,GPIO.OUT)
		GPIO.setup(self.apLed,GPIO.OUT)
		manager=multiprocessing.Manager()
		self.states=manager.dict()
		self.states["ST1Mode"] = 0
		self.states["ST2Mode"] = 0
		self.reverse = True

	def getMode(self,mode1,mode2):
		self.states["ST1Mode"] = mode1
		self.states["ST2Mode"] = mode2
        
	def run(self):
		ON_Mode_Unit = [1,1,5,1]
		OFF_Mode_Unit = [49,19,5,1]
		ST1_OnOff = [1,49]
		ST1_OnOff_Count = 0
		ST1_Count = 0
		ST2_OnOff = [1,49]
		ST2_OnOff_Count = 0
		ST2_Count = 0
		AP_OnOff = 0
		AP_OnOff_Count = 0
		ST1Mode = 0
		ST2Mode = 0
		APMode = 0
		apCheckCount = 0
		resetCount = 0
		try:
			pid = str(os.popen('/home/pi/tool_sh/eeprom -r 1').readline().strip())
		except:
			pid = ''
		if pid != '':
			checkSPIIDER = 1
		else:
			checkSPIIDER = 0
		while(1):
			if ST1Mode != self.states["ST1Mode"]:
				ST1Mode = self.states["ST1Mode"]
				ST1_OnOff_Count = 0
				if self.states["ST1Mode"] != -1:
					ST1_OnOff[0] = ON_Mode_Unit[self.states["ST1Mode"]]
					ST1_OnOff[1] = OFF_Mode_Unit[self.states["ST1Mode"]]
				else:
					ST1_OnOff[0] = 0
					ST1_OnOff[1] = 0
					GPIO.output(self.ST1,(0)^self.reverse)
			if ST2Mode != self.states["ST2Mode"]:
				ST2Mode = self.states["ST2Mode"]
				ST2_OnOff_Count = 0
				if self.states["ST2Mode"] != -1:
					ST2_OnOff[0] = ON_Mode_Unit[self.states["ST2Mode"]]
					ST2_OnOff[1] = OFF_Mode_Unit[self.states["ST2Mode"]]
				else:
					ST2_OnOff[0] = 0
					ST2_OnOff[1] = 0
					GPIO.output(self.ST2,(0)^self.reverse)
			#print(ST1Mode,ST2Mode)
			if(ST1_OnOff_Count < ST1_OnOff[ST1_Count]):
				GPIO.output(self.ST1,ST1_Count^1^self.reverse)
				ST1_OnOff_Count+=1
				
			elif(ST1_OnOff[ST1_Count] != 0):
				ST1_Count = (ST1_Count+1)%2
				GPIO.output(self.ST1,ST1_Count^1^self.reverse)
				ST1_OnOff_Count=1
				
			if(ST2_OnOff_Count < ST2_OnOff[ST2_Count]):
				GPIO.output(self.ST2,ST2_Count^1^self.reverse)
				ST2_OnOff_Count+=1
				
			elif(ST2_OnOff[ST2_Count] != 0):
				ST2_Count = (ST2_Count+1)%2
				GPIO.output(self.ST2,ST2_Count^1^self.reverse)
				ST2_OnOff_Count=1
				
			if(APMode == 0):
				GPIO.output(self.apLed,0^self.reverse)
			elif(APMode == 2):
				GPIO.output(self.apLed,AP_OnOff^self.reverse)
				AP_OnOff_Count+=1
				if(AP_OnOff_Count == 10):
					AP_OnOff^=1
					AP_OnOff_Count=0
			elif(APMode == 1):
				GPIO.output(self.apLed,1^self.reverse)
			
			#Check AP status
			apCheckCount+=1
			if apCheckCount == 100:
				apCheckCount = 0
				APMode = getApStatus(checkSPIIDER)
			#Check shutdown button
			if GPIO.input(self.shutdownPin) == 0:
				shutdown()
			#Check reset button
			if GPIO.input(self.resetPin) == 0:
				resetCount+=1
				if resetCount == 20:
					reset()
			else:
				resetCount = 0
			time.sleep(0.1)
					
class FTP_status_upload(multiprocessing.Process):
	def __init__(self):
		multiprocessing.Process.__init__(self)
		self.exit = multiprocessing.Event()
		self.systemConfigPath = 's'
		self.workConfigPath = 'w'
		print("Server FTP upload create")
		manager=multiprocessing.Manager()
		self.states=manager.dict()
		self.states["ip_changed_flag"] = False

	def cd_dir(self,path,ftp):
		if path != "":
			try:
				ftp.cwd("/"+path)
				print("found ftp folder.")
			except:
				self.cd_dir("/".join(path.split("/")[:-1]),ftp)
				ftp.mkd("/"+path)
				ftp.cwd("/"+path)
				print("Not found ftp folder, create " + path)
		
	def ipChangedCheck(self):
		if self.states["ip_changed_flag"]:
			self.states["ip_changed_flag"] = False
			return True
		return False
	
	def run(self):
		try:
			pid = str(os.popen('/home/pi/tool_sh/eeprom -r 1').readline().strip())
		except:
			pid = ''
		systemConfig = loadConfig(self.systemConfigPath)
		workConfig = loadConfig(self.workConfigPath)
		#FTP upload IP+MAC
		check_FTP_Count = 0
		bootFTP = 0
		FTP_HOST = getDictItem(systemConfig,"ftp","ip","")
		FTP_USER = getDictItem(systemConfig,"ftp","name","")
		FTP_PASS = getDictItem(systemConfig,"ftp","pwd","")
		wifiIP = ""
		lanIP = ""
		lan2IP = ""
		ftpSuccessF = False
		if FTP_HOST != "":
			try:
				segCount = 0
				bootFTP = 1
				while(1):
					segCount+=1
					segStr = "segmentation_" + str(segCount)
					segType = getDictItem(workConfig,segStr,"type","-1")
					print(segStr,segType)
					if(segType == "-1"):
						break
					if(segType != "0"):
						segTool = getDictItem(workConfig,segStr,"name","unknown")
						path = "SPIIDER-D/Raspberry_Detail/" + segTool
						wifiIP = getWifiIP()
						lanIP = getLanIP()
						lan2IP = getLan2IP()
						ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS,timeout=10)
						if FTP_USER == '':
							ftp.login()
						ftp.encoding = "utf-8"
						self.cd_dir(path,ftp)
						fileName = "_".join([
								getMacID().replace(":",""),
								wifiIP,
								lanIP,
								lan2IP,
								pid
								])
						x = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
						bio = io.BytesIO(bytes(x,encoding='utf8'))
						ftp.storbinary("STOR "+ '/' +path + '/' + fileName, bio)
						print("Server FTP upload success")
				ftpSuccessF = True
			except Exception as e:
				ftpSuccessF = False
				print(e)
		while(1):
			time.sleep(0.1)
			check_FTP_Count+=1
			if bootFTP == 0:
				systemConfig = loadConfig(self.systemConfigPath)
				FTP_HOST = getDictItem(systemConfig,"ftp","ip","")
				FTP_USER = getDictItem(systemConfig,"ftp","name","")
				FTP_PASS = getDictItem(systemConfig,"ftp","pwd","")
				if FTP_HOST != "":
					try:
						segCount = 0
						bootFTP = 1
						while(1):
							segCount+=1
							segStr = "segmentation_" + str(segCount)
							segType = getDictItem(workConfig,segStr,"type","-1")
							print(segStr,segType)
							if(segType == "-1"):
								break
							if(segType != "0"):
								segTool = getDictItem(workConfig,segStr,"name","unknown")
								path = "SPIIDER-D/Raspberry_Detail/" + segTool
								wifiIP = getWifiIP()
								lanIP = getLanIP()
								lan2IP = getLan2IP()
								ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS,timeout=10)
								if FTP_USER == '':
									ftp.login()
								ftp.encoding = "utf-8"
								self.cd_dir(path,ftp)
								fileName = "_".join([
										getMacID().replace(":",""),
										wifiIP,
										lanIP,
										lan2IP,
										pid
										])
								x = datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
								bio = io.BytesIO(bytes(x,encoding='utf8'))
								ftp.storbinary("STOR "+ '/' +path + '/' + fileName, bio)
								print("Server FTP upload success")
						ftpSuccessF = True
					except Exception as e:
						ftpSuccessF = False
						print(e)
			else:
				if check_FTP_Count >= 600:
					print("ftp ip check")
					check_FTP_Count = 0
					systemConfig = loadConfig(self.systemConfigPath)
					if not ftpSuccessF:
						print("Retry status upload to ftp.")
						bootFTP = 0
					if wifiIP != getWifiIP() or lanIP != getLanIP() or lan2IP != getLan2IP() or FTP_HOST != getDictItem(systemConfig,"ftp","ip",""):
						print("ip change.")
						self.states["ip_changed_flag"] = True
						bootFTP = 0
				
class API_status_upload(multiprocessing.Process):
	def __init__(self):
		multiprocessing.Process.__init__(self)
		self.exit = multiprocessing.Event()
		self.deviceConfigPath = 'd'
		self.systemConfigPath = 's'
		#upload status count
		manager=multiprocessing.Manager()
		self.queueData=manager.Queue()
		#Check Flag
		self.states=manager.dict()
		self.states["connectMode"] = 0
		
		print("Server API upload create")
		
	def put(self,data):
		self.queueData.put(data)
		
	def getQueueSize(self):
		return self.queueData.qsize()
	
	def getConnectMode(self):
		return self.states["connectMode"]
	
	def run(self):
		#Read config data
		configDict = loadConfig(self.deviceConfigPath)
		systemConfig = loadConfig(self.systemConfigPath)
		check_API_Count = 0
		upload_data = ''
		#API params
		API_URL = getDictItem(systemConfig,"status","ip","")
		API_PROXY = getDictItem(systemConfig,"status","proxy","")
		
		#Check Wifi connect
		checkIPFlag = False
		while (getWifiIP() == "") and (getLanIP() == "") and (getLan2IP() == ""):
			print("Wait for internet connect.")
			checkIPFlag = False
			time.sleep(3)
		checkIPFlag = True
		#Check IP first
		checkAuoFlag = False
		ipFirstByte = getWifiIP().split(".")[0]
		if ipFirstByte == "":
			ipFirstByte = getLanIP().split(".")[0]
			if ipFirstByte == "":
				ipFirstByte = getLan2IP().split(".")[0]
		if ipFirstByte  == "10":
			auoProxy = getMappingProxy()
			print(auoProxy)
			if auoProxy != "":
				checkAuoFlag = True
			else:
				checkAuoFlag = False
			"""
			#Check internet to decide Auo or not
			recordPath = os.path.abspath(os.getcwd())
			if(os.path.exists("proxy_search_record")):
				os.remove("proxy_search_record")
				print("Remove proxy_search_record")
			checkIPFlag = False
			checkIPFlag = IoTInfoTrans(0,0)
			print(checkIPFlag)
			"""
			if checkAuoFlag:
				#self.states["connectMode"] = 1
				print("New format for Auo.")
				self.states["connectMode"] = 2
				if (getDictItem(configDict,'environment','server_connect',"0") == "0"):
					writeConfig(self.deviceConfigPath,'environment','server_connect',"1")
			else:
				self.states["connectMode"] = 2
		else:
			checkAuoFlag = False
			self.states["connectMode"] = 2
		
		while(1):
			try:
				if checkAuoFlag:
					if API_URL == "":
						API_URL = "http://myiot:8080/api/CIotPhmdevices/updateStatus2"
					API_PROXY = auoProxy
				if not self.queueData.empty() or upload_data != '':
					if self.queueData.qsize() > 100:
						self.queueData.get()
					#When API url be setting, Upload.
					if API_URL != "" and checkIPFlag:
						#When pre_upload success, get new upload_data
						if upload_data == '':
							data = self.queueData.get()
							upload_data = json.dumps(data,separators=(',',':'))
							print(upload_data)
						#API upload
						print("Request:",API_URL)
						if API_PROXY == "":
							d=requests.request("POST",
								API_URL, #iot platform ip
								headers={"Content-Type":"application/json"},
								data=upload_data,
								timeout = 10)
						elif API_URL[0:5] == "https":
							print("HTTPS")
							d=requests.request("POST",
								API_URL, #iot platform ip
								headers={"Content-Type":"application/json"},
								proxies={"https":API_PROXY},
								data=upload_data,
								timeout = 10)
						else:
							print("HTTP")
							print(API_PROXY)
							d=requests.request("POST",
								API_URL, #iot platform ip
								headers={"Content-Type":"application/json"},
								proxies={"http":API_PROXY},
								data=upload_data,
								timeout = 10)
							
							
						print(d.status_code)
						print(d.text)
						#return_code = d.text[8:11]
						if(d.status_code == 200):
							upload_data = ''
							if (getDictItem(configDict,'environment','server_connect',"0") == "0"):
								writeConfig(self.deviceConfigPath,'environment','server_connect',"1")
							writeConfig(self.deviceConfigPath,'environment','time_status',time.time())
						else:
							if (getDictItem(configDict,'environment','server_connect',"0") == "1"):
								writeConfig(self.deviceConfigPath,'environment','server_connect',"0")
							time.sleep(15)
					else:
						if (getDictItem(configDict,'environment','server_connect',"0") == "1"):
							writeConfig(self.deviceConfigPath,'environment','server_connect',"0")

				#1min check API_URL
				check_API_Count+=1
				if check_API_Count == 600:
					check_API_Count = 0
					#check IP
					if (getWifiIP() == '' and getLanIP() == '' and getLan2IP() == ''):
						checkIPFlag = False
					else:
						checkIPFlag = True
					print("Queue size:%d"%self.queueData.qsize())
					systemConfig = loadConfig(self.systemConfigPath)
					configDict = loadConfig(self.deviceConfigPath)
					API_URL = getDictItem(systemConfig,"status","ip","")
					API_PROXY = getDictItem(systemConfig,"status","proxy","")
					gc.collect()
				time.sleep(0.1)
				
			#Error
			except Exception as e:
				print(e)
				#print("Status upload error.")
				if (getDictItem(configDict,'environment','server_connect',"0") == "1"):
					writeConfig(self.deviceConfigPath,'environment','server_connect',"0")
				#check IP
				if (getWifiIP() == '' and getLanIP() == '' and getLan2IP() == ''):
					checkIPFlag = False
				else:
					checkIPFlag = True
				print("Queue size:%d"%self.queueData.qsize())
				systemConfig = loadConfig(self.systemConfigPath)
				configDict = loadConfig(self.deviceConfigPath)
				API_URL = getDictItem(systemConfig,"status","ip","")
				API_PROXY = getDictItem(systemConfig,"status","proxy","")
				gc.collect()
				time.sleep(15)
                
def release(self):
	if self.is_alive():
		self.join()
	self.exit.set()		

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
	def setup(self):
		http.server.SimpleHTTPRequestHandler.setup(self)
		self.request.settimeout(10)
		
	def address_string(self):
		return self.client_address[0]

	def do_GET(self):
		global my_queue
		parsed = urlparse(self.path)
		if(self.client_address[0] == "127.0.0.1"):
			query_string = requests.utils.unquote(parsed.query)
			my_queue.put(query_string)

			self.send_response(200)
			self.end_headers()
			self.wfile.write(bytes("Get success.","utf-8"))
		
	def do_PUT(self):
		print("do put")
		


if __name__ == "__main__":
	my_queue = queue.Queue()
	handler_object = MyHttpRequestHandler
	PORT = 81
	try:
		httpd = socketserver.TCPServer(("", PORT), handler_object) 
		print("Server is running at 127.0.0.1:%s" %PORT)
		LED_Thread = LED_Control(my_queue)
		LED_Thread.start()
		httpd.serve_forever()
	except:
		httpd.shutdown()
			
