"""
.. include:: ../README.md
.. include:: ../docs/classification.md
.. include:: ../docs/requirements.md
.. include:: ../docs/testing.md

# API Documentation
"""

from os import path
from spamdetector.analyzer import *

__all__ = ['MailAnalyzer', 'MailAnalysis']

__version__ = "0.0.1"
__config_path__ = path.join(path.expanduser('~'), '.config', 'spamdetector')

__defaults__ = {
    "SPAMDETECTOR_CONF_PATH": __config_path__,
    "SPAMDETECTOR_CONF_FILE": path.join(__config_path__, "config.yaml"),
    "SPAMDETECTOR_VERSION": __version__,
}