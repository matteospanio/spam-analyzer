from argparse import ArgumentParser, Namespace, FileType
import yaml

def add_args(parser: ArgumentParser, config: dict) -> None:

    with open('config.yaml') as f:
        yaml_config: dict = yaml.safe_load(f)

    parser.add_argument('-f', '--file', help='The file or directory to analyze', required=True)
    parser.add_argument('-l', '--wordlist', help='A file containing the spam wordlist', default=yaml_config['constants']['wordlist'], type=FileType('r'))
    parser.add_argument('-H', '--add-headers', help="If set it adds the headers field in the email containig the analysis report", action='store_true')
    parser.add_argument('-w', '--custom-weights', help='A file containing custom weights', default=yaml_config['constants']['weights'], type=FileType('r'))
    parser.add_argument('-v', '--verbose', help='More program output', action='store_true')
    parser.add_argument('-V', '--version', help='Show program version', action='version', version=f'%(prog)s {config["project"]["version"]}')
    parser.add_argument('-o', '--output-format', help='Format output in a different way', choices=['csv', 'json'], metavar='FORMAT', dest='output_format', default='')

def parse_args(args, config: dict) -> Namespace:
    parser = ArgumentParser(
        prog=config['project']['name'],
        description=config['project']['description'],
        epilog='if you find any bug write an email to matteo.spanio97@gmail.com'
    )
    add_args(parser, config)
    return parser.parse_args(args)
