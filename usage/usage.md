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

## Python library

```python
--8<-- "examples/analyzer.py"
```

The `spamanalyzer` library provides a really simple interface to extract features from an email. The `SpamAnalyzer` class provides the `analyze` method that takes in input the path to the email and returns a `MailAnalysis` object containing the analysis of the email.

Furthermore, the `MailAnalysis` class provides the `is_spam` method that returns `True` if the email is spam, `False` otherwise. Further examples are available in the folder `examples` of the source code.
