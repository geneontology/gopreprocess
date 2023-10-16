"""testing ontology processor."""
import unittest
from unittest import skip

from gopreprocess.file_processors.ontology_processor import get_GO_aspector


class TestOntologyProcessor(unittest.TestCase):

    """Test the Ontology processor."""

    @skip("go.json location is unknown to code until pipeline runs")
    def test_ontology_processor(self):
        """Test that the aspector is working to retrieve ancestors."""
        go_aspector = get_GO_aspector("GO")
        self.assertTrue(go_aspector.is_biological_process("GO:0051179"))
        self.assertFalse(go_aspector.is_biological_process("GO_0051179"))
        self.assertFalse(go_aspector.is_biological_process("0051179"))


if __name__ == "__main__":
    """
    Run the unit tests

    """
    unittest.main()
