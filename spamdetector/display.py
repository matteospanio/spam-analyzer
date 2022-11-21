import json
import rich
from rich.panel import Panel
from rich.text import Text
from rich.console import Console, Group
from rich.columns import Columns
from rich.table import Table
from spamdetector import MailAnalysis

HEADER = [
    'File',
    'Domain',
    'SPF',
    'DKIM',
    'DMARC',
    'Auth Warning',
    'has spam word',
    'script',
    'http link',
    'Trust'
]

def print_output(data, output_format: str, verbose: bool) -> None:
    """Prints the output of the `MailAnalysis` in the specified format (csv, json or default).

    Args:
        data (`list`): a list of data to output
        output_format (`str`): the type of output (csv | json | default)
        verbose (`bool`): valid only for `default` output_format, it prints a description for each element of the list
        
    Often when we work with data we want to output it in a specific format, this function handles the output of the data in the specified format,
    at the moment it supports only json and default stdout which will print a whit the rich library a card for each email analyzed
    in the default pager of the terminal; outside the pager the output will be a table with the summary of the analysis where
    are reported the number of spam and ham emails and the mean score of each class.

    > Return later: future versions of spamdetector will support csv output format
    """
    if output_format == 'csv':
        _print_to_csv(data)
    elif output_format == 'json':
        _print_to_json(data)
    else:
        _print_default(data, verbose)

def _print_to_csv(data):
    raise NotImplementedError

def _print_to_json(data):
    dict_data = [analysis.to_dict() for analysis in data]
    print(json.dumps(dict_data, indent=4))

def _print_default(data, verbose):
    count = 0
    total_spam_score = 0
    total_ok_score = 0

    console = Console()
    renderables = []
    for analysis in data:
        score = analysis.get_score()
        if score <= 3.50:
            count += 1
            total_ok_score += score
        else:
            total_spam_score += score
        if verbose:
            renderables.append(_print_details(analysis))

    if verbose and len(renderables) > 0:
        with console.pager(styles=True):
            console.print(Columns(renderables, equal=True))

    _print_summary(count, len(data) - count, total_ok_score, total_spam_score)

def _print_summary(ok_count, spam_count, total_ok_score, total_spam_score) -> None:
    table = Table(title="Summary", box=rich.box.ROUNDED, highlight=True)
    
    table.add_column("Email class", justify="center")
    table.add_column("Quantity", justify="center")
    table.add_column("Mean score", justify="center")
    
    table.add_row("[green][bold]HAM[/bold][/green]", str(ok_count), str(total_ok_score / (ok_count if ok_count > 0 else 1)))
    table.add_row("[red][bold]SPAM[/bold][/red]", str(spam_count), str(total_spam_score / (spam_count if spam_count > 0 else 1)))

    console = Console()
    console.print(table)

def _print_details(email: MailAnalysis):
    mail_dict = email.to_dict()
    score, headers, body, attachments = _stringify_email(mail_dict)

    panel_group = Group(
        Text(score, justify="center"),
        Panel(headers, title="Headers", border_style="light_coral"),
        Panel(body, title="Body", border_style="light_coral"),
        Panel(attachments, title="Attachments", border_style="light_coral"),
    )

    return (
        Panel(
            panel_group,
            title=f"[bold]{mail_dict['file_name'].split('/')[-1][0:20]}[/bold]",
            border_style="cyan"
            )
        )

def _stringify_email(email: dict):
    header = email['headers']
    bd = email['body']
    att = email['attachments']

    headers = ""
    body = ""
    attachments = ""
    
    for key, value in header.items():
        k, v = _format_output(key, value)
        k = k.removeprefix('has_')

        headers += f"{k}: [bold]{v}[/bold]\n"
    
    for key, value in bd.items():
        k, v = _format_output(key, value)
        k = k.removeprefix('contains_')
        k = k.replace('percentage', '%')

        body += f"{k}: [bold]{v}[/bold]\n"
    
    for key, value in att.items():
        k, v = _format_output(key, value)

        attachments += f"{k}: [bold]{v}[/bold]\n"
    
    score = f"\nspamassassin: {email['spamassassin']}\tscore: {email['score']:.2f}\n"

    return (score, headers, body, attachments)

def _format_output(k: str, v):
    key = k.replace('_', ' ')
    key = key.capitalize()
    
    if v == True:
        v = f"[green]{v}[/green]"
    elif v == False:
        v = f"[red]{v}[/red]"
    
    if type(v) == float:
        v = f"{v:.4f}"

    return (key, v)