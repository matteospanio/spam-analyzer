import os, sys

from spamdetector.files import get_files_from_dir
from spamdetector.lib.data_structures import MailAnalyzer


def app(file: str, wordlist, ignore_headers: bool, ignore_body: bool, verbose: bool) -> None:
    wordlist = wordlist.read().splitlines()
    data = []

    analyzer = MailAnalyzer(wordlist, ignore_headers, ignore_body)

    if os.path.isdir(file):
        file_list = get_files_from_dir(file)
        for mail_path in file_list:
            analysis = analyzer.analyze(mail_path)
            data.append(analysis)

    elif os.path.isfile(file):
        analysis = analyzer.analyze(file)
        data.append(analysis)

    else:
        print('The file or directory doesn\'t exist')
        sys.exit(1)

    for analysis in data:
        print(analysis.file_path.split('.')[0], analysis.is_spam())

    spam = 0
    warning = 0
    trust = 0
    for analysis in data:
        if analysis.is_spam() == 'Spam':
            spam += 1
        if analysis.is_spam() == 'Warning':
            warning += 1
        if analysis.is_spam() == 'Trust':
            trust += 1
    print('Spam: ', spam, 'su', len(data))
    print('Warning: ', warning, 'su', len(data))
    print('Trust: ', trust, 'su', len(data))
