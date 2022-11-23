from argparse import ArgumentParser, Namespace, FileType
from spamdetector import __version__
import os

def add_args(parser: ArgumentParser, config: dict) -> None:

    parser.add_argument('-f', '--file', help='The file or directory to analyze', required=True)
    parser.add_argument('-l', '--wordlist', help='A file containing the spam wordlist', default=os.path.expandvars(config['files']['wordlist']), type=FileType('r'))
    parser.add_argument('-H', '--add-headers', help="If set it adds the headers field in the email containig the analysis report", action='store_true')
    parser.add_argument('-w', '--custom-weights', help='A file containing custom weights', default=config['weights'], type=FileType('r'))
    parser.add_argument('-v', '--verbose', help='More program output', action='store_true')
    parser.add_argument('-V', '--version', help='Show program version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('-d', '--debug', help='Show debug messages', action='store_true')
    # add model configuration and training options
    # parser.add_argument('-m', '--model', help='The model to use', default=config['files']['classifier'], type=FileType('rb'))

    # TODO: add csv output format
    parser.add_argument('-fmt', '--output-format', help='Format output in a different way', choices=['json'], metavar='FORMAT', dest='output_format')
    parser.add_argument('-o', '--output-file', help='Write output to a file', type=FileType('w'), metavar='FILE', dest='output_file')
    parser.add_argument('--destination-dir', help='The directory where to save the output', metavar='DIRECTORY', default='.')

def parse_args(args, config: dict) -> Namespace:
    parser = ArgumentParser(
        prog="spam-detector",
        description="A simple spam detector",
        epilog='if you find any bug write an email to matteo.spanio97@gmail.com',
    )
    add_args(parser, config)
    return parser.parse_args(args)
