#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: etao
"""
import VibrationHub
import time



if __name__ == "__main__":
    vib = VibrationHub.VibHub(0)
    startTime = time.time()
    while True:
        s = vib.CheckSlave()
        if s:
            print("CheckSlave connrcted. ",time.time()-startTime)
        else:
            print("CheckSlave disconnrcted. ",time.time()-startTime)
            break
        time.sleep(1)
        
        
        
        
        
        
        
        
