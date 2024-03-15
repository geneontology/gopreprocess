"""testing ontology processor."""

from unittest import skip

from gopreprocess.file_processors.ontology_processor import get_GO_aspector, get_ontology_factory


@skip("go.json location is unknown to code until pipeline runs")
def test_ontology_processor():
    """
    Test that the aspector is working to retrieve ancestors.

    """
    go_aspector = get_GO_aspector("GO")
    assert go_aspector.is_biological_process("GO:0051179") is True
    assert go_aspector.is_biological_process("GO_0051179") is False
    assert go_aspector.is_biological_process("0051179") is False


def test_ontology_factory():
    """
    Test that the ontology factory is working to retrieve ancestors.

    """
    go_onto = get_ontology_factory("GO_RELEASE")
    assert go_onto is not None
    print(go_onto[0:10])
