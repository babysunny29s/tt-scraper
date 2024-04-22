import config.config as cf
import json

def read_config():
    config_path = cf.config_path
    with open(config_path, "r", encoding="utf-8") as list_config_file:
        list_config_data = json.load(list_config_file)
    return list_config_data

def get_list_config_id():
    list_config_id = list()
    list_config_data = read_config()
    for config in list_config_data:
        config_id = config.get("id")
        list_config_id.append(config_id)
    return list_config_id

def get_mode_config(config_id):
    list_config_data = read_config()
    for config in list_config_data:
        id = config.get("id")
        if id == config_id:
            mode = config["mode"]["id"]
            break
    return mode

