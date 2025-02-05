"""
Module contains the AnnotationConverter class, which is responsible for converting annotations.

As input, this package takes a GAF from one species and generates a GAF for another species (using Alliance orthology
to map genes between species).
"""

import collections
import copy
import sys
from datetime import datetime
from typing import List

import click
import pandas as pd
import pystow
from ontobio.model.association import ConjunctiveSet, Curie, GoAssociation, map_gp_type_label_to_curie
from ontobio.util.go_utils import GoAspector

from gopreprocess.file_processors.ontology_processor import get_GO_aspector
from src.gopreprocess.file_processors.alliance_orthology_processor import OrthoProcessor
from src.gopreprocess.file_processors.gaf_processor import GafProcessor
from src.gopreprocess.file_processors.gpi_processor import GpiProcessor
from src.gopreprocess.file_processors.xref_processor import XrefProcessor
from src.utils.decorators import timer
from src.utils.download import concatenate_gafs, download_file, download_files
from src.utils.settings import iso_eco_code, taxon_to_provider


def convert_curie_to_string(x):
    """Converts a Curie object to a string."""
    if isinstance(x, Curie):  # Replace 'Curie' with the actual Curie class
        return str(x)
    return x


def dump_converted_annotations(converted_target_annotations: List[List[str]], source_taxon: str, target_taxon: str) -> None:
    """
    Dumps the converted annotations to a TSV file.

    :param converted_target_annotations: The converted annotations.
    :type converted_target_annotations: List[List[str]]
    :param source_taxon: The source taxon ID.
    :type source_taxon: str
    :param target_taxon: The target taxon ID.
    :type target_taxon: str

    """
    # using pandas in order to take advantage of pystow in terms of file location and handling
    df = pd.DataFrame(converted_target_annotations)
    df = df.applymap(convert_curie_to_string)
    # Deduplicate the rows
    df_deduplicated = df.drop_duplicates()

    # Convert column 13 to numeric
    df_deduplicated.loc[:, 13] = pd.to_numeric(df_deduplicated[13], errors="coerce")

    # Replace negative values with 0
    df_deduplicated.loc[:, 13] = df_deduplicated[13].apply(lambda x: x if x >= 0 else 0)

    # Group by all other columns and get the min value in column 13
    df_final = df_deduplicated.groupby(df_deduplicated.columns.drop(13).tolist())[13].min().reset_index()

    df_final.columns = [
        "subject.id.namespace",
        "subject.id.identity",
        "subject.label",
        "qualifier",
        "object.id",
        "evidence.has_supporting_reference",
        "evidence.type",
        "evidence.with_support_from",
        "aspect",
        "subject.fullname",
        "subject.synonyms",
        "subject.type",
        "taxon",
        "provided_by",
        "object_extensions",
        "gp_isoforms",
        "date",
    ]

    desired_column_order = [
        "subject.id.namespace",
        "subject.id.identity",
        "subject.label",
        "qualifier",
        "object.id",
        "evidence.has_supporting_reference",
        "evidence.type",
        "evidence.with_support_from",
        "aspect",
        "subject.fullname",
        "subject.synonyms",
        "subject.type",
        "taxon",
        "date",
        "provided_by",
        "object_extensions",
        "gp_isoforms",
    ]

    # Swap columns 13 and 14 because the groupby operation above swaps them
    df_final = df_final.reindex(columns=desired_column_order)

    pystow.dump_df(
        key=taxon_to_provider[target_taxon],
        obj=df_final,
        sep="\t",
        name=taxon_to_provider[target_taxon].lower() + "-" + taxon_to_provider[source_taxon].lower() + "-ortho-temp.gaf",
        to_csv_kwargs={"index": False, "header": False},
    )

    # we need to add the #gaf-version: 2.2 header to the file
    filepath = pystow.join(
        key=taxon_to_provider[target_taxon],
        name=taxon_to_provider[target_taxon].lower() + "-" + taxon_to_provider[source_taxon].lower() + "-ortho-temp.gaf",
        ensure_exists=True,
    )

    # get the new file we have to create to add the header via pystow, so everything is managed together
    header_filepath = pystow.join(
        key="GAF_OUTPUT",
        name=taxon_to_provider[target_taxon].lower() + "-" + taxon_to_provider[source_taxon].lower() + "-ortho.gaf",
        ensure_exists=True,
    )
    with open(filepath, "r") as file:
        file_contents = file.readlines()

    # here's the final write to the final file
    with open(header_filepath, "w") as header_filepath:
        header_filepath.write("!gaf-version: 2.2\n")
        header_filepath.write("!Generated by: GO_Central preprocess pipeline\n")
        header_filepath.write("!Date Generated: " + str(datetime.now()) + "\n")
        header_filepath.writelines(file_contents)


class AnnotationCreationController:

    """
    Converts annotations from one species to another based on ortholog relationships between the two species.

    :param namespaces: The namespaces to convert.
    :type namespaces: List[str]
    :param target_taxon: The target taxon ID.
    :type target_taxon: str
    :param source_taxon: The source taxon ID.
    :type source_taxon: str
    :param ortho_reference: The ortholog reference.
    :type ortho_reference: str

    """

    def __init__(self, namespaces: List[str], target_taxon: str, source_taxon: str, ortho_reference: str):
        """Initialize the AnnotationConverter class."""
        self.namespaces = namespaces
        self.target_taxon = target_taxon
        self.source_taxon = source_taxon
        self.iso_code = iso_eco_code[4:]  # we always want the ECO code for "inferred from sequence similarity"
        self.ortho_reference = ortho_reference.split(":")[1]

    @timer
    def convert_annotations(self) -> None:
        """
        Convert source species annotations to target species annotations based on ortholog relationships.

        :returns: None
        """
        converted_target_annotations = []

        # assemble data structures needed to convert annotations: including the ortholog map,
        # the target genes data structure, and the source genes data structure.
        ortho_path, source_gaf_path, target_gpi_path = download_files(self.source_taxon, self.target_taxon)
        if self.source_taxon == "NCBITaxon:9606":
            human_iso_filepath = download_file(target_directory_name="HUMAN_ISO", config_key="HUMAN_ISO", gunzip=True)
            concatenate_gafs(file1=source_gaf_path, file2=human_iso_filepath, output_file=source_gaf_path)

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

        source_genes = OrthoProcessor(target_genes, ortho_path, self.target_taxon, self.source_taxon).genes

        transformed = {}
        for key, values in source_genes.items():
            for value in values:
                if value not in transformed:
                    transformed[value] = []
                transformed[value].append(key)

        # transformed genes example:
        # "MGI:1334433": [
        #     "HGNC:8984","HGNC:8985"
        # ]

        xrefs = XrefProcessor()
        uniprot_to_hgnc_map = xrefs.uniprot_to_hgnc_map
        hgnc_to_uniprot_map = xrefs.hgnc_to_uniprot_map

        # assign the output of processing the source GAF to a source_annotations variable
        gp = GafProcessor(
            source_gaf_path,
            taxon_to_provider=taxon_to_provider,
            target_taxon=self.target_taxon,
            namespaces=self.namespaces,
            uniprot_to_hgnc_map=uniprot_to_hgnc_map,
            source=None,
        )

        source_annotations = gp.parse_ortho_gaf()

        source_gene_set = set(source_genes.keys())

        # this needs to be changed to a non-hardcoded value, what we want here is the config key for the URL that we
        # need in order to download and store the gene ontology JSON file used to create the closure in the
        # GoAspector object.
        go_aspector = get_GO_aspector("GO")
        for annotation in source_annotations:
            click.echo(annotation)
            if str(annotation.subject.id) in source_gene_set:
                # generate the target annotation based on the source annotation
                new_annotations = self.generate_annotation(
                    annotation=annotation,
                    source_genes=source_genes,
                    target_genes=target_genes,
                    hgnc_to_uniprot_map=hgnc_to_uniprot_map,
                    go_aspector=go_aspector,
                    transformed_source_genes=transformed,
                )
                for new_annotation in new_annotations:
                    click.echo(new_annotation.to_gaf_2_2_tsv())
                    converted_target_annotations.append(new_annotation.to_gaf_2_2_tsv())

        if converted_target_annotations:
            dump_converted_annotations(converted_target_annotations, source_taxon=self.source_taxon, target_taxon=self.target_taxon)
        else:
            print("FAIL!: no annotations to dump!")
            click.echo("No annotations were converted.")
            sys.exit(1)  # Exit with a non-zero status to indicate failure

    def generate_annotation(
        self,
        annotation: GoAssociation,
        source_genes: dict,
        target_genes: dict,
        hgnc_to_uniprot_map: dict,
        go_aspector: GoAspector,
        transformed_source_genes: dict,
    ) -> List[GoAssociation]:
        """
        Generates a new annotation based on ortholog assignments.

        :param annotation: The original annotation.
        :param source_genes: A dictionary with key being the source gene IDs, HGNC or RGD id to target gene IDs (there
        may be more than one target gene, MGI gene, that is mapped via orthology to the HGNC id or RGD ID), so value
        of this dictionary is a list of strings: a list of MGI, aka "target", CURIEs.
        :param target_genes: A dict of dictionaries containing the target gene details.
        :param hgnc_to_uniprot_map: A dict mapping HGNC IDs to UniProtKB IDs.
        :param go_aspector: A GoAspector object that holds the closure for Object Terms.
        :param transformed_source_genes: A dict of lists containing the target gene details.
        :returns: The new generated annotation.
        :raises KeyError: If the gene ID is not found in the gene map.
        """
        # make with_from include original source annotation identifier, if the
        # original annotation was to UniProtKB, then here it is likely the MOD or HGNC identifier.

        annotation_skipped = []
        annotations = []

        # this is used to measure how many orthologs a gene has, if it has more than one and the annotation
        # is to any subclass_of "Biological Process" then we skip it

        if str(annotation.subject.id) in source_genes.keys():
            for gene in source_genes[str(annotation.subject.id)]:
                if gene in transformed_source_genes and len(transformed_source_genes[gene]) > 1 and go_aspector.is_biological_process(str(annotation.object.id)):
                    output = (
                        "NON_1TO1_BP"
                        + str(annotation.subject.id)
                        + " "
                        + str(annotation.relation)
                        + " "
                        + str(annotation.object.id)
                        + " "
                        + str(annotation.evidence.type)
                        + " "
                        + str(annotation.evidence.has_supporting_reference)
                    )
                    # print("greater than 1 BP")
                    annotation_skipped.append(output)
                else:
                    new_annotation = copy.deepcopy(annotation)
                    if str(annotation.subject.id) in hgnc_to_uniprot_map.keys():
                        # print("HGNC to UniProt map", str(annotation.subject.id))
                        uniprot_id = hgnc_to_uniprot_map[str(annotation.subject.id)]  # convert back to UniProtKB ID
                        uniprot_curie = Curie(namespace=uniprot_id.split(":")[0], identity=uniprot_id.split(":")[1])
                        new_annotation.evidence.with_support_from = [ConjunctiveSet(elements=[uniprot_curie])]
                    else:
                        new_annotation.evidence.with_support_from = [ConjunctiveSet(elements=[str(annotation.subject.id)])]
                        # print("no HGNC to UniProt map", str(annotation.subject.id))
                    new_annotation.evidence.has_supporting_reference = [Curie(namespace="GO_REF", identity=self.ortho_reference)]
                    # if there is only one human ortholog of the mouse gene and the annotation is not a biological
                    # process, then we add it, else we skip it. inferred from sequence similarity
                    new_annotation.evidence.type = Curie(namespace="ECO", identity=iso_eco_code.split(":")[1])
                    # not sure why this is necessary, but it is, else we get a Subject with an extra tuple wrapper
                    new_annotation.subject.id = Curie(namespace="MGI", identity=gene)
                    new_annotation.subject.taxon = Curie.from_str(self.target_taxon)
                    new_annotation.subject.synonyms = []
                    new_annotation.object.taxon = Curie.from_str(self.target_taxon)
                    new_annotation.object_extensions = []
                    new_annotation.subject_extensions = []
                    new_annotation.provided_by = "GO_Central"

                    Date = collections.namedtuple("Date", ["year", "month", "day", "time"])

                    # Format the date as YYYYMMDD, which is suitable for GAF date requirements
                    gaf_date = datetime.now().strftime("%Y%m%d")

                    # Extract year, month, and day components from the YYYYMMDD string
                    year = gaf_date[:4]
                    month = gaf_date[4:6]
                    day = gaf_date[6:8]

                    # Create a Date object, time is set to an empty string.
                    date_object = Date(year=year, month=month, day=day, time="")
                    new_annotation.date = date_object

                    new_annotation.subject.fullname = target_genes[taxon_to_provider[self.target_taxon] + ":" + gene]["fullname"]
                    new_annotation.subject.label = target_genes[taxon_to_provider[self.target_taxon] + ":" + gene]["label"]

                    # have to convert these to curies in order for the conversion to
                    # GAF 2.2 type to return anything other than
                    # default 'gene_product' -- in ontobio, when this is a list, we just take the first item.
                    new_annotation.subject.type = [map_gp_type_label_to_curie(target_genes[taxon_to_provider[self.target_taxon] + ":" + gene].get("type")[0])]
                    annotations.append(new_annotation)

        return annotations
