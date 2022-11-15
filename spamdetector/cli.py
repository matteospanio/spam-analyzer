from argparse import ArgumentParser, Namespace, FileType

def add_args(parser: ArgumentParser, config: dict) -> None:
    """Add arguments to the parser

    Args:
        parser (ArgumentParser): the parser object
        config (dict): a dictionary containing the configuration
    """
    parser.add_argument('-f', '--file', help='The file or directory to analyze', required=True)
    parser.add_argument('-l', '--wordlist', help='A file containing the spam wordlist', default=config['constants']['wordlist'], type=FileType('r'))
    parser.add_argument('-H', '--ignore-headers', help="Don't check headers fields", action='store_true')
    parser.add_argument('-B', '--ignore-body', help="Don't parse body content", action='store_true')
    parser.add_argument('-v', '--verbose', help='More program output', action='store_true')
    parser.add_argument('-V', '--version', help='Show program version', action='version', version=f'%(prog)s {config["version"]}')
    parser.add_argument('-o', '--output-format', help='Format output in a different way', choices=['csv', 'json'], metavar='FORMAT', dest='output_format', default='')

def parse_args(args, config: dict) -> Namespace:
    """Read arguments from the command line

    Args:
        config (dict): a dictionary containing the configuration

    Returns:
        Namespace: a dictionary containing the arguments
    """
    parser = ArgumentParser(
        prog=config['name'],
        description=config['description'],
        epilog='if you find any bug write an email to matteo.spanio97@gmail.com'
    )
    add_args(parser, config)
    return parser.parse_args(args)
