<p style="display:flex;align-items:center;justify-content:center">
    <img src="http://matteospanio.me/assets/images/spam-detector-logo_transparent.png" width="300px" />
</p>

> A fast spam filter written in Python inspired by SpamAssassin integrated with machine learning.

[![Build Status](https://travis-ci.org/matteospanio/spam-detector.svg?branch=master)](https://travis-ci.org/matteospanio/spam-detector) [![Coverage Status](https://coveralls.io/repos/github/matteospanio/spam-detector/badge.svg?branch=master)](https://coveralls.io/github/matteospanio/spam-detector?branch=mas

# Table of Contents

- [Table of Contents](#table-of-contents)
- [What is Spam Detector?](#what-is-spam-detector)
- [Installation](#installation)
- [Usage](#usage)
  * [CLI](#cli)
  * [Python](#python)
- [Contributing](#contributing)
- [License](#license)


# What is spam-detector?

spam-detector is a CLI (Command Line Interface) application that aims be a viable alternative to spam filter services.

This program can classify the email given in inputs in spam or non-spam using a machine learning algorithm (Random Forest), the model is trained using a dataset of 19900 emails. Anyway it could be wrong sometimes, if you want to improve the accuracy of the model you can train it with your persolized dataset.

The main features of spam-detector are:

1. spam recognition with the option to display a detailed analysis of the email
2. JSON output
3. it can be used as a library in your Python project to extract features from an email
4. it is written in Python with its most modern features to ensure software correctness

## What is spam and how does spam-detector know it?

The analysis takes in consideration the following main aspects:
- the headers of the email
- the body of the email
- the attachments of the email

Since those are three separated parts of the email, the analysis can be done separately for each of them. The final result is the sum of the three results. This splitting should make possible to perform a faster analysis parallelizing the three parts.

Performance apart, the analysis is done extracting features from the email and then using a machine learning algorithm to classify the email. A detailed explanation of the features extraction is available in the [documentation](http://matteospanio.me/spam-detector/spamdetector/analyzer.html#MailAnalyzer.analyze).


# Installation

spam-detector is available on PyPI, so you can install it with pip:

```bash
pip install spam-detector
```

For the latest version, you can install it from the source code:

```bash
git clone https://github.com/matteospanio/spam-detector.git
cd spam-detector
pip install .
```

# Usage

## CLI

```
usage: spam-detector [-h] -f FILE [-l WORDLIST] [-v] [-V] [-fmt FORMAT] [-o FILE] [--destination-dir DIRECTORY]

A simple spam detector

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

-  `spam-detector -f <file>`: classify the email given in input
-  `spam-detector -f <file> -v`: classify the email given in input and display a detailed analysis
-  `spam-detector -f <file> -fmt json`: classify the email given in input and display the result in JSON format (useful for integration with other programs)
-  `spam-detector -f <file> -fmt json -o <file>`: classify the email given in input and write the result in JSON format in the file given in input
-  `spam-detector -f <file> -l <file>`: classify the email given in input using the wordlist given in input
-  `spam-detector -f <directory> --destination-dir <directory>`: classify all the emails in the directory given in input and copy them in the directory given in input splitted in spam and non-spam folders

### Advertences
1. The `--verbose` option is available only for the first use case, it will not work in combination with the `--output-format` option.
2. You should use the `--output-file` instead of the `>` operator to write the output in a file, because the `spam-detector` program prints some other information on the standard output while processing the email(s).

## Python

```python
from spamdetector import MailAnalyzer

analyzer = MailAnalyzer(wordlist_path="path/to/wordlist.txt")
analysis = analyzer.analyze("path/to/email.txt")
```

The `spamdetector` library provides a really simple interface to extract features from an email. The `MailAnalyzer` class provides the `analyze` method that takes in input the path to the email and returns a `MailAnalysis` object containing the analysis of the email.

Furthermore, the `MailAnalysis` class provides the `is_spam` method that returns `True` if the email is spam, `False` otherwise. Further examples are available in the folder `examples` of the source code.

# Contributing

Contributions are welcome! Please read the [contribution guidelines](CONTRIBUTING.md) first.

# License

spam-detector is licensed under the [GPLv3](LICENSE) license.
