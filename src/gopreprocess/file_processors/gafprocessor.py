"""Module contains the GafProcessor class."""
from pathlib import Path
from typing import List

from ontobio.ecomap import EcoMap
from ontobio.io.gafparser import GafParser
from ontobio.model.association import Curie

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
    for code, _, eco_id in ecomap.derived_mappings():
        if code in ["EXP", "IDA", "IPI", "IMP", "IGI"]:
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

    """
    A class for processing GAF (Gene Association Format) files.

    Attributes
    ----------
        filepath (str): The path to the GAF file.
        namespaces (List[str]): A list of namespaces.
        convertible_annotations (List[dict]): A list of convertible annotations.
        taxon_to_provider (dict): A dictionary mapping taxon IDs to providers.
        target_taxon (str): The target taxon ID.
        uniprot_to_hgnc_map (dict): A dictionary mapping UniProt IDs to HGNC IDs.

    Methods
    -------
        __init__(self, filepath, namespaces): Initializes a new instance of GafProcessor.
        parse_gaf(self): Parses the GAF file and processes the annotations.

    """

    def __init__(
        self,
        filepath: Path,
        namespaces: List,
        taxon_to_provider: dict,
        target_taxon: str,
        uniprot_to_hgnc_map: dict = None,
    ):
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
        self.skipped = []

    @timer
    def parse_gaf(self):
        """
        Parses the GAF file and processes the annotations.

        :return: None.
        """
        p = configure_parser()
        experimental_evidence_codes = get_experimental_eco_codes(EcoMap())
        skipped = []
        with open(self.filepath, "r") as file:
            counter = 0
            for line in file:
                annotation = p.parse_line(line)
                for source_assoc in annotation.associations:
                    if isinstance(source_assoc, dict):
                        continue
                    if source_assoc.negated:
                        skipped.append(
                            "NOT_RESTR    "
                            + str(source_assoc.subject.id)
                            + str(source_assoc.evidence.type)
                            + str(source_assoc.object.id)
                            + str(source_assoc.evidence.has_supporting_reference)
                            + str(source_assoc.evidence.with_support_from)
                            + str(source_assoc.relation)
                        )
                        continue
                    if source_assoc.subject.id.namespace not in self.namespaces:
                        skipped.append(
                            "OWN_TAIL_RESTR    "
                            + str(source_assoc.subject.id)
                            + str(source_assoc.evidence.type)
                            + str(source_assoc.object.id)
                            + str(source_assoc.evidence.has_supporting_reference)
                            + str(source_assoc.evidence.with_support_from)
                            + str(source_assoc.relation)
                        )
                        continue  # remove self-annotations from MGI
                    if str(source_assoc.evidence.type) not in experimental_evidence_codes:
                        skipped.append(
                            "EVCODE_RESTR    "
                            + str(source_assoc.subject.id)
                            + str(source_assoc.evidence.type)
                            + str(source_assoc.object.id)
                            + str(source_assoc.evidence.has_supporting_reference)
                            + str(source_assoc.evidence.with_support_from)
                            + str(source_assoc.relation)
                        )
                        continue
                    if source_assoc.provided_by == self.taxon_to_provider[self.target_taxon]:
                        skipped.append(
                            "OWN_TAIL_RESTR    "
                            + str(source_assoc.subject.id)
                            + str(source_assoc.evidence.type)
                            + str(source_assoc.object.id)
                            + str(source_assoc.evidence.has_supporting_reference)
                            + str(source_assoc.evidence.with_support_from)
                            + str(source_assoc.relation)
                        )
                        continue
                    has_reference = any(
                        reference.namespace == "PMID" for reference in source_assoc.evidence.has_supporting_reference
                    )
                    if not has_reference:
                        counter = counter + 1
                    if str(source_assoc.object.id) in ["GO:0005515", "GO:0005488"]:
                        continue
                    if source_assoc.subject.id.namespace == "UniProtKB":
                        # TODO convert to report files
                        # check if the incoming HGNC identifier is in the map we made from UniProt to HGNC via
                        # the MGI xref file
                        if str(source_assoc.subject.id) not in self.uniprot_to_hgnc_map.keys():
                            skipped.append(
                                "NO_ORTHO_RESTR    "
                                + str(source_assoc.subject.id)
                                + str(source_assoc.evidence.type)
                                + str(source_assoc.object.id)
                                + str(source_assoc.evidence.has_supporting_reference)
                                + str(source_assoc.evidence.with_support_from)
                                + str(source_assoc.relation)
                            )
                            continue
                        else:
                            # if it's in the mapped dictionary, then we can replace the UniProt identifier with the
                            # HGNC identifier, formatting that as a Curie with separate Namespace and ID fields.
                            mapped_id = self.uniprot_to_hgnc_map[str(source_assoc.subject.id)]
                            source_assoc.subject.id = Curie(
                                namespace=mapped_id.split(":")[0], identity=mapped_id.split(":")[1]
                            )
                    self.convertible_annotations.append(source_assoc)
        print("skipped_gafprocessor", len(skipped))
        with open("skipped_gafprocess.txt", "w") as file:
            for annotation in skipped:
                file.write(f"{annotation}\n")
