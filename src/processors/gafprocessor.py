from ontobio.ecomap import EcoMap
from ontobio.io.gafparser import GafParser
from typing import List


def get_experimental_eco_codes(ecomap) -> List[str]:
    experimental_evidence_codes = []
    for code, _, eco_id in ecomap.mappings():
        if code in ['EXP', 'IDA', 'IPI', 'IMP', 'IGI']:
            experimental_evidence_codes.append(eco_id)
    return experimental_evidence_codes


def configure_parser() -> GafParser:
    p = GafParser()
    p.config.ecomap = EcoMap()
    p.config.remove_double_prefixes = True
    return p


class GafProcessor:
    def __init__(self, genes, filepath, namespaces):
        self.filepath = filepath
        self.ortho_genes = genes
        self.namespaces = namespaces
        self.convertable_annotations = []
        self.parse_gaf()

    def parse_gaf(self):
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
