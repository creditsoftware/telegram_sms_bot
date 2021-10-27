import configparser
import os
import time

path = 'config.cfg'

def create_config():

    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "bot_token", "token")
    config.set("Settings", "admin_id_own", "0:1")
    config.set("Settings", "admin_id_manager", "0:1")
    config.set("Settings", "bot_login", "0")
    config.set("Settings", "ref_percent", "0")
    config.set("Settings", "qiwi_number", "0")
    config.set("Settings", "qiwi_token", "0")
    config.set("Settings", "api_smshub", "0")
    
    with open(path, "w") as config_file:
        config.write(config_file)


def check_config_file():
    if not os.path.exists(path):
        create_config()
        
        print('Config created')
        time.sleep(3)
        exit(0)


def config(what):
    
    config = configparser.ConfigParser()
    config.read(path)

    value = config.get("Settings", what)

    return value


def edit_config(setting, value):
    config = configparser.ConfigParser()
    config.read(path)

    config.set("Settings", setting, value)

    with open(path, "w") as config_file:
        config.write(config_file)

check_config_file()