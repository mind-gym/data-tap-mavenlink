SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

PYTHON := python3.9
SRC := $(shell find tap_mavenlink -type f -name "*.py" -or -name "*.json")
TESTS := $(shell find tests -type f -name "*.py")
VENV := ./.venv
VENV_DEV := $(VENV)/dev
VENV_BUILD := $(VENV)/build

.PHONY: help clean build upload test

## help                    : PHONY, provides help
help : Makefile
	@sed -n 's/^##//p' $<

## build                   : PHONY, builds distribution
## upload                  : PHONY, uploads to internal pypiserver
## test                    : PHONY, runs pytest
build: tmp/.sentinel.build
upload: tmp/.sentinel.upload
test: tmp/.sentinel.test

## clean                   : PHONY, removes virtual environments
clean:
	rm -rf tmp
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf $(VENV)

## tmp/.sentinel.venv-dev  : installs virtual environment for dev
tmp/.sentinel.venv-dev: setup.py pyproject.toml
	@mkdir -p $(@D)
	if [[ -d $(VENV_DEV) ]]; then
		rm -rf $(VENV_DEV)
	fi
	$(PYTHON) -m venv $(VENV_DEV)
	$(VENV_DEV)/bin/pip install --upgrade pip .[dev]
	touch $@

## tmp/.sentinel.venv-build: installs virtual environment for build & upload
tmp/.sentinel.venv-build: setup.py pyproject.toml
	@mkdir -p $(@D)
	if [[ -d $(VENV_BUILD) ]]; then
		rm -rf $(VENV_BUILD)
	fi
	$(PYTHON) -m venv $(VENV_BUILD)
	$(VENV_BUILD)/bin/pip install --upgrade pip build twine
	touch $@

## tmp/.sentinel.build     : creates a source & binary distribution
tmp/.sentinel.build: tmp/.sentinel.venv-build $(SRC)
	@mkdir -p $(@D)
	$(VENV_BUILD)/bin/python -m build
	touch $@

## tmp/.sentinel.upload    : uploads dist to pypiserver
tmp/.sentinel.upload: tmp/.sentinel.build
	@mkdir -p $(@D)
	$(VENV_BUILD)/bin/twine upload \
		--non-interactive \
		--verbose \
		--username . \
		--password . \
		--repository-url $(PYPISERVER_URL) \
		dist/*
	touch $@

## tmp/.sentinel.test      : runs pytest
tmp/.sentinel.test: tmp/.sentinel.venv-dev $(SRC) $(TESTS)
	@mkdir -p $(@D)
	$(VENV_DEV)/bin/pytest
	touch $@
