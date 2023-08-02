from ontobio.ecomap import EcoMap
from ontobio.io.gafparser import GafParser
from typing import List, Dict
from pathlib import Path
from src.utils.decorators import timer
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
    for code, _, eco_id in ecomap.derived_mappings():
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


class GafProcessor:
    def __init__(self,
                 filepath: Path,
                 namespaces: List,
                 taxon_to_provider: dict,
                 target_taxon: str,
                 uniprot_to_hgnc_map: dict = None):
        """
        Initializes a GafProcessor object.

        :param filepath: The path to the GAF file.
        :type filepath: str
        :param namespaces: A list of namespaces.
        :type namespaces: List[str]
        """
        self.filepath = filepath
        self.namespaces = namespaces
        self.convertible_annotations = []
        self.taxon_to_provider = taxon_to_provider
        self.target_taxon = target_taxon
        self.uniprot_to_hgnc_map = uniprot_to_hgnc_map
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
            counter = 0
            ecos_excluded = []
            for line in file:
                annotation = p.parse_line(line)
                for source_assoc in annotation.associations:
                    if isinstance(source_assoc, dict):
                        continue
                    if source_assoc.negated:
                        continue
                    if source_assoc.subject.id.namespace not in self.namespaces:
                        continue
                    if str(source_assoc.evidence.type) not in experimental_evidence_codes:
                        ecos_excluded.append(source_assoc.evidence.type)
                        continue
                    if source_assoc.provided_by == self.taxon_to_provider[self.target_taxon]:
                        continue
                    has_reference = any(
                        reference.namespace == "PMID" for reference in source_assoc.evidence.has_supporting_reference)
                    if not has_reference:
                        counter = counter + 1
                    if str(source_assoc.object.id) in ['GO:0005515', 'GO:0005488']:
                        continue
                    if source_assoc.subject.id.namespace == "UniProtKB":
                        # TODO convert to report files
                        if str(source_assoc.subject.id) not in self.uniprot_to_hgnc_map.keys():
                            continue
                        else:
                            mapped_id = self.uniprot_to_hgnc_map[str(source_assoc.subject.id)]
                            source_assoc.subject.id = Curie(namespace=mapped_id.split(":")[0],
                                                            identity=mapped_id.split(":")[1])
                    self.convertible_annotations.append(source_assoc)

