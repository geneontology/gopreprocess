import unittest
from src.processors.orthoprocessor import OrthoProcessor
import os
from pathlib import Path


class TestGPIProcessor(unittest.TestCase):

    def test_parse_gpi(self):
        data_path = os.path.expanduser("~/.data/ORTHO/")
        file_path = Path(os.path.join(data_path, "ORTHOLOGY-ALLIANCE-JSON_COMBINED.json"))
        self.assertTrue(file_path.exists())
        ortho_genes = OrthoProcessor(filepath=file_path,
                                     taxon1="NCBITaxon:10116",
                                     taxon2="NCBITaxon:10090",
                                     target_genes={"MGI:1915549": "RGD:1311391"})
        self.assertTrue(type(ortho_genes.genes) == dict)
        print(type(ortho_genes.genes))
        # print(len(ortho_genes.target_genes))
        # self.assertTrue(len(ortho_genes.target_genes) > 0)


if __name__ == '__main__':
    unittest.main()
