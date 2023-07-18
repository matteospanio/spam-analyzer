---
title: Usage
summary: How to use spam-analyzer
author: Matteo Spanio
date: 2023-07-18

---

# Usage

## CLI

spam-analyzer can be used as a CLI application:

```
usage: spam-analyzer [-h] -f FILE [-l WORDLIST] [-v] [-V] [-fmt FORMAT] [-o FILE] [--destination-dir DIRECTORY]

A simple program to analyzer emails

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The file or directory to analyze
  -l WORDLIST, --wordlist WORDLIST
                        A file containing the spam wordlist
  -v, --verbose         More program output
  -V, --version         Show program version
  -fmt FORMAT, --output-format FORMAT
                        Format output in a different way
  -o FILE, --output-file FILE
                        Write output to a file (works only for json format)
  --destination-dir DIRECTORY
                        The directory where copy your classified emails
```

-  `spam-analyzer -f <file>`: classify the email given in input
-  `spam-analyzer -f <file> -v`: classify the email given in input and display a detailed analysis[^1]
-  `spam-analyzer -f <file> -fmt json`: classify the email given in input and display the result in JSON format (useful for integration with other programs)
-  `spam-analyzer -f <file> -fmt json -o <file>`: classify the email given in input and write the result in JSON format in the file given in input[^2]
-  `spam-analyzer -f <file> -l <file>`: classify the email given in input using the wordlist given in input
-  `spam-analyzer -f <directory> --destination-dir <directory>`: classify all the emails in the directory given in input and copy them in the directory given in input splitted in spam and non-spam folders

### Configuration

`spam-analyzer` is thought to be highly configurable: on its first execution it will create a configuration file in `~/.config/spamanalyzer/` with some other default files. You can change the configuration file to customize the behavior of the program. At the moment of writing there are only paths to the wordlist and the model, but in the future there will be more options (e.g. senders blacklist and whitelist, a default path where to copy classified emails,...).

[^1]: The `--verbose` option is available only for the first use case, it will not work in combination with the `--output-format` option.

[^2]: You should use the `--output-file` instead of the `>` operator to write the output in a file, because the `spam-analyzer` program prints some other information on the standard output while processing the email(s).

## Python library

```python
from spamanalyzer import MailAnalyzer

analyzer = MailAnalyzer(wordlist_path="path/to/wordlist.txt")
analysis = analyzer.analyze("path/to/email.txt")
```

The `spamanalyzer` library provides a really simple interface to extract features from an email. The `MailAnalyzer` class provides the `analyze` method that takes in input the path to the email and returns a `MailAnalysis` object containing the analysis of the email.

Furthermore, the `MailAnalysis` class provides the `is_spam` method that returns `True` if the email is spam, `False` otherwise. Further examples are available in the folder `examples` of the source code.