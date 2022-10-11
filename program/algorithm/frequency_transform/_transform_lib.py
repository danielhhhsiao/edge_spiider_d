import numpy as np
from scipy.fftpack import fft
from scipy.signal import welch
import pywt


# FFT PAD  AutoCorr  DWT  WP
def get_fft_values(parm):
    y_values = parm['data']
    sampling_rate = parm['samplerate']
    # print('get_fft  sampling_rate:', sampling_rate)

    T = (1 / sampling_rate)
    N = len(y_values)
    freq_values = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
    fft_values_ = fft(y_values)
    fft_values = 2.0 / N * np.abs(fft_values_[0:N // 2])
    freq_values_int = [int(i) for i in freq_values]
    return freq_values_int, fft_values


def get_psd_values(parm):
    y_values = parm['data']
    sampling_rate = parm['samplerate']
    # print('get_psd  sampling_rate:', sampling_rate)

    freq_values, psd_values = welch(y_values, fs=sampling_rate)
    freq_values_int = [int(i) for i in freq_values]
    return freq_values_int, psd_values


def get_autocorr_values(parm):
    x = parm['data']
    # print('get_psd')
    # return 1

    result = np.correlate(x, x, mode='full')
    result = result[len(result) // 2:]
    x_val = np.arange(len(result))
    return x_val, result


def dec2bin(num, bin_count):
    num = '{0:b}'.format(num)
    return num.zfill(bin_count)


def gen_wavelet_packet_level_code(level):
    max_num = 2 ** level
    level_code = []

    for i in np.arange(max_num):
        bin2 = dec2bin(i, level)
        bin2 = bin2.replace("0", "a")
        bin2 = bin2.replace("1", "d")
        level_code.append(bin2)

    return level_code


def get_wavelet_packet_energy_3_level(parm):
    '''
    input: x, list of numbers.
    output: energy, array, (n_energy, 1).
    output: ave_energy, float.
    '''
    x = parm['data']
    level = parm['level']
    # print('get_waveletPacket  level:', level)
    level_code = gen_wavelet_packet_level_code(level)
    # print(level_code)

    wp = pywt.WaveletPacket(data=x, wavelet='db1', mode='symmetric')  # coif3   db1
    #     print((wp.level))
    wpcoef = []

    for code in level_code:
        wpcoef.append(wp[code].data)

    wpcoef = np.array(wpcoef)
    return level_code, wpcoef


def gen_wavedec_level_code(level):
    level_code = ['a']

    for i in np.arange(level):
        code = "d" * (i + 1)
        level_code.append(code)

    return level_code


def get_wavedec(parm):
    x = parm['data']
    level = parm['level']
    # print('get_waveletdec  level:', level)
    # return 1
    level_code = gen_wavedec_level_code(level)
    list_coeff = pywt.wavedec(x, 'coif3', level=level)
    return level_code, list_coeff


def get_time_domain_values(parm):
    return None, parm['data']
