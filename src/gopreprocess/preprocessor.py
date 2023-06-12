import pystow
from src.processors.orthoprocessor import OrthoProcessor
from src.utils.settings import get_alliance_ortho_url


def preprocess():
    # Usage example
    path = pystow.ensure_gunzip('ORTHO', url=get_alliance_ortho_url(), autoclean=True, force=True)
    ortho_processor = OrthoProcessor(path)
    data = ortho_processor.get_data()
    print(data.get("metadata"))


if __name__ == '__main__':
    preprocess()
