"""Test the Alliance Ortholog processor."""

from pathlib import Path

import pytest

from src.gopreprocess.file_processors.alliance_orthology_processor import OrthoProcessor

# The Alliance orthology TSV carries a block of "#" banner lines before the header.
BANNER = """\
##########################################################################
#
# Data type: Orthology
# Data format: tsv
# Alliance Database Version: 9.1.0
#
##########################################################################
"""

HEADER = "\t".join(
    [
        "Gene1ID",
        "Gene1Symbol",
        "Gene1SpeciesTaxonID",
        "Gene1SpeciesName",
        "Gene2ID",
        "Gene2Symbol",
        "Gene2SpeciesTaxonID",
        "Gene2SpeciesName",
        "Algorithms",
        "AlgorithmsMatch",
        "OutOfAlgorithms",
        "IsBestScore",
        "IsBestRevScore",
    ]
)

ROW = "\t".join(
    [
        "MGI:1270148",
        "0610005C13Rik",
        "NCBITaxon:10090",
        "Mus musculus",
        "SGD:S000002810",
        "Cyp2j6",
        "NCBITaxon:559292",
        "Saccharomyces cerevisiae",
        "InParanoid|OMA",
        "2",
        "9",
        "Yes",
        "Yes",
    ]
)

MOCK_TARGET_GENES = {
    "MGI:MGI:1270148": {"id": "MGI:MGI:1270148", "fullname": ["RIKEN cDNA 0610005C13 gene"], "label": "0610005C13Rik", "type": ["SO:0002127"]},
    "SGD:S000002810": {"id": "SGD:S000002810", "fullname": ["Cyp2j6"], "label": "Cyp2j6", "type": ["SO:0002127"]},
}


def write_tsv(tmp_path: Path, body: str, name: str = "ortho.tsv") -> Path:
    """Write a TSV fixture to a temp file and return its path."""
    filepath = tmp_path / name
    filepath.write_text(body)
    return filepath


@pytest.fixture
def ortho_file(tmp_path):
    """A well-formed Alliance orthology TSV with one mouse/yeast pair."""
    return write_tsv(tmp_path, BANNER + HEADER + "\n" + ROW + "\n")


def test_initialization(ortho_file):
    """
    Test the initialization of the OrthoProcessor.

    :param ortho_file: Path to a well-formed orthology TSV
    :type ortho_file: Path
    """
    ortho_processor = OrthoProcessor(target_genes=MOCK_TARGET_GENES, filepath=ortho_file, taxon1="NCBITaxon:10090", taxon2="NCBITaxon:559292")
    assert ortho_processor.taxon1 == "NCBITaxon:10090"
    assert ortho_processor.taxon2 == "NCBITaxon:559292"
    assert "SGD:S000002810" in ortho_processor.genes
    assert ortho_processor.genes["SGD:S000002810"] == ["MGI:1270148"]


def test_retrieve_ortho_map(ortho_file):
    """
    Test the retrieve_ortho_map method of the OrthoProcessor.

    :param ortho_file: Path to a well-formed orthology TSV
    :type ortho_file: Path
    """
    ortho_processor = OrthoProcessor(target_genes=MOCK_TARGET_GENES, filepath=ortho_file, taxon1="NCBITaxon:10090", taxon2="NCBITaxon:559292")
    genes = ortho_processor.retrieve_ortho_map()
    assert "SGD:S000002810" in genes
    assert genes["SGD:S000002810"] == ["MGI:1270148"]


def test_unexpected_schema_raises(tmp_path):
    """
    An upstream format change must fail loudly rather than yield an empty map.

    This is the gopreprocess#78 failure mode: the nested LinkML JSON the Alliance
    now publishes carries none of the columns this processor reads.

    :param tmp_path: pytest temporary directory
    :type tmp_path: Path
    """
    linkml_ish = write_tsv(tmp_path, "category\tsubjectGene\tobjectGene\ngene_to_gene_orthology\tMGI:2448436\tHGNC:11477\n")
    with pytest.raises(ValueError) as excinfo:
        OrthoProcessor(target_genes=MOCK_TARGET_GENES, filepath=linkml_ish, taxon1="NCBITaxon:10090", taxon2="NCBITaxon:559292")
    assert "Gene1ID" in str(excinfo.value)


def test_no_matching_orthologs_raises(ortho_file):
    """
    A well-formed file that yields nothing for the taxon pair must also raise.

    :param ortho_file: Path to a well-formed orthology TSV
    :type ortho_file: Path
    """
    with pytest.raises(ValueError) as excinfo:
        OrthoProcessor(target_genes=MOCK_TARGET_GENES, filepath=ortho_file, taxon1="NCBITaxon:10090", taxon2="NCBITaxon:9606")
    assert "No orthologs found" in str(excinfo.value)
