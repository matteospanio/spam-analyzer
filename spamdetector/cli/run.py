import toml

from spamdetector import _app
from spamdetector.cli import parser


def main(args=None):
    """
    The tool entry point, in order it:
    1. loads the configuration
    2. parses the arguments
    3. starts the application
    """
    config= toml.load('pyproject.toml')

    args = parser.parse_args(args, config)

    _app(args.file, args.wordlist, args.add_headers, args.verbose, args.output_format)


if __name__ == '__main__':
    main()
