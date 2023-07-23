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

### Changed

- documentation is now generated with mkdocs
- refactored the code to use click instead of argparse
- refactored the code to separate the CLI from the library (also tests)

### Fixed

- configuration files are now properly installed


## [0.2.0] - 2023-07-17

### Changed
- switched to poetry for dependency management
- updated all build/ci tools to use poetry
