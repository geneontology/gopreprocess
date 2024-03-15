"""Test the GAF processor."""
from unittest import skip

import pytest
from unittest.mock import patch, mock_open
from src.gopreprocess.file_processors.gaf_processor import GafProcessor
from pathlib import Path


# Sample GAF data reduced for brevity and example purposes
SAMPLE_GAF_DATA = """
!gaf-version: 2.2
!generated-by: RGD
!date-generated: 2024-03-09
RGD\t10045371\tMir155hg\tinvolved_in\tGO:0002605\tRGD:1624291\tISO\tUniProtKB:C0HMA1\tP\tMir155 host gene\t\tgene\ttaxon:10116\t20231002\tRGD\t\t
RGD\t10045371\tMir155hg\tlocated_in\tGO:0005634\tRGD:1624291\tISO\tUniProtKB:C0HMA1\tC\tMir155 host gene\t\tgene\ttaxon:10116\t20231002\tRGD\t\t
RGD\t10045371\tMir155hg\tlocated_in\tGO:0005737\tRGD:1624291\tISO\tUniProtKB:C0HMA1\tC\tMir155 host gene\t\tgene\ttaxon:10116\t20231002\tRGD\t\t
RGD\t10045371\tMir155hg\tenables\tGO:0030544\tRGD:1624291\tISO\tUniProtKB:C0HMA1\tF\tMir155 host gene\t\tgene\ttaxon:10116\t20231002\tRGD\t\t
RGD\t10045415\tKantr\tacts_upstream_of_or_within\tGO:0010629\tRGD:1624291\tISO\tMGI:1920247\tP\tKANTR integral membrane protein\t\tgene\ttaxon:10116\t20161221\tRGD\t\t
RGD\t10059729\tBaiap3\tenables\tGO:0000149\tRGD:1624291\tISO\tUniProtKB:O94812\tF\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20180326\tRGD\t\t
RGD\t10059729\tBaiap3\tinvolved_in\tGO:0001956\tRGD:1624291\tISO\tUniProtKB:O94812\tP\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20180326\tRGD\t\t
RGD\t10059729\tBaiap3\tenables\tGO:0005509\tRGD:1624291\tISO\tUniProtKB:O94812\tF\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20180326\tRGD\t\t
RGD\t10059729\tBaiap3\tenables\tGO:0005543\tRGD:1624291\tISO\tUniProtKB:O94812\tF\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20180326\tRGD\t\t
RGD\t10059729\tBaiap3\tlocated_in\tGO:0005829\tRGD:1624291\tISO\tUniProtKB:O94812\tC\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20180326\tRGD\t\t
RGD\t10059729\tBaiap3\tlocated_in\tGO:0005886\tRGD:1624291\tISO\tUniProtKB:O94812\tC\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20180326\tRGD\t\t
RGD\t10059729\tBaiap3\tinvolved_in\tGO:0006887\tGO_REF:0000043|RGD:1600115\tIEA\tUniProtKB-KW:KW-0268\tP\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20240129\tUniProt\t\tUniProtKB:A0A8I5Y6X2
RGD\t10059729\tBaiap3\tacts_upstream_of_or_within\tGO:0007186\tRGD:1624291\tISO\tUniProtKB:O94812\tP\tBAI1-associated protein 3\t\tgene\ttaxon:10116\t20091111\tRGD\t\t
"""


@pytest.fixture
def gaf_processor():
    """Fixture for creating a GafProcessor instance with mocked dependencies."""
    with patch('src.gopreprocess.file_processors.gaf_processor.GafParser') as MockGafParser, \
            patch('src.gopreprocess.file_processors.gaf_processor.EcoMap') as MockEcoMap:

        # Creating an instance of GafProcessor for testing
        processor = GafProcessor(
            filepath=Path("dummy/path"),
            namespaces=["P"],  # Adjust based on your test needs
            taxon_to_provider={"taxon:10116": "RGD"},  # Example mapping
            target_taxon="taxon:10116",  # Example taxon
            uniprot_to_hgnc_map={"UniProtKB:C0HMA1": "HGNC:12345"},  # Example mapping
            source="GOA"  # Example source
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
