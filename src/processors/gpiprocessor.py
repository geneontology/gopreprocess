from ontobio.io.entityparser import GpiParser
from typing import List
from pathlib import Path
from src.utils.decorators import timer

class GpiProcessor:
    """
    A class for processing GPI (Gene Product Information) files.

    Attributes:
        filepath (str): The path to the GPI file.
        target_genes (List[str]): A list of gene IDs extracted from the GPI file.

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
        self.target_genes: dict = self.parse_gpi()

    @timer
    def parse_gpi(self) -> dict:
        """
        Parses the GPI file and extracts the gene IDs.
        """
        p = GpiParser()
        target_genes = {}
        with open(self.filepath, 'r') as file:
            for line in file:
                original_line, gpi_object = p.parse_line(line)
                if original_line.startswith("!"):
                    continue
                else:
                    for gene in gpi_object:
                        target_genes[str(gene.get("id"))] = {
                                    "id": gene.get("id"),
                                    "fullname": gene.get("full_name"),
                                    "label": gene.get("label"),
                                    "type": gene.get("type")
                        }

        return target_genes
