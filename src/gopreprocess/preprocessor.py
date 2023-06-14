from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gafprocessor import GafProcessor
from src.processors.gpiprocessor import GpiProcessor
from src.utils.download import download_files
from ontobio.model.association import GoAssociation, Curie, map_gp_type_label_to_curie
import time
import pandas as pd
import pystow
from typing import List, Dict

namespaces = ["RGD", "UniProtKB"]
mouse_taxon = "NCBITaxon:10090"
rat_taxon = "NCBITaxon:10116"
human_taxon = "NCBITaxon:9606"
iso_code = "0000266"
ortho_reference = "0000096"


def preprocess() -> None:
    """
    Preprocesses the annotations by converting them based on ortholog relationships.

    :returns: None
    """
    start = time.time()

    converted_mgi_annotations = []

    # assemble data structures needed to convert annotations via ortholog relationships.
    print("downloading files...")
    ortho_path, rgd_gaf_path, mgi_gpi_path = download_files()
    end = time.time()
    print("time to execute", end - start)

    print("target species gpi parsing...")
    target_genes = GpiProcessor(mgi_gpi_path).target_genes
    end = time.time()
    print("time to execute", end - start)

    print("orthology file parsing...")
    source_genes = OrthoProcessor(target_genes, ortho_path, mouse_taxon, rat_taxon).genes
    end = time.time()
    print("time to execute", end - start)

    print("source gaf file parsing...")
    rgd_annotations = GafProcessor(source_genes, rgd_gaf_path, namespaces=namespaces).convertible_annotations
    end = time.time()
    print("time to execute", end - start)

    # just for performance of the check below for rat genes in the RGD GAF file that have
    # the appropriate ortholog relationship to a mouse gene in the MGI GPI file
    source_gene_set = set(source_genes.keys())
    converted_mgi_annotations.append(["!gaf-version: 2.2"])

    print("converting annotations...")
    for annotation in rgd_annotations:
        if str(annotation.subject.id) in source_gene_set:
            new_annotation = generate_annotation(annotation, source_genes, target_genes)  # generate the annotation based on orthology
            converted_mgi_annotations.append(new_annotation.to_gaf_2_2_tsv())
    end = time.time()

    print("time to execute", end - start)
    # using pandas in order to take advantage of pystow in terms of file location and handling
    # again; pandas is a bit overkill.
    df = pd.DataFrame(converted_mgi_annotations)
    pystow.dump_df(key="MGI",
                   obj=df,
                   name="mgi-rgd-ortho.gaf.gz",
                   to_csv_kwargs={"index": False, "header": False, "compression": "gzip"},
                   sep="\t")
    pystow.dump_df(key="MGI",
                   obj=df,
                   name="mgi-rgd-ortho-test.gaf",
                   to_csv_kwargs={"index": False, "header": False},
                   sep="\t")

    end = time.time()

    print("time to execute", end - start)


def generate_annotation(annotation: GoAssociation, gene_map: dict, target_genes: dict) -> GoAssociation:
    """
    Generates a new annotation based on ortholog assignments.

    :param annotation: The original annotation.
    :param gene_map: A dictionary mapping source gene IDs to mouse gene IDs.
    :param target_genes: A dict of dictionaries containing the target gene details.
    :returns: The new generated annotation.

    :raises KeyError: If the gene ID is not found in the gene map.
    """

    # rewrite with MGI gene ID
    annotation.evidence.has_supporting_reference = [Curie(namespace='GO_REF', identity=ortho_reference)]
    annotation.evidence.type = Curie(namespace='ECO', identity=iso_code)  # all annotations via ortho should have this ECO code

    # not sure why this is necessary, but it is, else we get a Subject with an extra tuple wrapper
    annotation.subject.id = Curie(namespace='MGI', identity=gene_map[str(annotation.subject.id)])
    annotation.subject.taxon = Curie.from_str(mouse_taxon)
    annotation.subject.fullname = []
    annotation.subject.label = ""
    annotation.subject.synonyms = []
    annotation.object.taxon = Curie.from_str(mouse_taxon)

    # have to convert these to curies in order for the conversion to GAF 2.2 type to return anything other than
    # default 'gene_product' -- in ontobio, when this is a list, we just take the first item.
    print(map_gp_type_label_to_curie(target_genes[str(annotation.subject.id)]["type"][0]))
    annotation.subject.type = map_gp_type_label_to_curie(target_genes[str(annotation.subject.id)]["type"][0])
    if annotation.provided_by == "RGD":
        annotation.provided_by = "MGI"

    annotation.subject.fullname = target_genes[str(annotation.subject.id)]["fullname"]
    annotation.subject.label = target_genes[str(annotation.subject.id)]["label"]
    annotation.subject.type = target_genes[str(annotation.subject.id)].get("type")

    return annotation


if __name__ == '__main__':
    preprocess()
