import logging
from enum import Enum
from os import path

import yaml

CONFIG = path.join(path.dirname(path.abspath(__file__)), "../config/download_config.yaml")
logger = logging.getLogger(__name__)

def get_alliance_ortho_url():
    """
    Retrieves the Alliance orthology URL from the configuration file.

    :return: The Alliance orthology URL.
    :rtype: str
    """
    with open(CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["Ortho"]["alliance_ortho_url"]


def get_mgi_gaf_url():
    """
    Retrieves the MGI GAF URL from the configuration file.

    :return: The MGI GAF URL.
    :rtype: str
    """
    with open(CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["MGI"]["mgi_goa_url"]


def get_mgi_gpi_url():
    """
    Retrieves the MGI GPI URL from the configuration file.

    :return: The MGI GPI URL.
    :rtype: str
    """
    with open(CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["MGI"]["mgi_gpi_url"]


def get_rgd_gpad_url():
    """
    Retrieves the RGD GPAD URL from the configuration file.

    :return: The RGD GPAD URL.
    :rtype: str
    """
    with open(CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["RGD"]["rgd_gaf_url"]