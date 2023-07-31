import copy
import json
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


def convert_curie_to_string(x):
    if isinstance(x, Curie):  # Replace 'Curie' with the actual Curie class
        return str(x)
    return x


def dump_converted_annotations(converted_target_annotations: List[List[str]],
                               source_taxon: str,
                               target_taxon: str) -> None:
    # using pandas in order to take advantage of pystow in terms of file location and handling
    df = pd.DataFrame(converted_target_annotations)
    print("this is the original dataframe head")
    print(df.head(4))
    df = df.applymap(convert_curie_to_string)
    # Deduplicate the rows
    print("this is the df head")
    print(df.head(4))
    df_deduplicated = df.drop_duplicates()

    # Convert column 13 to numeric
    df_deduplicated.loc[:, 13] = pd.to_numeric(df_deduplicated[13], errors='coerce')

    # Replace negative values with 0
    df_deduplicated.loc[:, 13] = df_deduplicated[13].apply(lambda x: x if x >= 0 else 0)

    # Group by all other columns and get the min value in column 13
    df_final = df_deduplicated.groupby(df_deduplicated.columns.drop(13).tolist())[13].min().reset_index()

    # Swap columns 13 and 14 because the groupby operation above swaps them
    temp_col = df_final.iloc[:, 13].copy()
    df_final.iloc[:, 13] = df_final.iloc[:, 14]
    df_final.iloc[:, 14] = temp_col

    print(df_final.head(4))

    pystow.dump_df(key=taxon_to_provider[target_taxon],
                   obj=df_final,
                   sep="\t",
                   name=taxon_to_provider[target_taxon].lower() + "-" + taxon_to_provider[
                       source_taxon].lower() + "-ortho-temp.gaf",
                   to_csv_kwargs={"index": False, "header": False})

    # we need to add the #gaf-version: 2.2 header to the file
    filepath = pystow.join(key=taxon_to_provider[target_taxon],
                           name=taxon_to_provider[target_taxon].lower() + "-"
                           + taxon_to_provider[source_taxon].lower() + "-ortho-temp.gaf",
                           ensure_exists=True)

    # get the new file we have to create to add the header via pystow, so everything is managed together
    header_filepath = pystow.join(key=taxon_to_provider[target_taxon],
                                  name=taxon_to_provider[target_taxon].lower() + "-"
                                  + taxon_to_provider[source_taxon].lower() + "-ortho.gaf",
                                  ensure_exists=True)
    with open(filepath, 'r') as file:
        file_contents = file.readlines()

    # here's the final write to the final file
    with open(header_filepath, 'w') as header_filepath:
        header_filepath.write('!gaf-version: 2.2\n')
        header_filepath.writelines(file_contents)


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
        file_path = 'target_genes.json'

        # Open the file in write mode
        with open(file_path, 'w') as file:
            # Write the dictionary to the file using json.dump()
            json.dump(target_genes, file, indent=4)

        source_genes = OrthoProcessor(target_genes, ortho_path, self.target_taxon, self.source_taxon).genes
        file_path = 'source_genes.json'

        # Open the file in write mode
        with open(file_path, 'w') as file:
            # Write the dictionary to the file using json.dump()
            json.dump(source_genes, file, indent=4)

        xrefs = XrefProcessor()
        uniprot_to_hgnc_map = xrefs.uniprot_to_hgnc_map
        hgnc_to_uniprot_map = xrefs.hgnc_to_uniprot_map
        source_annotations = GafProcessor(source_gaf_path,
                                          taxon_to_provider=taxon_to_provider,
                                          target_taxon=self.target_taxon,
                                          namespaces=self.namespaces,
                                          uniprot_to_hgnc_map=uniprot_to_hgnc_map).convertible_annotations

        source_gene_set = set(source_genes.keys())

        for annotation in source_annotations:
            if str(annotation.subject.id) in source_gene_set:
                # generate the target annotation based on the source annotation
                new_annotations = self.generate_annotation(annotation=annotation,
                                                           source_genes=source_genes,
                                                           target_genes=target_genes,
                                                           hgnc_to_uniprot_map=hgnc_to_uniprot_map)
                for new_annotation in new_annotations:
                    converted_target_annotations.append(new_annotation.to_gaf_2_2_tsv())

        dump_converted_annotations(converted_target_annotations,
                                   source_taxon=self.source_taxon,
                                   target_taxon=self.target_taxon)

    def generate_annotation(self,
                            annotation: GoAssociation,
                            source_genes: dict,
                            target_genes: dict,
                            hgnc_to_uniprot_map: dict) -> List[GoAssociation]:
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
        annotations = []
        if str(annotation.subject.id) in source_genes.keys():
            for gene in source_genes[str(annotation.subject.id)]:
                new_annotation = copy.deepcopy(annotation)
                if str(annotation.subject.id) in hgnc_to_uniprot_map.keys():
                    uniprot_id = hgnc_to_uniprot_map[str(annotation.subject.id)]  # convert back to UniProtKB ID
                    uniprot_curie = Curie(namespace=uniprot_id.split(":")[0], identity=uniprot_id.split(":")[1])
                    new_annotation.evidence.with_support_from = [ConjunctiveSet(
                        elements=[uniprot_curie]
                    )]
                else:
                    new_annotation.evidence.with_support_from = [ConjunctiveSet(
                        elements=[str(annotation.subject.id)]
                    )]
                new_annotation.evidence.has_supporting_reference = [
                    Curie(namespace='GO_REF', identity=self.ortho_reference)]
                # inferred from sequence similarity
                new_annotation.evidence.type = Curie(namespace='ECO', identity=iso_eco_code.split(":")[1])
                # not sure why this is necessary, but it is, else we get a Subject with an extra tuple wrapper
                new_annotation.subject.id = Curie(namespace='MGI', identity=gene)
                new_annotation.subject.taxon = Curie.from_str(self.target_taxon)
                new_annotation.subject.synonyms = []
                new_annotation.object.taxon = Curie.from_str(self.target_taxon)
                new_annotation.object_extensions = []
                new_annotation.subject_extensions = []
                new_annotation.provided_by = taxon_to_provider[self.target_taxon]

                # TODO: replace MGI with target_namespace

                new_annotation.subject.fullname = target_genes[taxon_to_provider[self.target_taxon] + ":" + gene]["fullname"]
                new_annotation.subject.label = target_genes[taxon_to_provider[self.target_taxon] + ":" + gene]["label"]

                # have to convert these to curies in order for the conversion to
                # GAF 2.2 type to return anything other than
                # default 'gene_product' -- in ontobio, when this is a list, we just take the first item.
                new_annotation.subject.type = [map_gp_type_label_to_curie(target_genes[taxon_to_provider[self.target_taxon]
                                                                                       + ":" + gene].get("type")[0])]
                annotations.append(new_annotation)

        return annotations
