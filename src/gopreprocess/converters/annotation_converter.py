from src.gopreprocess.processors.alliance_ortho_processor import OrthoProcessor
from src.gopreprocess.processors.gafprocessor import GafProcessor
from src.gopreprocess.processors.gpiprocessor import GpiProcessor
from src.gopreprocess.processors.xref_processor import XrefProcessor
from ontobio.model.association import Curie, ConjunctiveSet
from ontobio.model.association import map_gp_type_label_to_curie
from src.utils.download import download_files
from src.utils.decorators import timer
from ontobio.model.association import GoAssociation
import pandas as pd
import pystow
from typing import List
from src.utils.settings import taxon_to_provider, iso_eco_code


def dump_converted_annotations(converted_target_annotations: List[List[str]],
                               source_taxon: str,
                               target_taxon: str) -> None:
    # using pandas in order to take advantage of pystow in terms of file location and handling
    # again; pandas is a bit overkill.
    df = pd.DataFrame(converted_target_annotations)
    print(df.columns)
    print(df[1].head(10))
    df_unique = df.drop_duplicates()
    pystow.dump_df(key=taxon_to_provider[target_taxon],
                   obj=df_unique,
                   index=True,
                   name=taxon_to_provider[target_taxon].lower() + "-" + taxon_to_provider[source_taxon].lower() + "-ortho.gaf.gz",
                   to_csv_kwargs={"index": False, "header": False, "compression": "gzip"})
    pystow.dump_df(key=taxon_to_provider[target_taxon],
                   obj=df_unique,
                   index=True,
                   name=taxon_to_provider[target_taxon].lower() + "-" + taxon_to_provider[source_taxon].lower() + "-ortho-test.gaf",
                   to_csv_kwargs={"index": False, "header": False})


class AnnotationConverter:
    def __init__(self, namespaces: List[str],
                 target_taxon: str,
                 source_taxon: str,
                 ortho_reference: str):
        self.namespaces = namespaces
        self.target_taxon = target_taxon
        self.source_taxon = source_taxon
        self.iso_code = iso_eco_code[4:]  # we always want the ECO code for "inferred from sequence similarity"
        self.ortho_reference = ortho_reference.split(":")[1]

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
        ortho_path, source_gaf_path, target_gpi_path = download_files(self.source_taxon, self.target_taxon)
        target_genes = GpiProcessor(target_gpi_path).target_genes
        source_genes = OrthoProcessor(target_genes, ortho_path, self.target_taxon, self.source_taxon).genes
        xrefs = XrefProcessor()
        uniprot_to_hgnc_map = xrefs.uniprot_to_hgnc_map
        hgnc_to_uniprot_map = xrefs.hgnc_to_uniprot_map
        source_annotations = GafProcessor(source_genes,
                                          source_gaf_path,
                                          taxon_to_provider=taxon_to_provider,
                                          target_taxon=self.target_taxon,
                                          namespaces=self.namespaces,
                                          uniprot_to_hgnc_map=uniprot_to_hgnc_map).convertible_annotations

        source_gene_set = set(source_genes.keys())
        converted_target_annotations.append(["!gaf-version: 2.2"])

        for annotation in source_annotations:
            if str(annotation.subject.id) in source_gene_set:
                # generate the target annotation based on the source annotation
                new_annotation = self.generate_annotation(annotation=annotation,
                                                          source_genes=source_genes,
                                                          target_genes=target_genes,
                                                          hgnc_to_uniprot_map=hgnc_to_uniprot_map)
                converted_target_annotations.append(new_annotation.to_gaf_2_2_tsv())

        dump_converted_annotations(converted_target_annotations,
                                   source_taxon=self.source_taxon,
                                   target_taxon=self.target_taxon)

    def generate_annotation(self,
                            annotation: GoAssociation,
                            source_genes: dict,
                            target_genes: dict,
                            hgnc_to_uniprot_map: dict) -> GoAssociation:
        """
        Generates a new annotation based on ortholog assignments.

        :param annotation: The original annotation.
        :param source_genes: A dictionary mapping source gene IDs to target gene IDs.
        :param target_genes: A dict of dictionaries containing the target gene details.
        :param hgnc_to_uniprot_map: A dict mapping HGNC IDs to UniProtKB IDs.
        :returns: The new generated annotation.
        :raises KeyError: If the gene ID is not found in the gene map.
        """

        # make with_from include original source annotation identifier, if the
        # original annotation was to UniProtKB, then here it is likely the MOD or HGNC identifier.

        # source_genes 'HGNC:15042': 'MGI:3031248', annotation.subject.id 'HGNC:15042'
        # source_genes 'RGD:1309001': 'MGI:2443611', annotation.subject.id 'RGD:1309001'
        if str(annotation.subject.id) in source_genes.keys():
            if str(annotation.subject.id) in hgnc_to_uniprot_map.keys():
                uniprot_id = hgnc_to_uniprot_map[str(annotation.subject.id)]  # convert back to UniProtKB ID
                uniprot_curie = Curie(namespace=uniprot_id.split(":")[0], identity=uniprot_id.split(":")[1])
                annotation.evidence.with_support_from = [ConjunctiveSet(
                    elements=[uniprot_curie]
                )]
            else:
                annotation.evidence.with_support_from = [ConjunctiveSet(
                    elements=[str(annotation.subject.id)]
                )]
        annotation.evidence.has_supporting_reference = [Curie(namespace='GO_REF', identity=self.ortho_reference)]
        annotation.evidence.type = Curie(namespace='ECO', identity=iso_eco_code.split(":")[1])  # inferred from sequence similarity
        # not sure why this is necessary, but it is, else we get a Subject with an extra tuple wrapper
        annotation.subject.id = Curie(namespace='MGI', identity=source_genes[str(annotation.subject.id)])
        annotation.subject.taxon = Curie.from_str(self.target_taxon)
        annotation.subject.synonyms = []
        annotation.object.taxon = Curie.from_str(self.target_taxon)

        # have to convert these to curies in order for the conversion to GAF 2.2 type to return anything other than
        # default 'gene_product' -- in ontobio, when this is a list, we just take the first item.
        if annotation.provided_by == taxon_to_provider[self.source_taxon]:
            annotation.provided_by = taxon_to_provider[self.target_taxon]

        annotation.subject.fullname = target_genes[str(annotation.subject.id)]["fullname"]
        annotation.subject.label = target_genes[str(annotation.subject.id)]["label"]

        # have to convert these to curies in order for the conversion to GAF 2.2 type to return anything other than
        # default 'gene_product' -- in ontobio, when this is a list, we just take the first item.
        annotation.subject.type = [map_gp_type_label_to_curie(target_genes[str(annotation.subject.id)].get("type")[0])]

        return annotation
