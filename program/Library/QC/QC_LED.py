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
        parser = argparse.ArgumentParser()
        parser.add_argument("st",type=int,help="Select STx LED. (1: ST1. 2: ST2)",choices=[1,2])
        parser.add_argument("level",type=int,help="Setting STx status. (0: dark. 1: light.)",choices=[0,1])
        args = parser.parse_args()
        
        
        ST=[
            12,
            13
            ]
        
        
        GPIO.setwarnings(False)
        if GPIO.getmode()==-1 or GPIO.getmode()==None:
                GPIO.setmode(GPIO.BCM)
                
        pin = ST[args.st-1]
        GPIO.setup(pin, GPIO.OUT)
        if args.level==0:
                GPIO.output(pin, GPIO.HIGH)
        else:
                GPIO.output(pin, GPIO.LOW)
