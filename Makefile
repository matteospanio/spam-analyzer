.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
POETRY := poetry run

define PRINT_HELP_PYSCRIPT
import re, sys

BOLD = '\033[1m'
BLUE = '\033[94m'
END = '\033[0m'

print("Usage: make <target>\n")
print(BOLD + "%-20s%s" % ("target", "description") + END)
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print( BLUE + "%-20s" % (target) + END + "%s" % (help))
endef
export PRINT_HELP_PYSCRIPT

help: ## Show this help
	$(POETRY) python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test clean-docs ## Remove all build, test, coverage and Python artifacts

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -f coverage.xml

clean-docs:
	rm -fr site/

setup: clean ## Install dependencies
	poetry install

test: ## Run tests quickly with the default Python
	$(POETRY) pytest

coverage: ## Run tests with coverage
	$(POETRY) pytest --cov=src --cov-report=term-missing --cov-report=html

build: clean setup ## Build package and check with pyroma
	poetry build
	$(POETRY) pyroma .

deploy: build ## Deploy package to PyPI
	poetry publish

format: ## Format code with yapf, comments with docformatter and sort imports with isort
	$(POETRY) yapf --in-place --recursive ./src ./tests
	$(POETRY) docformatter --config ./pyproject.toml --in-place --recursive ./src ./tests
	$(POETRY) isort .

lint: format ## Lint code with pylint
	$(POETRY) pylint ./src ./tests

docs: ## Generate mkdocs HTML documentation, including API docs
	$(POETRY) mkdocs build

docs-serve: ## Serve mkdocs HTML documentation
	$(POETRY) mkdocs serve

update: ## Update dependencies
	poetry update
	$(POETRY) pre-commit autoupdate
