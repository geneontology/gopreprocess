from src.processors.orthoprocessor import OrthoProcessor
from src.processors.gafprocessor import GafProcessor
from src.processors.gpiprocessor import GpiProcessor
from ontobio.model.association import Curie
from ontobio.model.association import map_gp_type_label_to_curie
from src.utils.download import download_files
from src.utils.decorators import timer
from ontobio.model.association import GoAssociation
import pandas as pd
import pystow
from typing import List


class AnnotationConverter:
    def __init__(self, namespaces: List[str],
                 target_taxon: str,
                 source_taxon: str,
                 iso_code: str,
                 ortho_reference: str):
        self.namespaces = namespaces
        self.target_taxon = target_taxon
        self.source_taxon = source_taxon
        self.iso_code = iso_code
        self.ortho_reference = ortho_reference

    @timer
    def convert_annotations(self) -> None:
        """
        Convert source species annotations to target species annotations based on ortholog relationships
        between the source and target species.

        :returns: None
        """
        converted_target_annotations = []

        # assemble data structures needed to convert annotations: including the ortholog map,
        # the target genes data structure, and the source genes data structure.
        ortho_path, source_gaf_path, target_gpi_path = download_files()
        target_genes = GpiProcessor(target_gpi_path).target_genes
        source_genes = OrthoProcessor(target_genes, ortho_path, self.target_taxon, self.source_taxon).genes
        source_annotations = GafProcessor(source_genes, source_gaf_path, namespaces=self.namespaces).convertible_annotations

        # just for performance of the check below for rat genes in the RGD GAF file that have
        # the appropriate ortholog relationship to a mouse gene in the MGI GPI file

        source_gene_set = set(source_genes.keys())
        converted_target_annotations.append(["!gaf-version: 2.2"])

        for annotation in source_annotations:
            if str(annotation.subject.id) in source_gene_set:
                new_annotation = self.generate_annotation(annotation, source_genes, target_genes)  # generate the annotation based on
                converted_target_annotations.append(new_annotation.to_gaf_2_2_tsv())

        # using pandas in order to take advantage of pystow in terms of file location and handling
        # again; pandas is a bit overkill.
        df = pd.DataFrame(converted_target_annotations)
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

    def generate_annotation(self, annotation: GoAssociation, gene_map: dict, target_genes: dict) -> GoAssociation:
        """
        Generates a new annotation based on ortholog assignments.

        :param annotation: The original annotation.
        :param gene_map: A dictionary mapping source gene IDs to mouse gene IDs.
        :param target_genes: A dict of dictionaries containing the target gene details.
        :returns: The new generated annotation.
        :raises KeyError: If the gene ID is not found in the gene map.
        """

        # rewrite with MGI gene ID
        annotation.evidence.has_supporting_reference = [Curie(namespace='GO_REF', identity=self.ortho_reference)]
        annotation.evidence.type = Curie(namespace='ECO', identity=self.iso_code)  # all annotations via ortho should have this ECO c

        # not sure why this is necessary, but it is, else we get a Subject with an extra tuple wrapper
        annotation.subject.id = Curie(namespace='MGI', identity=gene_map[str(annotation.subject.id)])
        annotation.subject.taxon = Curie.from_str(self.target_taxon)
        annotation.subject.synonyms = []
        annotation.object.taxon = Curie.from_str(self.target_taxon)

        # have to convert these to curies in order for the conversion to GAF 2.2 type to return anything other than
        # default 'gene_product' -- in ontobio, when this is a list, we just take the first item.
        if annotation.provided_by == "RGD":
            annotation.provided_by = "MGI"

        annotation.subject.fullname = target_genes[str(annotation.subject.id)]["fullname"]
        annotation.subject.label = target_genes[str(annotation.subject.id)]["label"]

        # have to convert these to curies in order for the conversion to GAF 2.2 type to return anything other than
        # default 'gene_product' -- in ontobio, when this is a list, we just take the first item.
        annotation.subject.type = [map_gp_type_label_to_curie(target_genes[str(annotation.subject.id)].get("type")[0])]

        return annotation
