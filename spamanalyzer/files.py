from os import path, listdir, makedirs
from importlib.resources import files
from spamanalyzer import __defaults__
from rich.progress import track
import mailparser
import shutil
import yaml
import os, sys


def get_files_from_dir(directory: str, verbose: bool = False) -> list[str]:
    file_list = []
    for filename in track(listdir(directory),
                          description='Reading files from directory'):
        mail_path = path.join(directory, filename)
        if os.path.isfile(mail_path) and file_is_valid_email(mail_path):
            file_list.append(mail_path)
        else:
            if verbose:
                print("Invalid file found: {}".format(mail_path))

    file_list.sort()
    return file_list


def file_is_valid_email(file_path: str) -> bool:
    mail = mailparser.parse_from_file(file_path)
    return path.isfile(file_path) and mail.headers.get(
        'Received') is not None and mail.headers.get('From') is not None


def handle_configuration_files():

    config_file = files('conf').joinpath('config.yaml')
    wordlist = files('conf').joinpath('word_blacklist.txt')
    model = files('conf').joinpath('classifier.pkl')

    if not path.exists(__defaults__['SPAMANALYZER_CONF_PATH']):
        makedirs(__defaults__['SPAMANALYZER_CONF_PATH'])

    if not path.exists(__defaults__['SPAMANALYZER_CONF_FILE']):
        shutil.copy(config_file, __defaults__['SPAMANALYZER_CONF_FILE'])

    with open(__defaults__['SPAMANALYZER_CONF_FILE']) as f:
        try:
            config: dict = yaml.safe_load(f)
        except Exception:
            raise Exception('Error while loading config file')

    try:
        wordlist_path = path.expandvars(config['files']['wordlist'])
        if not path.exists(wordlist_path):
            shutil.copy(wordlist, wordlist_path)
    except Exception:
        raise Exception(
            'Error while loading wordlist at the file path specified in the config file'
        )

    try:
        classifier_path = path.expandvars(config['files']['classifier'])
        if not path.exists(classifier_path):
            shutil.copy(model, classifier_path)
    except Exception:
        raise Exception(
            'Error while loading the classifier model at the file path specified in the config file'
        )

    return (config, wordlist_path, classifier_path)


def sort_emails(expanded_dest, files):

    if not path.exists(path.join(expanded_dest, 'ham')):
        makedirs(path.join(expanded_dest, 'ham'))
    if not path.exists(path.join(expanded_dest, 'spam')):
        makedirs(path.join(expanded_dest, 'spam'))

    for mail in files:
        if mail.is_spam():
            shutil.copy(mail.file_path, path.join(expanded_dest, 'spam'))
        else:
            shutil.copy(mail.file_path, path.join(expanded_dest, 'ham'))


def expand_destination_dir(destination_dir: str) -> str:
    expanded_dest = path.expandvars(destination_dir)
    if not path.isdir(expanded_dest):
        print('The destination directory does not exist or is not a directory')
        sys.exit(1)

    return expanded_dest
