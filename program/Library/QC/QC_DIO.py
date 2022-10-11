#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Dec  27 10:00:01 2021

@author: etao
"""

import sys
import time
import argparse
import RPi.GPIO as GPIO
        
if __name__ == "__main__":
        reverse = False
        parser = argparse.ArgumentParser()
        parser.add_argument("output",type=str,help="Setting DO ch1~ch4 level. Pull high. (0: logic low[switch open to get high level]. 1: logic high[switch pass to get low level].)")
        parser.add_argument("target",type=str,help="Setting DI target. (0: logic low[From 9~12V by high level]. 1: logic high[From 0~1.2V by low level].)")
        args = parser.parse_args()
        
        
        if len(args.output)!=4:
                print("error: invalid output channel setting length.")
                sys.exit()
        else:
                for c in args.output:
                        if c!="0" and c !="1":
                                print("error: invalid output channel setting value.")
                                sys.exit()
        
        if len(args.target)!=4:
                print("error: invalid target channel setting length.")
                sys.exit()
        else:
                for c in args.target:
                        if c!="0" and c !="1":
                                print("error: invalid target channel setting value.")
                                sys.exit()
        
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
        
        
        GPIO.setwarnings(False)
        if GPIO.getmode()==-1 or GPIO.getmode()==None:
                GPIO.setmode(GPIO.BCM)
        for i,c in enumerate(args.output):
                GPIO.setup(Dout[i], GPIO.OUT)
                if int(c)^int(reverse)==0:
                        GPIO.output(Dout[i], GPIO.LOW)
                else:
                        GPIO.output(Dout[i], GPIO.HIGH)
                
        time.sleep(0.1)
        result=""
        for i in Din:
                GPIO.setup(i, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
                if GPIO.input(i):
                        result+="1"
                else:
                        result+="0"
                        
        if result==args.target:
                print("PASS")
        else:
                print("FAIL")
                        
        
                
        
        

