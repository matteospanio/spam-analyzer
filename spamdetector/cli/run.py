import os, sys

import spamdetector.files as files
from spamdetector.cli import parser
from spamdetector.analyzer.data_structures import MailAnalyzer
from spamdetector.display import print_output
from rich.progress import track


def app(file: str, wordlist, add_headers: bool, verbose: bool, output_format: str) -> None:
    wordlist = wordlist.read().splitlines()
    data = []

    analyzer = MailAnalyzer(wordlist)

    if os.path.isdir(file):
        file_list = files.get_files_from_dir(file, verbose)
        for mail_path in track(file_list, description='Analyzing mail list'):
            analysis = analyzer.analyze(mail_path, add_headers)
            data.append(analysis)

    elif os.path.isfile(file) and files.file_is_valid_email(file):
        analysis = analyzer.analyze(file, add_headers)
        data.append(analysis)

    else:
        if verbose:
            print('The file is not analyzable')
        sys.exit(1)

    print_output(data, output_format=output_format, verbose=verbose)


def main(args=None):
    """
    The tool entry point, in order it:
    1. loads the configuration
    2. parses the arguments
    3. starts the application
    """
    config, _ = files.handle_configuration_files()

    args = parser.parse_args(args, config)

    app(args.file, args.wordlist, args.add_headers, args.verbose, args.output_format)


if __name__ == '__main__':
    main()
