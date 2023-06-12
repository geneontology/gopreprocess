import gzip
import shutil
import os
import requests
from src.utils.download import unzip_gz, download_file


class GafProcessor:
    def __init__(self, url, destination):
        self.url = url
        self.destination = destination


