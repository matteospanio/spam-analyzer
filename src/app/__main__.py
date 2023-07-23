import os
import sys

import click
from rich.progress import track

from spamanalyzer.data_structures import MailAnalyzer
from app import files
from app.io import print_output

conf, _, _ = files.handle_configuration_files()


class Args:

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


@cli.command()
@click.option(
    "-l",
    "--wordlist",
    help="A file containing the spam wordlist",
    default=lambda: os.path.expanduser(conf["files"]["wordlist"]),
    show_default="standard wordlist",
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
@click.option("--destination-dir",
              help="The directory where copy your classified emails")
@click.argument(
    "file",
    type=click.Path(exists=True,
                    file_okay=True,
                    dir_okay=True,
                    readable=True,
                    resolve_path=True),
    required=True,
)
@pass_args
def analyze(
    args: Args,
    wordlist,
    output_format: str,
    output_file,
    destination_dir: str,
    file: str,
) -> None:
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
    verbose = args.verbose

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
            click.echo("The file is not analyzable")
        sys.exit(1)

    print_output(data,
                 output_format=output_format,
                 verbose=verbose,
                 output_file=output_file)

    if destination_dir is not None:
        expanded_dest_dir = files.expand_destination_dir(destination_dir)
        files.sort_emails(expanded_dest_dir, data)


@cli.group()
@click.help_option()
def config():
    """Configure the program"""
    pass


@config.command()
def edit():
    """Edit the configuration file"""

    click.edit(filename=os.path.expanduser("~/.config/spamanalyzer/config.yaml"))

    sys.exit(0)


@config.command()
def show():
    """Show the configuration file"""

    conf_file = os.path.expanduser("~/.config/spamanalyzer/config.yaml")
    with open(conf_file, "r", encoding="utf-8") as f:
        click.echo(f.read())

    sys.exit(0)


@config.command()
def reset():
    """Reset the configuration file"""

    os.remove(os.path.expanduser("~/.config/spamanalyzer/config.yaml"))
    _ = files.handle_configuration_files()

    sys.exit(0)
