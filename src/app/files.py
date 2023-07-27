import os
import shutil
import sys
from importlib.resources import files
from os import listdir, path

import click
import yaml


def get_files_from_dir(directory: str, verbose: bool = False) -> list[str]:
    file_list = []
    for filename in listdir(directory):
        mail_path = path.join(directory, filename)
        if os.path.isfile(mail_path) and file_is_valid_email(mail_path):
            file_list.append(mail_path)
        else:
            if verbose:
                print(f"Invalid file found: {mail_path}")

    file_list.sort()
    return file_list


def file_is_valid_email(file_path: str) -> bool:
    from spamanalyzer import SpamAnalyzer

    mail = SpamAnalyzer.parse(file_path)
    return (path.isfile(file_path) and mail.headers.get("Received") is not None
            and mail.headers.get("From") is not None)


def handle_configuration_files():
    config_dir = click.get_app_dir("spam-analyzer")

    config_file = str(files(__package__).joinpath("conf/config.yaml"))
    wordlist = str(files(__package__).joinpath("conf/word_blacklist.txt"))
    model = str(files("spamanalyzer.ml").joinpath("classifier.pkl"))

    os.makedirs(config_dir, exist_ok=True)

    if not path.exists(path.join(config_dir, "config.yaml")):
        with open(config_file, "r", encoding="utf-8") as f:
            config_dict: dict = yaml.safe_load(f)
        config_dict["cli"]["analyze"]["wordlist"] = path.join(
            config_dir, "word_blacklist.txt")
        config_dict["cli"]["analyze"]["classifier"] = path.join(
            config_dir, "classifier.pkl")
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False)
        shutil.copy(config_file, path.join(config_dir, "config.yaml"))

    with open(path.join(config_dir, "config.yaml"), encoding="utf-8") as f:
        try:
            config: dict = yaml.safe_load(f)
        except Exception as e:
            raise Exception("Error while loading config file") from e

    try:
        wordlist_path = path.expanduser(
            path.expandvars(config["cli"]["analyze"]["wordlist"]))
        if not path.exists(wordlist_path):
            shutil.copy(wordlist, wordlist_path)
    except Exception as e:
        raise Exception(
            "Error while loading wordlist at the file path specified in the config file"
        ) from e

    try:
        classifier_path = path.expanduser(
            path.expandvars(config["cli"]["analyze"]["classifier"]))
        if not path.exists(classifier_path):
            shutil.copy(model, classifier_path)
    except Exception as e:
        raise Exception("Error while loading the classifier model at"
                        "the file path specified in the config file") from e

    return (config, wordlist_path, classifier_path)


def sort_emails(expanded_dest, file_list):
    if not path.exists(path.join(expanded_dest, "ham")):
        os.makedirs(path.join(expanded_dest, "ham"))
    if not path.exists(path.join(expanded_dest, "spam")):
        os.makedirs(path.join(expanded_dest, "spam"))

    for mail in file_list:
        if mail.is_spam():
            shutil.copy(mail.file_path, path.join(expanded_dest, "spam"))
        else:
            shutil.copy(mail.file_path, path.join(expanded_dest, "ham"))


def expand_destination_dir(destination_dir: str) -> str:
    expanded_dest = path.expandvars(destination_dir)
    if not path.isdir(expanded_dest):
        print("The destination directory does not exist or is not a directory")
        sys.exit(1)

    return expanded_dest
