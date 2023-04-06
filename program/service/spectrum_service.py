import math

import pandas
import numpy as np

from algorithm.frequency_transform import transform_lib
from service.config_services import get_feature_config_by_id, get_parameter_list_by_id
#20220825 Danielhhhsiao
#20230213 ErwinJSLiang(add model-based)
from service.statistical_service import transform_statistical,transform_psd_vel,transform_defect_frequency
from algorithm.frequency_transform.build_model import Build_model
from algorithm.feature_extract import defined_recipe 
#20230210 ErwinJSLiang(add multi-regime)


def transform_spectrum(project_id, df: pandas):
    feature_name_all = []
    feature_val_all = []

    # select setting
    parameter_list_ = get_parameter_list_by_id(project_id)

    for parameter in parameter_list_:
        parameter_rawData = df[parameter].values.tolist()
        parameter_rawData = [(0 if i is None else i) for i in parameter_rawData]

        config_spectrum_list = _get_specific_set(project_id, parameter)

        col_name_list, col_val_list = _cal_spectrum(parameter_rawData, parameter, config_spectrum_list)
        feature_name_all = feature_name_all + col_name_list
        feature_val_all = feature_val_all + col_val_list

    df = pandas.DataFrame([feature_val_all], columns=feature_name_all)
    return df


def _get_specific_set(project_id, parameter):
    result = None

    # select setting
    feature_config_ = get_feature_config_by_id(project_id)

    for attrs in feature_config_:
        if attrs['parameter'] == parameter:
            spectrum_list = attrs['spectrum']
            return spectrum_list

    return result


def _cal_spectrum(raw_data, parameter, config_spectrum_list):
    spectrum_model = Build_model()
    column_name_list = []
    feature_val_list = []

    for spectrum_obj in config_spectrum_list:
        obj = {
            "RawData": raw_data,
            "Setting": {
                "SensorType": parameter,
                "Spectrum": {
                    "type": spectrum_obj['item']
                }
            }
        }

        # 1.Freq_Transform
        for par_key in (spectrum_obj['spectrum_param']).keys():
            obj['Setting']['Spectrum'][par_key] = spectrum_obj['spectrum_param'][par_key]

        if spectrum_obj['item'] == 'VibVelocity': #20220825 Danielhhhsiao
            spectrum_data = {}
            spectrum_data['psd_rms'], spectrum_data['df_psd'], spectrum_data['bin_width'] = spectrum_model.run(data=raw_data, parm=obj) #20230210 ErwinJSLiang(revise parameter)
            
        elif spectrum_obj['item'] == 'DefectFrequency': #20230210 ErwinJSLiang(add model-based)
            spectrum_data = {}
            spectrum_data['df_psd'], spectrum_data['base_freq'], spectrum_data['real_base_freq'] = spectrum_model.run(data=raw_data, parm=obj)
            spectrum_data["params"] = spectrum_obj['spectrum_param']['params']
        else:
            if spectrum_obj['item'] != 'recipe': #20230210 ErwinJSLiang(add multi-regime)
                x_val, y_val = spectrum_model.run(data=raw_data, parm=obj)
                
        spectrum_wp_dwt_name_list = None

        if spectrum_obj['item'] in ['WP', 'DWT']:
            bin_spec_data_list = y_val

            if spectrum_obj['item'] == 'WP':
                wp_level = math.log(len(bin_spec_data_list), 2)

                if not wp_level.is_integer():
                    raise Exception(f'WP level ({wp_level}) not integer.')

                spectrum_wp_dwt_name_list = transform_lib.gen_wavelet_packet_level_code(int(wp_level))

            elif spectrum_obj['item'] == 'DWT':
                spectrum_wp_dwt_name_list = transform_lib.gen_wavedec_level_code(len(bin_spec_data_list) - 1)

        elif spectrum_obj['item'] == 'Time_Domain':
            bin_spec_data_list = [y_val]

        elif spectrum_obj['item'] == 'VibVelocity': #20220825 Danielhhhsiao
            bin_spec_data_list = []
            
        elif spectrum_obj['item'] == 'DefectFrequency': #20230210 ErwinJSLiang(add model-based)
            bin_spec_data_list = []
            
        else:
            if spectrum_obj['item'] != 'recipe': #20230210 ErwinJSLiang(add multi-regime)
                bin_spec_data_list = np.array_split(y_val, spectrum_obj['bin'], axis=0)
        
        #20220825 Danielhhhsiao
        for statistical_item in spectrum_obj['statistical']:
            if spectrum_obj['item'] == 'VibVelocity': #20220825 Danielhhhsiao
                statistical_result=transform_psd_vel(parameter,
                                                     spectrum_obj['item'],
                                                     statistical_item,
                                                     spectrum_data,
                                                     spectrum_obj)
                if math.isnan(statistical_result):
                    statistical_result = 0
                feature_val_list.append(statistical_result)
                column_name_list.append(f'{parameter}_{spectrum_obj["item"]}_{statistical_item}_1')
            
            elif spectrum_obj['item'] == 'DefectFrequency': #20230210 ErwinJSLiang(add model-based)
                if statistical_item == 'MultipleMax' or statistical_item == 'MultipleRms':
                    for sta_item in spectrum_obj['spectrum_param']['params']:
                        new_statistical_item = sta_item + '_' + statistical_item
                        
                        statistical_result = transform_defect_frequency(parameter,
                                                                        spectrum_obj['item'],
                                                                        new_statistical_item,
                                                                        spectrum_data)
                        if math.isnan(statistical_result):
                            statistical_result = 0
                        feature_val_list.append(statistical_result)
                        column_name_list.append(f'{parameter}_{spectrum_obj["item"]}_{new_statistical_item}_1')
            
            elif spectrum_obj['item']=='recipe': #20230210 ErwinJSLiang(add multi-regime)
                recipe_name = defined_recipe.run(data=raw_data, fs=spectrum_obj['spectrum_param']['samplerate'])
                feature_val_list.append(recipe_name)
                column_name_list.append(f'{parameter}_{spectrum_obj["item"]}_name_1')
            
            else:
                for i, v_val in enumerate(bin_spec_data_list):
                    # 2.Feature_Statistical
                    statistical_result = transform_statistical(parameter,
                                                               spectrum_obj['item'],
                                                               statistical_item,
                                                               v_val)
                    if math.isnan(statistical_result):
                        statistical_result = 0
    
                    feature_val_list.append(statistical_result)
    
                    if spectrum_obj['item'] in ['WP', 'DWT']:
                        bin_name = spectrum_wp_dwt_name_list[i]
    
                    else:
                        bin_name = str(i + 1)
    
                    column_name_list.append(f'{parameter}_{spectrum_obj["item"]}_{statistical_item}_{bin_name}')

    return column_name_list, feature_val_list


if __name__ == '__main__':
    df = pandas.read_csv('../sample_data/CKCGL8041_NG/CKCGL8041_20191116_161457_3999_2.csv')
    result = transform_spectrum(df)
    print(result)
