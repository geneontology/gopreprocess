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
    reversed_dict = {}
    for key, value in input_dict.items():
        if value not in reversed_dict:
            reversed_dict[value] = key
        else:
            # If the value is already in the reversed_dict, set it to None to indicate it's not unique
            reversed_dict[value] = None

    # Create a new dictionary with only the unique values
    output_dict = {value: key for value, key in reversed_dict.items() if key is not None}
    qc_output_dict = {value: key for value, key in reversed_dict.items() if key is None}
    filename = "output_dict.txt"
    qc_filename = "removed_xrefs_output_dict.txt"
    # Write the dictionary to a file
    with open(filename, "w") as file:
        for key, value in output_dict.items():
            file.write(f"{key} {value}\n")

    with open(qc_filename, "w") as file:
        for key, value in qc_output_dict.items():
            file.write(f"{key} {value}\n")

    return output_dict


class GpiProcessor:
    """
    A class for processing GPI (Gene Product Information) files.

    :param filepath: The path to the GPI file.
    :type filepath: str
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
        Parses the GPI using the GpiParser class.

        Extracts column 9, the xrefs into a dictionary that contains the gene as the key and the xrefs as a
        list of values.

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
                            # MGI:MGI:1914937 UniProtKB:Q9DAF8
                            if not row.get("id").startswith("MGI:"):
                                continue
                            for xid in row.get("xrefs"):
                                # we only want 1:1 mappings between genes and each xref
                                if xid.startswith("UniProtKB:"):
                                    uniprot_ids[row.get("id")] = xid

        qc_filename = "xrefs_mgi.txt"
        with open(qc_filename, "w") as file:
            for key, value in uniprot_ids.items():
                file.write(f"{key} {value}\n")

        # eliminate duplicate mappings
        xrefs = eliminate_repeated_values(uniprot_ids)
        return xrefs

    @timer
    def get_protein_xrefs(self) -> (dict, dict):
        """
        Parses the GPI using the GpiParser class.

        Extracts column 9, the xrefs into a dictionary that contains the protein (PRO id) as the key and the xrefs as a
        list of values.

        :return: dictionary of protein ids and xrefs
        """
        p = GpiParser()
        xref_ids = {}
        parent_xref_ids = {}
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
                            if row.get("id").startswith("PR:"):
                                # PR:Q9DAQ4-1 = UniProtKB:Q9DAQ4-1
                                # PR:Q9DAQ4-1 = MGI:MGI:87961
                                for xid in row.get("xrefs"):
                                    if xid.startswith("UniProtKB:"):
                                        xref_ids[row.get("id")] = xid
                                for ebid in row.get("encoded_by"):
                                    if ebid.startswith("MGI:"):
                                        parent_xref_ids[row.get("id")] = ebid

        qc_filename = "xref_pr.txt"
        with open(qc_filename, "w") as file:
            for key, value in xref_ids.items():
                file.write(f"{key} {value}\n")

        parents_filename = "parent_pr.txt"
        with open(parents_filename, "w") as file:
            for key, value in parent_xref_ids.items():
                file.write(f"{key} {value}\n")

        # eliminate duplicate mappings
        xrefs = eliminate_repeated_values(xref_ids)
        return xrefs, parent_xref_ids
