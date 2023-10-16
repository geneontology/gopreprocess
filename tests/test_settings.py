"""Test the settings module."""
import unittest
from unittest import skip

from src.utils.settings import get_url


class TestGetURL(unittest.TestCase):

    """Test the get_url function."""

    @skip("gaf file location in flux")
    def test_get_url(self):
        """Test the get_url function."""
        expected_url = "ftp.ebi.ac.uk/pub/databases/GO/goa/MOUSE/goa_mouse.gaf.gz"
        actual_url = get_url("MGI_GAF")
        self.assertEqual(actual_url, expected_url)


if __name__ == "__main__":
    """
    Run the unit tests

    """
    unittest.main()
