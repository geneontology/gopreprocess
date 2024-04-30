"""Utils for merging files together."""

import gzip
import sys
from collections import defaultdict
from pathlib import Path

import pystow
from gopreprocess.file_processors.ontology_processor import get_ontology_factory
from ontobio.io.assocparser import AssocParserConfig
from ontobio.io.gafparser import GafParser

from src.utils.decorators import timer


def merge_files_from_directory(source_directory: str):
    """
    Merge all .gaf files in the given directory into a single gzip-compressed file.

    :param source_directory: Directory containing .gaf files.
    :return: None
    """
    dir_path = pystow.join(source_directory, ensure_exists=True)
    source_directory = Path(dir_path)

    if not source_directory.exists() or not source_directory.is_dir():
        raise ValueError(f"{source_directory} is not a valid directory.")

    # Initialize lists to store headers and data lines
    headers = []
    data_lines = []

    target_file_output = source_directory / "mgi-p2go-homology.gaf.gz"

    # Get all .gaf files in the directory
    gaf_files = list(Path(source_directory).glob("*.gaf"))

    config = AssocParserConfig(ontology=get_ontology_factory("GO"), rule_set="all")
    parser = GafParser(config=config)
    # Process each file
    for file in gaf_files:
        with open(file, "r") as f:
            for line in f:
                # If the line starts with '!', it's a header line
                parser.parse_line(line)
                if line.startswith("!"):
                    headers.append(line.strip())
                else:
                    data_lines.append(line)

    dump_valid_file(headers, data_lines, target_file_output)
    # Get all errors from the parser
    validate_errors(parser)


@timer
def dump_valid_file(headers, data_lines, target_file_output):
    """
    Write the merged headers and data lines to a gzip-compressed file.

    :param headers: List of headers.
    :type headers: list
    :param data_lines: List of data lines.
    :type data_lines: list
    :param target_file_output: Path to the target file.
    :type target_file_output: str
    :return: Path to the target file.

    """
    # Deduplicate headers
    unique_headers = list(set(headers))

    # Sort headers just to ensure consistent ordering
    unique_headers.sort()

    # Write the merged file with gzip compression
    with gzip.open(target_file_output, "wt") as out:  # "wt" mode for writing text in a gzip file
        # Write the merged headers
        for header in unique_headers:
            out.write(header + "\n")

        # Write the data lines
        for line in data_lines:
            out.write(line)

    out.close()
    return target_file_output


@timer
def parse_errors(errors: list) -> int:
    """
    Count number of errors per GO Rule and lines in source vs. resulting GAF to check if this upstream should fail.

    :param errors: A list of errors.
    :type errors: list
    :return: The percentile change in annotations.
    :rtype: int
    """
    error_counts = defaultdict(int)
    summary = []
    # Assuming 'errors' is a list of dictionaries representing error entries

    for row in errors:
        if row.get("level") == "ERROR":
            rule_message_key = (row.get("rule"), row.get("message"))
            error_counts[rule_message_key] += 1

    # Generate summary from error_counts
    for (rule, message), count in error_counts.items():
        summary.append(f"Rule: {rule}, Message: '{message}', Errors: {count}")

    print("Error summary:", summary)


@timer
def validate_errors(parser):
    """
    Validate the errors in the parser and write the valid file. EXIT if more than 5000 errors.

    :param parser: The parser object.
    :type parser: object
    :param headers: List of headers.
    :type headers: list
    :param data_lines: List of data lines.
    :type data_lines: list
    :param target_file_output: Path to the target file.
    :type target_file_output: str
    :return: None

    """
    errors = []
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
        parse_errors(errors)
