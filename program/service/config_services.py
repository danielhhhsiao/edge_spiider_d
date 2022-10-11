import service


def get_feature_config_by_id(project_id):
    return _get_config_by_id(project_id)['feature_config']


def get_parameter_list_by_id(project_id):
    return _get_config_by_id(project_id)['parameter_list']


def _get_config_by_id(project_id):
    print(service.config_dict.keys())
    if project_id not in service.config_dict.keys():
        raise Exception('project id (' + str(project_id) + ') config not find.')

    return service.config_dict[project_id]
