"""testing GPI processor."""

import pytest
from unittest.mock import mock_open
from pathlib import Path
from src.gopreprocess.file_processors.gpi_processor import GpiProcessor, eliminate_repeated_values


def test_eliminate_repeated_values():
    """
    Test the eliminate_repeated_values function.

    """
    input_dict = {
        "key1": "value1",
        "key2": "value1",  # Duplicate value
        "key3": "value2",
    }
    expected_output = {
        "value2": "key3",
    }
    assert eliminate_repeated_values(input_dict) == expected_output


mock_gpi_lines = """!gpi-version: 1.2
MGI\tMGI:1915609\t0610010K14Rik\tRIKEN cDNA 0610010K14 gene\tAMOT\tprotein_coding_gene\ttaxon:10090\tUniProtKB:Q4VCS5\tUniProtKB:test\tdb_subset=test
MGI\tMGI:1915975\t1110032F04Rik\tRIKEN cDNA 1110032F04 gene\tAMOT\tprotein_coding_gene\ttaxon:10090\tUniProtKB:Q4VCS5\tUniProtKB:test\tdb_subset=test
MGI\tMGI:1916647\t1700019A02Rik\tRIKEN cDNA 1700019A02 gene\tAMOT\tprotein_coding_gene\ttaxon:10090\tUniProtKB:Q4VCS5\tUniProtKB:A0A087WPV9\tdb_subset=test
"""


# Using pytest-mock to mock the open function
@pytest.fixture
def mock_file_open(mocker):
    """
    Mock the open function and return a mock object.

    """
    mock_open_obj = mock_open(read_data="".join(mock_gpi_lines))
    mocker.patch("builtins.open", mock_open_obj)
    return mock_open_obj


# Test the GpiProcessor.get_target_genes method
def test_get_target_genes(mock_file_open):
    """
    Test the get_target_genes method of the GpiProcessor.

    """
    processor = GpiProcessor(filepath=Path("/fake/path"))
    target_genes = processor.get_target_genes()
    # Define your expected output based on the mock_gpi_lines and assert here
    assert target_genes.get("MGI:MGI:1915609") == {
                                    'fullname': ['RIKEN cDNA 0610010K14 gene'],
                                    'id': 'MGI:MGI:1915609',
                                    'label': '0610010K14Rik',
                                    'type': ['protein_coding_gene']
    }
    xrefs = processor.get_xrefs()
    assert xrefs.get('UniProtKB:A0A087WPV9') == "MGI:MGI:1916647"



