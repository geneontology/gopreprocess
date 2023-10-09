MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

all: install

dev: install

test: unit-tests lint spell

lint:
	poetry run tox -e lint-fix

spell:
	poetry run tox -e codespell

unit-tests:
	poetry run pytest tests/*.py

install:
	poetry install

human:
	poetry run convert_annotations --namespaces 'HUMAN','UniProtKB' --target_taxon "NCBITaxon:10090" --source_taxon "NCBITaxon:9606" --ortho_reference "GO_REF:0000096"

rat:
	poetry run convert_annotations
