from ontobio.io.entityparser import GpiParser
from typing import List


class GpiProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.mgi_genes: List[str] = []
        self.parse_gpi()

    def parse_gpi(self):
        p = GpiParser()
        with open(self.filepath, 'r') as file:
            for line in file:
                _, gpi_object = p.parse_line(line)
                self.mgi_genes.append(gpi_object.id)
