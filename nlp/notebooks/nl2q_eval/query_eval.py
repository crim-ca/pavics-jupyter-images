"""
Evaluates a set of natural language query test annotations
given their equivalent gold annotations.
Calculates several evaluation metrics (data, span, attribute, value)
and fills in predefined metrics template dictionaries defined in json file.
"""
import pprint
import json
import os
import sys
from MetricsClasses import *
from typing import List, Dict


def eval_query(gold: Dict, test: Dict) -> (DataMeasures, SpanMeasures, AttributeMeasures, ValueMeasures):
    """
    Calculate all measures (data, span, attribute, value)
    for one natural language query test annotations
    given the equivalent gold annotations.
    Return appropriate class instances with the results.
    """
    return eval_data(gold, test), \
        eval_span(gold, test), \
        eval_attribute(gold, test), \
        eval_value(gold, test)


def eval_data(gold: Dict, test: Dict) -> DataMeasures:
    """
    Calculate data measures for one query test annotations
    given the gold equivalent query annotations.
    Return a DataMeasures instance with the results.
    """
    # create measures dictionary
    data_measures = DataMeasures.get_data_measures(gold['annotations'], test['annotations'])
    return data_measures


def eval_span(gold: Dict, test: Dict) -> SpanMeasures:
    """
    Calculate span measures for one query test annotations
    given the gold equivalent query annotations.
    Return a SpanMeasures instance with the results.
    """
    # create measures dictionary
    span_measures = SpanMeasures.get_span_measures(gold['annotations'], test['annotations'])
    return span_measures


def eval_attribute(gold: Dict, test: Dict) -> AttributeMeasures:
    """
    Calculate attribute measures for one query test annotations
    given the gold equivalent query annotations.
    Return an AttributeMeasures instance with the results.
    """
    # print("Attribute measures: ")
    attribute_measures = AttributeMeasures.get_attribute_measures(gold=gold['annotations'],
                                                                  test=test['annotations'])
    # pprint.pprint(attribute_measures)
    return attribute_measures


def eval_value(gold: Dict, test: Dict) -> ValueMeasures:
    """
    Calculate value measures for one test query annotations
    given the gold equivalent query annotations.
    Return a ValueMeasures instance with the results.
    """
    value_measures = ValueMeasures.get_value_measures(gold['annotations'], test['annotations'])
    # print("Value measures: ")
    # pprint.pprint(value_measures)
    return value_measures


def calc_global_data_scores(data_measures_list: List[DataMeasures]) -> DataMeasures:
    """
    Calculates global data evaluation scores
    given a dictionary of individual data scores
    per annotation.
    Returns a DataMeasures instance with the results.
    """
    # a list of data dicts
    # a data dict is one 'data_measurements' dict
    global_data_measures = DataMeasures()

    for data_type in DATA_TYPES:
        global_data_measures.get_data_metrics(data_type).total_annotation = sum(
            [data_measures.get_data_metrics(data_type).total_annotation for data_measures in data_measures_list])
        global_data_measures.get_data_metrics(data_type).annotation_per_query = MinMaxAvg.calc_avg_min_max(
            [data_measures.get_data_metrics(data_type).total_annotation for data_measures in data_measures_list])
        for annot_type in ANNOTATION_TYPES:
            global_data_measures.get_data_metrics(data_type).set_metric(annot_type, sum(
                [data_measures.get_data_metrics(data_type).get_metric(annot_type) for data_measures in
                 data_measures_list]))
    return global_data_measures


def calc_global_span_scores(span_measures_list: List[SpanMeasures]) -> SpanMeasures:
    """
   Calculates global span evaluation scores
   given a dictionary of individual span scores
   per annotation.
   Returns a SpanMeasures instance with the results.
   """
    global_span_measures = SpanMeasures()
    # count global measures
    count = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    overlap = {'property': [], 'location': [], 'tempex': [], 'target': []}
    overlap_t = {'property': [], 'location': [], 'tempex': [], 'target': []}

    for annot_type in ANNOTATION_TYPES:
        # total span counts per type
        span_metric_annot_type = global_span_measures.get_span_metrics(annot_type)
        span_metric_annot_type.count = sum(
            [span_measures.get_span_metrics(annot_type).count for span_measures in span_measures_list])
        count[annot_type] = span_metric_annot_type.count
        global_span_measures.get_span_metrics('global').count += span_metric_annot_type.count
        span_metric_annot_type.perfect_begin_no_type_match = sum(
            [span_measures.get_span_metrics(annot_type).perfect_begin_no_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.perfect_begin_type_match = sum(
            [span_measures.get_span_metrics(annot_type).perfect_begin_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.perfect_end_no_type_match = sum(
            [span_measures.get_span_metrics(annot_type).perfect_end_no_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.perfect_end_type_match = sum(
            [span_measures.get_span_metrics(annot_type).perfect_end_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.perfect_match_no_type_match = sum(
            [span_measures.get_span_metrics(annot_type).perfect_match_no_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.perfect_match_type_match = sum(
            [span_measures.get_span_metrics(annot_type).perfect_match_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.split_gold_no_type_match = sum(
            [span_measures.get_span_metrics(annot_type).split_gold_no_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.split_gold_type_match = sum(
            [span_measures.get_span_metrics(annot_type).split_gold_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.split_test_type_no_type_match = sum(
            [span_measures.get_span_metrics(annot_type).split_test_type_no_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0
        span_metric_annot_type.split_test_type_match = sum(
            [span_measures.get_span_metrics(annot_type).split_test_type_match
             for span_measures in span_measures_list]) / count[annot_type] if count[annot_type] else 0

        overlap[annot_type] = [span_measures.get_span_metrics(annot_type).overlapping_span_no_type_match.minn for
                               span_measures in
                               span_measures_list]
        overlap_t[annot_type] = [span_measures.get_span_metrics(annot_type).overlapping_span_type_match.minn for
                                 span_measures in
                                 span_measures_list]
        span_metric_annot_type.overlapping_span_no_type_match = MinMaxAvg.calc_avg_min_max(
            overlap[annot_type])
        span_metric_annot_type.overlapping_span_type_match = MinMaxAvg.calc_avg_min_max(
            overlap_t[annot_type])

    type_count = len([x for x in count.keys() if count[x]>0])
    # calculate percentage of test
    global_span_measures.get_span_metrics('global').overlapping_span_no_type_match = MinMaxAvg.calc_avg_min_max(
        sum(overlap.values(), []))
    global_span_measures.get_span_metrics('global').overlapping_span_type_match = MinMaxAvg.calc_avg_min_max(
        sum(overlap_t.values(), []))
    global_span_measures.get_span_metrics('global').perfect_begin_no_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).perfect_begin_no_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').perfect_begin_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).perfect_begin_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').perfect_end_no_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).perfect_end_no_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').perfect_end_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).perfect_end_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').perfect_end_no_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).perfect_end_no_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').perfect_match_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).perfect_match_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').perfect_match_no_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).perfect_match_no_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').split_gold_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).split_gold_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').split_test_type_no_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).split_test_type_no_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    global_span_measures.get_span_metrics('global').split_test_type_match = sum(
        [global_span_measures.get_span_metrics(annot_type).split_test_type_match
         for annot_type in ANNOTATION_TYPES]) / type_count
    return global_span_measures


def calc_global_attr_scores(attribute_measures_list: List[AttributeMeasures]) -> AttributeMeasures:
    """
    Calculates global attribute evaluation scores
    given a dictionary of individual attribute scores
    per annotation.
    Returns an AttributeMeasures instance with the results.
    """
    global_attribute_measures = AttributeMeasures()
    per_annot_attr_match = []
    type_count = 0
    for annot_type in ANNOTATION_TYPES:
        attrib_metric = global_attribute_measures.get_attribute_metrics(annot_type)
        attrib_metric.count = sum(
            [attribute_measures.get_attribute_metrics(annot_type).count for attribute_measures in
             attribute_measures_list])
        if attrib_metric.count > 0:
            type_count += 1
        attrib_metric.total_span_type_match = sum(
            [attribute_measures.get_attribute_metrics(annot_type).total_span_type_match for attribute_measures in
             attribute_measures_list])
        attrib_metric.perfect_match_precision = sum(
            [attribute_measures.get_attribute_metrics(annot_type).perfect_match_precision for attribute_measures in
             attribute_measures_list])
        attrib_metric.overlapping_perfect_match = sum(
            [attribute_measures.get_attribute_metrics(annot_type).overlapping_perfect_match for attribute_measures in
             attribute_measures_list])
        per_annot_attr_match += [attribute_measures.get_attribute_metrics(annot_type).attribute_match.minn for
            attribute_measures in attribute_measures_list if attribute_measures.get_attribute_metrics(annot_type).count>0]
        attrib_metric.attribute_match = MinMaxAvg.calc_avg_min_max(
            [attribute_measures.get_attribute_metrics(annot_type).attribute_match.minn for attribute_measures in
             attribute_measures_list if attribute_measures.get_attribute_metrics(annot_type).count>0])
        global_attribute_measures.get_attribute_metrics(
            'global').count += global_attribute_measures.get_attribute_metrics(annot_type).count
        global_attribute_measures.get_attribute_metrics(
            'global').total_span_type_match += global_attribute_measures.get_attribute_metrics(
            annot_type).total_span_type_match
        global_attribute_measures.get_attribute_metrics('global').overlapping_perfect_match += \
            global_attribute_measures.get_attribute_metrics(annot_type).overlapping_perfect_match
        count_attribute_measures_list = len(
            [x for x in attribute_measures_list if x.get_attribute_metrics(annot_type).count > 0])
        attrib_metric.perfect_match_precision = attrib_metric.perfect_match_precision / count_attribute_measures_list \
            if count_attribute_measures_list else 0
        global_attribute_measures.get_attribute_metrics(
            'global').perfect_match_precision += global_attribute_measures.get_attribute_metrics(
            annot_type).perfect_match_precision
        attrib_metric.overlapping_perfect_match = attrib_metric.overlapping_perfect_match / \
            count_attribute_measures_list if count_attribute_measures_list else 0

    global_attribute_measures.get_attribute_metrics('global').perfect_match_precision = \
        global_attribute_measures.get_attribute_metrics('global').perfect_match_precision / type_count
    global_attribute_measures.get_attribute_metrics('global').attribute_match = MinMaxAvg.calc_avg_min_max(
        per_annot_attr_match)

    return global_attribute_measures


def calc_global_val_scores(value_measures_list: List[ValueMeasures]) -> ValueMeasures:
    """
    Calculate global value scores,
    given a dictionary of individual value scores
    per annotation.
    Returns a ValueMeasures instance with the results.
    """
    global_value_measures = ValueMeasures()

    for value_type in VALUE_TYPES:  # annotation type
        global_value_measures.get_value_metrics(value_type).total_matching_attributes = sum(
            [value_measures.get_value_metrics(value_type).total_matching_attributes
             for value_measures in value_measures_list])
        nr_annotations_value_type = len([value_measures
                                         for value_measures in value_measures_list if
                                         value_measures.get_value_metrics(value_type).total_matching_attributes > 0])

        global_value_measures.get_value_metrics(value_type).perfect_value_match = (sum(
            [value_measures.get_value_metrics(value_type).perfect_value_match
             for value_measures in value_measures_list if
             value_measures.get_value_metrics(value_type).total_matching_attributes > 0])
                / nr_annotations_value_type) if nr_annotations_value_type else 0

    global_value_measures.get_value_metrics('global').total_matching_attributes = sum(
        [global_value_measures.get_value_metrics(value_type).total_matching_attributes
         for value_type in VALUE_TYPES])
    global_value_measures.global_ratio_matching_attribute = sum(
        [value_measures.global_ratio_matching_attribute
         for value_measures in value_measures_list]) / \
         len([x for x in value_measures_list if x.get_value_metrics('global').total_matching_attributes>0])
    global_value_measures.get_value_metrics('global').perfect_value_match = sum(
        [global_value_measures.get_value_metrics(value_type).perfect_value_match
         for value_type in VALUE_TYPES]) / len([x for x in VALUE_TYPES
        if global_value_measures.get_value_metrics(x).total_matching_attributes >0])
    global_value_measures.name_levenstein = MinMaxAvg.calc_avg_min_max(
        [value_measures.name_levenstein.minn for value_measures in value_measures_list if value_measures.name_value.total_matching_attributes>0])
    global_value_measures.bbox_iou = MinMaxAvg.calc_avg_min_max(
        [value_measures.bbox_iou.minn for value_measures in value_measures_list if value_measures.bbox_value.total_matching_attributes>0])
    global_value_measures.tempex_duration_overlap = MinMaxAvg.calc_avg_min_max(
        [value_measures.tempex_duration_overlap.minn for value_measures in value_measures_list if value_measures.tempex_value.total_matching_attributes>0])
    global_value_measures.numeric_value_offset = MinMaxAvg.calc_avg_min_max(
        [value_measures.numeric_value_offset.minn for value_measures in value_measures_list if value_measures.name_value.total_matching_attributes>0])
    global_value_measures.target_matching_element = MinMaxAvg.calc_avg_min_max(
        [value_measures.target_matching_element.minn for value_measures in value_measures_list if value_measures.target_value.total_matching_attributes>0])

    return global_value_measures


def read_files(gold_path, test_path):
    try:
        # open the two files
        with open(gold_path) as f:
            gold_file = json.load(f)
        with open(test_path) as f:
            test_file = json.load(f)
        return gold_file, test_file
    except Exception as exc:
        print("Encountered an error while reading input files. "
              "Please check the correct file paths!")
        print(exc)
        return


def global_stats_from_file(gold_path: str, test_path: str) -> EvalMeasures:
    """
       Calculate global statistics given a
       - gold and test query annotations file path
       Checks if all test queries have their gold defined,
       and calculates all metrics (data, span, attribute, value),
       and returns an EvalMeasures instance.
    """
    gold_file, test_file = read_files(gold_path, test_path)
    return global_stats(gold_file, test_file)


def global_stats(gold_file: Dict, test_file: Dict) -> EvalMeasures:
    """
    Calculate global statistics given a
    - gold and test query annotation dictionaries
    Checks if all test queries have their gold defined,
    and calculates all metrics (data, span, attribute, value),
    and returns an EvalMeasures instance.
    """
    gold_qs, test_qs = [], []
    if gold_file and test_file:
        # the root key is 'queries'
        if 'queries' in gold_file.keys() and 'queries' in test_file.keys():
            gold_qs = gold_file['queries']
            test_qs = test_file['queries']
        else:
            print("Error: JSON format not as expected. No 'queries' key! ")
            sys.exit()

        # sanity checks if all queries are there
        if len(gold_qs) != len(test_qs):
            print("Error: Number of queries different in gold and test! ")
            sys.exit()

        # all good
        stats = EvalMeasures()

        # vars to hold list of individual results,
        # and calculate global scores with
        global_data = []
        global_span = []
        global_attr = []
        global_value = []
        for gold_q in gold_qs:
            test_q = [t for t in test_qs if t['query'] == gold_q['query']][0]
            data, span, attr, value = eval_query(gold_q, test_q)
            global_data.append(data)
            global_span.append(span)
            global_attr.append(attr)
            global_value.append(value)

        # calculate global scores
        stats.data_measures = calc_global_data_scores(global_data)
        print("\nGLOBAL data measures:")
        pprint.pprint(stats.data_measures.to_dict())
        stats.span_measures = calc_global_span_scores(global_span)
        print("\nGLOBAL span measures: ")
        pprint.pprint(stats.span_measures.to_dict())
        stats.attribute_measures = calc_global_attr_scores(global_attr)
        print("\nGLOBAL attribute measures: ")
        pprint.pprint(stats.attribute_measures.to_dict())
        stats.value_measures = calc_global_val_scores(global_value)
        print("\nGLOBAL value measures: ")
        pprint.pprint(stats.value_measures.to_dict())

        return stats


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    stats = global_stats_from_file(gold_path=os.path.join(path, "ceda_gold_queries.json"),
                                   test_path=os.path.join(path, "v1_ceda_test_results.json"))

    # out_path = os.path.join(path, "v3_ceda_eval_out.json")
    # with open(out_path, "w") as outf:
    #     json.dump(stats.to_dict(), outf)
