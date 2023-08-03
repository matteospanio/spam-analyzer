<p style="display:flex;align-items:center;justify-content:center">
    <img src="docs/assets/images/logo_transparent.png" width="300px" />
</p>

> A fast spam filter written in Python inspired by SpamAssassin integrated with machine learning.

[![test workflow](https://github.com/matteospanio/spam-analyzer/actions/workflows/test.yml/badge.svg)](https://github.com/matteospanio/spam-analyzer/actions/workflows/test.yml/badge.svg)
![CircleCI](https://img.shields.io/circleci/build/github/matteospanio/spam-analyzer?label=circleci-build&logo=CIRCLECI)
[![Coverage Status](https://coveralls.io/repos/github/matteospanio/spam-analyzer/badge.svg?branch=master)](https://coveralls.io/github/matteospanio/spam-analyzer?branch=master)
[![PyPI version](https://badge.fury.io/py/spam-analyzer.svg)](https://badge.fury.io/py/spam-analyzer)
![PyPI - Status](https://img.shields.io/pypi/status/spam-analyzer)
[![Python version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)](https://img.shields.io/badge/python-3.10%20%7C%203.7%20%7C%203.11-blue)
[![Downloads](https://pepy.tech/badge/spam-analyzer)](https://pepy.tech/project/spam-analyzer)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Dependencies](https://img.shields.io/librariesio/github/matteospanio/spam-analyzer)](https://libraries.io/github/matteospanio/spam-analyzer)

# Table of Contents

- [Table of Contents](#table-of-contents)
- [What is Spam Analyzer?](#what-is-spam-analyzer)
- [Installation](#installation)
- [Usage](#usage)
  * [CLI](#cli)
  * [Python](#python)
- [Contributing](#contributing)
- [License](#license)


# What is spam-analyzer?

spam-analyzer is a CLI (Command Line Interface) application that aims be a viable alternative to spam filter services.

This program can classify the email given in inputs in spam or non-spam using a machine learning algorithm (Random Forest), the model is trained using a dataset of 19900 emails. Anyway it could be wrong sometimes, if you want to improve the accuracy of the model you can train it with your persolized dataset.

The main features of spam-analyzer are:

1. spam recognition with the option to display a detailed analysis of the email
2. JSON output
3. it can be used as a library in your Python project to extract features from an email
4. it is written in Python with its most modern features to ensure software correctness
5. extensible with plugins
6. 100% containerized with Docker

## What is spam and how does spam-analyzer know it?

The analysis takes in consideration the following main aspects:
- the headers of the email
- the body of the email
- the attachments of the email

The most significant parts are the headers and the body of the email. The headers are analyzed to extract the following features:
- SPF (Sender Policy Framework)
- DKIM (DomainKeys Identified Mail)
- DMARC (Domain-based Message Authentication, Reporting & Conformance)
- If the sender domain is the same as the first in received headers
- The subject of the email
- The send date
- If the send date is compliant to the RFC 2822 and if it was sent from a valid time zone
- The date of the first received header

While the body is analyzed to extract the following features:
- If there are links
- If there are images
- If links are only http or https
- The percentage of the body that is written in uppercase
- The percentage of the body that contains blacklisted words
- The polarity of the body calculated with TextBlob
- The subjectivity of the body calculated with TextBlob
- If it contains mailto links
- If it contains javascript code
- If it contains html code
- If it contains html forms

The task could be solved in a programmatic way, chaining a long set of `if` statements based on the features extracted from the email. However, this approach is not scalable and it is not easy to maintain. Moreover, it is not possible to improve the accuracy of the model without changing the code and, the most important, the analysis would be based on the conaissance of the programmer and not on the data. Since we live in the data era, we should use the data to solve the problem, not the programmer's knowledge. So I decided to use a machine learning algorithm to solve the problem using all the features extracted from the email.

# Installation

spam-analyzer is available on PyPI, so you can install it with pip:

```bash
pip install spam-analyzer
```

For the latest version, you can install it from the source code:

```bash
git clone https://github.com/matteospanio/spam-analyzer.git
cd spam-analyzer
pip install .
```

# Usage

## CLI

spam-analyzer can be used as a CLI application:

```
Usage: spam-analyzer [OPTIONS] COMMAND [ARGS]...

  A simple program to analyze emails.

Options:
  -h, --help                Show this message and exit.
  -v, --verbose             Enables verbose mode.
  --version                 Show the version and exit.
  -C, --config CONFIG_PATH  Location of the configuration file. Supports glob
                            pattern of local path and remote URL.

Commands:
  analyze    Analyze emails from a file or directory.
  configure  Configure the program.
  plugins    Show all available plugins.
```

-  `spam-analyzer analyze <file>`: classify the email given in input
-  `spam-analyzer -v analyze <file>`: classify the email given in input and display a detailed analysis[^1]
-  `spam-analyzer analyze -fmt json <file>`: classify the email given in input and display the result in JSON format (useful for integration with other programs)
-  `spam-analyzer analyze -fmt json -o <outpath> <file> `: classify the email given in input and write the result in JSON format in the file given in input[^2]
-  `spam-analyzer analyze -l <wordlist> <file>`: classify the email given in input using the wordlist given in input

### Configuration

`spam-analyzer` is thought to be highly configurable: on its first execution it will create a configuration file in `~/.config/spamanalyzer/` with some other default files. You can change the configuration file to customize the behavior of the program. At the moment of writing there are only paths to the wordlist and the model, but in the future there will be more options (e.g. senders blacklist and whitelist, a default path where to copy classified emails,...).

[^1]: The `--verbose` option is available only for the first use case, it will not work in combination with the `--output-format` option.

[^2]: You should use the `--output-file` instead of the `>` operator to write the output in a file, because the `spam-analyzer` program prints some other information on the standard output while processing the email(s).

## Python

```python
from spamanalyzer import SpamAnalyzer

analyzer = SpamAnalyzer(forbidden_words=["viagra", "cialis"])
analysis = await analyzer.analyze("path/to/email.txt")
```

The `spamanalyzer` library provides a really simple interface to extract features from an email. The `SpamAnalyzer` class provides the `analyze` method that takes in input the path to the email and returns a `SpamAnalyzer` object containing the analysis of the email.

Furthermore, the `MailAnalysis` class provides the `is_spam` method that returns `True` if the email is spam, `False` otherwise. Further examples are available in the folder `examples` of the source code.

# Contributing

Contributions are welcome! Please read the [contribution guidelines](CONTRIBUTING.md) first.

# License

spam-analyzer is licensed under the [GPLv3](LICENSE) license.
