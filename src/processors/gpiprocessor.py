from ontobio.io.entityparser import GpiParser
from typing import List


class GpiProcessor:
    """
    A class for processing GPI (Gene Product Information) files.

    Attributes:
        filepath (str): The path to the GPI file.
        genes (List[str]): A list of gene IDs extracted from the GPI file.

    Methods:
        __init__(self, filepath): Initializes a new instance of GpiProcessor.
        parse_gpi(self): Parses the GPI file and extracts the gene IDs.
    """

    def __init__(self, filepath: str):
        """
        Initializes a new instance of GpiProcessor.

        :param filepath: The path to the GPI file.
        :type filepath: str
        """
        self.filepath = filepath
        self.genes: List[str] = []
        self.parse_gpi()

    def parse_gpi(self):
        """
        Parses the GPI file and extracts the gene IDs.
        """
        p = GpiParser()

        with open(self.filepath, 'r') as file:
            for line in file:
                original_line, gpi_object = p.parse_line(line)
                if original_line.startswith("!"):
                    continue
                else:
                    for gene in gpi_object:
                        self.genes.append(gene.get("id")[4:])  # remove MGI:MGI: prefix
