"""Module contains the Ontology processor class."""

from src.utils.decorators import timer
from src.utils.download import download_file
from src.gopreprocess.file_processors.gafprocessor import GafProcessor
from src.gopreprocess.file_processors.xref_processor import XrefProcessor
from src.utils.settings import taxon_to_provider


@timer
def add_protein_to_go_files():
    """
    Downloads the protein to GO annotation files for concatenation with other GAF files.

    :return: None
    """
    xrefs = XrefProcessor()
    uniprot_to_hgnc_map = xrefs.uniprot_to_hgnc_map

    source_gaf_path = download_file(target_directory_name="GAF_OUTPUT", config_key="GOA_MOUSE", gunzip=True)
    source_isoform_gaf_path = download_file(target_directory_name="GAF_OUTPUT", config_key="GOA_MOUSE_ISOFORM", gunzip=True)


    # Process the GAF files
    source_annotations = GafProcessor(
        source_gaf_path,
        taxon_to_provider=taxon_to_provider,
        target_taxon=target_taxon,
        namespaces=namespaces,
        uniprot_to_hgnc_map=uniprot_to_hgnc_map,
    ).convertible_annotations