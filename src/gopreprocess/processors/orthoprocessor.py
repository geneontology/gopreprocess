import requests
import gzip
import json
from src.utils.download import unzip_gz, download_file


def parse_data():
    with open('data.json', 'r') as file:
        data = json.load(file)
    return data


class OrthoProcessor:
    def __init__(self, url, destination):
        self.url = url
        self.destination = destination

    def get_data(self):
        download_file(self.url, self.destination)
        unzip_gz(self.destination)
        data = parse_data()
        return data
