"""Utils for merging files together."""

from pystow import join
import gzip
from pathlib import Path
from src.utils.settings import taxon_to_provider


def merge_files_from_directory(source_directory: str):
    """
    Merge all .gaf files in the given directory into a single file.

    :return: None
    """
    source_directory = join(
        key=source_directory,
        ensure_exists=True,
    )

    target_taxon = "NCBITaxon:10090"
    target_file_name = taxon_to_provider[target_taxon].lower() + "-p2go-homology.gaf.gz"

    # Construct the target file output path with gzip extension
    target_file_output = join(
        key=taxon_to_provider[target_taxon],
        name=target_file_name,
        ensure_exists=True,
    ).as_posix()  # Use as_posix() to get the path as a string, assuming pystow >= 0.3.0

    # Initialize lists to store headers and data lines
    headers = []
    data_lines = []

    # Get all .gaf files in the directory
    gaf_files = list(Path(source_directory).glob("*.gaf"))

    # Process each file
    for file in gaf_files:
        with open(file, "r") as f:
            for line in f:
                if line.startswith("!"):
                    headers.append(line.strip())
                else:
                    data_lines.append(line)

    # Deduplicate and sort headers
    unique_headers = sorted(set(headers))

    # Write the merged file with gzip compression
    with gzip.open(target_file_output, "wt") as out:  # "wt" mode for writing text in a gzip file
        # Write the merged headers
        for header in unique_headers:
            out.write(header + "\n")

        # Write the data lines
        for line in data_lines:
            out.write(line)

    return target_file_output