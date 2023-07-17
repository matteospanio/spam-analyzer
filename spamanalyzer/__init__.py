"""
.. include:: ../README.md
.. include:: ../docs/classification.md
.. include:: ../docs/requirements.md
.. include:: ../docs/testing.md
"""

from os import path
import tomli
from spamanalyzer.analyzer import *
from .files import handle_configuration_files

__all__ = ["MailAnalyzer", "MailAnalysis", "Domain", "Date"]

with open(path.join(path.dirname(__file__), "..", "pyproject.toml"), "rb") as f:
    __version__ = tomli.load(f)["tool"]["poetry"]["version"]
__config_path__ = path.join(path.expanduser("~"), ".config", "spamanalyzer")

__defaults__ = {
    "SPAMANALYZER_CONF_PATH": __config_path__,
    "SPAMANALYZER_CONF_FILE": path.join(__config_path__, "config.yaml"),
    "SPAMANALYZER_VERSION": __version__,
}

handle_configuration_files()
