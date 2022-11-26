"""
.. include:: ../README.md
.. include:: ../docs/classification.md
.. include:: ../docs/requirements.md
.. include:: ../docs/testing.md

# API Documentation
"""

from os import path
from spamanalyzer.analyzer import *

__all__ = ['MailAnalyzer', 'MailAnalysis', 'Domain', 'Date']

__version__ = "0.0.1"
__config_path__ = path.join(path.expanduser('~'), '.config', 'spamanalyzer')

__defaults__ = {
    "SPAMANALYZER_CONF_PATH": __config_path__,
    "SPAMANALYZER_CONF_FILE": path.join(__config_path__, "config.yaml"),
    "SPAMANALYZER_VERSION": __version__,
}