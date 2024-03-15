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


mock_gpi_lines = """!gpi-version: 2.0
MGI:MGI:1918911\t0610005C13Rik\tRIKEN cDNA 0610005C13 gene\t\tSO:0002127\tNCBITaxon:10090\t\t\t\t\t
MGI:MGI:1923503\t0610006L08Rik\tRIKEN cDNA 0610006L08 gene\t\tSO:0002127\tNCBITaxon:10090\t\t\t\t\t
MGI:MGI:1915609\t0610010K14Rik\tRIKEN cDNA 0610010K14 gene\t\tSO:0001217\tNCBITaxon:10090\t\t\t\tUniProtKB:Q9DCT6\t
PR:Q9D937\tm1810009A15Rik\tuncharacterized protein C11orf98 homolog (mouse)\tm1810009A15Rik\tPR:000000001\tNCBITaxon:10090\tMGI:MGI:1913526\t\t\tUniProtKB:Q9D937\t
PR:Q9D727\tm2310039H08Rik\tuncharacterized protein C6orf226 homolog (mouse)\tm2310039H08Rik\tPR:000000001\tNCBITaxon:10090\tMGI:MGI:1914351\t\t\tUniProtKB:Q9D727\t

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
    assert target_genes.get("MGI:MGI:1918911") == {'id': 'MGI:MGI:1918911',
                                                   'fullname': ['RIKEN cDNA 0610005C13 gene'],
                                                   'label': '0610005C13Rik',
                                                   'type': ['SO:0002127']}
    xrefs = processor.get_xrefs()
    assert xrefs.get("UniProtKB:Q9DCT6") == 'MGI:MGI:1915609'
    protein_xrefs, parent_xrefs = processor.get_protein_xrefs()
    print(protein_xrefs)
    assert protein_xrefs, parent_xrefs == (
                             {'UniProtKB:Q9D937': 'PR:Q9D937', 'UniProtKB:Q9D727': 'PR:Q9D727'},
                             {'PR:Q9D937': 'MGI:MGI:1913526', 'PR:Q9D727': 'MGI:MGI:1914351'}
                            )



