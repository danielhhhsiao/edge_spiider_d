import traceback
from algorithm.frequency_transform.transform_lib import get_fft_values, get_psd_values, get_autocorr_values, \
    get_wavelet_packet_energy_3_level, get_wavedec, get_time_domain_values, get_iso, get_psd_vel_values, get_base_frequency_values
#20220825 Danielhhhsiao
#20230210 ErwinJSLiang(add Model-based feature)
import pandas as pd


class Build_model():
    "PHM model start of function"

    def __init__(self):
        self.PHM_main_dict = {'FFT': get_fft_values,
                              'PSD': get_psd_values,
                              'AUTOCORR': get_autocorr_values,
                              'WP': get_wavelet_packet_energy_3_level,
                              'DWT': get_wavedec,
                              'Time_Domain': get_time_domain_values, 
                              'ISO': get_iso, #20230210 ErwinJSLiang(copy from PHM Platform code)
                              'VibVelocity': get_psd_vel_values, #20220825 Danielhhhsiao
                              'DefectFrequency': get_base_frequency_values} #20230210 ErwinJSLiang(copy from PHM Platform code)

        self.transform_key = {"FFT": ["samplerate"],
                              "PSD": ["samplerate"],
                              "autocorr": [],
                              "WP": ["level"],
                              "DWT": ["level"],
                              "Time_Domain": [],
                              "ISO": ["samplerate"], #20230210 ErwinJSLiang(copy from PHM Platform code)
                              "VibVelocity": ["samplerate", "base_freq"], #20220825 Danielhhhsiao
                              "DefectFrequency": ["samplerate", "base_freq", "max_base_freq"]} #20230210 ErwinJSLiang(copy from PHM Platform code)

    def run(self, data, parm):
        self.parm = parm
        self.data = data
        try:
            # for i in self.parm["Setting"]:
            #     spectrum_list=i["Spectrum"]
            #     #  level , samplerate
            #     self._run_each_spectrum(spectrum_list)

            spectrum = self.parm["Setting"]["Spectrum"]
            #20230210 ErwinJSLiang(copy from PHM Platform code)
            if spectrum["type"] == 'VibVelocity':
                return self._run_PSD_spectrum(spectrum)
            #20230210 ErwinJSLiang(copy from PHM Platform code)
            elif spectrum["type"] == 'DefectFrequency':
                return self._run_base_frequency_spectrum(spectrum)
            else:
                return self._run_spectrum(spectrum)

            # return self.PHM_main_dict[self.param['mode_type']](data,param)

        except Exception as e:
            print(traceback.print_exc())
            print("PHM_main_dict fail", e)
            raise
        
    def _run_spectrum(self, spectrum):
        spectrum_type = spectrum["type"]
        parm_list = self.transform_key[spectrum_type]

        # 製作Param Object
        parm_obj = {}
        parm_obj['data'] = self.data

        for i in parm_list:
            parm_obj[i] = spectrum[i]
        # aaa=[spectrum[i] for i in parm_list]
        x_val, y_val = self.PHM_main_dict[spectrum_type](parm_obj)
        # print('Result:')
        # print(x_val)

        # par_list = transform_key[spectrum_list]
        return x_val, y_val
    
    #20230210 ErwinJSLiang(copy from PHM Platform code)
    def _run_PSD_spectrum(self, spectrum):
        spectrum_type = spectrum["type"]
        parm_list = self.transform_key[spectrum_type]

        # 製作Param Object
        parm_obj = {}
        parm_obj['data'] = self.data

        for i in parm_list:
            parm_obj[i] = spectrum[i]
        # aaa=[spectrum[i] for i in parm_list]
        x_val, y_val, z_val = self.PHM_main_dict[spectrum_type](parm_obj)
        # print('Result:')
        # print(x_val)

        # par_list = transform_key[spectrum_list]
        return x_val, y_val, z_val

    #20230210 ErwinJSLiang(copy from PHM Platform code)
    def _run_base_frequency_spectrum(self, spectrum):
        spectrum_type = spectrum["type"]
        parm_list = self.transform_key[spectrum_type]

        # 製作Param Object
        parm_obj = {}
        parm_obj['data'] = self.data

        for i in parm_list:
            parm_obj[i] = spectrum[i]
        # aaa=[spectrum[i] for i in parm_list]
        x_val, y_val, z_val = self.PHM_main_dict[spectrum_type](parm_obj)
        # print('Result:')
        # print(x_val)

        # par_list = transform_key[spectrum_list]
        return x_val, y_val, z_val


if __name__ == '__main__':
    df = pd.read_csv('../test_data/1104_Segmentation/ABIEXJ00IF/ABIEXJ00IF_RR_20191104_015842_1658_2')
    ct_val = df['CT1'].values
    param = {
        "RawData": [1, 2, 3, 4, 5],
        "Setting": {
            "SensorType": "vibr",
            "Spectrum": {"type": "wavedec", "level": 5}
        }
    }
    param['RawData'] = ct_val
    print(ct_val)

    bm = Build_model()
    result = bm.run(data=ct_val, parm=param)
    print(result)
