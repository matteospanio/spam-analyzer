import asyncio
import os
import sys
from io import TextIOWrapper
from typing import List

import click
import click_extra
from click import Context
from rich.console import Console

import app.files as files
import spamanalyzer.plugins as plugins
from app.io import print_output
from spamanalyzer import SpamAnalyzer


@click.command()
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
@plugins.async_command
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

    wordlist_content: List[str] = wordlist.read().splitlines()
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
        results=results,
        output_file=output_file,
    )
