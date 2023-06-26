from ontobio.ecomap import EcoMap
from ontobio.io.gafparser import GafParser
from typing import List
from pathlib import Path
from src.utils.decorators import timer
from src.utils.settings import get_url
from src.utils.download import download_file
from ontobio.model.association import Curie


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


def generate_gene_protein_map() -> dict:
    uniprot_map = {}
    cross_reference_filepath = download_file("ALLIANCE", "ALLIANCE_XREF")
    with open(cross_reference_filepath, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = line.strip().split("\t")
            # UniProtKB ID is in column 1, HGNC ID is in column 0
            uniprot_map[line[1]] = line[0]
    return uniprot_map


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
        gene_protein_map = None
        with open(self.filepath, 'r') as file:
            for line in file:
                annotation = p.parse_line(line)
                for source_assoc in annotation.associations:
                    if isinstance(source_assoc, dict):
                        continue
                    if source_assoc.subject.id.namespace == "UniProtKB":
                        print("found UniProtKB in the subject, convert to HGNC to map to Alliance ortholog")
                        if gene_protein_map is None:
                            gene_protein_map = generate_gene_protein_map()
                        print(source_assoc.subject.id)
                        if str(source_assoc.subject.id) not in gene_protein_map.keys():
                            continue
                        else:
                            mapped_id = gene_protein_map[str(source_assoc.subject.id)]
                            source_assoc.subject.id = Curie(namespace=mapped_id.split(":")[0],
                                                        identity=mapped_id.split(":")[1])
                            print(source_assoc.subject.id)
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
