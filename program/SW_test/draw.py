#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 25 15:34:13 2021

@author: etao
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('test_recode_2021_05_25_17_03_57.csv')
df=df.T
data=dict()
for c in df.columns:
    data[df[c][0]]=df[c][1:]
    
    
plt.plot(data['recodeTimestamp'],data['cpuUsage'])
plt.show()
    
    
fig, axs = plt.subplots(len(data)-1)

index=0
for key in data.keys():
    if key=="recodeTimestamp":
        continue
    axs[index].plot(data['recodeTimestamp'],data[key])
    axs[index].set_title(key)
    index=index+1
    
fig.tight_layout()
plt.subplots_adjust(left=0.125,
                    bottom=0.1, 
                    right=0.9, 
                    top=1, 
                    wspace=0.2, 
                    hspace=0.35)
fig.set_figheight(10)
fig.set_figwidth(20)
plt.savefig("result.png",bbox_inches = 'tight')