import click
from src.gopreprocess.annotation_converter import AnnotationConverter


@click.command()
@click.option("--namespaces", default=["RGD", "UniProtKB"], help="List of providers in the source GAF that should be "
                                                                 "used to retrieve source annotations for conversion. "
                                                                 "e.g. [RGD, UniProtKB]")
@click.option("--target_taxon", default="NCBITaxon:10090", help="Target taxon in curie format using NCBITaxon prefix. "
                                                                "e.g. NCBITaxon:10090")
@click.option("--source_taxon", default="NCBITaxon:10116", help="Source taxon in curie format using NCBITaxon prefix. "
                                                                "e.g. NCBITaxon:10116")
@click.option("--ortho_reference", default="GO_REF:0000096", help="Ortho reference in curie format. "
                                                                  "e.g. GO_REF:0000096")
def convert_annotations(namespaces, target_taxon, source_taxon, ortho_reference):
    print("namespaces: ", namespaces)
    print("target_taxon: ", target_taxon)
    print("source_taxon: ", source_taxon)
    print("ortho_reference: ", ortho_reference)
    converter = AnnotationConverter(namespaces, target_taxon, source_taxon, ortho_reference)
    converter.convert_annotations()


if __name__ == '__main__':
    convert_annotations()

