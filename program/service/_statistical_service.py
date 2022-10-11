from algorithm.feature_extract.build_model import Build_model


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
