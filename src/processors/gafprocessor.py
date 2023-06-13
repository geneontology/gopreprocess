from ontobio.ecomap import EcoMap
from ontobio.io.gafparser import GafParser
from typing import List


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


class GafProcessor:
    def __init__(self, genes, filepath, namespaces):
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
        self.convertable_annotations = []
        self.parse_gaf()

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
                for rgd_assoc in annotation.associations:
                    if (type(rgd_assoc)) == dict:
                        continue
                    else:
                        if rgd_assoc.negated:  # no negated annotations from ortho sources
                            continue
                        else:
                            if rgd_assoc.subject.id.namespace in self.namespaces:  # only RGD or UniProtKB annotations
                                if rgd_assoc.evidence not in experimental_evidence_codes:  # only non-experimental evidence codes
                                    if rgd_assoc.provided_by != 'MGI':  # no tail eating
                                        for reference in rgd_assoc.evidence.has_supporting_reference:
                                            if reference.namespace == "PMID":  # must have a PMID
                                                if rgd_assoc.object.id not in ['GO:0005515', 'GO:0005488']:  # exclude GO list
                                                    self.convertable_annotations.append(rgd_assoc)
                                                else:
                                                    continue
                                            else:
                                                continue
                                    else:
                                        continue
                                else:
                                    continue
                            else:
                                continue
