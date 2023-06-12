from ontobio.io.entityparser import GpiParser
from typing import List


class GpiProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.genes: List[str] = []
        self.parse_gpi()

    def parse_gpi(self):
        p = GpiParser()

        with open(self.filepath, 'r') as file:
            for line in file:
                original_line, gpi_object = p.parse_line(line)
                if original_line.startswith("!"):
                    continue
                else:
                    for gene in gpi_object:
                        self.genes.append(gene.get("id")[4:])  # remove MGI:MGI: prefix
