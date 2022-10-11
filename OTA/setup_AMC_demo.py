# This is demo version
# disable FW update
# disable size limit
# disable AP rename/setting/reboot
# disable close service
# disable rename hostname

import io
import sys
import os
from subprocess import Popen, PIPE, TimeoutExpired
from uncryptoFile import uncrypto 
from SpiSlaveScan import scanSlave
import requests
import time
import json
from datetime import datetime

keyword = "EtaoIsNiceMan!"

mainPath="/home/pi/OTA/"
backupPath="/home/pi/backup/"
bufferPath=mainPath+"buffer/"
keyPath=bufferPath+"key"
MCUPath=bufferPath+"MCU/"
FOTAPath=mainPath+"AT32_OTA_"+str(sys.version_info.major)+str(sys.version_info.minor)

listFileName=bufferPath+"list.txt"
flagFileName=mainPath+"flag.txt"
installFileName = bufferPath+"install.sh"
vibFileName=MCUPath+"vib.hex"
adcFileName=MCUPath+"adc.hex"
cryptoFileName = bufferPath+"new.bin"
uncryptoFileName = bufferPath+"new.tar"
privateFileName = mainPath+"private.pem"

busMap = [["0","0"],["0","1"],["1","0"],["1","1"]]



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
    
def writeConfig(target,section,item,value):
    payload = {'t' : target, 's' : section, 'i' : item, 'v' : value}
    d = requests.get('http://127.0.0.1/api/write',params = payload)
    data = json.loads(d.text)
    
    if data["state"]==200:
        return True
    return False
    
def startOTA():
    writeConfig("d","environment","ota_status","2") 
    
def returnErr(msg):
    global bufferPath
    writeConfig("d","environment","ota_status","4") #err done
    writeConfig("d","environment","ota_msg",msg) #msg
    
    if os.path.isdir(bufferPath):
        popen_retry(["rm",bufferPath,"-R"])
        os.makedirs(bufferPath)
    
    print(msg)
    returnDone()
    sys.exit()
    
def returnDone():
    #flag down
    print("\nflag down")
    with open(flagFileName, "w") as f:
        f.write("0")
    
def run():
    #start OTA
    timeStr = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d_%H-%M-%S")
    print("Start",timeStr)
    
    #flag up
    print("\nflag up")
    with open(flagFileName, "w") as f:
        f.write("1")
    
    
    #uncrypto file
    try:
        print("\nDecrypto file")
        if not os.path.isfile(cryptoFileName):
            returnErr("Upload file fail.")
        print("uncrypto file",cryptoFileName,"to",uncryptoFileName)
        uncrypto(cryptoFileName,uncryptoFileName,privateFileName)
    except:
        returnErr("Decrypto fail.")
    
    
    
    #uncompress file
    print("\nuncompress file")
    if not os.path.isdir(bufferPath):
        os.makedirs(bufferPath)
    try:
        popen_retry(["tar","-C",bufferPath,"-xvf",uncryptoFileName ])
    except:
        returnErr("Uncompress fail.")
    

    #check key
    print("\ncheck key")
    if not os.path.isfile(keyPath):
        returnErr("key file not exist.")
        
    with open(keyPath, "r") as f:
        key = f.read(-1).replace("\n","")
    if key !=keyword:
        returnErr("key file error")
      
    
    #get list
    print("\nget file list",listFileName)
    if not os.path.isfile(listFileName):
        returnErr("File list not exist.")
    with open(listFileName, "r") as f:
        fileList = f.read(-1).split("\n")
    print(fileList)
    
    #replace file
    print("\nreplace file")
    for fileName in fileList:
        if os.path.isfile(fileName):
            name = fileName.split("/")[-1]
            popen_retry(["rm",fileName])
            popen_retry(["cp",bufferPath+name,fileName])
            print( bufferPath+name,"move to",fileName)
        if os.path.isdir(fileName):
            name = fileName.split("/")[-1]
            popen_retry(["rm",fileName,"-R"])
            popen_retry(["cp","-r",bufferPath+name,fileName])
            print( bufferPath+name,"move to",fileName)
    
    
    
    #finish
    returnDone()
    
    #remove buffer
    print("\nremove buffer")
    if os.path.isdir(bufferPath):
        popen_retry(["rm",bufferPath,"-R"])
        os.makedirs(bufferPath)
        
        
if __name__ == "__main__":
    run()
    
    
        
        
