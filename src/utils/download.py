from src.utils.settings import get_alliance_ortho_url, get_rgd_gpad_url, get_mgi_gpi_url
import pystow


def download_files():
    ortho_path = pystow.ensure_gunzip('ORTHO', url=get_alliance_ortho_url())  # autoclean=True, force=False)
    rgd_gaf_path = pystow.ensure_gunzip('RGD', url=get_rgd_gpad_url())  # autoclean=True, force=True)
    mgi_gpi_path = pystow.ensure_gunzip('MGI', url=get_mgi_gpi_url())  # autoclean=True, force=True)
    return ortho_path, rgd_gaf_path, mgi_gpi_path