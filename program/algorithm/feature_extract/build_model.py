import numpy as np
from algorithm.feature_extract import feature_lib
from scipy.stats import skew, kurtosis
import traceback
import pandas as pd


# Entropy , Quantile_5 , Quantile_25 , Quantile_50 , Quantile_75
# Quantile_95 , Mean , Std ,Var , Rms ,Skewness ,Kurtusis
class Build_psd_vel_model():
    def __init__(self):
        self.PHM_main_dict = {
            'vel_psd_rms': feature_lib.get_vel_psd_rms,
            'low_psd_rms': feature_lib.get_low_psd_rms,
            'mid_psd_rms': feature_lib.get_mid_psd_rms,
            'high_psd_rms': feature_lib.get_high_psd_rms,
        }
    def run(self, parm):
        self.parm = parm

        try:
            # spectrum = self.parm["Setting"]
            return self._run_spectrum()

        except Exception as e:
            print(traceback.print_exc())
            print("PHM_main_dict fail", e)
            raise
    def _run_spectrum(self):
        feature_type = self.parm["Setting"]["Feature"]
        df_psd = self.parm['RawData']['df_psd']  # self.data
        psd_rms = self.parm['RawData']['psd_rms']
        bin_width = self.parm['Setting']['bin_width']
        if 'vel_psd_rms' in feature_type:
            val = self.PHM_main_dict[feature_type](df_psd, bin_width)
        else:
            base_freq = self.parm["Setting"]["base_freq"]
            fs = self.parm["Setting"]["fs"]
            val = self.PHM_main_dict[feature_type](psd_rms, base_freq, fs, bin_width)
        return val
        
    
    
    
class Build_model():
    def __init__(self):
        self.PHM_main_dict = {
            'Entropy': feature_lib.get_entropy,
            'Quantile_5': feature_lib.get_quantile,
            'Quantile_25': feature_lib.get_quantile,
            'Quantile_50': feature_lib.get_quantile,
            'Quantile_75': feature_lib.get_quantile,
            'Quantile_95': feature_lib.get_quantile,
            'Mean': np.mean,
            'Std': np.std,
            'Var': np.var,
            'Rms': feature_lib.get_rms,
            'Skewness': skew,
            'Kurtosis': kurtosis,
            'Max': np.max,
            'Min': np.min,
            'Max_Min': feature_lib.get_p2p,
            'Crest': feature_lib.get_crest,
            'Clearance': feature_lib.get_clearance,
            'Shape': feature_lib.get_shape,
            'Impulse': feature_lib.get_impulse,
        }

    def run(self, parm):
        self.parm = parm

        try:
            # spectrum = self.parm["Setting"]
            return self._run_spectrum()

        except Exception as e:
            print(traceback.print_exc())
            print("PHM_main_dict fail", e)
            raise

    def _run_spectrum(self):
        feature_type = self.parm["Setting"]["Feature"]
        data = self.parm['RawData']  # self.data

        if 'Quantile' in feature_type:
            bin = feature_type.split('_')[1]
            bin_num = int(bin)
            val = self.PHM_main_dict[feature_type](data, bin=bin_num)
        else:
            val = self.PHM_main_dict[feature_type](data)
        # print('Result:')
        # print(val)

        # par_list = transform_key[spectrum_list]
        return val


# Unit Test
if __name__ == '__main__':
    df = pd.read_csv('../test_data/1104_Segmentation/ABIEXJ00IF/ABIEXJ00IF_RR_20191104_015842_1658_2')
    ct_val = df['CT1'].values

    param = {
        "RawData": [1, 2, 3, 4, 5],
        "Setting": {
            "SensorType": "vibr",
            "Spectrum": "fft",
            "Feature": "Quantile_25"  # ""
        }
    }
    param['RawData'] = ct_val

    bm = Build_model()
    result = bm.run(parm=param)
    print(result)
