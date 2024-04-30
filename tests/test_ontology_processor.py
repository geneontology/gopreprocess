"""testing ontology processor."""

from gopreprocess.file_processors.ontology_processor import get_GO_aspector, get_ontology_factory


def test_ontology_processor():
    """Test that the aspector is working to retrieve ancestors."""
    go_aspector = get_GO_aspector("GO")
    assert go_aspector.is_biological_process("GO:0051179") is True
    assert go_aspector.is_biological_process("GO_0051179") is False
    assert go_aspector.is_biological_process("0051179") is False


def test_ontology_factory():
    """Test that the ontology factory is working to retrieve ancestors."""
    # using this special "GO_RELEASE" key because often times the go.json file is missing from one or another
    # pipeline skyhook locations so for the tests, we use the one from release that is most likely to be there.
    go_onto = get_ontology_factory("GO")
    assert go_onto is not None
