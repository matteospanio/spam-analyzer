import asyncio
import functools
import os
import sys
from io import TextIOWrapper
from typing import List

import click
import click_extra
from click import Context
from rich.console import Console

from app import files
from app.io import print_output
from spamanalyzer.data_structures import SpamAnalyzer

conf, _, _ = files.handle_configuration_files()
config_dir = click.get_app_dir("spam-analyzer")


def async_command(coro_func):

    @functools.wraps(coro_func)
    def sync_func(*args, **kwargs):
        return asyncio.run(coro_func(*args, **kwargs))

    return sync_func


@click.group()
@click_extra.help_option
@click_extra.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click_extra.extra_version_option(package_name="spam-analyzer")
@click_extra.config_option
@click_extra.pass_context
def cli(ctx: Context, verbose: bool) -> None:
    """A simple program to analyze emails."""
    # ctx.verbose = verbose
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    os.makedirs(config_dir, exist_ok=True)


@cli.command()
@click_extra.option(
    "-l",
    "--wordlist",
    help="A file containing the spam wordlist",
    type=click.File("r"),
)
@click_extra.option(
    "-fmt",
    "--output-format",
    help="Format output in a different way",
    type=click.Choice(["json"]),
)
@click_extra.option(
    "-o",
    "--output-file",
    help="Write output to a file (works only for json format)",
    type=click.File("w"),
)
@click_extra.argument(
    "input",
    type=click.Path(exists=True,
                    file_okay=True,
                    dir_okay=True,
                    readable=True,
                    resolve_path=True),
    required=True,
)
@async_command
@click_extra.pass_context
async def analyze(
    ctx: Context,
    wordlist: TextIOWrapper,
    output_format: str,
    output_file: click.File,
    input: str,
) -> None:
    """Analyze emails from a file or directory."""

    # The tool entry point, in order it:
    # 1. loads the configuration
    # 2. starts the application

    wordlist_content: List[str] = wordlist.read().splitlines()  # type: ignore
    data = []

    console = Console()

    analyzer = SpamAnalyzer(wordlist_content)

    if os.path.isdir(input):
        with console.status("[bold]Reading files...", spinner="dots"):
            file_list = files.get_files_from_dir(input, ctx.obj["verbose"])
        with console.status("[bold]Analyzing emails...", spinner="dots"):
            for mail_path in file_list:
                analysis = analyzer.analyze(mail_path)
                data.append(analysis)
            data = await asyncio.gather(*data)

    elif os.path.isfile(input) and files.file_is_valid_email(input):
        analysis = await analyzer.analyze(input)
        data.append(analysis)

    else:
        if ctx.obj["verbose"]:
            click.echo("The file is not analyzable")
        sys.exit(1)

    results = analyzer.classify_multiple_input(data)

    print_output(
        data,
        output_format=output_format,
        verbose=ctx.obj["verbose"],
        analyzer=analyzer,
        output_file=output_file,
    )


@cli.group()
@click_extra.help_option
def configure():
    """Configure the program."""
    pass


@configure.command()
def edit():
    """Edit the configuration file."""

    click.edit(filename=os.path.join(config_dir, "config.yaml"))
    sys.exit(0)


@configure.command()
def show():
    """Show the configuration file."""

    conf_file = os.path.join(config_dir, "config.yaml")
    with click.open_file(conf_file, "r", encoding="utf-8") as f:
        click.echo(f.read())

    sys.exit(0)


@configure.command()
@click.confirmation_option(
    prompt="Are you sure you want to reset the configuration file?")
def reset():
    """Reset the configuration file."""

    os.remove(os.path.join(config_dir, "config.yaml"))
    _ = files.handle_configuration_files()

    sys.exit(0)
