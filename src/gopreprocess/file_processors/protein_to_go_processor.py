"""Module contains the Ontology processor class."""

from src.utils.decorators import timer
from src.utils.download import download_file
from src.gopreprocess.file_processors.gaf_processor import GafProcessor
from src.gopreprocess.file_processors.xref_processor import XrefProcessor
from src.utils.settings import taxon_to_provider
from src.utils.merge_gafs import merge_files_from_directory
from src.gopreprocess.ortho_annotation_creation_controller import dump_converted_annotations

@timer
def add_protein_to_go_files():
    """
    Downloads the protein to GO annotation files for concatenation with other GAF files.

    :return: None
    """
    xrefs = XrefProcessor()
    uniprot_to_hgnc_map = xrefs.uniprot_to_hgnc_map

    download_file(target_directory_name="P2G_OUTPUT", config_key="GOA_MOUSE", gunzip=True)
    download_file(target_directory_name="P2G_OUTPUT", config_key="GOA_MOUSE_ISOFORM", gunzip=True)

    resulting_merged_file = merge_files_from_directory("P2G_OUTPUT")

    #TODO: genericize
    target_taxon = "NCBITaxon:10090"
    namespaces = ["UniProtKB"]

    # Process the GAF files
    source_annotations = GafProcessor(
        resulting_merged_file,
        taxon_to_provider=taxon_to_provider,
        target_taxon=target_taxon,
        namespaces=namespaces,
        uniprot_to_hgnc_map=uniprot_to_hgnc_map,
    ).convertible_annotations


    dump_converted_annotations(source_annotations, target_taxon, namespaces, "GAF_OUTPUT")