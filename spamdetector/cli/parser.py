import yaml, os, shutil
from importlib.resources import files
from argparse import ArgumentParser, Namespace, FileType, ArgumentDefaultsHelpFormatter
from spamdetector import __version__, __defaults__

def add_args(parser: ArgumentParser) -> None:

    config_file = files('conf').joinpath('config.yaml')
    wordlist_file = files('conf').joinpath('word_blacklist.txt')
    
    if not os.path.exists(__defaults__['SPAMDETECTOR_CONF_PATH']):
        os.makedirs(__defaults__['SPAMDETECTOR_CONF_PATH'])
        shutil.copy(wordlist_file, __defaults__['SPAMDETECTOR_CONF_PATH'])
    
    if not os.path.exists(__defaults__['SPAMDETECTOR_CONF_FILE']):
        shutil.copy(config_file, __defaults__['SPAMDETECTOR_CONF_FILE'])

    with open(__defaults__['SPAMDETECTOR_CONF_FILE']) as f:
        try:
            config: dict = yaml.safe_load(f)
        except Exception:
            raise Exception('Error while loading config file')

    parser.add_argument('-f', '--file', help='The file or directory to analyze', required=True)
    parser.add_argument('-l', '--wordlist', help='A file containing the spam wordlist', default=os.path.join(__defaults__['SPAMDETECTOR_CONF_PATH'], config['files']['wordlist']), type=FileType('r'))
    parser.add_argument('-H', '--add-headers', help="If set it adds the headers field in the email containig the analysis report", action='store_true')
    parser.add_argument('-w', '--custom-weights', help='A file containing custom weights', default=config['weights'], type=FileType('r'))
    parser.add_argument('-v', '--verbose', help='More program output', action='store_true')
    parser.add_argument('-V', '--version', help='Show program version', action='version', version=f'%(prog)s {__version__}')
    # TODO: add csv output format
    parser.add_argument('-o', '--output-format', help='Format output in a different way', choices=['json'], metavar='FORMAT', dest='output_format')

def parse_args(args) -> Namespace:
    parser = ArgumentParser(
        prog="spam-detector",
        description="A simple spam detector",
        epilog='if you find any bug write an email to matteo.spanio97@gmail.com',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    add_args(parser)
    return parser.parse_args(args)
