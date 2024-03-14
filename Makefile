MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

all: install test run

dev: install

test: unit-tests lint spell

# this takes a bit longer than not removing the .tox dir, but otherwise we get GH actions failures
# due to the .tox dir being static as compared to the GH refreshed tox environment
lint:
	@echo "Checking for .tox directory..."
	@if [ -d .tox ]; then \
		echo "Removing .tox directory..."; \
		rm -rf .tox; \
	fi
	@echo "Running lint-fix..."
	poetry run tox -e lint-fix

lint-fix: lint

spell:
	poetry run tox -e codespell

unit-tests:
	poetry run pytest tests/*.py

install:
	poetry install

download_human:
	poetry run download -source_taxon "NCBITaxon:9606" -target_taxon "NCBITaxon:10090"

download_rat:
	poetry run download -source_taxon "NCBITaxon:10116" -target_taxon "NCBITaxon:10090"

convert_human:
	poetry run convert_annotations --namespaces 'HUMAN','UniProtKB' --target_taxon "NCBITaxon:10090" --source_taxon "NCBITaxon:9606" --ortho_reference "GO_REF:0000119"

convert_rat:
	poetry run convert_annotations --ortho_reference "GO_REF:0000096" --target_taxon "NCBITaxon:10090" --source_taxon "NCBITaxon:10116" --namespaces 'RGD'

compare_human:
	poetry run compare -file1 Lori_human.tsv -file2 mgi-human-ortho.gaf -o compare_human

compare_rat:
	poetry run compare -file1 Lori_rat.tsv -file2 mgi-rat-ortho.gaf -o compare_rat

convert_gpad:
	poetry run convert_gpad

convert_p2g_annotations:
	poetry run convert_p2g_annotations --source_taxon "NCBITaxon:10090" --isoform=True

get_goa_files:
	poetry run get_goa_files

merge_gafs:
	poetry run merge_files

validate_merged_gafs:
	poetry run validate_merged_gafs --target_taxon "NCBITaxon:10090"

get_gpad:
	poetry run merge_files
	poetry run get_gpad_file

merge_files: merge_gafs

run: download_human download_rat convert_human convert_rat convert_p2g_annotations merge_gafs validate_merged_gafs