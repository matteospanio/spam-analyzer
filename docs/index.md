<p style="display:flex;align-items:center;justify-content:center">
    <img src="assets/images/logo_transparent.png" width="300px" />
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

## What is spam-analyzer?

spam-analyzer is a CLI (Command Line Interface) application that aims be a viable alternative to spam filter services.

This program can classify the email given in inputs in spam or non-spam using a machine learning algorithm (Random Forest), the model is trained using a dataset of 19900 emails. Anyway it could be wrong sometimes, if you want to improve the accuracy of the model you can train it with your persolized dataset.

The main features of spam-analyzer are:

1. spam recognition with the option to display a detailed analysis of the email
2. JSON output
3. it can be used as a library in your Python project to extract features from an email
4. it is written in Python with its most modern features to ensure software correctness

### What is spam and how does spam-analyzer know it?

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

About attachments we only know if they are present or not and if they are executable files.

The task could be solved in a programmatic way, chaining a long set of `if` statements based on the features extracted from the email. However, this approach is not scalable and it is not easy to maintain. Moreover, it is not possible to improve the accuracy of the model without changing the code and, the most important, the analysis would be based on the conaissance of the programmer and not on the data. Since we live in the data era, we should use the data to solve the problem, not the programmer's knowledge. So I decided to use a machine learning algorithm to solve the problem using all the features extracted from the email.

# License

spam-analyzer is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html#license-text) license.

This means that you can use, modify and distribute it freely, but you must give credits to the original authors.