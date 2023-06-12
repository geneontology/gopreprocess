import json


def parse_data(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


class OrthoProcessor:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_data(self):
        data = parse_data(self.filepath)
        return data
