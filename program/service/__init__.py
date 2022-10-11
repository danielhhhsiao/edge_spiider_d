from os import listdir
from os.path import isdir, isfile, join
import pathlib
import json

config_dict = {}
config_path = str(pathlib.Path(__file__).parent.parent.absolute()) + '/configs'

if not isdir(config_path):
    raise Exception('Config folder not find. ({0})'.format(config_path))

file_name_list = [file_name for file_name in listdir(config_path) if
                  '.json' in file_name and isfile(join(config_path, file_name))]
print("FE file_name_list")
print(file_name_list)
for file_name in file_name_list:
    file_path = join(config_path, file_name)

    with open(file_path, 'r') as reader:
        temp = json.loads(reader.read())

        if 'project_id' not in temp or not temp['project_id']:
            raise Exception('Config file ({0}) project id not find.'.format(file_path))

        if temp['project_id'] in config_dict:
            raise Exception('Config file ({0}) project id ({1}) duplicate.'.format(file_path, temp['project_id']))

        config_dict[temp['project_id']] = temp
