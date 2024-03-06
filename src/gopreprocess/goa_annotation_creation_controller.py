"""Protein 2 GO AnnotationConverter class."""

import copy
import datetime
from typing import Any, Union

import pystow
from ontobio.model.association import Curie, GoAssociation

from src.gopreprocess.file_processors.gaf_processor import GafProcessor
from src.gopreprocess.file_processors.gpi_processor import GpiProcessor
from src.utils.decorators import timer
from src.utils.download import download_file, download_with_retry


def generate_annotation(
    annotation: GoAssociation, xrefs: dict, isoform: bool, protein_xrefs: dict, parent_xrefs: dict
) -> Union[GoAssociation, None]:
    """
    Generate a new annotation based on the given protein 2 GO annotation.

    :param annotation: The protein 2 GO annotation.
    :type annotation: GoAssociation
    :param xrefs: The xrefs dictionary from the parsed GPI file, mapping the gene of the target
    species to the set of UniProt ids for the source - in this case, the source is the protein 2 GO GAF file,
    so really we're still dealing with the source taxon.
    :type xrefs: dict
    :param isoform: Whether to process isoform annotations.
    :type isoform: bool
    :param protein_xrefs: The protein xrefs dictionary from the parsed GPI file, mapping the protein of the target
    species to the set of UniProt ids for the source
    :type protein_xrefs: dict
    :param parent_xrefs: The parent xrefs dictionary from the parsed GPI file, mapping the gene of the target
    species to the set of UniProt ids for the source PR:Q9DAQ4-1 = MGI:MGI:1918911
    :type parent_xrefs: dict

    :return: A new annotation.
    :rtype: GoAssociation
    """
    if str(annotation.subject.id) in protein_xrefs.keys():
        # PR:Q9DAQ4-1 = UniProtKB:Q9DAQ4-1
        if isoform:
            pr_id = protein_xrefs[str(annotation.subject.id)]
            # print("pr_id", pr_id)
            # print("parent_xrefs", parent_xrefs[pr_id])
            # print("annotation.subject.id", annotation.subject.id)
            # PR:Q9DAQ4-1 = MGI:MGI:1918911
            mgi_id = parent_xrefs[pr_id]
            new_gene = Curie(namespace=mgi_id.split(":")[0], identity=mgi_id.replace("MGI:MGI:", "MGI:"))

        else:
            new_gene = Curie(
                namespace=xrefs[str(annotation.subject.id)],
                identity=xrefs[str(annotation.subject.id)].replace("MGI:MGI:", "MGI:"),
            )
        new_annotation = copy.deepcopy(annotation)
        new_annotation.subject.id = new_gene
        new_annotation.subject.synonyms = []
        new_annotation.object.taxon = Curie.from_str("NCBITaxon:10090")
        print(datetime.datetime.now().strftime("%Y%m%d"))
        new_annotation.date = str(datetime.datetime.now().strftime("%Y%m%d"))

        # gp_isoforms: self.subject_extensions[0].term

        if new_annotation.subject_extensions and str(new_annotation.subject_extensions[0].term) in protein_xrefs.keys():
            new_annotation.subject_extensions[0].term = Curie(
                namespace=protein_xrefs[str(new_annotation.subject_extensions[0].term)].split(":")[0],
                identity=protein_xrefs[str(new_annotation.subject_extensions[0].term)].split(":")[1],
            )

        # retain provided_by from upstream
        # new_annotation.provided_by = annotation.provided_by

        return new_annotation
    else:
        return None


def get_source_annotations(
    isoform: bool, taxon: str
) -> tuple[dict, Any, Any, Any, Any] | tuple[dict, dict, Any, None, None]:
    """
    Get the source annotations from the protein 2 GO GAF file.

    :param isoform: Whether to process isoform annotations.
    :type isoform: bool
    :param taxon: The target taxon to which the annotations belong.
    :type taxon: str
    :return: A tuple containing the xrefs dictionary, the source annotations, and optionally the isoform
    source annotations.
    :rtype: tuple[dict, Any]
    """
    taxon = taxon.replace("NCBITaxon:", "taxon_")
    p2go_file = download_with_retry(target_directory_name=f"GOA_{taxon}", config_key=f"GOA_{taxon}", gunzip=True)

    target_gpi_path = download_file(target_directory_name="MGI_GPI", config_key="MGI_GPI", gunzip=True)

    gpi_processor = GpiProcessor(target_gpi_path)
    xrefs = gpi_processor.get_xrefs()

    # assign the output of processing the source GAF to a source_annotations variable
    gp = GafProcessor(filepath=p2go_file, source="GOA")
    source_annotations = gp.parse_p2g_gaf()

    if isoform:
        protein_xrefs, parent_xrefs = gpi_processor.get_protein_xrefs()
        p2go_isoform_file = download_file(
            target_directory_name=f"GOA_{taxon}_ISOFORM", config_key=f"GOA_{taxon}_ISOFORM", gunzip=True
        )
        gp_isoform = GafProcessor(filepath=p2go_isoform_file, source="GOA")
        source_isoform_annotations = gp_isoform.parse_p2g_gaf()
        return xrefs, protein_xrefs, source_annotations, source_isoform_annotations, parent_xrefs
    else:
        return xrefs, xrefs, source_annotations, None, None


def dump_annotations(annotations, isoform):
    """Dump annotations to a file."""
    file_suffix = "-isoform" if isoform else ""
    header_filepath = pystow.join(
        key="GAF_OUTPUT",
        name=f"mgi-p2g-converted{file_suffix}.gaf",
        ensure_exists=True,
    )
    with open(header_filepath, "w") as file:
        file.write("!gaf-version: 2.2\n")
        file.write("!Generated by: GO_Central preprocess pipeline: protein to GO transformation\n")
        file.write("!Date Generated: " + str(datetime.date.today()) + "\n")
        for annotation in annotations:
            file.write("\t".join(map(str, annotation)) + "\n")


class P2GAnnotationCreationController:

    """Converts annotations from one species to another based on ortholog relationships between the two species."""

    def __init__(self):
        """Initialize the AnnotationConverter class."""

    @timer
    def convert_annotations(self, isoform: bool, taxon: str) -> None:
        """
        Convert Protein to GO annotations from source to target taxon.

        :param isoform: Whether to process isoform annotations.
        :type isoform: bool
        :param taxon: The target taxon to which the annotations belong.
        :type taxon: str
        :returns: None
        """
        # Gather source annotations and cross-references
        xrefs, protein_xrefs, source_annotations, isoform_annotations, parent_xrefs = get_source_annotations(
            isoform=isoform, taxon=taxon
        )

        # Convert source annotations to target format
        converted_target_annotations = [
            annotation_obj.to_gaf_2_2_tsv()
            for annotation in source_annotations
            if (
                annotation_obj := generate_annotation(
                    annotation=annotation,
                    xrefs=xrefs,
                    isoform=isoform,
                    protein_xrefs=protein_xrefs,
                    parent_xrefs=parent_xrefs,
                )
            )
            is not None
        ]

        # Dump non-isoform annotations
        dump_annotations(converted_target_annotations, isoform=False)

        # Process isoform annotations if required
        if isoform:
            converted_target_isoform_annotations = [
                annotation_obj.to_gaf_2_2_tsv()
                for annotation in isoform_annotations
                if (
                    annotation_obj := generate_annotation(
                        annotation=annotation,
                        xrefs=protein_xrefs,
                        isoform=isoform,
                        protein_xrefs=protein_xrefs,
                        parent_xrefs=parent_xrefs,
                    )
                )
                is not None
            ]

            # Dump isoform annotations
            dump_annotations(converted_target_isoform_annotations, isoform=True)
