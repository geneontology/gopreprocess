from ontobio.ecomap import EcoMap
from ontobio.io.gafparser import GafParser
from typing import List
from pathlib import Path
from src.utils.decorators import timer


def get_experimental_eco_codes(ecomap) -> List[str]:
    """
    Retrieves a list of experimental evidence codes from the given EcoMap.

    :param ecomap: The EcoMap object containing the evidence code mappings.
    :type ecomap: EcoMap

    :return: A list of experimental evidence codes.
    :rtype: List[str]
    """
    experimental_evidence_codes = []
    for code, _, eco_id in ecomap.mappings():
        if code in ['EXP', 'IDA', 'IPI', 'IMP', 'IGI']:
            experimental_evidence_codes.append(eco_id)
    return experimental_evidence_codes


def configure_parser() -> GafParser:
    """
    Configures and returns a GafParser object.

    :return: A configured GafParser object.
    :rtype: GafParser
    """
    p = GafParser()
    p.config.ecomap = EcoMap()
    p.config.remove_double_prefixes = True
    return p


def generate_uniprot_map() -> dict:
    """
    Generates a dictionary mapping UniProtKB IDs to HGNC IDs.

    :return: A dictionary mapping UniProtKB IDs to HGNC IDs.
    :rtype: dict
    """
    uniprot_map = {}
    with open("data/uniprot_map.txt", "r") as f:
        for line in f:
            line = line.strip().split()
            uniprot_map[line[0]] = line[1]
    return uniprot_map


def generate_gene_protein_map() -> dict:

    return {}


class GafProcessor:
    def __init__(self, genes: List,
                 filepath: Path,
                 namespaces: List,
                 taxon_to_provider: dict,
                 target_taxon: str):
        """
        Initializes a GafProcessor object.

        :param genes: A list of genes.
        :type genes: Any
        :param filepath: The path to the GAF file.
        :type filepath: str
        :param namespaces: A list of namespaces.
        :type namespaces: List[str]
        """
        self.filepath = filepath
        self.ortho_genes = genes
        self.namespaces = namespaces
        self.convertible_annotations = []
        self.taxon_to_provider = taxon_to_provider
        self.target_taxon = target_taxon
        self.parse_gaf()

    @timer
    def parse_gaf(self):
        """
        Parses the GAF file and processes the annotations.

        :return: None
        """
        p = configure_parser()
        experimental_evidence_codes = get_experimental_eco_codes(EcoMap())
        with open(self.filepath, 'r') as file:
            for line in file:
                annotation = p.parse_line(line)
                for source_assoc in annotation.associations:
                    if source_assoc.subject.id.namespace.startswith("UniProtKB"):
                        print("found UniProtKB in the subject, convert to HGNC to map to Alliance orthology")
                        generate_gene_protein_map()
                    if isinstance(source_assoc, dict):
                        continue
                    if source_assoc.negated:
                        continue
                    if source_assoc.subject.id.namespace not in self.namespaces:
                        continue
                    if str(source_assoc.evidence.type) not in experimental_evidence_codes:
                        continue
                    if source_assoc.provided_by == self.taxon_to_provider[self.target_taxon]:
                        continue
                    has_pmid_reference = any(
                        reference.namespace == "PMID" for reference in source_assoc.evidence.has_supporting_reference)
                    if not has_pmid_reference:
                        continue
                    if str(source_assoc.object.id) in ['GO:0005515', 'GO:0005488']:
                        continue

                    self.convertible_annotations.append(source_assoc)
