import unittest
from src.gopreprocess.processors.alliance_ortho_processor import OrthoProcessor
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


if __name__ == '__main__':
    unittest.main()
