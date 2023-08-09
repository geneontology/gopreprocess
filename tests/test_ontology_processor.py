"""testing ontology processor."""
import os
import unittest
from pathlib import Path
from gopreprocess.processors.ontology_processor import get_GO_aspector


class TestOntologyProcessor(unittest.TestCase):

    """
    Test the Ontology processor.

    """

    def test_ontology_processor(self):
        """
        Test the files exist.

        """
        data_path = os.path.expanduser("tests/resources")
        file_path = Path(os.path.join(data_path, "localization.json"))
        print(file_path)
        go_aspector = get_GO_aspector("GO")
        self.assertTrue(go_aspector.is_biological_process("GO:0051179"))
        self.assertFalse(go_aspector.is_biological_process("GO_0051179"))
        self.assertFalse(go_aspector.is_biological_process("0051179"))


if __name__ == "__main__":
    """
    Run the unit tests

    """
    unittest.main()
