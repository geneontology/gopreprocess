from pathlib import Path
from src.utils.decorators import timer
from src.utils.settings import get_url
import pystow
from typing import Tuple


@timer
def download_files(source_taxon: str, target_taxon: str) -> tuple[Path, Path, Path]:
    """
    Downloads and retrieves the required files for preprocessing.

    :return: A tuple containing the file paths of the downloaded files: ortho_path, rgd_gaf_path, mgi_gpi_path.
    :rtype: Tuple[str, str, str]

    Args:
        source_taxon:
        target_taxon:
    """
    ortho_path = pystow.ensure_gunzip('ORTHO', url=get_url("ORTHO"))  # autoclean=True, force=False)
    rgd_gaf_path = pystow.ensure_gunzip('RGD', url=get_url("RGD"))  # autoclean=True, force=True)
    mgi_gpi_path = pystow.ensure_gunzip('MGI', url=get_url("MGI_GPI"))  # autoclean=True, force=True)
    return ortho_path, rgd_gaf_path, mgi_gpi_path
