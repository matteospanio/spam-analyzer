import asyncio
import functools
from typing import List

from click_extra import Command, command

# The list to hold registered plugin commands
plugin_commands: List[Command] = []


def plugin(func):
    """Decorator to register a function as a plugin command."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    _command = command(name=func.__name__)(wrapper)
    plugin_commands.append(_command)

    return _command


def async_command(coro_func):
    """Decorator for async commands."""

    @functools.wraps(coro_func)
    def sync_func(*args, **kwargs):
        return asyncio.run(coro_func(*args, **kwargs))

    return sync_func
