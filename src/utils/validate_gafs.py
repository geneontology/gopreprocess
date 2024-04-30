
"""Module contains the wrapper for GORules to validate gopreprocess package resulting GAFs."""
import gzip
import shutil
import sys

import click
from gopreprocess.file_processors.ontology_processor import get_ontology_factory

from ontobio.io.assocparser import AssocParserConfig
from ontobio.io.gafparser import GafParser
from ontobio.io.gpadparser import GpadParser
from pystow import join

from src.utils.settings import taxon_to_provider
def validate(target_taxon: str, file_key: str, file_name: str):
    """
    Validate a merged GAF file.

    :param file_key: The key of the file to validate.
    :type file_key: str
    :param file_name: The name of the file to validate.
    :type file_name: str
    :param target_taxon: The target taxon in curie format.
    :type target_taxon: str
    """
    # Ontology Factory
    config = AssocParserConfig(ontology=get_ontology_factory("GO"), rule_set="all")
    if file_key is None and file_name is None:
        file_key = taxon_to_provider[target_taxon]
        file_name = taxon_to_provider[target_taxon].lower() + "-p2go-homology.gaf.gz"
        print(file_name)

    gaf_to_validate = join(
        key=file_key,
        name=file_name,
        ensure_exists=True,
    )
    gaf_to_validate_out = file_name[:-3]  # Remove the .gz extension
    # Decompress the gzip file
    with gzip.open(gaf_to_validate, 'rb') as f_in:
        with open(gaf_to_validate_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("file to validate: ", f_out)

    if "gpad" in file_name:
        parser = GpadParser(config=config)
    elif "gaf" in file_name:
        parser = GafParser(config=config)
    else:
        raise ValueError("File must be a GAF or GPAD and filename must reflect this.")
    errors = []
    parser.parse(file=str(f_out), skipheader=True)
    print("parsing complete")
    for error_report in parser.report.messages:
        if error_report.get("level") == "ERROR":
            errors.append(error_report)

    # create the report.json file full of errors to store on skyhook
    # calculate percentile drop in annotations coming out vs. going in and fail if over 10%
    # error_file_length = check_errors(errors)

    if len(errors) > 5000:
        print("FAIL!: first 10 errors of more than 5000 returned")
        for item in errors[:10]:
            print(item)
        sys.exit(1)  # Exit with a non-zero status to indicate failure
    else:
        print("PASS!: less than 5000 errors returned")
        check_errors(errors)
        sys.exit(0)