"""A module for processing GPI (Gene Product Information) files."""

from pathlib import Path

from ontobio.io.entityparser import GpiParser

from src.utils.decorators import timer

@timer
def eliminate_repeated_values(input_dict):
    """
    Eliminates repeated values from a dictionary.

    :param input_dict: The input dictionary.
    :type input_dict: dict
    :return: A new dictionary with only the unique values.
    :rtype: dict
    """
    # Reverse the dictionary to identify unique values
    first_item = next(iter(input_dict.items()))
    print(first_item)
    reversed_dict = {}
    print(len(input_dict))
    for key, value in input_dict.items():
        if value not in reversed_dict:
            reversed_dict[value] = key
        else:
            # If the value is already in the reversed_dict, set it to None to indicate it's not unique
            reversed_dict[value] = None

    # Create a new dictionary with only the unique values
    output_dict = {value: key for value, key in reversed_dict.items() if key is not None}
    print(len(output_dict))
    first_item = next(iter(output_dict.items()))
    print(first_item)
    return output_dict


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
        """
        Parses the GPI file and extracts the gene IDs.

        :return: A dictionary of gene IDs.
        """
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

    @timer
    def get_xrefs(self) -> dict:
        """
        Parses the GPI using the GpiParser class, extracts column 9, the xrefs into a dictionary that contains the gene
         as the key and the xrefs as a list of values.

        :return: dictionary of gene ids and xrefs
        """
        p = GpiParser()
        uniprot_ids = {}
        with open(self.filepath, "r") as file:
            for line in file:
                original_line, gpi_object = p.parse_line(line)
                if original_line.startswith("!"):
                    continue
                else:
                    # parse_line returns a list of dictionaries for some reason.
                    for row in gpi_object:
                        if row.get("xrefs") is None:
                            continue
                        else:
                            for xid in row.get('xrefs'):
                                # we only want 1:1 mappings between genes and each xref
                                if xid.startswith("UniProtKB:"):
                                    uniprot_ids[row.get("id")] = xid

        # eliminate duplicate mappings
        xrefs = eliminate_repeated_values(uniprot_ids)
        return xrefs
