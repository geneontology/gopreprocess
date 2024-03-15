"""Test the settings module."""

from src.utils.settings import get_url


def test_get_url():
    """Test the get_url function."""
    expected_url = "http://skyhook.berkeleybop.org/silver-issue-325-gopreprocess/products/upstream_and_raw_data/mgi-src.gaf.gz"
    actual_url = get_url("MGI_GAF")
    assert actual_url == expected_url
