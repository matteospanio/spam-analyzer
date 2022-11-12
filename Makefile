setup:
	pip install -r requirements.txt

run:
	python spam-detector.py -f data/00.1d30d499c969369915f69e7cf1f5f5e3fdd567d41e8721bf8207fa52a78aff9a -v

test:
	pytest

build-local:
	python setup.py develop

build:
	python setup.py sdist bdist_wheel

deploy:
	twine upload --repository testpypi --skip-existing dist/*

help:
	$(info "Usage: make [setup|run|test|build-local|build|deploy|help]")