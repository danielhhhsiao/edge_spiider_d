import time

import os

import glob

import pandas as pd

import configparser

import shutil

#

import matplotlib.pyplot as plt

from scipy.signal import spectrogram, find_peaks

import numpy as np

 

def short_time_fourier_transform(X, fs, nperseg, noverlap):

    X = X.values.ravel() # ravel將資料格式從1D陣列(n,1)轉換成扁平陣列(n,)

    f, t, Sx = spectrogram(X, fs=fs, window = 'hamming', nperseg=nperseg, noverlap = noverlap) # 短時距傅立葉轉換

    return f, t, np.abs(Sx)

 

def seg_using_STFT_freq(signal, fs, distance, height, sig_threshold, time_range, sx_energy_threshold, certain_freq):

    nperseg = int(fs//5)

    noverlap = nperseg-1

    f, t, Sx = short_time_fourier_transform(signal, fs, nperseg, noverlap)

    Sx[np.isnan(Sx)] = 0

    Sx[Sx<=np.mean(Sx)] = 0

    f_max_idx = np.argmax(Sx, axis = 0)

    f_max = f[f_max_idx]

    f_max = np.append([0],f_max) # prevent find peak error

    f_max = np.append(f_max,[0]) # prevent find peak error

    peak_idx = find_peaks(f_max, distance = distance, height = height)[0]

    peak_idx = peak_idx-1

    f_peaks = f_max[peak_idx]

    if np.max(Sx[:, peak_idx[0]]) > sx_energy_threshold:

        if np.max(signal.abs()) > sig_threshold:

            #thres_freq = int(f_peaks[0])*thres

            f_range = pd.Series(f_max[int(max(peak_idx[0]-time_range,0)):int(min(peak_idx[0]+time_range,len(f_max)))])

            #idx = f_range[f_range > thres_freq].index

            start_idx = int(signal.index[0]+peak_idx[0] - time_range)

            stop_idx = int(signal.index[0]+peak_idx[0] + time_range)

            if certain_freq == 0 or int(f_peaks[0])==certain_freq:

                return [start_idx,stop_idx],int(f_peaks[0]),f_range

            else:

                return None,int(f_peaks[0]),f_range

    return None,int(f_peaks[0]),None

 

def stft_segmentation_logic(config_dic, data_dic, log_path):

    segmentation_dic = {}

    save_plt = int(config_dic['save_plt'])

    basis_column = config_dic['basis_column']

    operation_reverse = int(config_dic['operation_reverse'])

    operation_threshold = float(config_dic['operation_threshold'])

   

    height = 4 #float(config_dic['height'])

    padding = float(config_dic['padding'])

    sig_threshold = 1.5 #float(config_dic['sig_threshold'])

    sx_energy_threshold = 0.01 #float(config_dic['sx_energy_threshold'])

    certain_freq = int(config_dic['certain_freq'])

   

    for data_key, data_value in data_dic.items():

        print(data_key)

        fs = int(data_key.split("_")[-1].split(".")[0])

       

        operation_count = float(config_dic['operation_count']) * fs

        sub_operation_count = float(config_dic['sub_operation_count']) * fs

        operation_half = int(operation_count / 2)

        operation_quarter = int(operation_count / 4)

        operation_filter = float(config_dic['operation_filter']) * fs

        operation_shift = float(config_dic['operation_shift']) * fs

       

        if operation_filter == 0:

            operation_filter = operation_count

           

        if sub_operation_count == 0:

            sub_operation_count = operation_filter

           

        time_range = int(sub_operation_count / 2)

           

        final_operation_half = int(sub_operation_count / 2)

       

        temp_dic = {}

       

        #data_pd = data_value[100:1000]

        data_pd = data_value

        data_pd_s = data_pd.index[0]

        data_pd_e = data_pd.index[-1]

       

        if not basis_column in data_pd:

            print('Not Found basis_column "',basis_column,'"')

            continue

       

        #mode

        mode = data_pd[basis_column].mode()[0]

        #abs

        data_abs = (data_pd[basis_column] - mode).abs()

        #rolling

        #data_rolling = data_abs.rolling(operation_half).mean() * 1000

        data_rolling = data_abs.rolling(operation_half).sum()  # v2

       

        #reverse

        if operation_reverse:

            data_rolling = (data_rolling * (-1)) + (operation_threshold * 2)

       

        #cut_threshold

        cut_threshold = data_rolling.iloc[:] >= operation_threshold

       

        #平移相減

        sf = [0] * (data_pd_s + 1)

        sf[data_pd_s + 1:] = cut_threshold

        cut_shift = pd.Series(sf[:-data_pd_s - 1])

        cut_index = (cut_threshold - cut_shift)

        cut_index = cut_index[cut_index != 0].dropna()

       

        if save_plt:

            fig, (plt1, plt2, plt3, plt4) = plt.subplots(4,1,figsize=(16,15))

           

            plt1.set_title("Original")

            plt1.set_xlim(data_pd_s, data_pd_e)

            plt1.plot(data_pd[basis_column])

   

            plt2.set_title("Rolling")

            plt2.set_xlim(data_pd_s, data_pd_e)

            plt2.plot(data_rolling)

           

            if operation_threshold > 0:

                plt2.axhline(operation_threshold, color='r')

           

            plt3.set_title("Frequency")

            plt3.set_xlim(data_pd_s, data_pd_e)

            plt3.plot(data_pd[basis_column])

            plt3f = plt3.twinx()

            plt3f.plot(0)

           

            #佔用藍色

            plt4.set_title("Overlap")

            plt4.plot(0)       

        

        

        #取擷取中心點

        ind_o = 0

        cut_s = 0

        cut_ary = []

        filter_cnt = 0

       

        for ind,value in cut_index.items():

            if ind_o == 0 or (ind - ind_o) > 10:

                if value == 1:

                    cut_s = ind

                else:

                    if cut_s > operation_half:

                        #排除突波

                        cut_len = ind - cut_s

                        if cut_len > operation_quarter:

                            if operation_filter != operation_count:

                                if cut_len < (operation_filter-padding*fs) or cut_len > (operation_filter+padding*fs):

                                    continue

                               

                            filter_cnt += 1

                            print('cut_len_',filter_cnt,':',cut_len)

                            cut_ary.append(int(cut_s) + operation_shift)

                               

                            if save_plt:

                                #Rolling

                                plt2.plot(data_rolling[cut_s:ind], label=str(filter_cnt)+'_len:{}'.format(cut_len))

                                plt2.legend(loc='upper right')

       

            ind_o = ind

           

        print('cut_ary:',cut_ary)

   

        #segmentation   

        last_index = 0

        segmentation_cnt = 0

        freq_ary = []

        for index in cut_ary:

            if last_index == 0 or (last_index + operation_filter) < index:

                cut_s = index - final_operation_half

                cut_e = index + final_operation_half

           

                if cut_s >= 0 and cut_e <= len(data_pd):

                    last_index = index

                    save_data = data_pd.loc[cut_s:cut_e]

                    signal = save_data[basis_column]

                    idx,peak_freq,f_range = seg_using_STFT_freq(signal, fs, operation_count, height, sig_threshold, time_range, sx_energy_threshold, certain_freq)

                    freq_ary.append(peak_freq)

                    if idx != None:

                        if idx[0] >= 0 and idx[1] < len(data_pd):

                            save_data = data_pd.loc[idx[0]:idx[1]]

                           

                            segmentation_cnt += 1

                       

                            temp_dic[str(segmentation_cnt)] = save_data

                       

                            if save_plt:

                                #Original

                               plt1.plot(save_data[basis_column])

                                                               

                                #Overlap

                                overlap = save_data[basis_column].reset_index(drop=True)

                               

                                plt4.plot(overlap, label=str(segmentation_cnt)+'_peak_freq:{} Hz'.format(peak_freq), alpha=0.8)

                                plt4.legend(loc='upper right')

                    if save_plt and type(f_range) != type(None):

                        plt3f.plot(signal.index[0]+f_range.index,f_range, label='peak_freq:{} Hz'.format(peak_freq))

                        plt3f.legend(loc='upper right')

        print('freq_ary:',freq_ary)

        if save_plt:

            fig.tight_layout()

            plt.savefig(log_path + '/' + data_key + '.jpg')

            #plt.show()

            plt.close()

        else:

            plt.close()

   

        segmentation_dic[data_key] = temp_dic

       

    return segmentation_dic

 

def segmentation_logic(config_dic, data_dic, log_path):

    segmentation_dic = {}

    save_plt = int(config_dic['save_plt'])

    basis_column = config_dic['basis_column']

    operation_reverse = int(config_dic['operation_reverse'])

    operation_threshold = float(config_dic['operation_threshold'])

   

    for data_key, data_value in data_dic.items():

        print(data_key)

        fs = int(data_key.split("_")[-1].split(".")[0])

       

        operation_count = float(config_dic['operation_count']) * fs

        sub_operation_count = float(config_dic['sub_operation_count']) * fs

        operation_half = int(operation_count / 2)

        operation_quarter = int(operation_count / 4)

        operation_filter = float(config_dic['operation_filter']) * fs

        operation_shift = float(config_dic['operation_shift']) * fs

       

        if operation_filter == 0:

            operation_filter = operation_count

           

        if sub_operation_count == 0:

            sub_operation_count = operation_filter

           

        final_operation_half = int(sub_operation_count / 2)

       

        temp_dic = {}

       

        #data_pd = data_value[100:1000]

        data_pd = data_value

        data_pd_s = data_pd.index[0]

        data_pd_e = data_pd.index[-1]

       

        if not basis_column in data_pd:

            print('Not Found basis_column "',basis_column,'"')

            continue

       

        #mode

        mode = data_pd[basis_column].mode()[0]

        #abs

        data_abs = (data_pd[basis_column] - mode).abs()

        #rolling

        #data_rolling = data_abs.rolling(operation_half).mean() * 1000

        data_rolling = data_abs.rolling(operation_half).sum()  # v2

       

        #reverse

        if operation_reverse:

            data_rolling = (data_rolling * (-1)) + (operation_threshold * 2)

       

        #cut_threshold

        cut_threshold = data_rolling.iloc[:] >= operation_threshold

       

        #平移相減

        sf = [0] * (data_pd_s + 1)

        sf[data_pd_s + 1:] = cut_threshold

        cut_shift = pd.Series(sf[:-data_pd_s - 1])

        cut_index = (cut_threshold - cut_shift)

        cut_index = cut_index[cut_index != 0].dropna()

       

        if save_plt:

            fig, (plt1, plt2, plt3) = plt.subplots(3,1,figsize=(16,15))

           

            plt1.set_title("Original")

            plt1.set_xlim(data_pd_s, data_pd_e)

            plt1.plot(data_pd[basis_column])

   

            plt2.set_title("Rolling")

            plt2.set_xlim(data_pd_s, data_pd_e)

            plt2.plot(data_rolling)

           

            if operation_threshold > 0:

                plt2.axhline(operation_threshold, color='r')

       

            #佔用藍色

            plt3.set_title("Overlap")

            plt3.plot(0)       

        

        

        #取擷取中心點

        ind_o = 0

        cut_s = 0

        cut_ary = []

        filter_cnt = 0

       

        for ind,value in cut_index.items():

            if ind_o == 0 or (ind - ind_o) > 10:

                if value == 1:

                    cut_s = ind

                else:

                    if cut_s > operation_half:

                        #排除突波

                        cut_len = ind - cut_s

                        if cut_len > operation_quarter:

                            if operation_filter != operation_count:

                                if cut_len < (operation_filter * 0.95) or cut_len > (operation_filter * 1.05):

                                    continue

                                

                            filter_cnt += 1

                            print('cut_len_',filter_cnt,':',cut_len)

                            cut_ary.append(int(cut_s) + operation_shift)

                               

                            if save_plt:

                                #Rolling

                                plt2.plot(data_rolling[cut_s:ind], label=filter_cnt)

                                plt2.legend(loc='upper right')

       

            ind_o = ind

           

        print('cut_ary:',cut_ary)

   

        #segmentation   

        last_index = 0

        segmentation_cnt = 0

       

        for index in cut_ary:

            if last_index == 0 or (last_index + operation_filter) < index:

                cut_s = index - final_operation_half

                cut_e = index + final_operation_half

           

                if cut_s >= 0 and cut_e <= len(data_pd):

                    last_index = index

                   

                    save_data = data_pd.loc[cut_s:cut_e]

                    segmentation_cnt += 1

               

                    temp_dic[str(segmentation_cnt)] = save_data

               

                    if save_plt:

                        #Original

                        plt1.plot(save_data[basis_column])

               

                        #Overlap

                        overlap = save_data[basis_column].reset_index(drop=True)

                       

                        plt3.plot(overlap, label=segmentation_cnt, alpha=0.8)

                        plt3.legend(loc='upper right')

   

        if save_plt:

            plt.savefig(log_path + '/' + data_key + '.jpg')

            plt.close()

   

        segmentation_dic[data_key] = temp_dic

       

    return segmentation_dic

 

   

'''

def closet(list, num):

    aux = []

    for value in list:

        aux.append(abs(num-value))

       

    return aux.index(min(aux))

'''

 

def processing(config_dic, data_dic):

    segmentation_dic = {}

    log_path = phm_func.data_path + '/Segmentation'

   

    try:

    #if True:

        save_data = int(config_dic['save_data'])

        segmentation_type = int(config_dic['segmentation_type'])

       

        

        if(segmentation_type == 1):

            for data_key in data_dic:

                fs = int(data_key.split("_")[-1].split(".")[0])

                operation_count = float(config_dic['operation_count']) * fs

                temp_data = data_dic[data_key]

                temp_cnt = 0

                temp_dic = {}

               

                while len(temp_data) > operation_count:

                    temp_cnt += 1

                    temp_dic[str(temp_cnt)] = temp_data[:operation_count]

                    temp_data = temp_data[operation_count:]

                   

                segmentation_dic[data_key] = temp_dic

               

        elif(segmentation_type == 2):

            segmentation_dic = segmentation_logic(config_dic, data_dic, log_path)

        elif(segmentation_type == 3):

            segmentation_dic = stft_segmentation_logic(config_dic, data_dic, log_path)

        else:

            return segmentation_dic

 

       

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

           

            if not os.path.exists(log_path):

                os.mkdir(log_path)

       

            for data_key in segmentation_dic:

                for count_key in segmentation_dic[data_key]:

                    segmentation_dic[data_key][count_key].to_csv(log_path + '/' + data_key + '_' + count_key + '.csv', index=False)

   

    except Exception as e:

        print('Segmentation error:', e)

    

    return segmentation_dic

 

if __name__ == "__main__":

    import phm_func

    self_file_path=os.path.realpath(__file__)

    self_path=os.path.dirname(self_file_path)

    home_path='/'.join(self_path.split('/')[:-1])

    print('Start --->', time.ctime())

    for config_path in sorted(glob.glob(home_path+'/config*.ini')):

        print('config path --->', config_path)

        config_name=config_path.split("/")[-1][:-4]

        phm_func.check_directory_of_phm_data(config_path)

       

        sensor_dic = {}

        segmentation_config = {}

       

        config = configparser.ConfigParser()

        config.read(config_path)

       

        #segmentation

        items = config.items('segmentation')

        for item in items:

            segmentation_config[item[0]] = item[1]

           

        

        for csv_file in glob.glob(phm_func.data_path + '/Sensor/*csv'):

            print(csv_file)

           

            data_name = os.path.basename(csv_file)[:-4]

            sensor_data = pd.read_csv(csv_file)

            sensor_dic[data_name] = sensor_data

   

        print('Segmentation: ',segmentation_config)

        segmentation_dic = processing(segmentation_config, sensor_dic)

        for key in segmentation_dic.keys():

            for index in segmentation_dic[key]:

                csv_name=phm_func.data_path + '/Segmentation/'+config_name+'_'+key+'_'+index+'.csv'

                segmentation_dic[key][index].to_csv(csv_name)

                print("output:",csv_name)

   

    print('Endt --->', time.ctime())

else:

    import Library.phm_func as phm_func
