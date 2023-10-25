"""
This module contains the Protein 2 GO AnnotationConverter class.
"""
from src.gopreprocess.file_processors.gafprocessor import GafProcessor
from src.utils.decorators import timer
from src.utils.download import concatenate_gafs, download_file, download_files
from src.gopreprocess.file_processors.gpiprocessor import GpiProcessor
from ontobio.model.association import Curie, GoAssociation
import copy


class P2GAnnotationCreationController:

    """
    Converts annotations from one species to another based on ortholog relationships between the two species.

    """

    def __init__(self):
        """
        Initialize the AnnotationConverter class.

        """

    @timer
    def generate_annotation(
        self,
        annotation: GoAssociation,
        xrefs: dict
    ) -> GoAssociation:
        """
        Generate a new annotation based on the given protein 2 GO annotation.

        :param annotation: The protein 2 GO annotation.
        :type annotation: GoAssociation
        :param xrefs: The xrefs dictionary from the parsed GPI file, mapping the gene of the target
        species to the set of UniProt ids for the source - in this case, the source is the protein 2 GO GAF file,
        so really we're still dealing with the source taxon.

        :return: A new annotation.
        :rtype: GoAssociation
        """

        for key, values in xrefs.items():
            if "UniProtKB:"+str(annotation.subject.id) in values:
                if len(values) > 1:
                    continue
                else:
                    new_gene = Curie(namespace="MGI", identity=key)
                    new_annotation = copy.deepcopy(annotation)
                    # not sure why this is necessary, but it is, else we get a Subject with an extra tuple wrapper
                    new_annotation.subject.id = new_gene
                    new_annotation.subject.synonyms = []
                    new_annotation.object.taxon = Curie.from_str("NCBITaxon:10090")
                    new_annotation.object_extensions = []
                    new_annotation.subject_extensions = []
                    new_annotation.provided_by = "GO_Central"
            else:
                continue
        return annotation



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

        gpi_processor = GpiProcessor(target_gpi_path)
        xrefs = gpi_processor.get_xrefs()

        # source genes example:
        # "HGNC:8984": [
        #     "MGI:1334433"
        # ]

        # assign the output of processing the source GAF to a source_annotations variable
        gp = GafProcessor()
        source_annotations = gp.parse_p2g_gaf()

        for annotation in source_annotations:
            new_annotation = self.generate_annotation(
                    annotation=annotation,
                    xrefs=xrefs
            )
            converted_target_annotations.append(new_annotation.to_gaf_2_2_tsv())

        dump_converted_annotations(
            converted_target_annotations, source_taxon=self.source_taxon, target_taxon=self.target_taxon
        )
