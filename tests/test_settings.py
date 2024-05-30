"""Test the settings module."""

from src.utils.settings import get_url


def test_get_url():
    """Test the get_url function."""
    expected_url = "http://snapshot.geneontology.org/products/upstream_and_raw_data/mgi-src.gpi.gz"
    actual_url = get_url("MGI_GPI")
    assert actual_url == expected_url
