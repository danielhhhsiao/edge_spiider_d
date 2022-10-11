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
import RPi.GPIO as GPIO

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
        handler = logging.FileHandler(path+"DIOtest_log_"+startTimeStr+".txt","w","utf-8")
        handler.setFormatter(logging.Formatter('%(name)s %(message)s'))
        root_logger.addHandler(handler)
        root_logger.addHandler(logging.StreamHandler())
        logging.info("Software version: "+__version__)
        
        
        parser = argparse.ArgumentParser()
        parser.add_argument("cycle",type=int,help="Testing cycle. Set to <=0 will loop until press Ctrl+C to end this processing. Default is -1."
                ,nargs='?',default = -1)
        parser.add_argument("cpu",help="Set the cpu core. Example 0,1,2. Default is 3."
                ,nargs='?',default = "3")
        parser.add_argument("-e","--end",help="Auto endding processing",action="store_true")
        args = parser.parse_args()
        
        os.system("taskset -cp %s %d" %(args.cpu,os.getpid()))
        
        loop=False
        if args.cycle<=0:
                loop=True
                
        
        Din=[
            4,
            23,
            22,
            6
            ]
        Dout=[
            24,
            25,
            26,
            27
            ]
        
        logging.info("Din pin: GPIO 4 / 23 / 22 / 6 mapping to DI_0 / DI_1 / DI_2 / DI_3")
        logging.info("Dout pin: GPIO 24 / 25 / 26 / 27 mapping to DO_0 / DO_1 / DO_2 / DO_3")
        
        GPIO.setwarnings(False)
        if GPIO.getmode()==-1 or GPIO.getmode()==None:
                GPIO.setmode(GPIO.BCM)
        for i in Din:
                GPIO.setup(i, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        for i in Dout:
                GPIO.setup(i, GPIO.OUT)
                GPIO.output(i, GPIO.LOW)
                
                
        count = 0
        DoutH=False
        while loop or count<args.cycle:
                startTime = time.time()
                serialStr = ", perial:"+str(count+1)
                if args.cycle>0:
                        serialStr = serialStr+"/"+str(args.cycle)
                logging.info("\n\n***** "+datetime.fromtimestamp(startTime).strftime("%Y-%m-%d %H:%M:%S")+serialStr)
                if not DoutH:
                        DoutH=True
                        for i in Dout:
                                GPIO.output(i, GPIO.HIGH)
                        logging.info("Dout turn high!")
                else:
                        DoutH=False
                        count=count+1
                        for i in Dout:
                                GPIO.output(i, GPIO.LOW)
                        logging.info("Dout turn low!")
                logging.info("Din status")
                for i,v in enumerate(Din):
                        if GPIO.input(v):
                                logging.info("\tDI_"+str(i)+"(GPIO "+str(v)+"): High")
                        else:
                                logging.info("\tDI_"+str(i)+"(GPIO "+str(v)+"): Low")
                        
                sleepTime = 1-(time.time()-startTime)
                if sleepTime>0:
                        time.sleep(sleepTime)
                
        
        
        endMassage("",args.end)
                
        
        

