import json
from io import TextIOWrapper
from typing import Optional, Sequence

from rich.box import ROUNDED
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from spamanalyzer.data_structures import MailAnalysis


def print_output(
    data: Sequence[MailAnalysis],
    output_format: str,
    verbose: bool,
    results: Sequence[bool],
    output_file=None,
) -> None:
    """Prints the output of the `MailAnalysis` in the specified format (csv, json
    or default).

    Args:
        data (list): a list of data to output
        output_format (str): the type of output (csv | json | default)
        verbose (bool): valid only for `default` output_format, it prints a
        description for each element of the list

    Often when we work with data we want to output it in a specific format, this
    function handles the output of the data in the specified format,
    at the moment it supports only json and default stdout which will print a whit the
    rich library a card for each email analyzed in the default pager of the terminal;
    outside the pager the output will be a table with the summary of the analysis where
    are reported the number of spam and ham emails and the mean score of each class.

    > Return later: future versions of spamanalyzer will support csv output format

    """
    if output_format == "csv":
        __print_to_csv(data, output_file)
    elif output_format == "json":
        __print_to_json(data, results, output_file)
    else:
        __print_default(data, results, verbose)


def __print_to_csv(data, output_file):
    raise NotImplementedError


def __print_to_json(
    data: Sequence[MailAnalysis],
    results: Sequence[bool],
    output_file: Optional[TextIOWrapper],
):
    dict_data = [analysis.to_dict() for analysis in data]
    for analysis, origin, is_spam in zip(dict_data, data, results):
        if analysis["headers"]["send_date"] is not None:
            analysis["headers"]["send_date"] = analysis["headers"]["send_date"].to_dict(
            )
        if analysis["headers"]["received_date"] is not None:
            analysis["headers"]["received_date"] = analysis["headers"][
                "received_date"].to_dict()
        analysis["filename"] = origin.file_path
        analysis["is_spam"] = str(is_spam).lower()
    if output_file is not None:
        json.dump(dict_data, output_file, indent=4)
    else:
        print(json.dumps(dict_data, indent=4))


def __print_default(data: Sequence[MailAnalysis], labels: Sequence[bool],
                    verbose: bool):
    classifier_spam = 0
    classifier_ham = 0

    console = Console()
    renderables = []

    for analysis, label in zip(data, labels):
        if label:
            classifier_spam += 1
        else:
            classifier_ham += 1

        if verbose:
            renderables.append(__print_details(analysis, label))

    if verbose and len(renderables) > 0:
        with console.pager(styles=True):
            console.print(Columns(renderables, equal=True))

    __print_summary(classifier_ham, classifier_spam)


def __print_summary(ok_count, spam_count) -> None:
    table = Table(title="Summary", box=ROUNDED, highlight=True)

    table.add_column("Email class", justify="center")
    table.add_column("Quantity", justify="center")

    table.add_row("[green][bold]HAM[/bold][/green]", str(ok_count))
    table.add_row("[red][bold]SPAM[/bold][/red]", str(spam_count))

    console = Console()
    console.print(table)


def __print_details(email: MailAnalysis, result: bool):
    mail_dict = email.to_dict()
    score, headers, body, attachments = __stringify_email(mail_dict, result)

    panel_group = Group(
        Text(score, justify="center"),
        Panel(headers, title="Headers", border_style="light_coral"),
        Panel(body, title="Body", border_style="light_coral"),
        Panel(attachments, title="Attachments", border_style="light_coral"),
    )

    return Panel(
        panel_group,
        border_style="cyan",
    )


def __stringify_email(email: dict, result: bool):
    header: dict = email["headers"]
    bd: dict = email["body"]
    att: dict = email["attachments"]

    headers = ""
    body = ""
    attachments = ""

    for key, value in header.items():
        k, v = __format_output(key, value)
        k = k.removeprefix("has_")

        headers += f"{k}: [bold]{v}[/bold]\n"

    for key, value in bd.items():
        k, v = __format_output(key, value)
        k = k.removeprefix("contains_")
        k = k.replace("percentage", "%")

        body += f"{k}: [bold]{v}[/bold]\n"

    for key, value in att.items():
        k, v = __format_output(key, value)

        attachments += f"{k}: [bold]{v}[/bold]\n"

    score = f"\nspam: {result}\n"

    return (score, headers, body, attachments)


def __format_output(k: str, v):
    key = k.replace("_", " ")
    key = key.capitalize()

    if v is True:
        v = f"[green]{v}[/green]"
    elif v is False:
        v = f"[red]{v}[/red]"

    if isinstance(v, float):
        v = f"{v:.4f}"

    return (key, v)
