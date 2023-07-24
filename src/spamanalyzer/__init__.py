"""
The package contains the main classes and functions used to analyze the emails.

## Abstraction

In information technology, abstraction is the process of hiding the implementation
details from the user and it is one of the three fundamental concepts of object-oriented
programming (OOP).

Here we use abstraction to hide the complexity of the email analysis process from the
user. And provide a simple interface to use the package.
The following code showes the core concept of this package:
```python
from spamanalyzer.analyzer import MailAnalyzer

analyser = MailAnalyzer(wordlist)
analysis = analyser.analyze(email_path) # in the future we will support asynchroneous
analysis

analysis.is_spam()
```
we istantiate the `MailAnalyzer` class and pass the wordlist to it. Then we call the
`analyze` method to get the analysis of the email:
in this way we can also parallelize the analysis of multiple emails.
"""

from os import path

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version

from spamanalyzer.data_structures import MailAnalyzer, MailAnalysis
from spamanalyzer.date import Date
from spamanalyzer.domain import Domain
from . import utils
from app.files import handle_configuration_files


def __get_package_version__():
    try:
        return package_version("spam-analyzer")
    except PackageNotFoundError:
        return (
            "Version information not available."
            "Make sure you have installed your package using Poetry."
        )


__all__ = ["MailAnalyzer", "MailAnalysis", "Domain", "Date", "utils"]
__config_path__ = path.join(path.expanduser("~"), ".config", "spamanalyzer")

__defaults__ = {
    "SPAMANALYZER_CONF_PATH": __config_path__,
    "SPAMANALYZER_CONF_FILE": path.join(__config_path__, "config.yaml"),
}

handle_configuration_files()
