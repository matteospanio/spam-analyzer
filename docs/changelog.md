# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

!!! note
    The *Unreleased* section is for changes that are not yet released, but are
    going to be released in the next version.


## [1.0.11]

### Changed

- update dependencies
- update test gh workflow

## [1.0.10]

### Changed

- update dependencies
- add python 3.12 to the supported versions
- update the documentation
- refactor coverage configuration inside pyproject.toml

## [1.0.9]

### Added

- py.typed file to make the package PEP 561 compliant
- missing type annotations

### Fixed

- type annotations typos
- update dependencies
- erroneous docstrings

## [1.0.8]

### Fixed

- update gitpython to fix security vulnerabilities
- update dependencies

## [1.0.1..7]

### Fixed

- updated dependencies to fix security vulnerabilities

## [1.0.0]

### Added

- new specific domain for github pages docs, go to https://docs.spamanalyzer.tech
- getting_started.md page
- installation.md page
- integration tests for the CLI
- docker image for the CLI application
- has been added the `parse` method to the `SpamAnalyzer` class to parse a single mail, use that instead of the mailparser library to don't see unwanted logs
- pre-commit hooks to check the code before committing
- plugin system to extend the CLI application

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
