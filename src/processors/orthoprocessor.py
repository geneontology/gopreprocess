import json


class OrthoProcessor:
    def __init__(self, filepath, taxon1, taxon2):
        self.filepath = filepath
        self.taxon1 = taxon1
        self.taxon2 = taxon2

        self.genes = self.get_data()

    def get_data(self):
        with open(self.filepath, 'r') as file:
            data = json.load(file)
        genes = {}
        for pair in data.get('data'):
            if pair.get('Gene1SpeciesTaxonID') == self.taxon1 and pair.get(
                    'Gene2SpeciesTaxonID') == self.taxon2:
                genes[pair.get('Gene2ID')] = pair.get('Gene1ID')  # rat gene id: mouse gene id
        return genes

