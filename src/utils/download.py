from pathlib import Path
from src.utils.decorators import timer
from src.utils.settings import get_url
import pystow
from typing import Tuple
from src.utils.settings import taxon_to_provider, iso_eco_code


@timer
def download_files(source_taxon: str, target_taxon: str) -> tuple[Path, Path, Path]:
    """
    Downloads and retrieves the required files for preprocessing.

    :return: A tuple containing the file paths of the downloaded files: ortho_path, rgd_gaf_path, mgi_gpi_path.
    :rtype: Tuple[str, str, str]

    autoclean=True: download new file every time the program is run, false means to check if it exists and avoid
    downloading from scratch if it does.

    :param: source_taxon (str): The source taxon that provides the annotations.
    :param: target_taxon (str): The target taxon to which the annotations will be converted via orthology.
    """
    ortho_path = pystow.ensure_gunzip('ALLIANCE', url=get_url("ALLIANCE_ORTHO"), autoclean=True)
    rgd_gaf_path = pystow.ensure_gunzip(taxon_to_provider[source_taxon],
                                        url=get_url(taxon_to_provider[source_taxon]), autoclean=True)
    mgi_gpi_path = pystow.ensure_gunzip(taxon_to_provider[target_taxon],
                                        url=get_url(taxon_to_provider[target_taxon] + "_GPI"), autoclean=True)
    return ortho_path, rgd_gaf_path, mgi_gpi_path


def download_file(target_directory_name: str, config_key: str) -> Path:
    """
    Downloads a file from the given URL.

    :param target_directory_name: The name of the directory to download the file to.
    :param config_key: The key in the config file that contains the URL to download the file from.
    :return: None

    """
    file_path = pystow.ensure(target_directory_name,
                                     url=get_url(config_key),
                                     autoclean=True)
    return file_path
