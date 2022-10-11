import os
import time
import datetime
import numpy as np
import pandas as pd
from os import listdir


rootPath = '../simulator'
data = None
files = listdir(rootPath)
for f in files:
	if f[-4:]==".csv" or  f[-4:]==".CSV":
		df = pd.read_csv(rootPath+"/"+f)
		if 'datetime' in df.columns:
			realSec = pd.unique(df['datetime'])
			df = df.drop(df.loc[df['datetime'] == realSec[0]].index)     #remove not complete sec at head
			df = df.drop(df.loc[df['datetime'] == realSec[-1]].index)    #remove not complete sec at fial
			realSec = pd.unique(df['datetime'])
			Fs = len(df['datetime'])/len(realSec)
			startTime = time.mktime(datetime.datetime.strptime(df['datetime'].values[0],"%Y-%m-%d %H:%M:%S").timetuple())
			df['datetime'] = startTime+np.arange(len(df['datetime']))/Fs
			data = df
			enableName = list(df.columns)
			enableName.remove('datetime')
			print("Simulator file:",rootPath+"/"+f)
			print("columns:",enableName)
			break
			
print(data)

test =data.loc[(data['datetime']>=0) & (data['datetime']<10000000000000000000000000000)]
print(test)
