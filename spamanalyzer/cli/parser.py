from argparse import ArgumentParser, Namespace, FileType
from spamanalyzer import __version__
import os


def add_args(parser: ArgumentParser, config: dict) -> None:
    parser.add_argument("-f",
                        "--file",
                        help="The file or directory to analyze",
                        required=True)
    parser.add_argument(
        "-l",
        "--wordlist",
        help="A file containing the spam wordlist",
        default=os.path.expanduser(config["files"]["wordlist"]),
        type=FileType("r"),
    )
    parser.add_argument("-v",
                        "--verbose",
                        help="More program output",
                        action="store_true")
    parser.add_argument(
        "-V",
        "--version",
        help="Show program version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    # add model configuration and training options
    # parser.add_argument(
    # '-m', '--model', help='The model to use',
    # default=config['files']['classifier'], type=FileType('rb'))

    # TODO: add csv output format
    parser.add_argument(
        "-fmt",
        "--output-format",
        help="Format output in a different way",
        choices=["json"],
        metavar="FORMAT",
        dest="output_format",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="Write output to a file (works only for json format)",
        type=FileType("w"),
        metavar="FILE",
        dest="output_file",
    )
    parser.add_argument(
        "--destination-dir",
        help="The directory where copy your classified emails",
        metavar="DIRECTORY",
        default=None,
    )


def parse_args(args, config: dict) -> Namespace:
    parser = ArgumentParser(
        prog="spam-analyzer",
        description="A simple program to analyzer emails",
        epilog="if you find any bug write an email to matteo.spanio97@gmail.com",
    )
    add_args(parser, config)
    return parser.parse_args(args)
