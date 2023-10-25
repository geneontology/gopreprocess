"""A module for processing GPI (Gene Product Information) files."""

from pathlib import Path

from ontobio.io.entityparser import GpiParser

from src.utils.decorators import timer


class GpiProcessor:

    """
    A class for processing GPI (Gene Product Information) files.

    Attributes
    ----------
        filepath (str): The path to the GPI file.
        target_genes (List[str]): A list of gene IDs extracted from the GPI file.

    Methods
    -------
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
        self.target_genes: dict = self.get_target_genes()

    @timer
    def get_target_genes(self) -> dict:
        """Parses the GPI file and extracts the gene IDs."""
        p = GpiParser()
        target_genes = {}
        with open(self.filepath, "r") as file:
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
                            "type": gene.get("type"),
                        }

        return target_genes

    def get_xrefs(self) -> dict:
        """
        Parses the GPI using teh GpiParser class, extracts column 9, the xrefs into a dictionary that contains the gene
         as the key and the xrefs as a list of values.

        :return: dictionary of gene ids and xrefs
        """
        p = GpiParser()
        xrefs = {}
        with open(self.filepath, "r") as file:
            for line in file:
                original_line, gpi_object = p.parse_line(line)
                if original_line.startswith("!"):
                    continue
                else:
                    for gene in gpi_object:
                        if len(gene.get('xrefs')) > 1:
                            continue
                        else:
                            xrefs[str(gene.get("id"))] = gene.get("xrefs")
        return xrefs
