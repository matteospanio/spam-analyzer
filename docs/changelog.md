# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

!!! note
    The *Unreleased* section is for changes that are not yet released, but are
    going to be released in the next version.

## [Unreleased]

### Added

- new specific domain for github pages docs, go to https://docs.spamanalyzer.tech
- getting_started.md page
- installation.md page
- integration tests for the CLI
- docker image for the CLI application
- has been added the `parse` method to the `SpamAnalyzer` class to parse a single mail, use that instead of the mailparser library to don't see unwanted logs
- pre-commit hooks to check the code before committing

### Changed

- changed to async methods for faster execution
- documentation is now generated with mkdocs
- refactored the code to use click instead of argparse
- refactored the code to separate the CLI from the library (also tests)
- `MailAnalyzer` class has been renamed to `SpamAnalyzer
- `MailAnalysis` class has no longer methods to decide if a mail is spam or not, those are now in the `SpamAnalyzer` class
- to make the package really modular, now the classification model can be injected in the `SpamAnalyzer` class (if not provided, the default one will be used)
- config folder is now created in the standard OS path for configuration files using click

### Fixed

- configuration files are now properly installed
- now there's a better timezone detection and management


## [0.2.0] - 2023-07-17

### Changed
- switched to poetry for dependency management
- updated all build/ci tools to use poetry
