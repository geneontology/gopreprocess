import pystow
from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gpiprocessor import GpiProcessor
from src.utils.settings import get_alliance_ortho_url, get_rgd_gpi_url


def preprocess():
    preprocess_alliance_ortho()


def preprocess_alliance_ortho():
    path = pystow.ensure_gunzip('ORTHO', url=get_alliance_ortho_url(), autoclean=True, force=True)
    ortho_processor = OrthoProcessor(path)
    data = ortho_processor.get_data()
    print(data.get("metadata"))


def preprocess_rgd():
    rgd_gpi_path = pystow.ensure_gunzip('RGD', url=get_rgd_gpi_url(), autoclean=True, force=True)
    rgd_gpi_processor = GpiProcessor(rgd_gpi_path)
    data = rgd_gpi_processor.get_data()
    print(data)


if __name__ == '__main__':
    preprocess()
