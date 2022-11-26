"""
The package contains the main classes and functions used to analyze the emails.

## Abstraction

In information technology, abstraction is the process of hiding the implementation details from the user
and it is one of the three fundamental concepts of object-oriented programming (OOP).

Here we use abstraction to hide the complexity of the email analysis process from the user. And provide a simple interface to use the package.
The following code showes the core concept of this package:
```python
from spamanalyzer.analyzer import MailAnalyzer

analyser = MailAnalyzer(wordlist)
analysis = await analyser.analyze(email_path)

analysis.is_spam()
```
we istantiate the `MailAnalyzer` class and pass the wordlist to it. Then we call the `analyze` method to get the analysis of the email:
in this way we can also parallelize the analysis of multiple emails.
"""

from spamanalyzer.analyzer.data_structures import Domain, MailAnalysis, MailAnalyzer
from spamanalyzer.analyzer.utils import get_domain, inspect_headers, inspect_body, inspect_attachments

__all__ = [
    "Domain", "MailAnalysis", "MailAnalyzer", "get_domain", "inspect_attachments",
    "inspect_body", "inspect_headers"
]
