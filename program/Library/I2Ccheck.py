#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec  27 10:00:01 2021

@author: etao
"""

from datetime import datetime
import os
import sys
import time
import logging
import argparse
import time
import smbus  

def endMassage(m="",e=True):
        if m !="":
                logging.info(m)
        if not e:
                input("Press enter to end the processing")
        sys.exit()
        
        
if __name__ == "__main__":
        
        
        path = "data/"
        __version__ = "1.0.0"
        if not os.path.exists(path):
                os.makedirs(path)
                
        startTimeStr = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(path+"I2Ccheck_log_"+startTimeStr+".txt","w","utf-8")
        handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
        root_logger.addHandler(handler)
        root_logger.addHandler(logging.StreamHandler())
        logging.info("Software version: "+__version__)
        
        
        parser = argparse.ArgumentParser()
        parser.add_argument("bus",type=int,help="I2C bus. default is bus 1"
                ,nargs='?',default = 1)
        parser.add_argument("addr",type=lambda x:int(x,16),help="I2C check address. default=48 for ADS1115"
                ,nargs='?',default = 0x48)
        parser.add_argument("-e","--end",help="Auto endding processing",action="store_true")
        args = parser.parse_args()
        
        
        logging.info("I2C address("+hex(args.addr)+") check...")
        
        try:
                i2c = smbus.SMBus(args.bus)
        except:
                endMassage("\tFailt! I2C bus "+str(args.bus)+" not found!",args.end)
                
        try:
                i2c.read_byte(args.addr)
        except:
                endMassage("\tFailt! Device not founc on address "+hex(args.addr)+"!",args.end)
        logging.info("\tSuccess! The device exist on address "+hex(args.addr)+".")
                
                
        logging.info("\nADS1115 module reading/writing test...")
        i2c.write_i2c_block_data(args.addr,0x1,[0x95,0x83])
        time.sleep(0.1)
        a = i2c.read_i2c_block_data(args.addr,0x1,2)
        #print(hex(a[0]))
        #print(hex(a[1]))
        if a[0]!=0x95 or a[1]!=0x83:
                endMassage("\tFailt!",args.end)
        else:
                logging.info("\tSuccess!")
        endMassage("",args.end)
                
        
        

