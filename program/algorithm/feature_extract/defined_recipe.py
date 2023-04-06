import pandas as pd
import numpy as np
from scipy.signal import stft
import copy


# class Defined_recipe():
#     def __init__(self):

def run(data, fs):
    stft_value, stft_t, stft_f = get_STFT(data, 0.1, fs)
    stft_value_t = transform_STFT(stft_value)
    stft_sequence = get_STFT_sequence(stft_value_t, stft_t, stft_f)
    return get_name(stft_sequence.iloc[:, :-1])


def get_STFT(data, sec, fs):
    data = data - np.mean(data)
    f, t, Zxx = stft(data, fs=fs, nperseg=sec * fs * 2)
    return np.abs(Zxx) ** 2, t, f


def transform_STFT(values):
    values_t = copy.deepcopy(values)
    for j in range(np.shape(values)[1]):
        for i in range(np.shape(values)[0]):
            if (values[i, j] == np.max(values[:, j])) and (values[i, j] >= 0.01):
                values_t[i, j] = 1
            else:
                values_t[i, j] = 0
    return values_t


def get_STFT_sequence(stft_value_t, stft_t, stft_f):
    maxfreq = stft_f[np.argmax(stft_value_t, axis=0)]
    df = pd.DataFrame(maxfreq.reshape(1, -1), columns=np.round(stft_t, 2))
    df.columns = df.columns.astype(str)
    return df


def get_name(stft_sequence):
    sq = stft_sequence ** 2
    tt_len = stft_sequence.shape[1]

    feature_time = round(tt_len * 0.1, 1)
    feature_max = (stft_sequence.max(axis=1)).round(0)[0]
    feature_rms = ((sq.mean(axis=1)) ** 0.5).round(0)[0]
    feature_crest = ((feature_max) / ((sq.sum(axis=1) / tt_len) ** 0.5)).round(1)[0]
    feature_shape = (((sq.sum(axis=1) / tt_len) ** 0.5) / ((stft_sequence.sum(axis=1)) / tt_len)).round(1)[0]

    name = '@' + str(feature_time) + '@' + str(feature_max) + '@' + str(feature_rms) + '@' + str(
        feature_crest) + '@' + str(feature_shape)
    return name


# Unit Test
if __name__ == '__main__':
    import os

    fs = 4032
    path = r'\\Tw100104365\mmfab3\3.Project_data\9.Others\L7A\CCCGL901\Segmentation\CCCGL102_IOT_SHOCK_1\2022/0504/'
    files = os.listdir(path)
    df = pd.read_pickle(path + files[0])
    CT_list = df['CT'].tolist()
    stft_value, stft_t, stft_f = get_STFT(CT_list, 0.1, fs)
    stft_value_t = transform_STFT(stft_value)
    stft_sequence = get_STFT_sequence(stft_value_t, stft_t, stft_f)
    recipe = get_name(stft_sequence.iloc[:, :-1])

