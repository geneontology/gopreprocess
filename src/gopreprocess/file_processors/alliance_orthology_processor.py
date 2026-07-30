"""Module for processing ortholog data from the Alliance of Genome Resources."""

import csv
from pathlib import Path

from src.utils.decorators import timer

# Columns this processor depends on. The Alliance orthology TSV has kept this
# layout across releases; the JSON payloads have not (see gopreprocess#78).
REQUIRED_COLUMNS = ("Gene1ID", "Gene1SpeciesTaxonID", "Gene2ID", "Gene2SpeciesTaxonID")


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

        Reads the Alliance orthology TSV. The file carries a leading block of
        "#" banner lines before the header row.

        :raises ValueError: if the file does not carry the expected columns, or if
            the resulting map is empty. Both are treated as errors rather than an
            empty result: this pipeline's output is consumed downstream (by GOA,
            and from there back into the GO release), so returning {} here would
            silently drop every orthology-inferred annotation instead of failing.
        :return: A dictionary mapping source gene IDs to lists of target gene IDs.
        """
        with open(self.filepath, "r") as file:
            reader = csv.DictReader((line for line in file if not line.startswith("#")), delimiter="\t")

            fieldnames = reader.fieldnames or []
            missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
            if missing:
                raise ValueError(
                    f"Alliance orthology file {self.filepath} is missing expected column(s): "
                    f"{', '.join(missing)}. Found: {', '.join(fieldnames) or '(no header)'}. "
                    "The upstream format has probably changed; see gopreprocess#78."
                )

            genes = {}
            target_gene_set = set(self.target_genes.keys())
            for pair in reader:
                if pair.get("Gene1SpeciesTaxonID") == self.taxon1 and pair.get("Gene2SpeciesTaxonID") == self.taxon2:
                    # Exclude any ortho pairs where the target gene (mouse) isn't in the GPI file.
                    if "MGI:" + str(pair.get("Gene1ID")) in target_gene_set:
                        # source gene id: target gene id, e.g. rat gene id : mouse gene id
                        if pair.get("Gene2ID") in genes:
                            genes[pair.get("Gene2ID")].append(pair.get("Gene1ID"))
                        else:
                            genes[pair.get("Gene2ID")] = [pair.get("Gene1ID")]

        if not genes:
            raise ValueError(
                f"No orthologs found in {self.filepath} for {self.taxon2} -> {self.taxon1}. "
                "Expected thousands. Either the upstream orthology file no longer covers this "
                "taxon pair, or the target GPI did not match any ortholog partners."
            )

        return genes
