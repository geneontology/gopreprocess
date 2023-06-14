from ontobio.io.entityparser import GpiParser
from typing import List
from pathlib import Path


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

    def __init__(self, filepath: Path):
        """
        Initializes a new instance of GpiProcessor.

        :param filepath: The path to the GPI file.
        :type filepath: str
        """
        self.filepath: Path = filepath
        self.genes: dict = self.parse_gpi()

    def parse_gpi(self) -> dict:
        """
        Parses the GPI file and extracts the gene IDs.
        """
        p = GpiParser()
        genes = {}
        with open(self.filepath, 'r') as file:
            for line in file:
                original_line, gpi_object = p.parse_line(line)
                if original_line.startswith("!"):
                    continue
                else:
                    for gene in gpi_object:
                        genes[str(gene.get("id")[4:])] = {  # remove MGI:MGI: prefix
                                    "fullname": gene.get("full_name"),
                                    "label": gene.get("label"),
                                    "type": gene.get("type")
                        }

        return genes
