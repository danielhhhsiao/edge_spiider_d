from algorithm.feature_extract.build_model import Build_model, Build_psd_vel_model


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

def  transform_psd_vel(parameter, spectrum_name,statistical, psd_rms, df_psd, base_freq, fs, bin_width):
    param = {
        "RawData": {
            "psd_rms": psd_rms,
            "df_psd": df_psd
        },
        "Setting": {
            "SensorType": parameter,
            "Spectrum": spectrum_name,
            "Feature": statistical,
            "base_freq": base_freq,
            "fs": fs,
            "bin_width": bin_width
        }
    }
    feature_model = Build_psd_vel_model()
    statistical_result = feature_model.run(param)
    return statistical_result
    