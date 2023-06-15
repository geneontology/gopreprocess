import unittest
from src.processors.gpiprocessor import GpiProcessor
import os
from pathlib import Path


class TestGPIProcessor(unittest.TestCase):

    def test_parse_gpi(self):
        data_path = os.path.expanduser("~/.data/MGI/")
        file_path = Path(os.path.join(data_path, "mgi.gpi"))
        self.assertTrue(file_path.exists())
        gpi_genes = GpiProcessor(file_path)
        self.assertTrue(type(gpi_genes.target_genes) == dict)
        self.assertTrue(len(gpi_genes.target_genes) > 0)
