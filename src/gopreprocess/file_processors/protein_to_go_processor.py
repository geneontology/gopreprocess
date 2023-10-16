"""Module contains the Ontology processor class."""

from src.utils.decorators import timer
from src.utils.download import download_file

@timer
def add_protein_to_go_files():
    """
    Downloads the protein to GO annotation files for concatenation with other GAF files

    :return: None
    """
    download_file(target_directory_name="GAF_OUTPUT", config_key="GOA_MOUSE", gunzip=True)
    download_file(target_directory_name="GAF_OUTPUT", config_key="GOA_MOUSE_ISOFORM", gunzip=True)
