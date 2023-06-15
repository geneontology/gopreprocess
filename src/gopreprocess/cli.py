import click
from preprocessor import AnnotationConverter


@click.command()
@click.option("--namespaces", default=["RGD", "UniProtKB"], help="List of namespaces to use.")
@click.option("--target_taxon", default="NCBITaxon:10090", help="Target taxon.")
@click.option("--source_taxon", default="NCBITaxon:10116", help="Source taxon.")
@click.option("--iso_code", default="0000266", help="ISO ECO code without prefix.")
@click.option("--ortho_reference", default="0000096", help="Ortho reference.")
def convert_annotations(namespaces, target_taxon, source_taxon, iso_code, ortho_reference):
    converter = AnnotationConverter(namespaces, target_taxon, source_taxon, iso_code, ortho_reference)
    converter.convert_annotations()


if __name__ == '__main__':
    convert_annotations()

