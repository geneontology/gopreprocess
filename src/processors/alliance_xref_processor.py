from src.utils.decorators import timer
from src.utils.download import download_file


class AllianceXrefProcessor:
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
    def generate_gene_protein_map(self) -> tuple[dict, dict]:
        hgnc_to_uniprot_map = {}
        uniprot_to_hgnc_map = {}
        cross_reference_filepath = download_file("ALLIANCE", "ALLIANCE_XREF")
        with open(cross_reference_filepath, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                line = line.strip().split("\t")
                # UniProtKB ID is in column 1, HGNC ID is in column 0
                uniprot_to_hgnc_map[line[1]] = line[0]
                hgnc_to_uniprot_map[line[0]] = line[1]
        return hgnc_to_uniprot_map, uniprot_to_hgnc_map

