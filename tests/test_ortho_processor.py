import unittest
from src.gopreprocess.processors.alliance_ortho_processor import OrthoProcessor
import os
from pathlib import Path


class TestGPIProcessor(unittest.TestCase):

    def test_parse_gpi(self):
        data_path = os.path.expanduser("tests/resources")
        file_path = Path(os.path.join(data_path, "test_ortho.json"))
        self.assertTrue(file_path.exists())


if __name__ == '__main__':
    unittest.main()
