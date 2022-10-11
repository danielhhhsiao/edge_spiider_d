import time
import os
import glob
import numpy as np
import pandas as pd
import configparser
import shutil
from scipy import stats
from math import sqrt
import Library.phm_func as phm_func
from scipy.fftpack import fft,ifft
#import FeatureExtractionMain as FeatureExtraction
from service.feature_engineer_service import get_feature_engineer

import pywt

def extraction_logic(config_dic, data_dic):
    extraction_dic = {}
    col_ary = config_dic['column'].split(',')
    use_pi_default_feature = config_dic.get('use_pi_default_feature', '0')  # add 2020/06/05
    project_id_list = config_dic.get('project_id',0).split(',')
    try :
        project_id_ary = []
        for id in project_id_list :
            project_id_ary.append(int(id))
    except :
        project_id_ary = [0]
    #project_id = int(config_dic.get('project_id',0))
    #if ((Prj_id) > 1) :
    #    project_id = int(sPrj_id, 0)
    #else:
    #    project_id = 0
    #print('extractuion, prj ID=',project_id_list, ',', project_id_ary)
    #return
    #print(col_ary)
    for prj_id in project_id_ary :
        
        for data_key in data_dic:
            #print('data_key=', data_key)        
            temp_df = pd.DataFrame()
            
            for count_key in data_dic[data_key]:
                #col_df = pd.DataFrame()
                oneSeg_df = pd.DataFrame()
                df_column = []
                df_value = []

            #
            
                #if not col in data_dic[data_key][count_key]:
                #    print('Not Found column "',col,'"')
                #    continue
                
                #data = data_dic[data_key][count_key][col]
                df_data = data_dic[data_key][count_key]
                #df_data=pd.DataFrame(data, columns=col_ary)
                #print('ID=',project_id)
                
                # IF PROJECT_ID >0 , use project_id setting
                #print('<--->')  
                #print('data_key=',data_key,'count_key=', count_key,'col_ary=', col_ary)
                #startTime = data_dic[data_key][count_key]['datetime'][0]
                #startTime = data_dic[data_key][count_key].iloc(0,0)
                #print('StartTime=',  startTime)
                startTime1 = df_data['datetime'].iloc[0]
                #startTime1 = data_dic[data_key][count_key]
                #print('StartTime1=',  startTime1)
                time_df = pd.DataFrame([startTime1], columns=['datetime'])
                if ( (prj_id > 0) and (use_pi_default_feature == '0') ) :
                    NewDataKey = "{}@{}@{}@{}".format(data_key.split('@')[0],data_key.split('@')[1], str(prj_id) , data_key.split('@')[-1])
                    #data_dic[NewDataKey] = data_dic.pop(data_key)
                    print('Feature extraction by project id',prj_id , ' , key=',NewDataKey)
                    
                    oneSeg_df =get_feature_engineer(prj_id, df_data)
                    #print('oneSeg_df=', oneSeg_df.info())
                    oneSeg_df = pd.concat([time_df,oneSeg_df],axis=1)
                else :
                    
                    for col in col_ary:
                        #print('col=',col)
                        data = data_dic[data_key][count_key][col]
                        #print('Data Len=',len(data))
                        stat_mean = np.mean(data)
                        
                        stat_var = data.var(axis=0) #sqrt(sum(((n - stat_mean)**2) for n in data)) / len(data)
                        #stat_std = data.std()
                        stat_max = np.max(data)
                        stat_min = np.min(data)
                        stat_p2p = stat_max - stat_min
                        stat_rms = sqrt(sum(n*n for n in data) / len(data))
                        #stat_kurto = (stat_mean ** 4) / (stat_var ** 4)
                        #stat_kurto = (stat_mean ** 4) / (stat_std ** 4)
                        stat_kurto = data.kurtosis(axis=0)
                        stat_skewness = data.skew(axis=0)
                        
                        datavalue_counts = data.value_counts()
                        stat_entropy = stats.entropy(datavalue_counts)
            
                        wavelet_energy = calc_wavelet_packet_energy(data)  
                        
                        df_column.append(col + '_mean')
                        df_value.append(stat_mean)
                        df_column.append(col + '_variance')
                        df_value.append(stat_var)
                        df_column.append(col + '_max')
                        df_value.append(stat_max)
                        df_column.append(col + '_min')
                        df_value.append(stat_min)
                        df_column.append(col + '_p2p')
                        df_value.append(stat_p2p)
                        df_column.append(col + '_rms')
                        df_value.append(stat_rms)
                        df_column.append(col + '_kurtosis')
                        df_value.append(stat_kurto)
                        df_column.append(col + '_skewness')
                        df_value.append(stat_skewness)
                        df_column.append(col + '_entropy')
                        df_value.append(stat_entropy)
        
                        for wavelet_key, wavelet_value in wavelet_energy.items():
                            df_column.append(col + '_wavelet_' + wavelet_key)
                            df_value.append(wavelet_value)
                        
                                              
                    oneSeg_df = pd.DataFrame([df_value], columns=df_column)
                    oneSeg_df = pd.concat([time_df,oneSeg_df],axis=1)
                if temp_df.empty:   
                    #print('empty -->')                     
                    temp_df = oneSeg_df
                    #temp_df = col_df
                else:
                    temp_df = pd.concat([temp_df,oneSeg_df])
            
            if ( prj_id > 0 ) :
                NewDataKey = "{}@{}@{}@{}".format(data_key.split('@')[0],data_key.split('@')[1], str(prj_id) , data_key.split('@')[-1])
                #data_dic[NewDataKey] = data_dic.pop(data_key)
                    
            if not temp_df.empty:
                if ( prj_id > 0 ) :
                    #print('NewDataKey= ',NewDataKey,' ,prj_id=', prj_id)
                    extraction_dic[NewDataKey] = temp_df
                else :
                    extraction_dic[data_key] = temp_df
        #print(temp_df)
    return extraction_dic

def calc_wavelet_packet_energy(x):
    wp = pywt.WaveletPacket(data=x, wavelet='db1', mode='symmetric', maxlevel=5)
       
    energy = {}
    energy['aaaaa'] = np.sum(wp['aaaaa'].data ** 2) / len(wp['aaaaa'].data)
    energy['aaaad'] = np.sum(wp['aaaad'].data ** 2) / len(wp['aaaad'].data)
    energy['aaad'] = np.sum(wp['aaad'].data ** 2) / len(wp['aaad'].data)
    energy['aad'] = np.sum(wp['aad'].data ** 2) / len(wp['aad'].data)
    energy['ad'] = np.sum(wp['ad'].data ** 2) / len(wp['ad'].data)
    energy['d'] = np.sum(wp['d'].data ** 2) / len(wp['d'].data)
        
    return energy

def processing(config_dic, data_dic):
    extraction_dic = {}
    log_path = phm_func.data_path + '/Extraction'
    #print('logpath=', log_path)
    
    try:
        save_data = int(config_dic.get('save_data'), 0)                
        #print('logpath=', log_path)
        extraction_dic = extraction_logic(config_dic, data_dic)
        
        
        #save data
        if save_data:
            #free memory 500MB
            if shutil.disk_usage('/').free//(2**20) < 500:
                files = glob.glob(log_path + '/*.csv')
                files.sort(key=os.path.getmtime)
                
                for csv_file in files:
                    os.remove(csv_file)
                    
                    if shutil.disk_usage('/').free//(2**20) > 500:
                        break
            
            #if not os.path.exists(log_path):
            #    os.mkdir(log_path)
        
            for data_key in extraction_dic:
                extraction_dic[data_key].to_csv(log_path + '/' + data_key + '.csv', index=False)
                
    except Exception as e:
        print('Extraction error :', e)
    
    return extraction_dic

if __name__ == "__main__":
    import phm_func as phm_func
    
    phm_func.check_directory_of_phm_data()
    config_path = "../config.ini"
    phm_func.data_path = '../../Data'
    segmentation_dic = {}
    extraction_config = {}
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    #extraction
    items = config.items('extraction')
    for item in items:
        extraction_config[item[0]] = item[1]
        
    print('Start --->', time.ctime())
    
    for csv_file in glob.glob(phm_func.data_path + '/Segmentation/*.csv'):
        print(csv_file)
        temp_dic = {}
        
        file_name = os.path.basename(csv_file)
        ind = file_name.rindex('_')
        
        data_name = file_name[:ind]
        count_name = file_name[ind+1:-4]
        
        temp_df = pd.read_csv(csv_file)
        
        temp_dic[count_name] = temp_df
        
        if data_name in segmentation_dic:
            segmentation_dic[data_name].update(temp_dic)
        else:
            segmentation_dic[data_name] = temp_dic


    print('Extraction: ',extraction_config)
    #print('ID=',extraction_config['project_id'])
    extraction_dic = processing(extraction_config, segmentation_dic)
    
    print('Endt --->', time.ctime())
