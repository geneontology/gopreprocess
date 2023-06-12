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


def parse_gaf_generator(filepath, namespaces):
    p = configure_parser()
    experimental_evidence_codes = get_experimental_eco_codes(EcoMap())
    with open(filepath, 'r') as file:
        for line in file:
            annotation = p.parse_line(line)
            for rgd_assoc in annotation.associations:
                if (type(rgd_assoc)) == dict:
                    continue
                else:
                    if rgd_assoc.subject.id.namespace in namespaces:  # only RGD or UniProtKB annotations
                        if rgd_assoc.evidence not in experimental_evidence_codes:  # only non-experimental evidence codes
                            if rgd_assoc.provided_by != 'MGI':  # no tail eating
                                if "PMID" in rgd_assoc.evidence.has_supporting_reference:
                                    if rgd_assoc.object.id not in ['GO:0005515', 'GO:0005488']:  # skip if in exclude list
                                        yield rgd_assoc


class GafProcessor:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_data(self, namespaces):
        data = parse_gaf_generator(self.filepath, namespaces)
        return data

