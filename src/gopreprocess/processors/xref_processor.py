from typing import Tuple, Dict

from src.utils.decorators import timer
from src.utils.download import download_file


class XrefProcessor:
    """
    Class that parses the Alliance cross-reference file and generates a map of HGNC IDs to UniProt IDs.
    It populates two maps, one keyed by UniProtKB identifier, one keyed by HGNC identifier.
    """

    def __init__(self):
        """
        Initializes an instance of the AllianceXrefProcessor.
        """

        self.hgnc_to_uniprot_map, self.uniprot_to_hgnc_map = self.generate_gene_protein_map()

    @timer
    def generate_gene_protein_map(self) -> tuple[dict[str, str], dict[str, str]]:
        """
        processes a cross-reference file to generate two dictionaries: hgnc_to_uniprot_map and uniprot_to_hgnc_map.
        These dictionaries establish a mapping between HGNC (HUGO Gene Nomenclature Committee) IDs and UniProtKB
        (Universal Protein Knowledgebase) IDs.
        """
        hgnc_to_uniprot_map = {}
        uniprot_to_hgnc_map = {}
        # hard coding this download path for now; this is one place that will need additional
        # work if we want to support other species.  Best case, we get this from the Alliance at some point.
        cross_reference_filepath = download_file("MGI", "MGI_XREF")
        with open(cross_reference_filepath, "r") as f:
            for line in f:
                if line.startswith("DB"):
                    continue
                line = line.split("\t")
                # UniProtKB ID is in column 1, HGNC ID is in column 0
                if line[1].startswith("human") and line[12] is not None and line[6] is not None:
                    if "," in line[12]:
                        uniprot_ids = line[12].split(",")
                    else:
                        uniprot_ids = [line[12].strip()]
                    for uniprot_id in uniprot_ids:
                        uniprot_to_hgnc_map["UniProtKB:"+uniprot_id.strip()] = line[6].strip()
                        hgnc_to_uniprot_map[line[6].strip()] = "UniProtKB:"+uniprot_id.strip()

        return hgnc_to_uniprot_map, uniprot_to_hgnc_map
