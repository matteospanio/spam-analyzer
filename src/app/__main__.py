import importlib.util
import os
import sys

import click
import click_extra
from click import Context

import app.files as files
import spamanalyzer.plugins as plugins
from app.__analyzer import analyze

config_dir = click.get_app_dir("spam-analyzer")


@click.group()
@click_extra.help_option
@click_extra.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click_extra.extra_version_option(package_name="spam-analyzer")
@click_extra.config_option
@click_extra.pass_context
def cli(ctx: Context, verbose: bool) -> None:
    """A simple program to analyze emails."""
    # ctx.verbose = verbose
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.group(name="plugins")
@click_extra.pass_context
def show_plugins(ctx: Context) -> None:
    """Show all available plugins."""
    pass


@cli.group()
@click_extra.help_option
def configure():
    """Configure the program."""
    pass


@configure.command()
def edit():
    """Edit the configuration file."""

    click.edit(filename=os.path.join(config_dir, "config.yaml"))
    sys.exit(0)


@configure.command()
def show():
    """Show the configuration file."""

    conf_file = os.path.join(config_dir, "config.yaml")
    with click.open_file(conf_file, "r", encoding="utf-8") as f:
        click.echo(f.read())

    sys.exit(0)


@configure.command()
@click.confirmation_option(
    prompt="Are you sure you want to reset the configuration file?")
def reset():
    """Reset the configuration file."""

    os.remove(os.path.join(config_dir, "config.yaml"))
    files.copy_config_file(config_dir)

    sys.exit(0)


def load_plugins():
    plugin_folder = os.path.join(config_dir, "plugins")
    if os.path.exists(plugin_folder):
        for filename in os.listdir(plugin_folder):
            if filename.endswith(".py"):
                module_name = filename[:-3]
                module_path = os.path.join(plugin_folder, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                if spec is not None:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)  ## type: ignore


def main():
    # Create the configuration directory if it doesn't exist
    if not os.path.exists(config_dir):
        _ = files.handle_configuration_files()

    # Load the plugins and add them to the Click app
    load_plugins()

    for command in plugins.plugin_commands:
        show_plugins.add_command(command)

    cli.add_command(analyze)
    cli()
