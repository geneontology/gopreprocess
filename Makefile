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

compare_human:
	poetry run compare -file1 Lori_human.tsv -file2 mgi-human-ortho.gaf -o compare_human

compare_rat:
	poetry run compare -file1 Lori_rat.tsv -file2 mgi-rat-ortho.gaf -o compare_rat

download_human:
	poetry run download -source_taxon "NCBITaxon:9606" -target_taxon "NCBITaxon:10090"

download_rat:
	poetry run download -source_taxon "NCBITaxon:11060" -target_taxon "NCBITaxon:10090"