from algorithm.feature_extract.build_model import Build_model,Build_psd_vel_model,Build_defect_frequency_model 
#20220825 Danielhhhsiao
#20230210 ErwinJSLiang(add Model-based feature)

def transform_statistical(parameter, spectrum_name, statistical, y_val):
    param = {
        "RawData": y_val,
        "Setting": {
            "SensorType": parameter,
            "Spectrum": spectrum_name,
            "Feature": statistical
        }
    }
    feature_model = Build_model()
    statistical_result = feature_model.run(param)
    return statistical_result


#20220825 Danielhhhsiao
#20230213 ErwinJSLiang(revise from PHM Platform code)
def transform_psd_vel(parameter, spectrum_name, statistical, spectrum_data, spectrum_object):
    param = {
        "RawData": {
            "psd_rms": spectrum_data['psd_rms'],
            "df_psd": spectrum_data['df_psd']
            },
        "Setting": {
            "SensorType": "",
            "Spectrum": spectrum_name,
            "Feature": statistical,
            "base_freq": spectrum_object['spectrum_param']['base_freq'],
            "fs": spectrum_object['spectrum_param']['samplerate'],
            "bin_width": spectrum_data['bin_width']
        }
    }
    feature_model = Build_psd_vel_model()
    statistical_result = feature_model.run(param)
    return statistical_result


#20230213 ErwinJSLiang(revise from PHM Platform code)
def transform_defect_frequency(parameter, spectrum_name, statistical, spectrum_data):
    param = {
        "RawData": {
            "df_psd": spectrum_data['df_psd']
            },
        "Setting": {
            "SensorType": "",
            "Spectrum": spectrum_name,
            "Feature": statistical,
            "base_freq": spectrum_data['base_freq'],
            "real_base_freq": spectrum_data['real_base_freq'],
            "params": spectrum_data['params']
        }
    }
    feature_model = Build_defect_frequency_model()
    statistical_result = feature_model.run(param)
    return statistical_result
    
    