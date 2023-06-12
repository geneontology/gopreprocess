from src.gopreprocess.processors.gafprocessor import GafProcessor
import pystow
from ontobio.io.gafparser import GafParser
from ontobio.ecomap import EcoMap
from src.gopreprocess.processors.orthoprocessor import OrthoProcessor
from src.utils.settings import get_alliance_ortho_url
from src.utils.settings import get_mgi_gaf_url

ecomap = EcoMap()
ecomap.mappings()


def parse_gaf(filepath):
    p = GafParser()
    p.config.ecomap = EcoMap()
    p.config.remove_double_prefixes = True

    try:
        results = p.parse(open(filepath, "r"), skipheader=True)
        return results
    except IOError as e:
        print(f"Failed to parse GAF file: {e}")

    return None


def preprocess():
    # Usage example
    url = get_alliance_ortho_url()
    path = pystow.ensure('ORTHO', url=url)
    ortho_processor = OrthoProcessor(url, path)
    data = ortho_processor.get_data()

    url = get_mgi_gaf_url()
    path = pystow.ensure('MOUSE', url=url)
    gaf_processor = GafProcessor(url, path)
    gaf_processor.get_data()
    results = parse_gaf(expanded_file)
    print(results[0])


if __name__ == '__main__':
    preprocess()
