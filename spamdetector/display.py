import json
import rich
from rich.panel import Panel
from rich.text import Text
from rich.console import Console, Group
from rich.columns import Columns
from rich.table import Table
from spamdetector import MailAnalysis

COLORS = {
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
}

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
    """Prints the output of the MailAnalysis in the specified format (csv, json or default).

    Args:
        data (list): a list of data to output
        output_format (str): the type of output (csv | json | default)
        verbose (bool): valid only for `default` output_format, it prints a description for each element of the list
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
        if score <= 3.1:
            count += 1
            total_ok_score += score
        else:
            total_spam_score += score
        if verbose:
            renderables.append(_print_details(analysis))

    if verbose:
        with console.pager(styles=True):
            console.print(Columns(renderables, equal=True))

    _print_summary(count, len(data) - count, total_ok_score, total_spam_score)

def _print_summary(ok_count, spam_count, total_ok_score, total_spam_score) -> None:
    table = Table(title="Summary", box=rich.box.ROUNDED, highlight=True)
    
    table.add_column("Email class", justify="center")
    table.add_column("Quantity", justify="center")
    table.add_column("Mean score", justify="center")
    
    table.add_row("[green][bold]OK[/bold][/green]", str(ok_count), str(total_ok_score / (ok_count if ok_count > 0 else 1)))
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
        pkey = key.removeprefix('has_')
        pkey = pkey.replace('_', ' ')
        pkey = pkey.capitalize()

        if value == True:
            value = f"[green]{value}[/green]"
        elif value == False:
            value = f"[red]{value}[/red]"

        headers += f"{pkey}: [bold]{value}[/bold]\n"
    
    for key, value in bd.items():
        pkey = key.removeprefix('contains_')
        pkey = pkey.replace('_', ' ')
        pkey = pkey.replace('percentage', '%')
        pkey = pkey.capitalize()

        if value == True:
            value = f"[green]{value}[/green]"
        elif value == False:
            value = f"[red]{value}[/red]"

        if type(value) == float:
            value = f"{value:.4f}"
        
        body += f"{pkey}: [bold]{value}[/bold]\n"
    
    for key, value in att.items():
        pkey = key.replace('_', ' ')
        pkey = pkey.capitalize()

        if value == True:
            value = f"[green]{value}[/green]"
        elif value == False:
            value = f"[red]{value}[/red]"

        attachments += f"{pkey}: [bold]{value}[/bold]\n"
    
    score = f"\nspam: {email['is_spam']}\tscore: {email['score']:.2f}\n"

    return (score, headers, body, attachments)