from ontobio.io import assocparser, gpadparser
from ontobio import ecomap
import pandas as pd
import datetime
from ontobio.io import qc
from ontobio.io.assocparser import Report
from ontobio.model.association import GoAssociation
from ontobio.model import collections
from typing import List


def compare_files(file1, file2, output, group_by_columns, restrict_to_decreases):
    """

    Method to compare two GPAD or GAF files and report differences on a file level and via converting
    file-based rows to GoAssociation objects.

    :param file1: Name of the source file to compare
    :type file1: str
    :param file2: Name of the target/second file to compare
    :type file2: str
    :param output: The prefix that will be appended to all the output files/reports created by this script.
    :type output: str
    :param group_by_columns: Name of the target/second file to compare
    :type group_by_columns: List
    :param restrict_to_decreases: An optional boolean flag that allows the grouping column counts to be returned only
        if they show a decrease in number beteween file1 and file2
    :type restrict_to_decreases: bool

    """
    pd.set_option('display.max_rows', 35000)

    df_file1, df_file2, assocs1, assocs2 = get_parser(file1, file2)
    generate_count_report(df_file1, df_file2, file1, file2, output)
    compare_associations(assocs1, assocs2, output, file1, file2)
    generate_group_report(df_file1, df_file2, group_by_columns, file1, file2, restrict_to_decreases, output)


def generate_count_report(df_file1, df_file2, file1, file2, output):
    """

    Method to generate a report of the number of distinct values of each of the columns
    in a GAF or GPAD file.  Currently restricted to the following columns: subject, qualifiers, object, evidence_code
    and reference.

    Uses pandas internal functions like merge and nunique to count and display metrics.

    :param df_file1: data frame representing a normalized columnar represenation of file1
    :type df_file1: pd
    :param df_file2: data frame representing a normalized columnar represenation of file2
    :type df_file2: pd
    :param file1: The file name of the file provided in the click for reporting purposes.
    :type file1: str
    :param file2: The file name of the file provided in the click for reporting purposes.
    :type file2: str
    :param output: Prefix of the reported files for reporting purposes.
    :type output: str

    """

    file1_groups, counts_frame1 = get_column_count(df_file1, file1)
    file2_groups, counts_frame2 = get_column_count(df_file2, file2)

    merged_frame = pd.concat([counts_frame1, counts_frame2], axis=1)
    print(merged_frame.head(10))
    merged_frame.astype('Int64')
    merged_frame.to_csv(output + "_counts_per_column_report", sep='\t')
    s = "\n\n## COLUMN COUNT SUMMARY \n\n"
    s += "This report generated on {}\n\n".format(datetime.date.today())
    s += "  * Compared Files: " + file1 + ", " + file2 + "\n"
    s += "  * See Report File: " + output + "_counts_per_column_report" + "\n\n"
    print(s)
    print(merged_frame)


def generate_group_report(df_file1, df_file2, group_by_columns, file1, file2, restrict_to_decreases, output):
    """

    Method to generate a report of the number of distinct values of each of the provided group_by columns
    in a GAF or GPAD file.  Currently restricted to the following columns: subject, object, evidence_code.

    :param df_file1: data frame representing a normalized columnar represenation of file1
    :type df_file1: pd
    :param df_file2: data frame representing a normalized columnar represenation of file2
    :type df_file2: pd
    :param group_by_columns: the columns to group by
    :type group_by_columns: List[str]
    :param file1: The file name of the file provided in the click for reporting purposes.
    :type file1: str
    :param file2: The file name of the file provided in the click for reporting purposes.
    :type file2: str
    :param restrict_to_decreases: An optional boolean flag that allows the grouping column counts to be returned only
        if they show a decrease in number beteween file1 and file2
    :type restrict_to_decreases: bool
    :param output: Prefix of the reported files for reporting purposes.
    :type output: str

    """

    if len(group_by_columns) > 0:
        s = "\n\n## GROUP BY SUMMARY \n\n"
        s += "This report generated on {}\n\n".format(datetime.date.today())
        s += "  * Group By Columns: " + str(group_by_columns) + "\n"
        s += "  * Compared Files: " + file1 + ", " + file2 + "\n"

        _, grouped_frame1 = get_group_by(df_file1, group_by_columns, file1)
        _, grouped_frame2 = get_group_by(df_file2, group_by_columns, file2)
        # rename the second count so the merge removes duplicate columns but not the counts.
        grouped_frame2 = grouped_frame2.rename(columns={'count': 'count2'})

        # bring the two data frames together
        merged_group_frame = pd.concat([grouped_frame1, grouped_frame2], axis=1)

        # remove nulls
        merged_group_frame_no_nulls = merged_group_frame.fillna(0)

        # Drop duplicate columns (excluding count columns)
        count_df = merged_group_frame_no_nulls.loc[:, ~merged_group_frame_no_nulls.columns.duplicated()]
        print(count_df.head(10))

        if restrict_to_decreases:
            filtered_df = merged_group_frame_no_nulls[merged_group_frame_no_nulls['count2'] < merged_group_frame_no_nulls['count']]
        else:
            filtered_df = merged_group_frame_no_nulls[
                merged_group_frame_no_nulls['count2'] != merged_group_frame_no_nulls['count']]

        s += "  * Number of unqiue " + str(group_by_columns) + "s that show differences: " + str(len(filtered_df.index)) + "\n"
        s += "  * See output file " + output + "_" + str(group_by_columns) + "_counts_per_column_report" + "\n"
        print(filtered_df.head(10))
        filtered_df.to_csv(output + "_" + str(group_by_columns) + "_counts_per_column_report", sep='\t')
        print(s)
        print("\n\n")


def compare_associations(assocs1, assocs2, output, file1, file2):
    """

    Method to compare files by turning them into collections of GoAssociation objects and comparing the
    content of the GoAssociations for matches between collections.

    :param assocs1: List of GoAssociations to compare from file1
    :type assocs1: List[GoAssociation]
    :param assocs2: List of GoAssociations to compare from file2
    :type assocs2: List[GoAssociation]
    :param file1: The file name of the file provided in the click for reporting purposes.
    :type file1: str
    :param file2: The file name of the file provided in the click for reporting purposes.
    :type file2: str
    :param output: Prefix of the reported files for reporting purposes.
    :type output: str

    """

    compare_report_file = open(output + "_compare_report", "w")
    processed_associations = len(assocs1)

    report = Report()

    set1 = set((str(x.subject.id),
                str(x.object.id),
                normalize_relation(x.relation),
                x.negated,
                x.evidence.type,
                x.evidence._supporting_reference_to_str(),
                x.evidence._with_support_from_to_str()
                ) for x in assocs2 if type(x) != dict)
    difference = [y for y in assocs1 if type(y) != dict
                  if (str(y.subject.id),
                      str(y.object.id),
                      normalize_relation(y.relation),
                      y.negated,
                      y.evidence.type,
                      y.evidence._supporting_reference_to_str(),
                      y.evidence._with_support_from_to_str()
                      ) not in set1]

    for diff in difference:
        report.add_association(diff)
        report.n_lines = report.n_lines + 1
        report.error(diff.source_line, qc.ResultType.ERROR, "line from %s has NO match in %s" % (file1, file2), "")

    md_report, number_of_messages = markdown_report(report, processed_associations)
    s = "\n\n## DIFF SUMMARY\n\n"
    s += "This report generated on {}\n\n".format(datetime.date.today())
    s += "  * Total Unmatched Associations: {}\n".format(number_of_messages)
    s += "  * Total Associations Compared: " + str(len(assocs1)) + "\n"
    s += "  * See report: " + output + "_compare_report" + "\n"

    print(s)
    compare_report_file.write(md_report)
    compare_report_file.close()


def markdown_report(report, processed_lines) -> (str, str):
    json = report.to_report_json()

    s = "\n\n## DIFF SUMMARY\n\n"
    s += "This report generated on {}\n\n".format(datetime.date.today())
    s += "  * Total Associations Compared: " + str(processed_lines) + "\n"

    for (rule, messages) in sorted(json["messages"].items(), key=lambda t: t[0]):
        s += "### {rule}\n\n".format(rule=rule)
        s += "* total missing annotations: {amount}\n".format(amount=len(messages))
        s += "\n"
        if len(messages) > 0:
            s += "#### Messages\n\n"
        for message in messages:
            obj = " ({})".format(message["obj"]) if message["obj"] else ""
            s += "* {level} - {type}: {message}{obj} -- `{line}`\n".format(level=message["level"],
                                                                           type=message["type"],
                                                                           message=message["message"],
                                                                           line=message["line"],
                                                                           obj=obj)

        return s, len(messages)


def get_typed_parser(file_handle, filename) -> [str, assocparser.AssocParser]:
    parser = assocparser.AssocParser()

    for line in file_handle:
        if assocparser.AssocParser().is_header(line):
            returned_parser = collections.create_parser_from_header(line, assocparser.AssocParserConfig())
            if returned_parser is not None:
                parser = returned_parser
        else:
            continue
    if isinstance(parser, gpadparser.GpadParser):
        print("Using GPAD parser")
        df_file = read_gpad_csv(filename, parser.version)
    else:
        print("Using GAF parser")
        df_file = read_gaf_csv(filename, parser.version)

    return df_file, parser


def normalize_relation(relation: str) -> str:
    if ":" in str(relation):
        return str(relation)
    else:
        return romap.keys()[romap.values().index(str(relation))]


def get_parser(file1, file2) -> (str, str, List[GoAssociation], List[GoAssociation]):
    file1_obj = assocparser.AssocParser()._ensure_file(file1)
    df_file1, parser1 = get_typed_parser(file1_obj, file1)
    file2_obj = assocparser.AssocParser()._ensure_file(file2)
    df_file2, parser2 = get_typed_parser(file2_obj, file2)

    assocs1 = parser1.parse(file1)
    print(len(assocs1), " associations in ", file1, " using ", type(parser1))
    assocs2 = parser2.parse(file2)
    print(len(assocs2), " associations in ", file2, " using ", type(parser2))

    return df_file1, df_file2, assocs1, assocs2


def read_gaf_csv(filename, version) -> pd:
    ecomapping = ecomap.EcoMap()
    data_frame = pd.read_csv(filename,
                             comment="!",
                             header=None,
                             na_filter=False,
                             engine='python',
                             delimiter="\t",
                             index_col=False,
                             names=["DB",
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
                                    "DB_Object_Type,"
                                    "Taxon",
                                    "Date",
                                    "Assigned_By",
                                    "Annotation_Extension",
                                    "Gene_Product_Form_ID"]).fillna("")
    new_df = data_frame.filter(['DB_Object_ID', 'Qualifier', 'GO_ID', 'Evidence_code', 'DB_Reference'], axis=1)
    for eco_code in ecomapping.mappings():
        for ev in new_df['Evidence_code']:
            if eco_code[2] == ev:
                new_df['Evidence_code'] = new_df['Evidence_code'].replace([eco_code[2]],
                                                                          ecomapping.ecoclass_to_coderef(
                                                                              eco_code[2])[0])
    return new_df


def read_gpad_csv(filename, version) -> pd:
    if version.startswith("1"):
        data_frame = pd.read_csv(filename,
                                 comment='!',
                                 header=None,
                                 na_filter=False,
                                 engine='python',
                                 delimiter="\t",
                                 names=gpad_1_2_format).fillna("")
        df = data_frame.filter(['db', 'subject', 'qualifiers', 'relation', 'object', 'evidence_code', 'reference'],
                               axis=1)
        concat_column = df['db'] + ":" + df['subject']
        df['concat_column'] = concat_column
        filtered_df = df.filter(['concat_column', 'qualifiers', 'relation', 'object', 'evidence_code', 'reference'])
        filtered_df.rename(columns={'concat_column': 'subject'}, inplace=True)
        new_df = filtered_df
    else:
        data_frame = pd.read_csv(filename,
                                 comment='!',
                                 sep='\t',
                                 header=None,
                                 na_filter=False,
                                 names=gpad_2_0_format).fillna("")
        new_df = data_frame.filter(['subject', 'negation', 'relation', 'object', 'evidence_code', 'reference'], axis=1)
    ecomapping = ecomap.EcoMap()
    for eco_code in ecomapping.mappings():
        for ev in new_df['evidence_code']:
            if eco_code[2] == ev:
                new_df['evidence_code'] = new_df['evidence_code'].replace([eco_code[2]],
                                                                          ecomapping.ecoclass_to_coderef(eco_code[2])[
                                                                              0])

    # normalize ids
    config = assocparser.AssocParserConfig()
    config.remove_double_prefixes = True
    parser = gpadparser.GpadParser(config=config)
    for i, r in enumerate(new_df['subject']):
        r1 = parser._normalize_id(r)
        new_df.at[i, 'subject'] = r1

    return new_df


def get_group_by(data_frame, groups, file) -> (pd, pd):
    print("Grouping by ", str(groups), type(groups))
    stats = {'filename': file, 'total_rows': data_frame.shape[0]}
    grouped_frame = data_frame.groupby(groups).size().reset_index(name='count')
    without_nulls = grouped_frame.fillna(0)
    return stats, without_nulls


def get_column_count(data_frame, file) -> (pd, pd):
    stats = {'filename': file, 'total_rows': data_frame.shape[0]}
    count_frame = data_frame.nunique().to_frame(file)
    return stats, count_frame


romap = {"RO:0002327": "enables",
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
         "RO:0002325": "colocalizes_with"}

gpad_1_2_format = ["db",
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
                   "properties"]

gpad_2_0_format = ["subject",
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
                   "properties"]

gaf_format = ["DB",
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
              "Gene_Product_Form_ID"]
