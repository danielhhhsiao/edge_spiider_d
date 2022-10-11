import pyaudio
import struct
import math
import alsaaudio
import wave
import os
import sys
import time
import threading
import Udev_Rules_lib
import numpy as np
#from tqdm import tqdm

from ctypes import *
from contextlib import contextmanager

FORMAT = pyaudio.paInt16 #or using paFloat32 
SHORT_NORMALIZE = (1.0/32768.0) #for def_RMS
CHANNELS = 1 # mono = 1, stereo =2
RATE = 44100  #smaple rate =44.1K
INPUT_BLOCK_TIME = 0.05 #for def_RMS
INPUT_FRAMES_PER_BLOCK = 4096


OUTPUT_DIR = 'WAV_output/'
RECORD_SECONDS = 3 #recording time

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
        print('Microphone %s :Created!'%self.device_ID)


def recording(filename, microphone_obj):
    stream = microphone_obj.open_mic_stream()
    print ("* recording")
    print('Microphone Loc: ',microphone_obj.device_ID,' Index: ',microphone_obj.device_index)
    obj_api_info = microphone_obj.pa.get_default_host_api_info()
    obj_api_index = obj_api_info.get('index')
    #print(obj_api_info,obj_api_index)
    print('Info: ',microphone_obj.pa.get_device_info_by_host_api_device_index(obj_api_index,microphone_obj.device_index))
    recording_data = np.zeros((RECORD_SECONDS*RATE+INPUT_FRAMES_PER_BLOCK)*CHANNELS, dtype=np.int16)
    for i in range(0, int(RATE / INPUT_FRAMES_PER_BLOCK * RECORD_SECONDS)+1):
        data = stream.read(INPUT_FRAMES_PER_BLOCK , exception_on_overflow = False)
        recording_data[i*INPUT_FRAMES_PER_BLOCK*CHANNELS:(i+1)*INPUT_FRAMES_PER_BLOCK*CHANNELS] = np.frombuffer(data,dtype = np.int16)
        
    print ("* done recording")
    microphone_obj.stop()
    microphone_obj.pa.terminate()
    save_as_wav(filename, microphone_obj,recording_data[0:RECORD_SECONDS*RATE*CHANNELS])
    #print(recording_data[0:RECORD_SECONDS*RATE*CHANNELS])
    #print(recording_data[0:RECORD_SECONDS*RATE*CHANNELS].astype(np.float32, order='C')*SHORT_NORMALIZE)
    return recording_data[0:RECORD_SECONDS*RATE]
    
def save_as_wav(filename, microphone_obj, data):
    wf=wave.open(OUTPUT_DIR+filename,'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(microphone_obj.pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()


#======alsaerr disable s=====
    
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)
    
#======alsaerr disable e=====

    
if __name__ == "__main__":
    udev_rule_seting = input('Set Rule?(Input Y or y for yes!)')
    if udev_rule_seting == 'Y' or udev_rule_seting == 'y':
        Udev_Rules_lib.build_rules()
    # initial
    
    with noalsaerr():
        p = pyaudio.PyAudio()
    microphone_index = []
    microphone_obj = []
    # get API info
    api_info = p.get_default_host_api_info()
    api_index = api_info.get('index')
    first_index = -1
    input_devices_num = 0
    
    print('-------------------------------')
    for i in range (0,p.get_device_count()):
        print ("Device id ", i, " - ", p.get_device_info_by_host_api_device_index(api_index,i))
                
    for i in range (0,len(alsaaudio.cards())):
        if p.get_device_info_by_host_api_device_index(api_index,i).get('maxInputChannels')>0:
            print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(api_index,i).get('name'))
            input_devices_num += 1
            if first_index < 0:
                first_index = p.get_device_info_by_host_api_device_index(api_index,i).get('index')

    index_offset = first_index - (len(alsaaudio.cards())-input_devices_num)

    print('-------------------')
    print(alsaaudio.cards(),'Input device number:',input_devices_num)
    print('First index:',first_index,'Offset',index_offset)
    print('-------------------')    
    
    for i in range(1,5):
        try:
            devinfo = p.get_device_info_by_index(alsaaudio.cards().index('usb%d'%i) + index_offset)
            microphone_index.append(devinfo.get('index'))
            microphone_obj.append("usb%d"%i)
        except:
            pass
        
    microphone_name = microphone_obj.copy()
    for i in range(len(microphone_index)):
        microphone_obj[i] = Microphone(microphone_index[i],microphone_name[i])
        microphone_obj[i].stop()

    #os.system('clear')
    
#     -----Threading Recording-----   

    INPUT_FRAMES_PER_BLOCK = 4096
    specified_mic_list =input("Enter the device ID for recording(Separated by commas, like:usb1,usb3...)\n")
    threads = []
    specified_mic = specified_mic_list.split(',')
    
    for i in range(len(microphone_name)):
        if microphone_obj[i].device_ID in specified_mic:
            threads.append(threading.Thread(target = recording, args = ("%s.wav"% microphone_obj[i].device_ID,microphone_obj[i],)))
            
    for i in range(len(threads)):
        threads[i].start()
    for i in range(len(threads)):
        threads[i].join()

    print("Done.")

     


