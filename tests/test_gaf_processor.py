"""Test the GAF processor."""

from pathlib import Path
from unittest import skip
from unittest.mock import mock_open, patch

import pytest

from src.gopreprocess.file_processors.gaf_processor import GafProcessor

# Sample GAF data reduced for brevity and example purposes
SAMPLE_GAF_DATA = """
!gaf-version: 2.2
!generated-by: RGD
!date-generated: 2024-03-09
RGD\t10045371\tMir155hg\tinvolved_in\tGO:0002605\tRGD:1624291\tISO\tUniProtKB:C0HMA1\tP\tMir155 host gene\t\tgene\ttaxon:10116\t20231002\tRGD\t\t
RGD\t10045371\tMir155hg\tlocated_in\tGO:0005634\tRGD:1624291\tISO\tUniProtKB:C0HMA1\tC\tMir155 host gene\t\tgene\ttaxon:10116\t20231002\tRGD\t\t
RGD\t10045371\tMir155hg\tlocated_in\tGO:0005737\tRGD:1624291\tISO\tUniProtKB:C0HMA1\tC\tMir155 host gene\t\tgene\ttaxon:10116\t20231002\tRGD\t\t
"""


@pytest.fixture
def gaf_processor():
    """Fixture for creating a GafProcessor instance with mocked dependencies."""
    with patch("src.gopreprocess.file_processors.gaf_processor.GafParser") as MockGafParser, patch("src.gopreprocess.file_processors.gaf_processor.EcoMap") as MockEcoMap:

        # Creating an instance of GafProcessor for testing
        processor = GafProcessor(
            filepath=Path("dummy/path"),
            namespaces=["P"],  # Adjust based on your test needs
            taxon_to_provider={"taxon:10116": "RGD"},  # Example mapping
            target_taxon="taxon:10116",  # Example taxon
            uniprot_to_hgnc_map={"UniProtKB:C0HMA1": "HGNC:12345"},  # Example mapping
            source="GOA",  # Example source
        )
        return processor


@skip("Not implemented")
def test_parse_ortho_gaf(gaf_processor):
    """Test the parse_ortho_gaf method of GafProcessor."""
    with patch("builtins.open", mock_open(read_data=SAMPLE_GAF_DATA)) as mocked_file:
        # Call the method under test
        annotations = gaf_processor.parse_ortho_gaf()
        print(annotations)

        assert len(annotations) > 0, "Should parse annotations from GAF data"
        assert annotations[0].subject.id == "HGNC:12345", "UniProt IDs should be mapped to HGNC IDs"
