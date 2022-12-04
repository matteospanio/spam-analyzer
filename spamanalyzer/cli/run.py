import os, sys, logging

import spamanalyzer.files as files
from spamanalyzer.cli import parser
from spamanalyzer.analyzer.data_structures import MailAnalyzer
from spamanalyzer.display import print_output
from rich.progress import track


def app(file: str, wordlist, verbose: bool, output_format: str, destination_dir: str,
        output_file, quiet: bool) -> None:
    wordlist = wordlist.read().splitlines()
    data = []

    logging.basicConfig(stream=sys.stdout, 
                        level=logging.ERROR if quiet else logging.INFO,
                        format='[%(levelname)s] %(message)s')

    log = logging.getLogger()

    analyzer = MailAnalyzer(wordlist)

    if os.path.isdir(file):
        file_list = files.get_files_from_dir(file, verbose)
        for mail_path in track(file_list, description='Analyzing mail list'):
            analysis = analyzer.analyze(mail_path)
            data.append(analysis)

    elif os.path.isfile(file) and files.file_is_valid_email(file):
        analysis = analyzer.analyze(file)
        data.append(analysis)

    else:
        if verbose:
            log.error("Invalid file found: {}, the file is not analyzable".format(file))
        sys.exit(1)

    print_output(data,
                 logger=log,
                 output_format=output_format,
                 verbose=verbose,
                 output_file=output_file)

    if destination_dir is not None:
        expanded_dest_dir = files.expand_destination_dir(destination_dir)
        files.sort_emails(expanded_dest_dir, data)


def main(args=None):
    """
    The tool entry point, in order it:
    1. loads the configuration
    2. parses the arguments
    3. starts the application
    """
    config, _, _ = files.handle_configuration_files()

    args = parser.parse_args(args, config)

    app(args.file, args.wordlist, args.verbose, args.output_format,
        args.destination_dir, args.output_file)


if __name__ == '__main__':
    main()
