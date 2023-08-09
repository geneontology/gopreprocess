"""Module contains the Ontology processor class."""
from ontobio.io import assocparser
from ontobio.ontol_factory import OntologyFactory
from src.utils.download import download_file
from src.utils.decorators import timer
from ontobio.util.go_utils import GoAspector as Aspector


@timer
def get_GO_aspector(ontology_config_key: str) -> Aspector:
    """
    Returns an Aspector object for the given ontology.

    :param ontology_config_key: The key in the config file in this repo
     that contains the URL to download the ontology from.
    :return: An ontobio Aspector object for the given ontology which has methods to get descendents, ancestors, etc.
    """
    ontology_json_filepath = download_file(target_directory_name="GO", config_key=ontology_config_key)
    go_onto = OntologyFactory().create(str(ontology_json_filepath))
    assoc_parser = assocparser.AssocParserConfig(ontology=go_onto)
    return Aspector(assoc_parser.ontology)
