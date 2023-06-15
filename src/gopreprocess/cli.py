import click
from src.gopreprocess.annotation_converter import AnnotationConverter


@click.command()
@click.option("--namespaces", default=["RGD", "UniProtKB"], help="List of providers in the source GAF that should be "
                                                                 "used to retrieve source annotations for conversion.")
@click.option("--target_taxon", default="NCBITaxon:10090", help="Target taxon in curie format using NCBITaxon prefix.")
@click.option("--source_taxon", default="NCBITaxon:10116", help="Source taxon in curie format using NCBITaxon prefix.")
@click.option("--ortho_reference", default="0000096", help="Ortho reference in curie format.")
def convert_annotations(namespaces, target_taxon, source_taxon, iso_code, ortho_reference):
    converter = AnnotationConverter(namespaces, target_taxon, source_taxon, ortho_reference)
    converter.convert_annotations()


if __name__ == '__main__':
    convert_annotations()

