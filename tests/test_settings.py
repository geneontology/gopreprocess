import unittest
from src.utils.settings import get_url


class TestGetURL(unittest.TestCase):
    def test_get_url(self):
        expected_url = "ftp.ebi.ac.uk/pub/databases/GO/goa/MOUSE/goa_mouse.gaf.gz"
        actual_url = get_url("MGI_GAF")
        self.assertEqual(actual_url, expected_url)


if __name__ == '__main__':
    unittest.main()
