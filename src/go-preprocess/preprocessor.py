from src.utils.download import FileDownloader
import pystow
from ontobio.io.gafparser import GafParser
from ontobio.ecomap import EcoMap

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

    url = 'https://ftp.ebi.ac.uk/pub/databases/GO/goa/MOUSE/goa_mouse.gaf.gz'
    path = pystow.ensure('MOUSE', url=url)
    downloader = FileDownloader(url, path)
    expanded_file = downloader.download_file()
    results = parse_gaf(expanded_file)
    print(results[0])


if __name__ == '__main__':
    preprocess()
