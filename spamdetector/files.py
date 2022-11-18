from os import path, listdir, makedirs
from importlib.resources import files
from spamdetector import __defaults__
from rich.progress import track
import mailparser
import shutil
import yaml

def get_files_from_dir(directory: str, verbose: bool = False) -> list[str]:
    file_list = []
    for filename in track(listdir(directory), description='Reading files from directory'):
        mail_path = path.join(directory, filename)
        if file_is_valid_email(mail_path):
            file_list.append(mail_path)
        else:
            if verbose:
                print("Invalid file found: {}".format(mail_path))

    file_list.sort()
    return file_list

def file_is_valid_email(file_path: str) -> bool:
    mail = mailparser.parse_from_file(file_path)
    return path.isfile(file_path) and mail.headers.get('Received') is not None and mail.headers.get('From') is not None

def handle_configuration_files():

    config_file = files('conf').joinpath('config.yaml')
    wordlist = files('conf').joinpath('word_blacklist.txt')
    
    if not path.exists(__defaults__['SPAMDETECTOR_CONF_PATH']):
        makedirs(__defaults__['SPAMDETECTOR_CONF_PATH'])
    
    if not path.exists(__defaults__['SPAMDETECTOR_CONF_FILE']):
        shutil.copy(config_file, __defaults__['SPAMDETECTOR_CONF_FILE'])

    with open(__defaults__['SPAMDETECTOR_CONF_FILE']) as f:
        try:
            config: dict = yaml.safe_load(f)
        except Exception:
            raise Exception('Error while loading config file')

    try:
        wordlist_path = path.expandvars(config['files']['wordlist'])
        if not path.exists(wordlist_path):
            shutil.copy(wordlist, wordlist_path)
    except Exception:
        raise Exception('Error while loading wordlist at the file path specified in the config file')

    return (config, wordlist_path)