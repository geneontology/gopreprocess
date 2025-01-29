"""Module for processing ortholog data from the Alliance of Genome Resources."""

import json
from pathlib import Path

from src.utils.decorators import timer


class OrthoProcessor:
    """
    Represents a processor for ortholog data between two taxa.

    :param target_genes: List of partner genes.
    :param filepath: Path to the ortholog data file.
    :param taxon1: Taxon ID of the first species.
    :param taxon2: Taxon ID of the second species.
    """

    def __init__(self, target_genes: dict, filepath: Path, taxon1: str, taxon2: str):
        """
        Initializes an instance of the OrthoProcessor.

        :param target_genes: List of source genes.
        :param filepath: Path to the ortholog data file.
        :param taxon1: Taxon ID of the first species.
        :param taxon2: Taxon ID of the second species.
        """
        self.target_genes = target_genes
        self.filepath = filepath
        self.taxon1 = taxon1
        self.taxon2 = taxon2
        self.genes = self.retrieve_ortho_map()

    @timer
    def retrieve_ortho_map(self):
        """
        Retrieves ortholog data between the two taxa.

        :return: A dictionary mapping rat gene IDs to corresponding mouse gene IDs.
        """
        with open(self.filepath, "r") as file:
            data = json.load(file)

        genes = {}
        target_gene_set = set(self.target_genes.keys())
        for pair in data.get("data"):
            if pair.get("Gene1SpeciesTaxonID") == self.taxon1 and pair.get("Gene2SpeciesTaxonID") == self.taxon2:
                # Exclude any ortho pairs where the target gene (mouse) isn't in the GPI file.
                if "MGI:" + str(pair.get("Gene1ID")) in target_gene_set:
                    # source gene id: target gene id, e.g. rat gene id : mouse gene id
                    if pair.get("Gene2ID") in genes:
                        genes[pair.get("Gene2ID")].append(pair.get("Gene1ID"))
                    else:
                        genes[pair.get("Gene2ID")] = [pair.get("Gene1ID")]

        return genes
