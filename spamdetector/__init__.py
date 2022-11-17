"""
.. include:: ../README.md
.. include:: ../docs/requirements.md
.. include:: ../docs/performance.md
.. include:: ../CONTRIBUTING.md
.. include:: ../docs/testing.md
"""

from os import path
from spamdetector.analyzer import *

__version__ = "0.0.1"
__config_path__ = path.join(path.expanduser('~'), '.config', 'spamdetector')
__alternative_config_path__ = '/etc/spamdetector'

__defaults__ = {
    "SPAMDETECTOR_CONF_PATH": __config_path__,
    "SPAMDETECTOR_ALT_CONF_PATH": __alternative_config_path__,
    "SPAMDETECTOR_CONF_FILE": path.join(__config_path__, "config.yaml"),
    "SPAMDETECTOR_VERSION": __version__,
}

