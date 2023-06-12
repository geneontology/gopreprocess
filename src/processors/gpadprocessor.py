from ontobio.io.gafparser import GafParser
from ontobio.ecomap import EcoMap


def parse_data(filepath):
    p = GafParser()
    p.config.ecomap = EcoMap()
    p.config.remove_double_prefixes = True

    try:
        results = p.parse(open(filepath, "r"), skipheader=True)
        return results
    except IOError as e:
        print(f"Failed to parse GPI file: {e}")

    return None


class GpadProcessor:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_data(self):
        data = parse_data(self.filepath)
        return data
