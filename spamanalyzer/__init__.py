"""
.. include:: ../README.md
.. include:: ../docs/classification.md
.. include:: ../docs/requirements.md
.. include:: ../docs/testing.md
"""

from os import path
from spamanalyzer.analyzer import *
from .files import handle_configuration_files

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version


def __get_package_version():
    try:
        return package_version("spam-analyzer")
    except PackageNotFoundError:
        return "Version information not available. Make sure you have installed your package using Poetry."


__all__ = ["MailAnalyzer", "MailAnalysis", "Domain", "Date"]
__version__ = __get_package_version()
__config_path__ = path.join(path.expanduser("~"), ".config", "spamanalyzer")

__defaults__ = {
    "SPAMANALYZER_CONF_PATH": __config_path__,
    "SPAMANALYZER_CONF_FILE": path.join(__config_path__, "config.yaml"),
    "SPAMANALYZER_VERSION": __version__,
}

handle_configuration_files()
