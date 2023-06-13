from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gafprocessor import GafProcessor
from src.processors.gpiprocessor import GpiProcessor
from src.utils.download import download_files
from ontobio.model.association import GoAssociation, Curie, Subject
from ontobio.io.assocwriter import GpadWriter
import time
import pandas as pd
import pystow
from typing import Mapping

namespaces = ["RGD", "UniProtKB"]
mouse_taxon = "NCBITaxon:10090"
rat_taxon = "NCBITaxon:10116"
human_taxon = "NCBITaxon:9606"
iso_code = "0000266"
protein_coding_gene = "SO:0001217"
ortho_reference = "0000096"


def preprocess() -> None:
    """
    Preprocesses the annotations by converting them based on ortholog relationships.

    :returns: None
    """
    start = time.time()

    converted_mgi_annotations = []

    # assemble data structures needed to convert annotations via ortholog relationships.
    ortho_path, rgd_gaf_path, mgi_gpi_path = download_files()
    mouse_genes = GpiProcessor(mgi_gpi_path).genes
    rat_genes = OrthoProcessor(mouse_genes, ortho_path, mouse_taxon, rat_taxon).genes
    rgd_annotations = GafProcessor(rat_genes, rgd_gaf_path, namespaces=namespaces).convertible_annotations

    # just for performance of the check below for rat genes in the RGD GAF file that have
    # the appropriate ortholog relationship to a mouse gene in the MGI GPI file
    rat_gene_set = set(rat_genes.keys())
    converted_mgi_annotations.append(["!gpa-version: 2.0"])
    for annotation in rgd_annotations:
        if str(annotation.subject.id) in rat_gene_set:
            new_annotation = generate_annotation(annotation, rat_genes)  # generate the annotation based on orthology
            converted_mgi_annotations.append(new_annotation.to_gpad_2_0_tsv())

    # using pandas in order to take advantage of pystow in terms of file location and handling
    # again; pandas is a bit overkill.
    df = pd.DataFrame(converted_mgi_annotations)
    pystow.dump_df(key="MGI",
                   obj=df,
                   name="mgi.gpad.gz",
                   to_csv_kwargs={"index": False, "header": False, "compression": "gzip"},
                   sep="\t")
    pystow.dump_df(key="MGI",
                   obj=df,
                   name="mgi-test.gpad",
                   to_csv_kwargs={"index": False, "header": False},
                   sep="\t")

    end = time.time()

    print("time to execute", end - start)


def generate_annotation(annotation: GoAssociation, gene_map: dict) -> GoAssociation:
    """
    Generates a new annotation based on ortholog assignments.

    :param annotation: The original annotation.
    :param gene_map: A dictionary mapping rat gene IDs to mouse gene IDs.

    :returns: The new generated annotation.

    :raises KeyError: If the gene ID is not found in the gene map.
    """
    new_evidence_type = Curie(namespace='ECO', identity=iso_code)  # all annotations via ortho should have this ECO code
    new_subject = Subject(
        id=Curie(namespace='MGI', identity=gene_map[str(annotation.subject.id)]),
        type=[protein_coding_gene],
        taxon=Curie.from_str(mouse_taxon),
        fullname=[],
        label="",
        synonyms=[]
    )  # rewrite with MGI gene ID
    new_has_supporting_reference = Curie(namespace='GO_REF', identity=ortho_reference)
    annotation.evidence.has_supporting_reference = [new_has_supporting_reference]
    annotation.evidence.type = new_evidence_type
    annotation.subject = new_subject

    return annotation


if __name__ == '__main__':
    preprocess()
