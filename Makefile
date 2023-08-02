MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

all: install export-requirements test

dev: install

test: unit-tests

unit-tests:
	poetry run pytest tests/*.py

export-requirements:
	poetry export -f requirements.txt --output requirements.txt

install:
	poetry install