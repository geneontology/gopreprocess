import os
import unittest
from pathlib import Path


class TestGPIProcessor(unittest.TestCase):
    def test_parse_gpi(self):
        data_path = os.path.expanduser("tests/resources")
        file_path = Path(os.path.join(data_path, "test_gaf.gaf"))
        self.assertTrue(file_path.exists())


if __name__ == "__main__":
    unittest.main()
