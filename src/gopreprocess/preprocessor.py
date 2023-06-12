import pystow
from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gafprocessor import GafProcessor
from src.utils.settings import get_alliance_ortho_url, get_rgd_gpad_url
from typing import List, Dict
from pprint import pprint


def preprocess():
    rat_genes = preprocess_alliance_ortho()
    rat_annotations = preprocess_rgd()
    for annotation in rat_annotations:
        if annotation.subject.id in rat_genes:



def preprocess_alliance_ortho() -> List[str]:
    path = pystow.ensure_gunzip('ORTHO', url=get_alliance_ortho_url())  # autoclean=True, force=False)
    ortho_processor = OrthoProcessor(path)
    rat_genes = []
    for pair in ortho_processor.get_data().get('data'):
        if pair.get('Gene1SpeciesTaxonID') == 'NCBITaxon:10090' and pair.get('Gene2SpeciesTaxonID') == 'NCBITaxon:10116':
            rat_genes.append({"rgd_gene": pair.get('Gene2ID'), "mgi_gene": pair.get('Gene1ID')})
    return rat_genes


def preprocess_rgd() -> Dict[str, List[str]]:
    rgd_gaf_path = pystow.ensure_gunzip('RGD', url=get_rgd_gpad_url())  # autoclean=True, force=True)
    rgd_gaf_processor = GafProcessor(rgd_gaf_path)
    data = rgd_gaf_processor.get_data()
    return data


if __name__ == '__main__':
    preprocess()
