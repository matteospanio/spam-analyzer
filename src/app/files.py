import os
import shutil
from importlib.resources import files
from os import listdir, path
from typing import Dict, Tuple

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


def copy_config_file(dst: str) -> None:
    config_file = str(files(__package__).joinpath("conf/config.yaml"))
    shutil.copy(config_file, dst)


def handle_configuration_files() -> Tuple[Dict, str, str]:
    config_dir = click.get_app_dir("spam-analyzer")
    os.makedirs(config_dir)

    dest_config_file = path.join(config_dir, "config.yaml")
    copy_config_file(dest_config_file)

    with open(dest_config_file, "r", encoding="utf-8") as f:
        config_dict: dict = yaml.safe_load(f)

    config_dict["cli"]["analyze"]["wordlist"] = path.join(config_dir,
                                                          "word_blacklist.txt")
    config_dict["cli"]["analyze"]["classifier"] = path.join(config_dir,
                                                            "classifier.pkl")

    with open(dest_config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False)

    wordlist = str(files(__package__).joinpath("conf/word_blacklist.txt"))
    try:
        wordlist_path: str = path.expanduser(
            path.expandvars(config_dict["cli"]["analyze"]["wordlist"]))
        if not path.exists(wordlist_path):
            shutil.copy(wordlist, wordlist_path)
    except Exception as e:
        raise Exception(
            "Error while loading wordlist at the file path specified in the config file"
        ) from e

    model = str(files("spamanalyzer.ml").joinpath("classifier.pkl"))
    try:
        classifier_path: str = path.expanduser(
            path.expandvars(config_dict["cli"]["analyze"]["classifier"]))
        if not path.exists(classifier_path):
            shutil.copy(model, classifier_path)
    except Exception as e:
        raise Exception("Error while loading the classifier model at"
                        "the file path specified in the config file") from e

    return (config_dict, wordlist_path, classifier_path)
