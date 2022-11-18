import shutil
import json

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
    for analysis in data:
        score = analysis.get_score() <= 4.1
        if score:
            count += 1
        print(f"{analysis.file_path.split('.')[0]}: {analysis.is_spam()}\t{score} {analysis.get_score()}")
    print(count)

def _print_center(text: str, char: str) -> None:
    col, _ = shutil.get_terminal_size()
    print(text.center(col, char))
