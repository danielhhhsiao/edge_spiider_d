from service import config_services


def valid_data(project_id, df):
    # Check if None Data
    if len(df) < 1:
        raise Exception('rows < 1')

    datetime_column_name = None

    for col in df.columns:
        if col.lower() == 'datetime':
            datetime_column_name = col
            break

    if not datetime_column_name:
        raise Exception('DataFrame not include "datetime" column.')

    parameter_list = config_services.get_parameter_list_by_id(project_id)
    # Check Parameter
    valid_parameter = parameter_list + [datetime_column_name]
    diff_list = (list(set(valid_parameter) - set(df.columns)))

    if len(diff_list) != 0:
        raise Exception('DataFrame columns not equal ' + str(valid_parameter))


# if __name__ == '__main__':
#     import pandas as pd
#
#     df = pd.read_csv('../sample_data/CKCGL8041_NG/CKCGL8041_20191116_161457_3999_2.csv')
#     # print(len(df))
#     # print(df.columns)
#     valid_data(df)
