from service.valid_service import valid_data
from service.spectrum_service import transform_spectrum


def get_feature_engineer(project_id, df):
    # 0.Data Valid
    valid_data(project_id, df)

    # 2.Feature Extract
    df_feature = transform_spectrum(project_id, df)
    return df_feature
