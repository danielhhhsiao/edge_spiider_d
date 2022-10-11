import pyaudio
import struct
import math
import alsaaudio
import wave
import os
import sys
import time
import threading
import numpy as np
import Udev_Rules_lib as Udev_Rules_lib


# INITIAL_THRESHOLD = 0.5
FORMAT = pyaudio.paInt16 #or using paFloat32 
SHORT_NORMALIZE = (1.0/32768.0) #for def_RMS
CHANNELS = 1 # mono = 1, stereo =2
RATE = 44100  #smaple rate =44.1K
INPUT_BLOCK_TIME = 0.05 #for def_RMS
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME) #def_RMS and recording buffer size


def get_rms(block): #input buffer block to get RMS info
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n
    return math.sqrt(sum_squares/count)

class Microphone(object): # create microphone object
    def __init__(self,device_index,device_ID):
        self.device_index = device_index #from pyaudio info
        self.device_ID = device_ID #from pyaudio info
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()

    def stop(self): #turn off the microphone
        self.stream.stop_stream()
        self.stream.close()
        print('Stop %s stream.'%self.device_ID)

    def open_mic_stream(self): #turn on the microphone
        stream = self.pa.open(format = FORMAT,
                              channels = CHANNELS,
                              rate = RATE,
                              input = True,
                              input_device_index = self.device_index,
                              frames_per_buffer = INPUT_FRAMES_PER_BLOCK)
        return stream
    
    def RMS(self): #for identification
        amplitude = get_rms(self.stream.read(INPUT_FRAMES_PER_BLOCK, exception_on_overflow = False))
        return amplitude*100
    
    def tester(self): #make sure that microphone was created successfully
        print('Monitor %s :Created!'%self.device_ID)

    
if __name__ == "__main__":
#    udev_rule_seting = input('Set Rule?(Input Y or y for yes!)')
#    if udev_rule_seting == 'Y' or udev_rule_seting == 'y':
    print('Setting USB port name')
    Udev_Rules_lib.build_rules()
#    else:
#        print('Skip Setting Process!')
    #initial
    p = pyaudio.PyAudio()
    microphone_index = []
    microphone_obj = []
    # get API info
    api_info = p.get_default_host_api_info()
    api_index = api_info.get('index')
    info = p.get_host_api_info_by_index(api_index)
    num_devices = info.get('deviceCount')
    first_index = -1
    input_devices_num = 0
    
    #os.system('clear')
    for i in range (0,num_devices):
        if p.get_device_info_by_host_api_device_index(api_index,i).get('maxInputChannels')>0\
        and 'USB' in p.get_device_info_by_host_api_device_index(api_index,i).get('name').upper():
            #print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(api_index,i).get('name'))
            input_devices_num += 1
            if first_index < 0:
                first_index = p.get_device_info_by_host_api_device_index(api_index,i).get('index')
#    print(first_index, input_devices_num)
#    index_offset = first_index - (len(alsaaudio.cards())-input_devices_num)
    try:
        for device in alsaaudio.cards():
            if 'USB' in device.upper():
                alsa_index = alsaaudio.cards().index(device)
                break
        index_offset = first_index - alsa_index
    except:
        print('Not found any device.')

    for i in range(1,5):
        try:
            devinfo = p.get_device_info_by_index(alsaaudio.cards().index('usb%d'%i) + index_offset)
            print ("usb%d: Selected device is "%i,devinfo.get('name'))
            print("usb%d: Selected device's index is "%i,devinfo.get('index'))
            microphone_index.append(devinfo.get('index'))
            microphone_obj.append("usb%d"%i)
        except:
#             print("please plug in usb%d!"%(i))
            pass
        finally:
            microphone_name = microphone_obj.copy()
#     -----Detect-----
    for i in range(len(microphone_index)):
        microphone_obj[i] = Microphone(microphone_index[i],microphone_name[i])
        microphone_obj[i].tester()
    print("All monitors created!")
    try:
        t=time.time()+60
        print("Press Ctrl+C to stop identification processing immediately!")
        while(time.time()-t <= 0):
            for i in range(len(microphone_index)):
                print(' {}:{:>5.2f}%'.format(microphone_obj[i].device_ID,microphone_obj[i].RMS()),end = '  ')
#                print(microphone_obj[i].device_ID,':%4.2f%%'%microphone_obj[i].RMS(),end = ' ')
            print(' Stop in %.0f s'% (t-time.time()),end = '  ')
            time.sleep(0.025)
            print('\r',end ='')
    except KeyboardInterrupt :
        print('\n')
        for i in range(len(microphone_index)):
            microphone_obj[i].stop()

    #input("Setting Finish! Press Enter to continue!")
    print("Setting Finish!")



     

