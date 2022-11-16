<p style="display:flex;align-items:center;justify-content:center">
    <img src="http://matteospanio.me/assets/images/spam-detector-logo_transparent.png" width="300px" />
</p>

> A fast spam filter written in Python inspired by SpamAssassin.

# What is spam-detector?

spam-detector is a CLI (Command Line Interface) application that aims be a viable alternative to spam filter services written in Python.

This program can catalog the email given in inputs in spam or non-spam givin a score to each parameter analyzed, when the score exceeds a certain threshold it is recognized as spam.

The main features of spam-detector are:

1. spam recognition with the option to receive in output a detailed analysis of the email
2. speed, analysis run in a paralelized way that drastically reduces waiting times
3. it is written in python with its most modern features to ensure software correctness

## Use cases

Basic usage and options samples:

```bash
spam-detector -f /path/to/file
```

In this case the program will use the default configuration and will return the result of the analysis.
The option `-f | --file` is mandatory, at the moment this program does not read from the standard input!

```bash
spam-detector -f /path/to/file -v
```

The option `-v | --verbose` outputs a detailed analysis description for each file taken in consideration.

```bash
spam-detector -f /path/to/file -o json
```

The option `-o | --output-format` defines the format of the program output, at the moment it takes in input only `json` as argument. It ignores the `--verbose` option.
