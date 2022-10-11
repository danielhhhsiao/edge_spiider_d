import os
import time
import datetime
import glob
import psutil
import pandas as pd
import Library.phm_func as phm_func 
import Library.Sensor as Sensor
import Library.Segmentation as Segmentation
import Library.Extraction as Extraction
import Library.Connection as Connection
import Library.wifi as wifi
import Library.iot as iot
import configparser
import gc

__version__ = '3.5.3_2021_0601_Improve_long_time_will_show_done_problem..'


def getSection(config,name):
    try:
        ret=config.items(name)
        return ret
    except:
        return {}
def get_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    
    #setting
    items = getSection(config,'setting')
    for item in items:
        setting_config[item[0]] = item[1]
   
    #sensor
    items = getSection(config,'sensor')
    for item in items:
        sensor_config[item[0]] = item[1]
   
    #ads1115
    items = getSection(config,'ads1115')
    for item in items:
        ads1115_config[item[0]] = item[1]
       
    #mpu9250
    items = getSection(config,'mpu9250')
    for item in items:
        mpu9250_config[item[0]] = item[1]
        
    #gy530
    items = getSection(config,'gy530')
    for item in items:
        gy530_config[item[0]] = item[1]
        
    #kashiyama
    items = getSection(config,'kashiyama')
    for item in items:
        kashiyama_config[item[0]] = item[1]
        
    #plc
    items = getSection(config,'PLC')
    for item in items:
        PLC_config[item[0]] = item[1]
        
    #I/O sample
    items = getSection(config,'IO_sample')
    for item in items:
        IO_sample_config[item[0]] = item[1]
        
    #polling_device_config
    items = getSection(config,'polling_device')
    for item in items:
        polling_device_config[item[0]] = item[1]
    
    #segmentation
    #I/O sample
    items = getSection(config,'segmentation')
    for item in items:
        segmentation_config[item[0]] = item[1]
        
    #extraction
    items = config.items('extraction')
    for item in items:
        extraction_config[item[0]] = item[1]
        #if (item[0] == 'project_id') :
        #    setting_config['project_id'] = item[1]
    #print(' setting project_id=',setting_config.get('project_id') )
    
    #Connection
    items = config.items('connection')
    for item in items:
        connection_config[item[0]] = item[1]    

def GetRaspberryInfo() :
    
    id_path = './.id.txt'        
    # 2020/05/23 Check id.txt exist ?
    #if (  os.path.isfile(id_path) == False ) :

    #Serial
    f = open('/proc/cpuinfo','r')
    for line in f:
        if line[0:6] == 'Serial':
            serial_no = line[10:26]
        if line[0:8] == 'Revision':
            revision = line[11:]
    
    #wlan mac
    f = open('/sys/class/net/wlan0/address','r')
    for line in f:
        wlan_mac_no = line.replace(':','')

    #eth mac
    f = open('/sys/class/net/eth0/address','r')
    for line in f:
        eth_mac_no = line.replace(':','')
    
    id_str = serial_no + wlan_mac_no + ';' + eth_mac_no + ';' + revision
    id_str = id_str.replace('\n','')
    
    fp = open(id_path, 'w')
    fp.write(id_str)
    fp.close()
    #print('Log Seriral No data.')

def readLogData() :
    logFilename = phm_func.data_path + '/Log/RunLog_' + datetime.date.today().strftime('%Y%m%d') + '.csv'
    
    if not os.path.isfile(logFilename):        
        print('Log is not exist!', logFilename)
        pd_log = pd.DataFrame()#[], columns=['datetime','Loopidx', 'sesnor','sampling_rate','record_second','sensor_list','segCount','featureCount'])
    else :        
        pd_log = pd.read_csv(logFilename) #, index= False)
        print('read log ,shape=', pd_log.shape)
    print('pd log shape=', pd_log.shape)
    return pd_log,logFilename

def saveRunLog(run_loop, pd_log,setting_config, connection_config,logFilename):
#    logFilename = phm_func.data_path + '/Log/RunLog_' + datetime.date.today().strftime('%Y%m%d') + '.csv'    
    pd_log.to_csv(logFilename, index= False) #
    if ((run_loop % 2) == 0) :
        if(run_connection):
            #print('Upload Raspberry Log...')
            key="RunLog_"+datetime.date.today().strftime('%Y%m%d') + '.csv'
            log_dic = {key:pd_log}
            Connection.processing('RunLog', setting_config, connection_config, log_dic )
        
if __name__ == "__main__":
    pid=os.getpid()
    os.system("taskset -cp 0-3 %d" %(pid))
#    os.system("renice -n -20 -p %d" %(pid))
    print("gc****",gc.isenabled())
    run_cnt = 1000
    memory_using = 0.
    config_list = []
    
    GetRaspberryInfo()
    
    wifiInfo=wifi.getInfo()
    wifiName="--"
    wifiQuality="--"
    wifiStrength="--"
    if wifiInfo != None and wifiInfo["Name"]!='':
        wifiName=wifiInfo["Name"]
        wifiQuality=wifiInfo["Quality"]
        wifiStrength=wifiInfo["Signal"]
    print("wifi Name:",wifiName)
    print("wifi Quality:",wifiQuality)
    print("wifi Strength:",wifiStrength)
    
    #phm_func.check_directory_of_phm_data()
    #system start
    for run_loop in range(run_cnt):        
        #Memory check
        info = psutil.virtual_memory()
        memory_using = info.percent
        
        print('Run loop:', run_loop + 1, '/', run_cnt, ' Memory Using:', memory_using, '%')
        
        if memory_using > 70:
            
            print('Memory Using Over Spec Restart Raspberry PI!')
            raise Exception('Memeory', 'using high')
            break
        
    #while memory_using < 90:
                
        config_path = './'
        for config_file in sorted(glob.glob(config_path + 'config*.ini')):
            print('<<<=== config_file=',config_file, '=======>>>')
            
            phm_func.check_directory_of_phm_data(config_file)
            #if ( run_loop ==  0) :
            pd_Log,pd_log_name = readLogData()
            #print('Main phm func , Home_dir=',phm_func.home_path,', data path=', phm_func.data_path)
            
            #config_path = config_path +  "config.ini"
            
            setting_config = {}
            sensor_config = {}
            ads1115_config = {}
            mpu9250_config = {}
            gy530_config = {}
            kashiyama_config = {}
            PLC_config={}
            IO_sample_config={}
            segmentation_config = {}
            extraction_config = {}
            connection_config = {}
            polling_device_config={}
    
            get_config(config_file)
            #sync time
            os.system('sudo ntpdate ' + connection_config['ftp_ip'])
            print('NTP update ',datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
            idle_minutes = float(setting_config.get('idle_minutes', 1)) * 60
            sensor_upload_samp = int(sensor_config['upload_per_data'])

            sensor_upload_cnt = sensor_upload_samp
            segmentation_upload_samp = int(segmentation_config['upload_per_data'])
            segmentation_upload_cnt = segmentation_upload_samp
            run_connection = int(connection_config['run_connection'])
            
            if(run_connection):
                #print('Upload Raspberry Log...')
                Connection.processing('Log', setting_config, connection_config, {})
    
            time.sleep(3)  ##待釋放資源
            print('Start --->', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), time.perf_counter())
            
            '''
            if(run_connection):
                print('Upload Raspberry Log...')
                Connection.processing('Log', setting_config, connection_config, {})
            '''
            
            '''
            for csv_file in glob.glob('/home/pi/PHM_v3/Data/Sensor/*.csv'):
                print(csv_file)
                
                data_name = os.path.basename(csv_file)[:-4]
                sensor_data = pd.read_csv(csv_file)
                signal_dic[data_name] = sensor_data
            '''
        
            #while True:
            #======Sensor Signal======
            signal_dic = {}
            #print('Start --->', time.ctime())
            #print('Get Sensor Signal...')
            signal_dic = Sensor.processing(setting_config, 
                                           sensor_config, 
                                           ads1115_config, 
                                           mpu9250_config, 
                                           gy530_config, 
                                           kashiyama_config,
                                           PLC_config,
                                           IO_sample_config,
                                           polling_device_config)
            
            segmentation_dic = {}
            if len(signal_dic) > 0:
                #======Segmentation Upload======
                sensor_upload_cnt += 1
                if sensor_upload_cnt >= sensor_upload_samp and sensor_upload_samp != 0:
                    sensor_upload_cnt = 0
                    #同步上傳segmentation
                    segmentation_upload_cnt = segmentation_upload_samp
                    
                    if(run_connection):
                        #print('Upload Sensor Signal...')
                        Connection.processing('Sensor', setting_config, connection_config, signal_dic)
                
                #======Segmentation======
                print('Segmentation...', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                segmentation_dic = Segmentation.processing(segmentation_config, signal_dic)
                gc.collect()
                
            extraction_dic = {}
            if len(segmentation_dic) > 0:
                #======Segmentation Upload======
                segmentation_upload_cnt += 1
                if segmentation_upload_cnt >= segmentation_upload_samp and segmentation_upload_samp != 0:
                    segmentation_upload_cnt = 0
                    
                    if(run_connection):
                        print('Upload Segmentation...', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        Connection.processing('Segmentation', setting_config, connection_config, segmentation_dic)
    
                #======Feature Extraction======
                print('Extraction...', time.ctime())
                extraction_dic = Extraction.processing(extraction_config, segmentation_dic)
    
                if len(extraction_dic) > 0:
                    
                    if(run_connection):
                        print('Upload Extraction...', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        Connection.processing('Extraction', setting_config, connection_config, extraction_dic)
            #columns=['datetime','Loopidx', 'sesnor','sampling_rate','record_second','sensor_list','segCount','featureCount'])
            cols =''
            realSf=0
            for key in signal_dic.keys():
                cols = signal_dic[key].columns
                sf=int(key.split("_")[-1].replace(".csv",""))
                realSf+=sf
            if len(signal_dic)>0:
                realSf=round(realSf/len(signal_dic),2)
            colStr = ",".join(cols[1:])
                
            wifiInfo=wifi.getInfo()   
            wifiName="--"
            wifiQuality="--"
            wifiStrength="--"
            wifiMac=wifi.get_wifi_mac()
            apMac=wifi.get_ap_mac()
            ipAddress=wifi.get_wifi_ip()
            if wifiInfo != None and wifiInfo["Name"]!='':
                wifiName=wifiInfo["Name"]
                wifiQuality=wifiInfo["Quality"]
                wifiStrength=wifiInfo["Signal"]
                
            info = psutil.virtual_memory()
            memory_using = info.percent
            diskinfo = psutil.disk_usage("/")
            disk_used=round(diskinfo.used/(1024*1024*1024),3)
            disk_free=round(diskinfo.free/(1024*1024*1024),3)
            ver=__version__.split("_")[0]
            device_infor=psutil.sensors_temperatures()
            cpu_temp="--"
            if("cpu-thermal" in device_infor.keys()):
                cpu_temp = device_infor["cpu-thermal"][0].current
            if("cpu_thermal" in device_infor.keys()):
                cpu_temp = device_infor["cpu_thermal"][0].current
            
            segmentation_len=0
            for key in segmentation_dic.keys():
                segmentation_len+=len(segmentation_dic[key])
            
            datetimeStr=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_Log= pd.DataFrame([[datetimeStr,
                                    ver,
                                    run_loop,
                                    len(signal_dic),
                                    realSf,
                                    sensor_config['record_second'], 
                                    colStr,
                                    segmentation_len,
                                    len(extraction_dic),
                                    memory_using,
                                    cpu_temp,
                                    disk_used,
                                    disk_free,
                                    wifiName,
                                    wifiQuality,
                                    wifiStrength,
                                    ipAddress]],
                    columns=['datetime',
                             'version',
                             'Loopidx',
                             'sensor',
                             'real_sampling_rate',
                             'record_second',
                             'sensor_list',
                             'segCount',
                             'featureCount',
                             'memory_using',
                             'cpu_temp',
                             'disk_used_G',
                             'disk_free_G',
                             'wifi_name',
                             'wifi_quality',
                             'wifi_stregth',
                             'ip_address'])
            
            iot.iot_api(__version__,
                setting_config['eqp_name']+setting_config['chamber'],
                run_loop,
                realSf,
                sensor_config['record_second'],
                colStr,
                segmentation_len,
                len(extraction_dic))
            
            if ( pd_Log.empty ): 
                print('empty, new_log shape=', new_Log.shape)
                pd_Log = new_Log
            else :
                pd_Log = pd.concat([pd_Log,new_Log], axis=0)            
            saveRunLog(run_loop, pd_Log,setting_config, connection_config,pd_log_name)
            print(run_loop, ' Endt --->', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))         
            
        time.sleep(idle_minutes)
