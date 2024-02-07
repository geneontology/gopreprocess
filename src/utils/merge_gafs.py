"""Utils for merging files together."""

from pystow import join

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

    target_file_output = join(
        key=taxon_to_provider[target_taxon],
        name=taxon_to_provider[target_taxon].lower() + "-merged.gaf",
        ensure_exists=True,
    )

    # Ensure the directory exists
    if not source_directory.exists() or not source_directory.is_dir():
        raise ValueError(f"{source_directory} is not a valid directory.")

    # Get all .gaf files in the directory
    gaf_files = list(source_directory.glob("*.gaf"))

    # List to store merged headers
    headers = []

    # List to store data lines
    data_lines = []

    # Process each file
    for file in gaf_files:
        with open(file, "r") as f:
            for line in f:
                # If the line starts with '!', it's a header line
                if line.startswith("!"):
                    headers.append(line.strip())
                else:
                    data_lines.append(line)

    # Deduplicate headers
    unique_headers = list(set(headers))

    # Sort headers just to ensure consistent ordering
    unique_headers.sort()

    # Write the merged file
    with open(target_file_output, "w") as out:
        # Write the merged headers
        for header in unique_headers:
            out.write(header + "\n")

        # Write the data lines
        for line in data_lines:
            out.write(line)

    out.close()

    return target_file_output
