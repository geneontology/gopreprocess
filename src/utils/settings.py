import logging
from enum import Enum
from os import path

import yaml

CONFIG = path.join(path.dirname(path.abspath(__file__)), "../config/download_config.yaml")
logger = logging.getLogger(__name__)


def get_alliance_ortho_url():
    with open(CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["Ortho"]["alliance_ortho_url"]


def get_mgi_gaf_url():
    with open(CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config["MGI"]["mgi_goa_url"]
