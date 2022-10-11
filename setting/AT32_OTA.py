import os
import zlib
import binascii
from functools import reduce
import spidev
import time
import argparse
import sys


#one line string to hex-8 list,except ':' and CR
def char2hex(line):
    line=list(map(ord,list(line)))
    for num in range(len(line)):
        if line[num]>=0x30 and line[num]<=0x39:
            line[num] = line[num] - 0x30
        elif line[num]>=0x41 and line[num]<=0x5A:
            line[num] = line[num] - 55
        else:
            pass
    line=line[1:-1]     #delete CR and ':', in terms of byte
    for i in range(0,len(line),2):
        line[i] = line[i]*16 + line[i+1]
        newline = line[::2]
    return newline

#checksum calculation of every line
def checksum(line):
    #considering if the checksum calculation result is 0x100
    sum = (0x100 - (reduce(lambda x,y:x+y,line[:-1]) % 256)) % 256
    if sum == line[-1]:     #check if sum calculated is equal to checksum byte in hex file
        return 0
    else:
        return 1
        
def crc32Cal(buf):
    fwCheckSum = 0;
    if len(buf) != 0:
        byteBuf = bytearray(buf)
        fwCheckSum = zlib.crc32(byteBuf,fwCheckSum)&0xFFFFFFFF
    return fwCheckSum
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("bus",type=int,help="SPI bus. Example 0 or 1.",choices=[0,1])
    parser.add_argument("cs",type=int,help="SPI CE. Example 0 or 1.",choices=[0,1])
    parser.add_argument("file",type=str,help="hex-file path. Example /home/pi/xx.hex")
    args = parser.parse_args()
    
    #Init SPI
    spi=spidev.SpiDev()
    spi.open(args.bus,args.cs) # bus,device
    spi.mode=0
    spi.max_speed_hz = 500000
    CMD_start = [0xF7,0xF8]
    
    #Read hex file
    f = open(args.file,'r')
    bin_buf = []
    for line in f.readlines():
        byte_num = 0
        if(line[0] == ':'):
            if(line[7:9] == '04'):
               line = char2hex(line)
               offsetAddr = (line[1]<<8) + line[2]
               if checksum(line) == 0:
                   addr_h = (line[4]<<24) +(line[5]<<16)
               else:
                   print('checksum failed!'+str(list(map(hex,line))))
            elif (line[7:9] == '00'):
                line = char2hex(line)
                if checksum(line) == 0:
                    addr_l = (line[1]<<8) + line[2]
                    LL = line[0]
                    byte_num = byte_num + LL
                    for data in line[4:-1]:
                        bin_buf.append(data)
                else:
                    print('checksum failed!'+str(list(map(hex,line))))
            elif(line[7:9] == '05'):
                line = char2hex(line)
                if checksum(line) == 0:
                    pass
                else:
                    print('checksum failed!'+str(list(map(hex,line))))
            elif(line[7:9] == '01'):
                line = char2hex(line)
                if checksum(line) == 0:
                    print(' *Total size : %d Bytes'%len(bin_buf))
                else:
                    print('checksum failed!'+str(list(map(hex,line))))
            else:
                pass
        else:
            print('illegal format!')

    f.close()
    
    #Send to reboot into bootloader
    tryCount = 0
    
    #Send start flag
    data=spi.xfer2([CMD_start[0]])
    time.sleep(2)
    while(data[0] != CMD_start[1]):
        tryCount+=1
        time.sleep(2)
        if tryCount == 15:
            print("Timeout, exit OTA.")
            print(sys.exit())
        data=spi.xfer2([CMD_start[0]])
        
        
    data=spi.xfer2([CMD_start[1]])
    
    binCheckSum = crc32Cal(bin_buf)
    print(' *checkSum : 0x%08X'%binCheckSum)
    binCheckSum = binCheckSum.to_bytes(4, byteorder='little')
    fwSize = len(bin_buf).to_bytes(4, byteorder='little')
    data=spi.xfer2(fwSize[0:4])
    data=spi.xfer2(binCheckSum[0:4])
    send2KBuffer = len(bin_buf)
    send2kCount = int(send2KBuffer/2000) + 1
    i = 0
    for j in range(send2kCount):
        if(send2KBuffer >= 2000):
            data=spi.xfer2(bin_buf[i:i+2000])
            i += 2000
            send2KBuffer -= 2000
        else:
            data=spi.xfer2(bin_buf[i:i+send2KBuffer])
