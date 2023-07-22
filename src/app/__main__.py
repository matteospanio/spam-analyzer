import os
import sys

import click
from rich.progress import track

from spamanalyzer.data_structures import MailAnalyzer
from app import files
from app.io import print_output


config, _, _ = files.handle_configuration_files()


class Args(object):
    def __init__(self):
        self.verbose = False
        self.wordlist = []
        self.output_format = None
        self.output_file = None
        self.destination_dir = None
        self.file = None


pass_args = click.make_pass_decorator(Args, ensure=True)


@click.group()
@click.version_option(package_name="spam-analyzer")
@click.option("-v", "--verbose", help="More program output", is_flag=True)
@pass_args
def cli(config: Args, verbose: bool) -> None:
    """A simple program to analyze emails"""

    config.verbose = verbose


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

    print_output(
        data, output_format=output_format, verbose=verbose, output_file=output_file
    )

    if destination_dir is not None:
        expanded_dest_dir = files.expand_destination_dir(destination_dir)
        files.sort_emails(expanded_dest_dir, data)


@cli.command()
@click.option(
    "-l",
    "--wordlist",
    help="A file containing the spam wordlist",
    default=os.path.expanduser(config["files"]["wordlist"]),
    type=click.File("r"),
)
@click.option(
    "-fmt",
    "--output-format",
    help="Format output in a different way",
    type=click.Choice(["json"]),
)
@click.option(
    "-o",
    "--output-file",
    help="Write output to a file (works only for json format)",
    type=click.File("w"),
)
@click.option(
    "--destination-dir", help="The directory where copy your classified emails"
)
@click.argument(
    "file",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True
    ),
    required=True,
)
@pass_args
def analyze(args: Args, wordlist, output_format, output_file, destination_dir, file):
    """Analyze emails from a file or directory"""

    # The tool entry point, in order it:
    # 1. loads the configuration
    # 2. parses the arguments
    # 3. starts the application

    args.wordlist = wordlist
    args.output_format = output_format
    args.output_file = output_file
    args.destination_dir = destination_dir
    args.file = file

    app(
        args.file,
        args.wordlist,
        args.verbose,
        args.output_format,
        args.destination_dir,
        args.output_file,
    )


@cli.command()
def config():
    """Configure the program"""
    pass
