#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  4 02:59:15 2021

@author: pi
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 10:00:01 2021

@author: pi
"""

import Library.ADCHub as ADCHub
import Library.SpiSlaveScan as SpiSlaveScan
import time
import numpy as np
import matplotlib.pyplot as plt
import gc

print(SpiSlaveScan.scanSlave())
print(SpiSlaveScan.listName())

adc = ADCHub.ADCHub(0)
print("CheckSlave:",adc.CheckSlave())
adc.ScanSensor()
print("Sansor Enable:",adc.enable)
adc.CheckSlave()

#vib.SelectOneSensor(0)
#vib.UnSelectOneSensor(0)

onsSample=16
sampleRate=8000
maxLen=8000
sampleSec=0.1
adc.SelectAllSensor([True,True,True,True,True,True,True,True])
#adc.SelectAllSensor([True,False,False,False,False,False,False,False])

exit()

adc.SetScale(0,8,False)
adc.SetScale(1,8,False)
#adc.SetScale(2,8,False)
#adc.SetScale(3,1,False)
#adc.SetScale(4,2,False)
#adc.SetScale(5,8,False)
#adc.SetScale(6,1,False)
#adc.SetScale(7,2,False)
#
adc.SetFs(sampleRate)





fig,ax=plt.subplots(nrows=4,ncols=4,tight_layout=True)
fig.set_figheight(8)
fig.set_figwidth(12)
plt.pause(0.0001) 


count=onsSample*sampleRate*sampleSec
total=0
outFlag=False
startTime=time.time()
adc.StartSample()
time.sleep(sampleSec)

while total<count or True:
#    vib.StopSample()
    dataLen=adc.GetBufferLen()
    print(dataLen)
    nowTime=time.time()
    readLen=int(int((dataLen)//onsSample)*onsSample)
    if(readLen>0):
        lasttTime=nowTime
        gc.collect()
        data=np.array(adc.GetBuffer(readLen))
#        vib.StartSample()
        
        total=total+readLen
        data=data[0::2]*256+data[1::2]
        data=data.reshape([-1,onsSample//2])[:maxLen,:]
        data=data.T
        timeS=np.array(range(len(data[0])))/sampleRate
        FsScale=np.array(range(len(data[0])//2))/len(data[0])*sampleRate
        for i in range(onsSample//2):
            num=i
            value=adc.ConvertData(data[i])
            print(value[:20])
            #value=value/32768.0*2.4/510*3210
            value=value/32768.0*2.4/820.0*5120.0
            
            """
            if i==7 or i == 5:
                value=(value*1000000.0-168000)/394.0+25
            if i==0 or i == 2 or i == 4:
                value=value*5.3*1.083*3
            """
            
            
            mean=np.mean(value)
#            if(axis==0):
#                print("-----------------------------",num,"---------")
#            print(axis_name[axis],mean)
            
            
            fft=np.fft.fft(value-mean)
            fft=np.abs(fft)
            fft_len=len(fft)
            fft=fft[:fft_len//2]/fft_len
            
            ax[num//4][num%4].cla()
            ax[num//4+2][num%4].cla()
            ax[num//4][num%4].plot(timeS,value)
            ax[num//4+2][num%4].plot(FsScale,fft)
            index=np.argmax(fft)
            ax[num//4+2][num%4].text(FsScale[index],fft[index],str(np.around(FsScale[index],2)))
            
    else:
        print("zero")
        
    print(readLen,",",total,",",total//onsSample,",",nowTime-startTime,",",(total//onsSample)/(nowTime-startTime))
    plt.margins(0)
    #plt.pause(0.01)    
    #plt.pause(100)      
    plt.show()
    break
print("total:",total)
adc.StopSample()
        
        
        
