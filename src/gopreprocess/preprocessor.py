from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gafprocessor import GafProcessor
from src.processors.gpiprocessor import GpiProcessor
from src.utils.download import download_files
from typing import List, Dict
from pprint import pprint


def preprocess():
    ortho_path, rgd_gaf_path, mgi_gpi_path = download_files()
    rat_genes = OrthoProcessor(ortho_path, "NCBITaxon:10116", "NCBITaxon:10090").genes
    mouse_genes = GpiProcessor(mgi_gpi_path).mgi_genes
    rgd_annotations = GafProcessor(rgd_gaf_path, namespaces=["RGD", "UniProtKB"]).annotations

    for annotation in rgd_annotations:
        print(annotation)


if __name__ == '__main__':
    preprocess()
