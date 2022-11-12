import yaml

from app import app, cli


def main():    
    with open('config.yaml') as f:
        config: dict = yaml.safe_load(f)

    args = cli.parse_args(config)

    app(args.file, args.wordlist, args.ignore_headers, args.ignore_body, args.verbose)


if __name__ == '__main__':
    main()