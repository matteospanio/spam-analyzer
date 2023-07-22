import os
import sys

from rich.progress import track
from app import files
from spamanalyzer.data_structures import MailAnalyzer
from app.display import print_output

from . import parser


def app(
    file: str,
    wordlist,
    verbose: bool,
    output_format: str,
    destination_dir: str,
    output_file,
) -> None:
    wordlist = wordlist.read().splitlines()
    data = []

    analyzer = MailAnalyzer(wordlist)

    if os.path.isdir(file):
        file_list = files.get_files_from_dir(file, verbose)
        for mail_path in track(file_list, description="Analyzing mail list"):
            analysis = analyzer.analyze(mail_path)
            data.append(analysis)

    elif os.path.isfile(file) and files.file_is_valid_email(file):
        analysis = analyzer.analyze(file)
        data.append(analysis)

    else:
        if verbose:
            print("The file is not analyzable")
        sys.exit(1)

    print_output(data,
                 output_format=output_format,
                 verbose=verbose,
                 output_file=output_file)

    if destination_dir is not None:
        expanded_dest_dir = files.expand_destination_dir(destination_dir)
        files.sort_emails(expanded_dest_dir, data)


def cli(args=None):
    """
    The tool entry point, in order it:
    1. loads the configuration
    2. parses the arguments
    3. starts the application
    """
    config, _, _ = files.handle_configuration_files()

    args = parser.parse_args(args, config)

    app(
        args.file,
        args.wordlist,
        args.verbose,
        args.output_format,
        args.destination_dir,
        args.output_file,
    )
