import numpy as np
from collections import Counter
from scipy.stats import entropy
# from scipy.stats import kurtosis
from . import detect_peaks


# Entropy , Quantile_5 , Quantile_25 , Quantile_50 , Quantile_75
# Quantile_95 , Mean , Std ,Var , Rms ,Skewness ,Kurtusis

# def calculate_statistics(list_values):
#     n5 = np.nanpercentile(list_values, 5)
#     n25 = np.nanpercentile(list_values, 25)
#     n75 = np.nanpercentile(list_values, 75)
#     n95 = np.nanpercentile(list_values, 95)
#     median = np.nanpercentile(list_values, 50)
#     mean = np.nanmean(list_values)
#     std = np.nanstd(list_values)
#     var = np.nanvar(list_values)
#     rms = np.nanmean(np.sqrt(list_values ** 2))
#     return [n5, n25, n75, n95, median, mean, std, var, rms]

def get_rms(list_values):
    return np.sqrt(np.mean(np.array(list_values) ** 2))


def get_quantile(list_values, bin):
    # df = pd.read_csv('../test_data/1104_Segmentation/ABIEXJ00IF/ABIEXJ00IF_RR_20191104_015842_1658_2')
    # ct_val = df['CT1'].values
    result = np.nanpercentile(list_values, bin)
    return result


# def calculate_crossings(list_values):
#     zero_crossing_indices = np.nonzero(np.diff(np.array(list_values) > 0))[0]
#     no_zero_crossings = len(zero_crossing_indices)
#     mean_crossing_indices = np.nonzero(np.diff(np.array(list_values) > np.nanmean(list_values)))[0]
#     no_mean_crossings = len(mean_crossing_indices)
#     return [no_zero_crossings, no_mean_crossings]

def get_entropy(list_values):
    counter_values = Counter(list_values).most_common()
    probabilities = [elem[1] / len(list_values) for elem in counter_values]
    entr = entropy(probabilities)
    return entr


def get_first_n_peaks(x, y, no_peaks=5):
    x_, y_ = list(x), list(y)

    if len(x_) >= no_peaks:
        return x_[:no_peaks], y_[:no_peaks]
    else:
        missing_no_peaks = no_peaks - len(x_)
        return x_ + [0] * missing_no_peaks, y_ + [0] * missing_no_peaks


def get_features(x_values, y_values, mph):
    indices_peaks = detect_peaks(y_values, mph=mph)
    peaks_x, peaks_y = get_first_n_peaks(x_values[indices_peaks], y_values[indices_peaks])
    return peaks_x + peaks_y


### change by GaryGWLin @MMFA

def get_p2p(list_values):
    pass
    result = max(list_values) - max(list_values)
    return result


def get_crest(list_values):
    ary_values = np.array(list_values)
    abs_max = np.abs(ary_values).max()
    len_ = len(list_values)
    result = abs_max / np.sqrt((np.sum(ary_values ** 2)) / len_)
    return result


def get_clearance(list_values):
    ary_values = np.array(list_values)
    abs_max = np.abs(ary_values).max()
    len_ = len(list_values)
    result = (abs_max) / (((np.sum(np.sqrt(np.abs(ary_values)))) / len_) ** 2)

    return result


def get_shape(list_values):
    ary_values = np.array(list_values)
    len_ = len(list_values)
    result = (np.sqrt((np.sum(ary_values ** 2)) / len_)) / ((np.sum(np.abs(ary_values))) / len_)

    return result


def get_impulse(list_values):
    ary_values = np.array(list_values)
    len_ = len(list_values)
    result = (np.abs(ary_values).max()) / ((np.sum(np.abs(ary_values))) / len_)

    return result


### change by GaryGWLin @MMFA


def get_first_n_peaks(x, y, no_peaks=5):
    x_, y_ = list(x), list(y)
    if len(x_) >= no_peaks:
        return x_[:no_peaks], y_[:no_peaks]
    else:
        missing_no_peaks = no_peaks - len(x_)
        return x_ + [0] * missing_no_peaks, y_ + [0] * missing_no_peaks


def get_features(x_values, y_values, mph):
    indices_peaks = detect_peaks(y_values, mph=mph)
    peaks_x, peaks_y = get_first_n_peaks(x_values[indices_peaks], y_values[indices_peaks])
    return peaks_x + peaks_y
#=====================================================================================================
#20220825 Danielhhhsiao
def get_vel_psd_rms(df_psd, bin_width):
    bin_width = bin_width
    df_vel_psd = df_psd.copy()
    df_vel_psd = df_vel_psd[0]/((df_vel_psd[0].index*2*np.pi)**2)
    vel_rms = df_vel_psd.values[int(10//bin_width):]*bin_width
    vel_rms = vel_rms.cumsum()**0.5
    return vel_rms[-1]*9.81*1000

def get_low_psd_rms(psd_rms, base_freq, fs, bin_width):
    lower=0
    upper=int(base_freq//bin_width)
    if lower == 0:
        result = psd_rms[upper]
    else:
        result = psd_rms[upper] - psd_rms[lower-1]
    return result
    
def get_mid_psd_rms(psd_rms, base_freq, fs, bin_width):
    lower = int(base_freq//bin_width)
    upper = int(base_freq//bin_width*5)
    result = psd_rms[upper] - psd_rms[lower-1]
    return result

def get_high_psd_rms(psd_rms, base_freq, fs, bin_width):
    lower = int(base_freq//bin_width*5)
    upper = len(psd_rms)-1
    result = psd_rms[upper] - psd_rms[lower-1]
    return result