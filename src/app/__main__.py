import asyncio
import functools
import os
import sys
from io import TextIOWrapper
from typing import List, Optional

import click
from rich.console import Console

from app import files
from app.io import print_output
from spamanalyzer.data_structures import SpamAnalyzer

conf, _, _ = files.handle_configuration_files()


def async_command(coro_func):

    @functools.wraps(coro_func)
    def sync_func(*args, **kwargs):
        return asyncio.run(coro_func(*args, **kwargs))

    return sync_func


class Args:
    destination_dir: Optional[str]
    input: Optional[str]
    output_file: Optional[click.File]
    output_format: Optional[str]
    verbose: bool
    wordlist: TextIOWrapper

    def __init__(self):
        self.verbose = False
        self.output_format = None
        self.output_file = None
        self.destination_dir = None
        self.input = None


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
@click.option("--destination-dir", help="The directory where copy your classified emails")
@click.argument(
    "input",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True, resolve_path=True),
    required=True,
)
@async_command
@pass_args
async def analyze(
    args: Args,
    wordlist: TextIOWrapper,
    output_format: str,
    output_file: click.File,
    destination_dir: str,
    input: str,
) -> None:
    """Analyze emails from a file or directory"""

    # The tool entry point, in order it:
    # 1. loads the configuration
    # 2. starts the application

    args.wordlist = wordlist
    args.output_format = output_format
    args.output_file = output_file
    args.destination_dir = destination_dir
    args.input = input
    verbose = args.verbose

    wordlist_content: List[str] = wordlist.read().splitlines()  # type: ignore
    data = []

    console = Console()

    analyzer = SpamAnalyzer(wordlist_content)

    if os.path.isdir(input):
        with console.status("[bold]Reading files...", spinner="dots"):
            file_list = files.get_files_from_dir(input, verbose)
        with console.status("[bold]Analyzing emails...", spinner="dots"):
            for mail_path in file_list:
                analysis = analyzer.analyze(mail_path)
                data.append(analysis)
            data = await asyncio.gather(*data)

    elif os.path.isfile(input) and files.file_is_valid_email(input):
        analysis = await analyzer.analyze(input)
        data.append(analysis)

    else:
        if verbose:
            click.echo("The file is not analyzable")
        sys.exit(1)

    print_output(
        data,
        output_format=output_format,
        verbose=verbose,
        analyzer=analyzer,
        output_file=output_file,
    )

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
    with click.open_file(conf_file, "r", encoding="utf-8") as f:
        click.echo(f.read())

    sys.exit(0)


@config.command()
@click.confirmation_option(prompt="Are you sure you want to reset the configuration file?")
def reset():
    """Reset the configuration file"""

    os.remove(os.path.expanduser("~/.config/spamanalyzer/config.yaml"))
    _ = files.handle_configuration_files()

    sys.exit(0)
