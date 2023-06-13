import json


class OrthoProcessor:
    """
    Represents a processor for orthology data between two taxa.

    :param partner_genes: List of partner genes.
    :param filepath: Path to the orthology data file.
    :param taxon1: Taxon ID of the first species.
    :param taxon2: Taxon ID of the second species.
    """

    def __init__(self, partner_genes, filepath, taxon1, taxon2):
        """
        Initializes an instance of the OrthoProcessor.

        :param partner_genes: List of partner genes.
        :param filepath: Path to the orthology data file.
        :param taxon1: Taxon ID of the first species.
        :param taxon2: Taxon ID of the second species.
        """

        self.partner_genes = partner_genes
        self.filepath = filepath
        self.taxon1 = taxon1
        self.taxon2 = taxon2

        self.genes = self.get_data()

    def get_data(self):
        """
        Retrieves orthology data between the two taxa.

        :return: A dictionary mapping rat gene IDs to corresponding mouse gene IDs.
        """

        with open(self.filepath, 'r') as file:
            data = json.load(file)

        genes = {}
        for pair in data.get('data'):
            if pair.get('Gene1SpeciesTaxonID') == self.taxon1 and pair.get('Gene2SpeciesTaxonID') == self.taxon2:
                if pair.get('Gene1ID') in self.partner_genes:
                    # Exclude any ortho pairs where the Mouse gene isn't in the GPI file.
                    genes[pair.get('Gene2ID')] = pair.get('Gene1ID')  # rat gene id: mouse gene id

        return genes
