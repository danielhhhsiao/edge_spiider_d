#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec  27 10:00:01 2021

@author: etao
"""

import sys
import argparse
import time
import smbus  

        
        
if __name__ == "__main__":
        i2cBus = 1
        addr = 0x48
        
        parser = argparse.ArgumentParser()
        args = parser.parse_args()
        
        
        
        try:
                i2c = smbus.SMBus(i2cBus)
        except:
                print("FAIL")
                exit()
                
        try:
                i2c.read_byte(addr)
        except:
                print("FAIL")
                exit()
                
                
                
        i2c.write_i2c_block_data(addr,0x1,[0x95,0x83])
        time.sleep(0.1)
        a = i2c.read_i2c_block_data(addr,0x1,2)
        
        if a[0]!=0x95 or a[1]!=0x83:
                print("FAIL")
                exit()
        else:
                print("PASS")
                exit()
                
        
        

