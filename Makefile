.PHONY: clean-pyc clean-build docs clean

TEST_FLAGS=--verbose
COVER_FLAGS=--cov=orb_api

install:  ## Install project requirements
	pip install -r requirements.txt
	python setup.py develop

clean: clean-build clean-pyc clean-test-all  ## Remove all build and test artifacts

clean-build:  ## Remove build artifacts only
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

clean-pyc:  ## Remove pyc files and friends
	-@find . -name '*.pyc' -follow -print0 | xargs -0 rm -f &> /dev/null
	-@find . -name '*.pyo' -follow -print0 | xargs -0 rm -f &> /dev/null
	-@find . -name '__pycache__' -type d -follow -print0 | xargs -0 rm -rf &> /dev/null

clean-test:  ## Remove coverage artifacts
	rm -rf .coverage coverage*
	rm -rf tests/.coverage test/coverage*
	rm -rf htmlcov/

clean-test-all: clean-test  ## Remove all tox environments
	rm -rf .tox/

lint:
	flake8 orb_api

test:  ## Run the tests
	pytest ${TEST_FLAGS}

test-coverage: clean-test  ## Run the tests with verbosity and coverage
	-py.test ${COVER_FLAGS} ${TEST_FLAGS}
	@exit_code=$?
	@-coverage html
	@exit ${exit_code}

test-all:  ## Run the full suite for all environments
	tox


check: clean-build clean-pyc clean-test lint test-coverage

build: clean  ## Create distribution files for release
	python setup.py sdist bdist_wheel

release: build  ## Create distribution files and publish to PyPI
	python setup.py check -r -s
	twine upload dist/*

sdist: clean  ##sdist Create source distribution only
	python setup.py sdist
	ls -l dist

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html


help:
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
