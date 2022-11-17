Here there is a recap of software design choices I made.

## What is spam?

The analysis takes in consideration the following main aspects:[^1]
- the headers of the email
- the body of the email
- the attachments of the email

[^1]: for further details about analysis rules look at [the documentation](http://matteospanio.me/spam-detector/spamdetector/analyzer.html#MailAnalyzer.analyze)

Since those are three separated parts of the email, the analysis is done separately for each of them. The final result is the sum of the three results. This splitting makes possible to perform a faster analysis parallelizing the three parts.

## Requirements
| Done | Name | Priority | Description |
|:-:|---|:--:|--|
| ✔️ | Analyze single files | high | The app should take in input a single email file and analyze it. |
| ✔️ | Analyze a list of files | high | The app should take in input a list of email files and analyze them. |
| ✔ | Handle non-mail files | high | The app should gently handle non email files, notifying to the user a wrong input, but should not stop its execution |
| 🚧 | Output spam score | high | The app should output a spam score for each analyzed email like spamassassin. |
| 🚧 | Output the analysis results | high | The app should output the analysis results in varoius formats (currently only json is aviable) to make possible further analysis with other tools |
| ❌ | Assign custom weights for spam scoring | medium | The app should take in input a configuration file to assign custom weights for spam scoring
| ❌ | Modular rules | low | The app should take in input a configuration file to assign a custom set of rules for spam scoring

✔️ = done | 🚧 = in progress | ❌ = todo
