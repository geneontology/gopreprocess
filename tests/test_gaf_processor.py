import unittest
from src.processors.gafprocessor import GafProcessor
import os
from pathlib import Path


class TestGPIProcessor(unittest.TestCase):

    def test_parse_gpi(self):
        data_path = os.path.expanduser("~/.data/RGD/")
        file_path = Path(os.path.join(data_path, "rgd.gaf"))
        self.assertTrue(file_path.exists())
        namespaces = ["UniProt", "RGD"]
        genes = ["RGD:1311391", "RGD:1586427"]
        resulting_genes = GafProcessor(filepath=file_path, namespaces=namespaces, genes=genes)
        self.assertTrue(len(resulting_genes.ortho_genes) > 0)


if __name__ == '__main__':
    unittest.main()
