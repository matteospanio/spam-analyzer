#!/usr/bin/env python
#
# File: spam-detector.py
# Author: Matteo Spanio <matteo.spanio97@gmail.com>
# Description: Spam detector for emails

import argparse, os

import lib.mail_checker as mail_checker
import lib.file_handler as file_handler
import lib.display as display
from app.costants import WORDLIST

from app import app


def add_args(parser):
    parser.add_argument('-f', '--file', help='The file or directory to analyze', required=True)
    parser.add_argument('-l', '--wordlist', help='A file containing the spam wordlist', default=WORDLIST)
    parser.add_argument('-H', '--ignore-headers', help="Don't check headers fields", action='store_true')
    parser.add_argument('-B', '--ignore-body', help="Don't parse body content", action='store_true')
    parser.add_argument('-v', '--verbose', help='More program output', action='store_true')


def main(parser):
    args = parser.parse_args()
    wordlist = file_handler.get_wordlist_from_file(args.wordlist)
    if os.path.isdir(args.file):
        file_list = file_handler.get_files_from_dir(args.file)
        data = []
        for mail_path in file_list:
            mail = mail_checker.analyze(mail_path, wordlist)
            is_spam = mail_checker.is_spam(mail)
            data.append([mail['path'].split('.')[0], mail['domain_match'], mail['has_spf'], mail['has_dkim'], mail['has_dmarc'], mail['auth_warn'], mail['has_forbidden_words'], mail['has_script'], mail['has_http_links'], is_spam])
    else:
        mail = mail_checker.analyze(args.file, wordlist)
        is_spam = mail_checker.is_spam(mail)
        data = [[mail['path'].split('.')[0], mail['domain_match'], mail['has_spf'], mail['has_dkim'], mail['has_dmarc'], mail['auth_warn'], mail['has_forbidden_words'], mail['has_script'], mail['has_http_links'], is_spam]]

    if args.verbose:
        display.summary(data)
    else:
        display.short(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='spam-detector',
        description='A program to detect spam',
        epilog='if you find any bug write an email to matteo.spanio97@gmail.com'
    )
    add_args(parser)
    main(parser)
