"""Test the Alliance Ortholog processor."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.gopreprocess.file_processors.alliance_orthology_processor import OrthoProcessor

# Mock data based on the given example
MOCK_ORTHOLOG_DATA = {
    "metadata": {},  # Assuming the metadata structure based on your example
    "data": [{"Gene1ID": "MGI:1270148", "Gene1SpeciesTaxonID": "NCBITaxon:10090", "Gene2ID": "SGD:S000002810", "Gene2SpeciesTaxonID": "NCBITaxon:559292"}],
}

# Mock target genes
MOCK_TARGET_GENES = {
    "MGI:MGI:1270148": {"id": "MGI:MGI:1270148", "fullname": ["RIKEN cDNA 0610005C13 gene"], "label": "0610005C13Rik", "type": ["SO:0002127"]},
    "SGD:S000002810": {"id": "SGD:S000002810", "fullname": ["Cyp2j6"], "label": "Cyp2j6", "type": ["SO:0002127"]},
}


@pytest.fixture
def mock_file():
    """Fixture for creating a mock file."""
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_ORTHOLOG_DATA))) as mock_file:
        yield mock_file


def test_initialization(mock_file):
    """
    Test the initialization of the OrthoProcessor.

    :param mock_file: A mock file object
    :type mock_file: MagicMock
    """
    ortho_processor = OrthoProcessor(target_genes=MOCK_TARGET_GENES, filepath=Path("fake/path"), taxon1="NCBITaxon:10090", taxon2="NCBITaxon:559292")
    assert ortho_processor.taxon1 == "NCBITaxon:10090"
    assert ortho_processor.taxon2 == "NCBITaxon:559292"
    # Assuming the retrieve_ortho_map method is called during initialization
    assert "SGD:S000002810" in ortho_processor.genes
    assert ortho_processor.genes["SGD:S000002810"] == ["MGI:1270148"]


def test_retrieve_ortho_map(mock_file):
    """
    Test the retrieve_ortho_map method of the OrthoProcessor.

    :param mock_file: A mock file object
    :type mock_file: MagicMock
    """
    ortho_processor = OrthoProcessor(target_genes=MOCK_TARGET_GENES, filepath=Path("fake/path"), taxon1="NCBITaxon:10090", taxon2="NCBITaxon:559292")
    genes = ortho_processor.retrieve_ortho_map()
    assert "SGD:S000002810" in genes
    assert genes["SGD:S000002810"] == ["MGI:1270148"]
