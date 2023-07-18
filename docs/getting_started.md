# Getting started

## Installation

```bash
pip install spam-analyzer
```

## CLI tool

Run `spam-analyzer --help` to see the available options.

### Example

```bash
spam-analyzer -f email.txt
```

## Python library

```python
from spamanalyzer import MailAnalyzer

analyzer = MailAnalyzer(blacklist=["cash", "money", "!!!"])
analysis = analyzer.analyze("email.txt")
```
