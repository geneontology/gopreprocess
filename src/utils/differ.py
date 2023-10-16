"""Diff tool for comparing files coming out of the pipeline with those going in."""
import csv
import datetime
from typing import List

import pandas as pd
from ontobio import ecomap
from ontobio.io import assocparser, gpadparser
from ontobio.model import collections
from ontobio.model.association import GoAssociation


def compare_files(file1, file2, output):
    """
    Method to compare two GPAD or GAF files and report differences.

    :param file1: Name of the source file to compare
    :type file1: str
    :param file2: Name of the target/second file to compare
    :type file2: str
    :param output: The prefix that will be appended to all the output files/reports created by this script.
    :type output: str
    :param group_by_columns: Name of the target/second file to compare
    :type group_by_columns: List

    """
    pd.set_option("display.max_rows", 50000)

    df_file1, df_file2, assocs1, assocs2 = get_parser(file1, file2)
    generate_count_report(df_file1, df_file2, file1, file2, output)
    compare_associations(assocs1, assocs2, output)


def generate_count_report(df_file1, df_file2, file1, file2, output):
    """
    Method to generate a report of the number of distinct values of each of the columns in a GAF or GPAD file.

    Currently restricted to the following columns: subject, qualifiers, object, evidence_code
    and reference.

    :param df_file1: data frame representing a normalized columnar representation of file1
    :type df_file1: pd
    :param df_file2: data frame representing a normalized columnar representation of file2
    :type df_file2: pd
    :param file1: The file name of the file provided in the click for reporting purposes.
    :type file1: str
    :param file2: The file name of the file provided in the click for reporting purposes.
    :type file2: str
    :param output: Prefix of the reported files for reporting purposes.
    :type output: str

    """
    _, counts_frame1 = get_column_count(df_file1, file1)
    _, counts_frame2 = get_column_count(df_file2, file2)

    merged_frame = pd.concat([counts_frame1, counts_frame2], axis=1)
    merged_frame.astype("Int64")
    merged_frame.to_csv(output + "_counts_per_column_report", sep="\t")
    s = "\n\n## COLUMN COUNT SUMMARY \n\n"
    s += "This report generated on {}\n\n".format(datetime.date.today())
    s += "  * Compared Files: " + file1 + ", " + file2 + "\n"
    s += "  * See Report File: " + output + "_counts_per_column_report" + "\n\n"
    print(s)
    print(merged_frame)


def compare_associations(assocs1, assocs2, output):
    """
    Method takes two lists of GoAssociation objects and compares them to each other, reporting the differences.

    Differences are based on three main criteria:
    1.  The subject, object, and evidence code act as a unit and must be the same between annotations
    or a difference is reported.

    :param assocs1: List of GoAssociation objects from the first file.
    :param assocs2: List of GoAssociation objects from the second file.
    :param output: Prefix of the reported files for reporting purposes.
    :type output: str

    """
    compare_report_file_path = output + "_compare_report"

    # Convert assocs2 into a set of tuples for faster lookup
    assoc1_list = []
    for go in assocs1:
        if type(go) is dict:
            continue
        new_tuple = (str(go.subject.id), str(go.object.id), str(go.evidence.type))
        assoc1_list.append(new_tuple)
    print(assoc1_list[0])

    assoc2_list = []

    for go2 in assocs2:
        if type(go2) is dict:
            continue
        new_tuple = (str(go2.subject.id), str(go2.object.id), str(go2.evidence.type))
        assoc2_list.append(new_tuple)
    print(len(assoc2_list))
    print(assoc2_list[0])

    assocs1_set = set(assoc1_list)
    assocs2_set = set(assoc2_list)

    common_elements, elements_unique_to_set1, elements_unique_to_set2 = compare_association_sets(
        assocs1_set, assocs2_set
    )
    common_file_path = output + "_common_elements.txt"
    unique_set1_file_path = output + "_" + "unique_to_set1.txt"
    unique_set2_file_path = output + "_" + "unique_to_set2.txt"

    write_set_to_file(common_file_path, common_elements)
    write_set_to_file(unique_set1_file_path, elements_unique_to_set1)
    write_set_to_file(unique_set2_file_path, elements_unique_to_set2)

    s = "\n\n## DIFF SUMMARY\n\n"
    s += "This report generated on {}\n\n".format(datetime.date.today())
    s += f"  * Total Common Associations: {len(common_elements)}\n"
    s += f"  * Total Elements Unique to File1: {len(elements_unique_to_set1)}\n"
    s += f"  * Total Elements Unique to File2: {len(elements_unique_to_set2)}\n"
    s += f"  * See report: {compare_report_file_path}\n"

    print(s)


def compare_association_sets(set1: set, set2: set):
    """
    Compare two sets of tuples and return the elements that are common and unique between them.

    :param set1: The first set of tuples.
    :type set1: set
    :param set2: The second set of tuples.
    :type set2: set
    :return: A tuple containing three sets: common elements, elements unique to set1, and elements unique to set2.
    :rtype: tuple
    """
    common_elements = set1.intersection(set2)
    elements_unique_to_set1 = set1.difference(set2)
    elements_unique_to_set2 = set2.difference(set1)

    return list(common_elements), list(elements_unique_to_set1), list(elements_unique_to_set2)


def write_set_to_file(file_path, data_set):
    """
    Write a set to a file.

    :param file_path: The path to the file to write.
    :type file_path: str
    :param data_set: The set to write to the file.
    :type data_set: set
    """
    with open(file_path, "w", newline="") as tsv_file:
        writer = csv.writer(tsv_file, delimiter="\t")
        for item in data_set:
            writer.writerow(item)


def markdown_report(report, processed_lines) -> (str, str):
    """
    Generate a markdown report from a report object.

    :param report: The report object to generate the markdown report from.
    :type report: Report
    :param processed_lines: The number of lines processed.
    :type processed_lines: int
    :return: A tuple containing the markdown report and the json report.
    :rtype: tuple
    """
    json = report.to_report_json()

    s = "\n\n## DIFF SUMMARY\n\n"
    s += "This report generated on {}\n\n".format(datetime.date.today())
    s += "  * Total Associations Compared: " + str(processed_lines) + "\n"

    for rule, messages in sorted(json["messages"].items(), key=lambda t: t[0]):
        s += "### {rule}\n\n".format(rule=rule)
        s += "* total missing annotations: {amount}\n".format(amount=len(messages))
        s += "\n"
        if len(messages) > 0:
            s += "#### Messages\n\n"
        for message in messages:
            obj = " ({})".format(message["obj"]) if message["obj"] else ""
            s += "* {level} - {type}: {message}{obj} -- `{line}`\n".format(
                level=message["level"], type=message["type"], message=message["message"], line=message["line"], obj=obj
            )

        return s, len(messages)


def get_typed_parser(file_handle, filename) -> [str, assocparser.AssocParser]:
    """
    Get the parser for a file based on the file header.

    :param file_handle: The file handle to read the file from.
    :type file_handle: file
    :param filename: The name of the file.
    :type filename: str
    :return: A tuple containing the dataframe and the parser.
    :rtype: tuple
    """
    parser = assocparser.AssocParser()

    for line in file_handle:
        if assocparser.AssocParser().is_header(line):
            returned_parser = collections.create_parser_from_header(line, assocparser.AssocParserConfig())
            if returned_parser is not None:
                parser = returned_parser
        else:
            continue
    if isinstance(parser, gpadparser.GpadParser):
        df_file = read_gpad_csv(filename, parser.version)
    else:
        df_file = read_gaf_csv(filename)

    return df_file, parser


def normalize_relation(relation: str) -> str:
    """
    Normalize a relation to a standard format.  For GAF this is a 3-letter code, for GPAD it is an ECO code.

    :param relation: The relation to normalize.
    :type relation: str
    :return: The normalized relation.
    :rtype: str
    """
    if ":" in str(relation):
        return str(relation)
    else:
        return romap.keys()[romap.values().index(str(relation))]


def get_parser(file1, file2) -> (str, str, List[GoAssociation], List[GoAssociation]):
    """
    Get the parser for a file based on the file header.

    :param file1: The first file to parse.
    :type file1: str
    :param file2: The second file to parse.
    :type file2: str
    :return: A tuple containing the dataframe and the parser.
    :rtype: tuple
    """
    file1_obj = assocparser.AssocParser()._ensure_file(file1)
    df_file1, parser1 = get_typed_parser(file1_obj, file1)
    file2_obj = assocparser.AssocParser()._ensure_file(file2)
    df_file2, parser2 = get_typed_parser(file2_obj, file2)

    assocs1 = parser1.parse(file1)
    assocs2 = parser2.parse(file2)
    print(assocs2[0])

    return df_file1, df_file2, assocs1, assocs2


def read_gaf_csv(filename) -> pd:
    """
    Read a GAF file into a dataframe.

    :param filename: The name of the file to read.
    :type filename: str
    :return: The dataframe containing the GAF data.
    :rtype: pd
    """
    ecomapping = ecomap.EcoMap()
    data_frame = pd.read_csv(
        filename,
        comment="!",
        header=None,
        na_filter=False,
        engine="python",
        delimiter="\t",
        index_col=False,
        names=[
            "DB",
            "DB_Object_ID",
            "DB_Object_Symbol",
            "Qualifier",
            "GO_ID",
            "DB_Reference",
            "Evidence_code",
            "With_or_From",
            "Aspect",
            "DB_Object_Name",
            "DB_Object_Synonym",
            "DB_Object_Type," "Taxon",
            "Date",
            "Assigned_By",
            "Annotation_Extension",
            "Gene_Product_Form_ID",
        ],
    ).fillna("")
    new_df = data_frame.filter(["DB_Object_ID", "Qualifier", "GO_ID", "Evidence_code", "DB_Reference"], axis=1)
    for eco_code in ecomapping.mappings():
        for ev in new_df["Evidence_code"]:
            if eco_code[2] == ev:
                new_df["Evidence_code"] = new_df["Evidence_code"].replace(
                    [eco_code[2]], ecomapping.ecoclass_to_coderef(eco_code[2])[0]
                )
    return new_df


def read_gpad_csv(filename, version) -> pd:
    """
    Read a GPAD file into a dataframe.

    :param filename: The name of the file to read.
    :type filename: str
    :param version: The version of the GPAD file.
    :type version: str
    :return: The dataframe containing the GPAD data.
    :rtype: pd

    """
    if version.startswith("1"):
        data_frame = pd.read_csv(
            filename, comment="!", header=None, na_filter=False, engine="python", delimiter="\t", names=gpad_1_2_format
        ).fillna("")
        df = data_frame.filter(
            ["db", "subject", "qualifiers", "relation", "object", "evidence_code", "reference"], axis=1
        )
        concat_column = df["db"] + ":" + df["subject"]
        df["concat_column"] = concat_column
        filtered_df = df.filter(["concat_column", "qualifiers", "relation", "object", "evidence_code", "reference"])
        filtered_df.rename(columns={"concat_column": "subject"}, inplace=True)
        new_df = filtered_df
    else:
        data_frame = pd.read_csv(
            filename, comment="!", sep="\t", header=None, na_filter=False, names=gpad_2_0_format
        ).fillna("")
        new_df = data_frame.filter(["subject", "negation", "relation", "object", "evidence_code", "reference"], axis=1)
    ecomapping = ecomap.EcoMap()
    for eco_code in ecomapping.mappings():
        for ev in new_df["evidence_code"]:
            if eco_code[2] == ev:
                new_df["evidence_code"] = new_df["evidence_code"].replace(
                    [eco_code[2]], ecomapping.ecoclass_to_coderef(eco_code[2])[0]
                )

    # normalize ids
    config = assocparser.AssocParserConfig()
    config.remove_double_prefixes = True
    parser = gpadparser.GpadParser(config=config)
    for i, r in enumerate(new_df["subject"]):
        r1 = parser._normalize_id(r)
        new_df.at[i, "subject"] = r1

    return new_df


def get_column_count(data_frame, file) -> (pd, pd):
    """
    Get the column count for a given dataframe.

    :param data_frame: The dataframe to get the column count for.
    :type data_frame: pd
    :param file: The name of the file.
    :type file: str
    :return: A tuple containing the stats and the count frame.
    :rtype: tuple
    """
    stats = {"filename": file, "total_rows": data_frame.shape[0]}
    count_frame = data_frame.nunique().to_frame(file)
    return stats, count_frame


romap = {
    "RO:0002327": "enables",
    "RO:0002326": "contributes_to",
    "RO:0002331": "involved_in",
    "RO:0002263": "acts_upstream_of",
    "RO:0004034": "acts_upstream_of_positive_effect",
    "RO:0004035": "acts_upstream_of_negative_effect",
    "RO:0002264": "acts_upstream_of_or_within",
    "RO:0004032": "acts_upstream_of_or_within_postitive_effect",
    "RO:0004033": "acts_upstream_of_or_within_negative_effect",
    "RO:0001025": "located_in",
    "BFO:0000050": "part_of",
    "RO:0002432": "is_active_in",
    "RO:0002325": "colocalizes_with",
}

gpad_1_2_format = [
    "db",
    "subject",
    "qualifiers",
    "object",
    "reference",
    "evidence_code",
    "with_or_from",
    "interacting_taxon",
    "date",
    "provided_by",
    "annotation_extensions",
    "properties",
]

gpad_2_0_format = [
    "subject",
    "negated",
    "relation",
    "object",
    "reference",
    "evidence_code",
    "with_or_from",
    "interacting_taxon",
    "date",
    "provided_by",
    "annotation_extensions",
    "properties",
]

gaf_format = [
    "DB",
    "DB_Object_ID",
    "DB_Object_Symbol",
    "Qualifier",
    "GO_ID",
    "DB_Reference",
    "Evidence_code",
    "With_or_From",
    "Aspect",
    "DB_Object_Name",
    "DB_Object_Synonym",
    "DB_Object_Type",
    "Taxon",
    "Date",
    "Assigned_By",
    "Annotation_Extension",
    "Gene_Product_Form_ID",
]
