"""testing ontology processor."""

import unittest
from unittest import skip

from gopreprocess.file_processors.ontology_processor import get_GO_aspector


@skip("go.json location is unknown to code until pipeline runs")
def test_ontology_processor():
    """
    Test that the aspector is working to retrieve ancestors.

    """
    go_aspector = get_GO_aspector("GO")
    assert go_aspector.is_biological_process("GO:0051179") is True
    assert go_aspector.is_biological_process("GO_0051179") is False
    assert go_aspector.is_biological_process("0051179") is False

