Here there is a recap of software design choices I made.

## Architecture

This is a standard CLI application: it takes input files and options from the command line, and outputs an email analysis to the command line. 

## Use cases

A basic usage sample:

```bash
spam-detector -f /path/to/file
```

In this case the program will use the default configuration and will return the result of the analysis.

## What is spam?

The analysis takes in consideration the following main aspects:
- the headers of the email
- the body of the email
- the attachments of the email

Since those are three separated parts of the email, the analysis is done separately for each of them. The final result is the sum of the three results. This splitting makes possible to perform a faster analysis parallelizing the three parts.

## Requirements
| Done | Name | Priority | Description |
|:-:|---|:--:|--|
| 🚧 | Analyze single files | high | The app should take in input a single email file and analyze it. |
| 🚧 | Analyze a list of files | high | The app should take in input a list of email files and analyze them. |
| 🚧 | Output spam score | high | The app should output a spam score for each analyzed email like spamassassin. |
| 🚧 | Output the analysis results | high | The app should output the analysis results in varoius formats to make possible further analysis with other tools |
| ❌ ️ | Assign custom weights for spam scoring | medium | The app should take in input a configuration file to assign custom weights for spam scoring

✔️ = done

🚧 = in progress

❌ = TODO