# Installation

## PIP

spam-analyzer is available on PyPI, so you can install it with pip:

```bash
pip install spam-analyzer
```

## Poetry

You can also install spam-analyzer with poetry as a dependency of your project:

```bash
poetry add spam-analyzer
```

## Source code

For the latest but not yet released version, you can install it from the source code:

=== "PIP"

    ```bash
    git clone https://github.com/matteospanio/spam-analyzer.git
    cd spam-analyzer
    pip install .
    ```
=== "Poetry"

    ```bash
    git clone https://github.com/matteospanio/spam-analyzer.git
    cd spam-analyzer
    poetry install # or poetry build
    ```

    !!! note
        There are also two make targets that can be used to build the project:

        - `make build` to build the project
        - `make setup` to setup the development environment