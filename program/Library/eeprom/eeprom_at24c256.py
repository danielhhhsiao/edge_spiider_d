#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 08 15:10:01 2022

@author: etao
https://gist.github.com/CRImier/b3922e0656825746a801594a7ccba8af
"""

import os
import sys
import time
import argparse
import math
from smbus2 import SMBus, i2c_msg
           
def findList(arr,target):
        try:
                ret = arr.index(target)
        except:
                ret=-1
        return ret
        
def write_to_eeprom(bus, address, string, bs=64, sleep_time=0.01):
        """
        Writes to a 16-bit EEPROM. Only supports starting from 0x0000, for now.
        (to support other start addresses, you'll want to improve the block splitting mechanism)
        Will (or *might*?) raise an IOError with e.errno=121 if the EEPROM is write-protected.
        Default write block size is 64 bytes per write.
        By default, sleeps for 0.01 seconds between writes (otherwise, errors might occur).
        Pass sleep_time=0 to disable that (at your own risk).
        """
        if string==-1:
                data = [255]*(32768)
        else:
                data = [ord(c) for c in string]+[0] #add end point
                data = data[:32768]
        b_l = len(data)
        # Last block may not be complete if data length not divisible by block size
        b_c = int(math.ceil(b_l/float(bs))) # Block count
        # Actually splitting our data into blocks
        blocks = [data[bs*x:][:bs] for x in range(b_c)]
        #print(blocks)
        for i, block in enumerate(blocks):
                if sleep_time:
                        time.sleep(sleep_time)
                start = i*bs
                hb, lb = start >> 8, start & 0xff
                #print([hb, lb])
                data = [hb, lb]+block
                write = i2c_msg.write(address, data)
                bus.i2c_rdwr(write)

def read_from_eeprom(bus, address,count=32768, bs=64):
        """
        Reads from a 16-bit EEPROM. Only supports starting from 0x0000, for now.
        (to add other start addresses, you'll want to improve the counter we're using)
        Default read block size is 64 bytes per read.
        """
        
        
        data = [] # We'll add our read results to here
        # If read count is not divisible by block size,
        # we'll have one partial read at the last read
        full_reads, remainder = divmod(count, bs)
        if remainder: full_reads += 1 # adding that last read if needed
        for i in range(full_reads):
                start = i*bs # next block address
                hb, lb = start >> 8, start & 0xff # into high and low byte
                #print([hb, lb])
                write = i2c_msg.write(address, [hb, lb])
                # If we're on last cycle and remainder != 0, not doing a full read
                count = remainder if (remainder and i == full_reads-1) else bs
                read = i2c_msg.read(address, count)
                bus.i2c_rdwr(write, read) # combined read&write
                newDate = list(read)
                #print(newDate)
                data += newDate
                #print(findList(newDate,0)>=0)
                if findList(newDate,0)>=0 or findList(newDate,0xFF)>=0:
                        index = findList(data,0)
                        if index==-1:
                                index = findList(data,0xFF)
                        data = data[:index]
                        break
        return ''.join(map(chr, data))

                
if __name__ == "__main__":
        __version__ = "1.0.0"
        address = 0x57
        i2c_bus = 1
        
        parser = argparse.ArgumentParser()
        parser.add_argument("word",type=str,help="limit to 256Kbit (32768 word)",nargs='?',default = "")
        parser.add_argument("-r","--read",help="Read eeprom from index 0. Return result.",action="store_true")
        parser.add_argument("-w","--write",help="Write word to eeprom from index 0. Writing succesful will return PASS, else FAIL.",action="store_true")
        parser.add_argument("-c","--check",help="Check eeprom data with word. The same data will return PASS, else FAIL.",action="store_true")
        parser.add_argument("-e","--empty",help="Write full 0xFF to eeprom. The function will process a few minutes. Reset succesful will return PASS, else FAIL.",action="store_true")
        parser.add_argument("-t","--test",help="Write full test text to eeprom. The function will process a few minutes. Reset succesful will return PASS, else FAIL.",action="store_true")
        args = parser.parse_args()
        
        
        try:
                i2c = SMBus(i2c_bus)
        except:
                if not args.read:
                        print("FAIL")
                sys.exit()
        
        if args.read:
                try:
                        print(read_from_eeprom(i2c,address))
                except:
                        sys.exit()
        elif args.empty:
                try:
                        write_to_eeprom(i2c,address,-1)
                        print("PASS")
                except:
                        print("FAIL")
        elif args.test:
                fullstr = "".join(["Etao is a good man (loop %04d). " % (i) for i in range(int(32768/32))])
                print(fullstr)
                try:
                        write_to_eeprom(i2c,address,fullstr)
                        print("PASS")
                except:
                        print("FAIL")
        elif args.write:
                try:
                        write_to_eeprom(i2c,address,args.word)
                        print("PASS")
                except:
                        print("FAIL")
        elif args.check:
                try:
                        eeprom_data = read_from_eeprom(i2c,address)
                except:
                        print("FAIL")
                        sys.exit()
                        
                if eeprom_data == args.word:
                        print("PASS")
                else:
                        print("FAIL")
        else:
                print("FAIL")
       

