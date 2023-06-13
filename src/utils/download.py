from pathlib import Path

from src.utils.settings import get_alliance_ortho_url, get_rgd_gpad_url, get_mgi_gpi_url
import pystow
from typing import Tuple


def download_files() -> tuple[Path, Path, Path]:
    """
    Downloads and retrieves the required files for preprocessing.

    :return: A tuple containing the file paths of the downloaded files: ortho_path, rgd_gaf_path, mgi_gpi_path.
    :rtype: Tuple[str, str, str]
    """
    ortho_path = pystow.ensure_gunzip('ORTHO', url=get_alliance_ortho_url())  # autoclean=True, force=False)
    rgd_gaf_path = pystow.ensure_gunzip('RGD', url=get_rgd_gpad_url())  # autoclean=True, force=True)
    mgi_gpi_path = pystow.ensure_gunzip('MGI', url=get_mgi_gpi_url())  # autoclean=True, force=True)
    return ortho_path, rgd_gaf_path, mgi_gpi_path
