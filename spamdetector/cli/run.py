import toml

from spamdetector import app
from spamdetector.cli import parser


def main(args=None):
    config= toml.load('pyproject.toml')

    args = parser.parse_args(args, config)

    app(args.file, args.wordlist, args.ignore_headers, args.ignore_body, args.verbose, args.output_format)


if __name__ == '__main__':
    main()
