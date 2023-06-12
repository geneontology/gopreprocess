import pystow
from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gpadprocessor import GpadProcessor
from src.utils.settings import get_alliance_ortho_url, get_rgd_gpad_url


def preprocess():
    preprocess_alliance_ortho()


def preprocess_alliance_ortho():
    path = pystow.ensure_gunzip('ORTHO', url=get_alliance_ortho_url())  # autoclean=True, force=False)
    ortho_processor = OrthoProcessor(path)
    data = ortho_processor.get_data()
    for pair in data.get('data'):
        if pair.get('Gene1SpeciesTaxonID') == 'NCBITaxon:10090' and pair.get('Gene2SpeciesTaxonID') == 'NCBITaxon:10116':
            print(pair)


def preprocess_rgd():
    rgd_gpad_path = pystow.ensure_gunzip('RGD', url=get_rgd_gpad_url())  # autoclean=True, force=True)
    rgd_gpad_processor = GpadProcessor(rgd_gpad_path)
    data = rgd_gpad_processor.get_data()
    print(data)


if __name__ == '__main__':
    preprocess()
