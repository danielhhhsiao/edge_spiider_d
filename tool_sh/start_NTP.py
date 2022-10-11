import os
import time
from subprocess import check_output
import requests
import json

_systemConfig = "s"

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

if __name__ == "__main__":
    #Init params
    delayCount = [0,0];
    successCountNTP = 3600
    failedCountNTP = 5
    
    while True:
        if delayCount[0] == delayCount[1]:
            delayCount[0] = 0
            try:
                #Load NTP IP
                configDict = loadConfig(_systemConfig)
                ntpIP = getDictItem(configDict, 'ntp', 'ip', "")
                check_output(['ntpdate', '-u', ntpIP])
                delayCount[1] = successCountNTP
                print("Successful")
                res = os.popen('sudo hwclock --systohc').readline().strip()
            except:
                delayCount[1] = failedCountNTP
                print("Failed")
        time.sleep(1)
        delayCount[0]+=1
