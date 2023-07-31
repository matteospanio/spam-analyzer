import click

from spamanalyzer.plugins import plugin


@plugin
@click.option("--name", default="World", help="Who to say hello to.")
def hello(name: str) -> None:
    """A simple plugin to say hello."""
    print(f"Hello, {name}!")
