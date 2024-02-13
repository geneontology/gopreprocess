"""Module contains functions for downloading files from the web."""

import time
from pathlib import Path

import pystow

from src.utils.decorators import timer
from src.utils.settings import get_url, taxon_to_provider


@timer
def download_files(source_taxon: str, target_taxon: str) -> tuple[Path, Path, Path]:
    """
    Downloads and retrieves the required files for preprocessing.

    :return: A tuple containing the file paths of the downloaded files: ortho_path, rgd_gaf_path, mgi_gpi_path.
    :rtype: Tuple[str, str, str]

    autoclean=True: download new file every time the program is run, false means to check if it exists and avoid
    downloading from scratch if it does.

    :param: source_taxon (str): The source taxon that provides the annotations.
    :param: target_taxon (str): The target taxon to which the annotations will be converted via orthology.
    """
    ortho_path = pystow.ensure_gunzip("ALLIANCE", url=get_url("ALLIANCE_ORTHO"), autoclean=True)
    source_gaf_path = pystow.ensure_gunzip(
        taxon_to_provider[source_taxon], url=get_url(taxon_to_provider[source_taxon]), autoclean=True
    )
    target_gpi_path = pystow.ensure_gunzip(
        taxon_to_provider[target_taxon], url=get_url(taxon_to_provider[target_taxon] + "_GPI"), autoclean=True
    )
    return ortho_path, source_gaf_path, target_gpi_path


def download_with_retry(target_directory_name, config_key, gunzip=True, retries=3):
    """
    Download a file with retry attempts.

    :param target_directory_name: The name of the directory to download the file to.
    :param config_key: The key in the config file that contains the URL to download the file from.
    :param gunzip: Whether to gunzip the file after downloading.
    :param retries: The number of retry attempts.
    :return: The file path of the downloaded file.

    """
    attempt = 0
    while attempt < retries:
        try:
            return download_file(target_directory_name, config_key, gunzip)
        except Exception as e:  # Broad exception catch due to the abstraction of download details
            print(f"Download failed on attempt {attempt + 1} due to: {e}. Retrying...")
            attempt += 1
            time.sleep(5)  # Wait for 5 seconds before retrying
    raise Exception(f"Failed to download file after {retries} attempts.")


def download_file(target_directory_name: str, config_key: str, gunzip=False) -> Path:
    """
    Downloads a file from the given URL.

    :param target_directory_name: The name of the directory to download the file to.
    :param config_key: The key in the config file that contains the URL to download the file from.
    :return: None

    """
    if gunzip:
        file_path = pystow.ensure_gunzip(target_directory_name, url=get_url(config_key), force=True)
    else:
        file_path = pystow.ensure(target_directory_name, url=get_url(config_key), force=True)
    return file_path


def concatenate_gafs(file1, file2, output_file):
    """
    Concatenate two GAF files into a single file.

    :param file1: The first GAF file.
    :param file2: The second GAF file.
    :param output_file: The output file.
    :return: None
    """
    # Open the first file and read its content
    with open(file1, "r") as f1:
        content1 = f1.readlines()

    # Open the second file and read its content
    with open(file2, "r") as f2:
        content2 = f2.readlines()

    # Strip lines from content2 that start with an exclamation point
    content2 = [line for line in content2 if not line.startswith("!")]

    # Write the combined content to the output file
    with open(output_file, "w") as out:
        out.writelines(content1 + content2)
