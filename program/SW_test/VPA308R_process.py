class VPA308R_process(multiprocessing.Process):
    def __init__(self,name,port,fs,gain,sec):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()

        self.default_Baudrate                    =921600
        self.oneSampleByte                       =1544
        self.VAP308R_GAIN=dict()
        self.VAP308R_GAIN[2]                     =0
        self.VAP308R_GAIN[4]                     =1
        self.VAP308R_GAIN[8]                     =2
        self.VAP308R_FS=dict()
        self.VAP308R_FS[4000]                     =0
        self.VAP308R_FS[2000]                     =1
        self.VAP308R_FS[1000]                     =2
        self.VAP308R_FS[500]                      =3
        self.VAP308R_BR=dict()
        self.VAP308R_BR[9600]                     =0
        self.VAP308R_BR[19200]                    =1
        self.VAP308R_BR[57600]                    =2
        self.VAP308R_BR[115200]                   =3
        self.VAP308R_BR[230400]                   =4
        self.VAP308R_BR[256000]                   =5
        self.VAP308R_BR[460800]                   =6
        self.VAP308R_BR[921600]                   =7
        self.stdCommand = b'*********** FIRMWARE ***********'
        
        
        self.sec = sec
        self.name = name
        self.sapleRate = fs
        self.port = serial.Serial(port,self.default_Baudrate,parity=serial.PARITY_NONE, bytesize=8 )
        if not self.port.isOpen():
            self.port.open()
            
        #init sensor
        self.stopSample(10)
        rdata=self.get_infor()
        if(self.stdCommand not in rdata):
            self.port_scan_baud()
            if self.port.baudrate != self.default_Baudrate:
                self.set_sensor_baud(self.default_Baudrate)
                rdata=self.get_infor()
                if(self.stdCommand not in rdata):
                    raise Exception('VPA308R ['+self.name+'] processing baudrate setting error.')
        
        
        self.set_fs(fs)
        self.set_gain(gain)
        self.set_bias('X',0)
        self.set_bias('Y',0)
        self.set_bias('Z',0)
        self.set_bias('T',0)
        self.set_raw()
        rdata=self.get_infor()
        print('VPA308R ['+self.name+'] information:',rdata.decode('utf-8'))
        
        
        manager=multiprocessing.Manager()
        self.data=manager.dict()
        self.states=manager.dict()
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        
    def stopSample(self,count=-1):
        if count>0:
            for j in range(count):
                self.port.flushInput()
                self.port.write(b'AT$S'+bytes([0x0D]))
                time.sleep(0.1)
        else:
            self.port.flushOutput()
            self.port.flushInput()
            self.port.write(b'AT$S'+bytes([0x0D]))
            time.sleep(0.1)
            while(self.port.in_waiting >0):
                self.port.flushOutput()
                self.port.flushInput()
                self.port.read(self.port.in_waiting)
                self.port.write(b'AT$S'+bytes([0x0D]))
                time.sleep(0.1)
        
    def port_scan_baud(self):
        baud_value = [9600,19200,57600,115200,230400,256000,460800,921600]
        for i in range(len(baud_value)):
            self.rdata=b''
            self.port.baudrate=baud_value[i]
            self.stopSample(10)
            self.port.flushOutput()
            self.port.flushInput()
            self.port.write(bytes([0x0D]))
            time.sleep(0.2)
            self.port.write(bytes([0x0D]))
            time.sleep(0.2)
            
            rdata=self.get_infor()
            #print("rdata",rdata)
            print('VPA308R ['+self.name+'] scan baudrate on %d' %baud_value[i],rdata[:50])
            if(self.stdCommand in rdata):
                print('VPA308R ['+self.name+'] oringinal baulrate is %d' %baud_value[i])
                return baud_value[i]
        raise Exception('VPA308R ['+self.name+'] processing search baudrate error! please check sensor is connected on RS422.')
        return None
                            
               
    def set_sensor_baud(self,baud_param):
        command = self.VAP308R_BR[baud_param]
        
        self.stopSample()
        time.sleep(1)  
        self.port.write(bytes([0x0D]))
        time.sleep(0.2)
        self.port.write(b'AT$BAUD'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        print('VPA308R ['+self.name+'] Setting Baud Success, Mode:%d' %baud_param)

        print('VPA308R ['+self.name+'] Reset Sensor...')
        time.sleep(0.2)
        self.port.write(b'AT$RESET'+bytes([0x0D]))
        time.sleep(5) 
        print('VPA308R ['+self.name+'] Reset Succussful')
        self.port.baudrate=baud_param
        self.stopSample()
        
        
    def set_fs(self,fs):
        command = self.VAP308R_FS[fs]
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$ODR'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        print('VPA308R ['+self.name+'] Setting fs to %d' %fs)
        
        
    def set_gain(self,gain):
        command = self.VAP308R_GAIN[gain]
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$GRAN'+ bytes(chr(command+48),'utf-8') +bytes([0x0D]))
        time.sleep(0.2)
        print('VPA308R ['+self.name+'] Setting gain to %d G' %gain)
        
        
    def set_raw(self):
        self.stopSample()
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        self.port.write(b'AT$RAW'+bytes([0x0D]))
        time.sleep(0.2)
                 
    def set_bias(self,target,value):
        self.stopSample()
        command=b'AT$BIAS'+bytes(target,'utf-8')+struct.pack('f',float(value))
        self.port.write(command)
        time.sleep(0.2)
                
    def get_infor(self):
        self.port.flushOutput()
        self.port.flushInput()
        self.port.write(b'AT$LIST'+bytes([0x0D]))
        time.sleep(0.2)
        self.port.write(bytes([0x0D]))
        time.sleep(0.1)
        
        dataLen = self.port.in_waiting
        return self.port.read(dataLen) 
                 
                            
    def getData(self):
        if self.states["new"]:
            self.states["new"]=False
            return self.data
        else:
            self.release()
            raise Exception('VPA308R ['+self.name+'] processing, please start this module working!')
            return None
          
    def sub_join(self,timeout=-1):
        print("sub_join",'VPA308R ['+self.name+'] processing')
        if timeout>0:
            timeout = timeout+2
            startTime=time.time()
            newTime=startTime
            while(self.states["run"] is True and newTime-startTime<timeout):
                time.sleep(0.1)
                newTime=time.time()
            if newTime-startTime>=timeout:
                self.release()
                raise Exception('VPA308R ['+self.name+'] processing sample timeout!')
        else:
            while self.states["run"] is True:
                time.sleep(0.1)
            
    def start_sample(self,sec=1):
        self.states["run"]=True
            
    def end_sample(self):
        self.states["run"]=False
        self.states["release"]=True
            
    def run(self):
        pid=os.getpid()
        print('VPA308R ['+self.name+'] pid is',pid)
        os.system("taskset -cp 0 %d" %(pid))
        self.states["new"]=False
        self.states["run"]=False
        self.states["release"]=False
        maxCount=int(self.sapleRate*self.sec*1.2*3) #one sample 4 byte 3 axis
        print("maxCount",maxCount)
        #sampleInteval = 128/self.sapleRate/2
        sampleInteval = 0.01
        lastIndex = -1
        currentIndex = 1
        oneSampleByte= 128*3
        stdArr = list(range(oneSampleByte))
        
        self.port.flushOutput()
        self.port.flushInput()
        #self.port.write(b'AT$RS'+bytes([0x0D])) #start sample
        self.port.write(b'AT$RESET'+bytes([0x0D])) #reset and start sample
        while self.port.in_waiting==0:
            time.sleep(0.01) #start sample
        while self.states["release"] is False:
            if self.states["run"] is False:
                time.sleep(0.01)
                
                while self.port.in_waiting > self.oneSampleByte:
                    data = self.port.read(self.oneSampleByte)
                    currentIndex = data[3]
                    lastIndex = currentIndex
                continue
            startTime = time.time()
            byteBuffer = b''
            #print('VPA308R ['+self.name+'] start access sample data:',lastIndex)
                
            bufferIndex = 0
            bufferArr = np.zeros(maxCount,dtype=np.float32)
            while(time.time()-startTime<self.sec ):
                time.sleep(sampleInteval)
                #print(self.port.in_waiting,time.time()-startTime,bufferIndex,bufferIndex/(time.time()-startTime)/3)
                while self.port.in_waiting > self.oneSampleByte:
                    lastTime = time.time()
                    data = self.port.read(self.oneSampleByte)
                    if data[0:3]!=b'AT3':
                        print('time:',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),file=sys.stderr)
                        print('VPA308R ['+self.name+'] data error:',data[0:3],file=sys.stderr)
                    else:
                        floatData = list(map(lambda x:struct.unpack('f',data[4+x*4:8+x*4])[0],stdArr))
                        bufferArr[bufferIndex:bufferIndex+oneSampleByte] = floatData
                        bufferIndex=bufferIndex+oneSampleByte
                        currentIndex = data[3]
                        diffIndex = abs(currentIndex-lastIndex)
                        if (diffIndex != 1 and diffIndex!=255):
                            print('time:',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),file=sys.stderr)
                            print('VPA308R ['+self.name+'] less data ar index (current/last):',currentIndex,"/",lastIndex,file=sys.stderr)
                        lastIndex=currentIndex
            
            bufferArr=bufferArr[:bufferIndex] / 1000
            bufferArr=np.reshape(bufferArr,(-1,3)).T
            
            timeList=np.arange(len(bufferArr[0]))/len(bufferArr[0])*(lastTime-startTime)
            timeList=timeList+startTime
            
            self.data["timestamp"]=timeList
            self.data["aX_"+self.name]=bufferArr[0]
            self.data["aY_"+self.name]=bufferArr[1]
            self.data["aZ_"+self.name]=bufferArr[2]
                
            
            self.stopSample(10)
            result=None #release
            timeList=None #release
            self.states["new"]=True
            self.states["run"]=False
            
        print(time.time(),"VPA308R ["+self.name+"] process out the main loop.")
        
    def release(self,timeout=-1):
        self.end_sample()
        if timeout>0:
            startTime = time.time()
            while self.is_alive() and time.time()-startTime<timeout:
                time.sleep(0.5)
            if self.is_alive():
                self.terminate()
                print("VPA308R ["+self.name+"] process join timeout!",file=sys.stderr)
                print("VPA308R ["+self.name+"] process join timeout!")
                print("Force kill!")
                self.join()
        else:
            if self.is_alive():
                self.join()
        print("release VPA308R ["+self.name+']  processing')
        self.exit.set()
    
        