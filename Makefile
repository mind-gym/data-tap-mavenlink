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

# PHONY
# =========================================================================
.PHONY: help clean build upload test

## help                    : PHONY, provides help
help : Makefile
	@sed -n 's/^##//p' $<

## build                   : PHONY, builds distribution
build: tmp/.sentinel.build
## upload                  : PHONY, uploads to internal pypiserver
upload: tmp/.sentinel.upload
## test                    : PHONY, runs pytest
test: tmp/.sentinel.test
## discover                : PHONY, runs the tap in discovery mode
discover: tmp/.sentinel.venv-dev
	@echo '{'                                 >  fake_config.json
	echo  '  "token"     : "fake_token",'     >> fake_config.json
	echo  '  "user_agent": "fake_user_agent"' >> fake_config.json
	echo  '}'                                 >> fake_config.json
	$(VENV_DEV)/bin/tap-mavenlink --config fake_config.json --discover
	rm fake_config.json

## clean                   : PHONY, removes sentinel and build files
clean:
	rm -rf tmp
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

## clean-hard              : PHONY, removes sentinel and build files, and virtual environments
clean-hard: clean
	rm -rf $(VENV)

# Install
# =========================================================================
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

# Checks
# =========================================================================
## tmp/.sentinel.test      : runs pytest
tmp/.sentinel.test: tmp/.sentinel.venv-dev $(SRC) $(TESTS)
	@mkdir -p $(@D)
	$(VENV_DEV)/bin/pytest
	touch $@

# Build & Upload
# =========================================================================
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
