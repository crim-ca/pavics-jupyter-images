"""
Evaluates a set of natural language query test annotations
given their equivalent gold annotations.
Calculates several evaluation metrics (data, span, attribute, value)
and fills in predefined metrics template dictionaries defined in json file.
"""
import pprint
import json
import os
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
           eval_span(gold, test),\
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
    attribute_measures = AttributeMeasures.get_attribute_measures(gold['annotations'], test['annotations'])
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


def calc_global_data_scores(data_dicts: List[DataMeasures]) -> DataMeasures:
    """
    Calculates global data evaluation scores
    given a dictionary of individual data scores
    per annotation.
    Returns a DataMeasures instance with the results.
    """
    # a list of data dicts
    # a data dict is one 'data_measurements' dict
    data_scores = DataMeasures()
    for data_type in DATA_TYPES:
        data_scores.getattr(data_type).total_annotation = sum(
            [data_dict.getattr(data_type).total_annotation for data_dict in data_dicts])
        data_scores.getattr(data_type).annotation_per_query = MinMaxAvg.calc_avg_min_max(
            [data_dict.getattr(data_type).total_annotation for data_dict in data_dicts])
        for annot_type in ANNOTATION_TYPES:
            data_scores.getattr(data_type).setattr(annot_type, sum(
                [data_dict.getattr(data_type).getattr(annot_type) for data_dict in data_dicts]))
    return data_scores


def calc_global_span_scores(span_dicts: List[SpanMeasures]) -> SpanMeasures:
    """
   Calculates global span evaluation scores
   given a dictionary of individual span scores
   per annotation.
   Returns a SpanMeasures instance with the results.
   """
    span_measures = SpanMeasures()
    # count global measures
    count = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    overlap = {'property': [], 'location': [], 'tempex': [], 'target': []}
    overlap_t = {'property': [], 'location': [], 'tempex': [], 'target': []}

    for annot_type in ANNOTATION_TYPES:
        # total span counts per type
        span_measures.getattr(annot_type).count = sum([span_dict.getattr(annot_type).count for span_dict in span_dicts])
        count[annot_type] = span_measures.getattr(annot_type).count
        span_measures.getattr('global').count += span_measures.getattr(annot_type).count
        span_measures.getattr(annot_type).perfect_begin_no_type_match = sum(
            [span_dict.getattr(annot_type).perfect_begin_no_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).perfect_begin_type_match = sum(
            [span_dict.getattr(annot_type).perfect_begin_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).perfect_end_no_type_match = sum(
            [span_dict.getattr(annot_type).perfect_end_no_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).perfect_end_type_match = sum(
            [span_dict.getattr(annot_type).perfect_end_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).perfect_match_no_type_match = sum(
            [span_dict.getattr(annot_type).perfect_match_no_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).perfect_match_type_match = sum(
            [span_dict.getattr(annot_type).perfect_match_type_match for span_dict in span_dicts]) / count[annot_type]
        overlap[annot_type] = [span_dict.getattr(annot_type).overlapping_span_no_type_match.minn for span_dict in
                               span_dicts]
        overlap_t[annot_type] = [span_dict.getattr(annot_type).overlapping_span_type_match.minn for span_dict in
                                 span_dicts]
        span_measures.getattr(annot_type).overlapping_span_no_type_match = MinMaxAvg.calc_avg_min_max(overlap[annot_type])
        span_measures.getattr(annot_type).overlapping_span_type_match = MinMaxAvg.calc_avg_min_max(overlap_t[annot_type])
        span_measures.getattr(annot_type).split_gold_no_type_match = sum(
            [span_dict.getattr(annot_type).split_gold_no_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).split_gold_type_match = sum(
            [span_dict.getattr(annot_type).split_gold_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).split_test_type_no_type_match = sum(
            [span_dict.getattr(annot_type).split_test_type_no_type_match for span_dict in span_dicts]) / count[annot_type]
        span_measures.getattr(annot_type).split_test_type_match = sum(
            [span_dict.getattr(annot_type).split_test_type_match for span_dict in span_dicts]) / count[annot_type]

    global_count = span_measures.getattr('global').count

    # calculate percentage of test
    span_measures.getattr('global').overlapping_span_no_type_match = MinMaxAvg.calc_avg_min_max(sum(overlap.values(), []))
    span_measures.getattr('global').overlapping_span_type_match = MinMaxAvg.calc_avg_min_max(sum(overlap_t.values(), []))
    span_measures.getattr('global').perfect_begin_no_type_match = sum(
        [span_measures.getattr(annot_type).perfect_begin_no_type_match for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures.getattr('global').perfect_begin_type_match = sum(
        [span_measures.getattr(annot_type).perfect_begin_type_match for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures.getattr('global').perfect_end_no_type_match = sum(
        [span_measures.getattr(annot_type).perfect_end_no_type_match for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures.getattr('global').perfect_end_type_match = sum(
        [span_measures.getattr(annot_type).perfect_end_type_match for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures.getattr('global').split_gold_no_type_match = sum(
        [span_measures.getattr(annot_type).split_gold_no_type_match for annot_type in
         ANNOTATION_TYPES]) / global_count
    span_measures.getattr('global').split_gold_type_match = sum(
        [span_measures.getattr(annot_type).split_gold_type_match for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures.getattr('global').split_test_type_no_type_match = sum(
        [span_measures.getattr(annot_type).split_test_type_no_type_match for annot_type in
         ANNOTATION_TYPES]) / global_count
    span_measures.getattr('global').split_test_type_match = sum(
        [span_measures.getattr(annot_type).split_test_type_match for annot_type in ANNOTATION_TYPES]) / global_count
    return span_measures


def calc_global_attr_scores(attr_dicts: List[AttributeMeasures]) -> AttributeMeasures:
    """
    Calculates global attribute evaluation scores
    given a dictionary of individual attribute scores
    per annotation.
    Returns an AttributeMeasures instance with the results.
    """
    attr_scores = AttributeMeasures()
    per_annot_attr_match = []
    for annot_type in ANNOTATION_TYPES:
        attr_scores.getattr(annot_type).count = sum(
            [attr_dict.getattr(annot_type).count for attr_dict in attr_dicts])
        attr_scores.getattr(annot_type).total_span_type_match = sum(
            [attr_dict.getattr(annot_type).total_span_type_match for attr_dict in attr_dicts])
        attr_scores.getattr(annot_type).perfect_match_precision = sum(
            [attr_dict.getattr(annot_type).perfect_match_precision for attr_dict in attr_dicts])
        attr_scores.getattr(annot_type).overlapping_perfect_match = sum(
            [attr_dict.getattr(annot_type).overlapping_perfect_match for attr_dict in attr_dicts])
        per_annot_attr_match += [attr_dict.getattr(annot_type).attribute_match.minn for attr_dict in
                                 attr_dicts]
        attr_scores.getattr(annot_type).attribute_match = MinMaxAvg.calc_avg_min_max(
            [attr_dict.getattr(annot_type).attribute_match.minn for attr_dict in attr_dicts])
        attr_scores.getattr('global').count += attr_scores.getattr(annot_type).count
        attr_scores.getattr('global').total_span_type_match += attr_scores.getattr(annot_type).total_span_type_match
        attr_scores.getattr('global').perfect_match_precision += attr_scores.getattr(annot_type).perfect_match_precision
        attr_scores.getattr('global').overlapping_perfect_match += \
            attr_scores.getattr(annot_type).overlapping_perfect_match
        attr_scores.getattr(annot_type).perfect_match_precision = \
            attr_scores.getattr(annot_type).perfect_match_precision / len(attr_dicts)
        attr_scores.getattr(annot_type).overlapping_perfect_match = \
            attr_scores.getattr(annot_type).overlapping_perfect_match / len(attr_dicts)

    attr_scores.getattr('global').attribute_match = MinMaxAvg.calc_avg_min_max(per_annot_attr_match)
    return attr_scores


def calc_global_val_scores(val_dicts: List[ValueMeasures]) -> ValueMeasures:
    """
    Calculate global value scores,
    given a dictionary of individual value scores
    per annotation.
    Returns a ValueMeasures instance with the results.
    """
    val_scores = ValueMeasures()

    for value_type in VALUE_TYPES:  # annotation type
        val_scores.getattr(value_type).total_matching_attributes = sum(
            [val_dict.getattr(value_type).total_matching_attributes for val_dict in val_dicts])
        val_scores.getattr(value_type).perfect_value_match = sum(
            [val_dict.getattr(value_type).perfect_value_match for val_dict in val_dicts]) / len(val_dicts)

    val_scores.global_ratio_matching_attribute = sum(
        [val_dict.global_ratio_matching_attribute for val_dict in val_dicts]) / len(val_dicts)
    val_scores.name_levenstein = MinMaxAvg.calc_avg_min_max(
        [val_dict.name_levenstein.minn for val_dict in val_dicts])
    val_scores.bbox_iou = MinMaxAvg.calc_avg_min_max([val_dict.bbox_iou.minn for val_dict in val_dicts])
    val_scores.tempex_duration_overlap = MinMaxAvg.calc_avg_min_max(
        [val_dict.tempex_duration_overlap.minn for val_dict in val_dicts])
    val_scores.numeric_value_offset = MinMaxAvg.calc_avg_min_max(
        [val_dict.numeric_value_offset.minn for val_dict in val_dicts])
    val_scores.target_matching_element = MinMaxAvg.calc_avg_min_max(
        [val_dict.target_matching_element.minn for val_dict in val_dicts])

    return val_scores


def global_stats(gold_path: str, test_path: str, out_path: str) -> None:
    """
    Calculate global statistics given a
    - gold and test query annotations file paths
    - output file path
    Checks if all test queries have their gold defined,
    and calculates all metrics (data, span, attribute, value),
    and serializes and writes them to the output file.
    """
    try:
        # open the two files
        with open(gold_path) as gold_f:
            gold_file = json.load(gold_f)
        with open(test_path) as test_f:
            test_file = json.load(test_f)
    except Exception as exc:
        print("Encountered an error while reading input files. Please check the ocrrect file paths!")
        print(exc)
        return
    else:
        # the root key is 'queries'
        if 'queries' in gold_file.keys() and 'queries' in test_file.keys():
            gold_qs = gold_file['queries']
            test_qs = test_file['queries']
        else:
            print("Error: JSON format not as expected. No 'queries' key! ")
            return

        # sanity checks if all queries are there
        if len(gold_qs) != len(test_qs):
            print("Error: Number of queries different in gold and test! ", gold_path, test_path)
            return

        # each query file consists of a list of {query: {}, annotations: {}} dicts
        gold_queries = [q["query"] for q in gold_qs]
        test_queries = [q["query"] for q in test_qs]
        for query in test_queries:
            if query not in gold_queries:
                print("Error: Query not found in gold! ", query)
                return

        # all good
        stats = {'global_stats': {}, 'gold_file': gold_path, 'test_file': test_path}
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
        stats['data_measures'] = calc_global_data_scores(global_data).to_dict()
        print("GLOBAL data measures:")
        pprint.pprint(stats['data_measures'])
        stats['span_measures'] = calc_global_span_scores(global_span).to_dict()
        print("GLOBAL span measures: ")
        pprint.pprint(stats['span_measures'])
        stats['attribute_measures'] = calc_global_attr_scores(global_attr).to_dict()
        print("GLOBAL attribute measures: ")
        pprint.pprint(stats['attribute_measures'])
        stats['value_measures'] = calc_global_val_scores(global_value).to_dict()
        print("GLOBAL value measures: ")
        pprint.pprint(stats['value_measures'])

        # write results to out path
        with open(out_path, "w") as outf:
            json.dump(stats, outf)


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    global_stats(gold_path=os.path.join(path, "gold_queries.json"),
                 test_path=os.path.join(path, "noisy_gold_queries.json"),
                 out_path=os.path.join(path, "out.json"))
