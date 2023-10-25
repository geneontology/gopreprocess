from typing import List
from gopreprocess.file_processors.ontology_processor import get_GO_aspector
from src.gopreprocess.file_processors.alliance_ortho_processor import OrthoProcessor
from src.gopreprocess.file_processors.gafprocessor import GafProcessor
from src.gopreprocess.file_processors.gpiprocessor import GpiProcessor
from src.gopreprocess.file_processors.xref_processor import XrefProcessor
from src.utils.decorators import timer
from src.utils.download import concatenate_gafs, download_file, download_files
from src.utils.settings import taxon_to_provider


class P2GAnnotationCreationController:

    """
    Converts annotations from one species to another based on ortholog relationships between the two species.

    """

    def __init__(self):
        """
        Initialize the AnnotationConverter class.

        """

    @timer
    def convert_annotations(self) -> None:
        """
        Convert Protein to GO annotations from source to target taxon.

        :returns: None
        """
        converted_target_annotations = []

        # assemble data structures needed to convert annotations: including the ortholog map,
        # the target genes data structure, and the source genes data structure.

        p2go_file = download_file(target_directory_name="GOA_MOUSE", config_key="GOA_MOUSE", gunzip=True)
        target_gpi_path = download_files(target_directory_name="MGI_GPI", config_key="MGI_GPI")

        # target genes example:
        # "MGI:MGI:1915609": {
        #     "id": "MGI:MGI:1915609",
        #     "fullname": [
        #         "RIKEN cDNA 0610010K14 gene"
        #     ],
        #     "label": "0610010K14Rik",
        #     "type": [
        #         "protein_coding_gene"
        #     ]
        # }

        target_genes = GpiProcessor(target_gpi_path).target_genes

        # source genes example:
        # "HGNC:8984": [
        #     "MGI:1334433"
        # ]

        # assign the output of processing the source GAF to a source_annotations variable
        gp = GafProcessor()
        source_annotations = gp.parse_p2g_gaf()

        for annotation in source_annotations:
            new_annotations = self.generate_annotation(
                    annotation=annotation,
                    source_genes=source_genes,
                    target_genes=target_genes,
                    hgnc_to_uniprot_map=hgnc_to_uniprot_map,
                    go_aspector=go_aspector,
                    transformed_source_genes=transformed,
            )
            for new_annotation in new_annotations:
                converted_target_annotations.append(new_annotation.to_gaf_2_2_tsv())

        dump_converted_annotations(
            converted_target_annotations, source_taxon=self.source_taxon, target_taxon=self.target_taxon
        )
