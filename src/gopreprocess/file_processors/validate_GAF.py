from ontobio.io.assocparser import AssocParserConfig
from ontobio.io.gafparser import GafParser
from gopreprocess.file_processors.ontology_processor import get_ontology_factory
from src.utils.decorators import timer
from src.utils.settings import taxon_to_provider
from pystow import join
import sys

@timer
def validate_gaf(target_taxon: str):
    print(target_taxon, "target_taxon")
    # Ontology Factory
    ont = get_ontology_factory
    config = AssocParserConfig(ontology=ont, rule_set="all")
    gaf_to_validate = join(
        key=taxon_to_provider[target_taxon],
        name=taxon_to_provider[target_taxon].lower() + "-merged.gaf",
        ensure_exists=True,
    )

    parser = GafParser(config=config)
    errors = []
    parser.parse(file=str(gaf_to_validate), skipheader=True)
    for error_report in parser.report.messages:
        if error_report.get("level") == "ERROR":
            errors.append(error_report)
    if errors:
        print("Errors found in GAF file:")
        for error in errors:
            print(error)  # Or format error information as needed
        sys.exit(1)  # Exit with a non-zero status to indicate failure

    # print(parser.report.to_report_json())


if __name__ == "__main__":
    validate_gaf("NCBITaxon:10090")
