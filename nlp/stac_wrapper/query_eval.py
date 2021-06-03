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

DATA_TYPES = ['gold_data', 'test_data']
ANNOTATION_TYPES = ["property", "location", "tempex", "target"]
VALUE_TYPES = ["global", "type", "name", "bbox", "tempex", "numeric", "target"]


def eval_query(gold: Dict, test: Dict) -> (Dict, Dict, Dict, Dict):
    """
    Calculate all measures (data, span, attribute, value)
    for one natural language query test annotations
    given the equivalent gold annotations.
    Return appropriate dictionaries with a predefined templates for the results.
    """
    return eval_data(gold, test), \
           eval_span(gold, test),\
           eval_attribute(gold, test), \
           eval_value(gold, test)


def eval_data(gold: Dict, test: Dict) -> Dict:
    """
    Calculate data measures for one query test annotations
    given the gold equivalent query annotations.
    Return a dictionary with a predefined template for the results.
    """
    # create measures dictionary
    data_measures = DataMeasures.get_data_measures(gold['annotations'], test['annotations'])
    return data_measures


def eval_span(gold: Dict, test: Dict) -> Dict:
    """
    Calculate span measures for one query test annotations
    given the gold equivalent query annotations.
    Return a dictionary with a predefined template for the results.
    """
    # create measures dictionary
    span_measures = SpanMeasures.get_span_measures(gold['annotations'], test['annotations'])
    return span_measures


def eval_attribute(gold: Dict, test: Dict) -> Dict:
    """
    Calculate attribute measures for one query test annotations
    given the gold equivalent query annotations.
    Return a dictionary with a predefined template for the results.
    """
    # print("Attribute measures: ")
    attribute_measures = AttributeMeasures.get_attribute_measures(gold['annotations'], test['annotations'])
    # pprint.pprint(attribute_measures)
    return attribute_measures


def eval_value(gold: Dict, test: Dict) -> Dict:
    """
    Calculate value measures for one test query annotations
    given the gold equivalent query annotations.
    Return a dictionary with a predefined template for the results.
    """
    value_measures = ValueMeasures.get_value_measures(gold['annotations'], test['annotations'])
    # print("Value measures: ")
    # pprint.pprint(value_measures)
    return value_measures


def avg_min_max(data_list: List) -> Dict:
    """
    Function that calculates average, min and max
    of a list of numeric values.
    Returns values in a dictionary.
    """
    return {'avg': sum(data_list) / len(data_list), 'min': min(data_list), 'max': max(data_list)}


def calc_global_data_scores(data_dicts: List[Dict]) -> Dict:
    """
    Calculates global data evaluation scores
    given a dictionary of individual data scores
    per annotation.
    Returns a dictionary with a predefined template.
    """
    # a list of data dicts
    # a data dict is one 'data_measurements' dict
    data_scores = DataMeasures().to_dict()
    for data_type in DATA_TYPES:
        data_scores[data_type]['total_annotation'] = sum(
            [data_dict[data_type]['total_annotation'] for data_dict in data_dicts])
        data_scores[data_type]['annotation_per_query'] = avg_min_max(
            [data_dict[data_type]['total_annotation'] for data_dict in data_dicts])
        for annot_type in ANNOTATION_TYPES:
            data_scores[data_type]['total_annotation_per_type'][annot_type] = sum(
                [data_dict[data_type]['total_annotation_per_type'][annot_type] for data_dict in data_dicts])
    return data_scores


def calc_global_span_scores(span_dicts: List[Dict]) -> Dict:
    """
   Calculates global span evaluation scores
   given a dictionary of individual span scores
   per annotation.
   Returns a dictionary with a predefined template.
   """
    span_measures = SpanMeasures().to_dict()
    # count global measures
    count = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    overlap = {'property': [], 'location': [], 'tempex': [], 'target': []}
    overlap_t = {'property': [], 'location': [], 'tempex': [], 'target': []}

    for annot_type in ANNOTATION_TYPES:
        # total span counts per type
        span_measures[annot_type]['count'] = sum([span_dict[annot_type]['count'] for span_dict in span_dicts])
        count[annot_type] = span_measures[annot_type]['count']
        span_measures['global']['count'] += span_measures[annot_type]['count']
        span_measures[annot_type]['perfect_begin']['no_type_match'] = sum(
            [span_dict[annot_type]['perfect_begin']['no_type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['perfect_begin']['type_match'] = sum(
            [span_dict[annot_type]['perfect_begin']['type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['perfect_end']['no_type_match'] = sum(
            [span_dict[annot_type]['perfect_end']['no_type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['perfect_end']['type_match'] = sum(
            [span_dict[annot_type]['perfect_end']['type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['perfect_match']['no_type_match'] = sum(
            [span_dict[annot_type]['perfect_match']['no_type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['perfect_match']['type_match'] = sum(
            [span_dict[annot_type]['perfect_match']['type_match'] for span_dict in span_dicts]) / count[annot_type]
        overlap[annot_type] = [span_dict[annot_type]['overlapping_span']['no_type_match']['min'] for span_dict in
                               span_dicts]
        overlap_t[annot_type] = [span_dict[annot_type]['overlapping_span']['type_match']['min'] for span_dict in
                                 span_dicts]
        span_measures[annot_type]['overlapping_span']['no_type_match'] = avg_min_max(overlap[annot_type])
        span_measures[annot_type]['overlapping_span']['type_match'] = avg_min_max(overlap_t[annot_type])
        span_measures[annot_type]['split_gold_span']['no_type_match'] = sum(
            [span_dict[annot_type]['split_gold_span']['no_type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['split_gold_span']['type_match'] = sum(
            [span_dict[annot_type]['split_gold_span']['type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['split_test_span']['no_type_match'] = sum(
            [span_dict[annot_type]['split_test_span']['no_type_match'] for span_dict in span_dicts]) / count[annot_type]
        span_measures[annot_type]['split_test_span']['type_match'] = sum(
            [span_dict[annot_type]['split_test_span']['type_match'] for span_dict in span_dicts]) / count[annot_type]

    global_count = span_measures['global']['count']

    # calculate percentage of test
    span_measures['global']['overlapping_span']['no_type_match'] = avg_min_max(sum(overlap.values(), []))
    span_measures['global']['overlapping_span']['type_match'] = avg_min_max(sum(overlap_t.values(), []))
    span_measures['global']['perfect_begin']['no_type_match'] = sum(
        [span_measures[annot_type]['perfect_begin']['no_type_match'] for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures['global']['perfect_begin']['type_match'] = sum(
        [span_measures[annot_type]['perfect_begin']['type_match'] for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures['global']['perfect_end']['no_type_match'] = sum(
        [span_measures[annot_type]['perfect_end']['no_type_match'] for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures['global']['perfect_end']['type_match'] = sum(
        [span_measures[annot_type]['perfect_end']['type_match'] for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures['global']['split_gold_span']['no_type_match'] = sum(
        [span_measures[annot_type]['split_gold_span']['no_type_match'] for annot_type in
         ANNOTATION_TYPES]) / global_count
    span_measures['global']['split_gold_span']['type_match'] = sum(
        [span_measures[annot_type]['split_gold_span']['type_match'] for annot_type in ANNOTATION_TYPES]) / global_count
    span_measures['global']['split_test_span']['no_type_match'] = sum(
        [span_measures[annot_type]['split_test_span']['no_type_match'] for annot_type in
         ANNOTATION_TYPES]) / global_count
    span_measures['global']['split_test_span']['type_match'] = sum(
        [span_measures[annot_type]['split_test_span']['type_match'] for annot_type in ANNOTATION_TYPES]) / global_count
    return span_measures


def calc_global_attr_scores(attr_dicts: List[Dict]) -> Dict:
    """
    Calculates global attribute evaluation scores
    given a dictionary of individual attribute scores
    per annotation.
    Returns a dictionary with a predefined template.
    """
    attr_scores = AttributeMeasures().to_dict()
    per_annot_attr_match = []
    for annot_type in ANNOTATION_TYPES:
        attr_scores[annot_type]["count"] = sum([attr_dict[annot_type]['count'] for attr_dict in attr_dicts])
        attr_scores[annot_type]["total_span_type_match"] = sum(
            [attr_dict[annot_type]["total_span_type_match"] for attr_dict in attr_dicts])
        attr_scores[annot_type]["per_annotation_span_perfect_match_precision"] = sum(
            [attr_dict[annot_type]["per_annotation_span_perfect_match_precision"] for attr_dict in attr_dicts])
        attr_scores[annot_type]["per_annotation_overlapping_span_perfect_match"] = sum(
            [attr_dict[annot_type]["per_annotation_overlapping_span_perfect_match"] for attr_dict in attr_dicts])
        per_annot_attr_match += [attr_dict[annot_type]["per_annotation_attribute_match"]['min'] for attr_dict in
                                 attr_dicts]
        attr_scores[annot_type]["per_annotation_attribute_match"] = avg_min_max(
            [attr_dict[annot_type]["per_annotation_attribute_match"]['min'] for attr_dict in attr_dicts])
        attr_scores['global']["count"] += attr_scores[annot_type]["count"]
        attr_scores['global']["total_span_type_match"] += attr_scores[annot_type]["total_span_type_match"]
        attr_scores['global']["per_annotation_span_perfect_match_precision"] += attr_scores[annot_type][
            "per_annotation_span_perfect_match_precision"]
        attr_scores['global']["per_annotation_overlapping_span_perfect_match"] += \
            attr_scores[annot_type]["per_annotation_overlapping_span_perfect_match"]
        attr_scores[annot_type]["per_annotation_span_perfect_match_precision"] = \
            attr_scores[annot_type]["per_annotation_span_perfect_match_precision"] / len( attr_dicts)
        attr_scores[annot_type]["per_annotation_overlapping_span_perfect_match"] = \
            attr_scores[annot_type][ "per_annotation_overlapping_span_perfect_match"] / len(attr_dicts)

    attr_scores['global']["per_annotation_attribute_match"] = avg_min_max(per_annot_attr_match)
    return attr_scores


def calc_global_val_scores(val_dicts: List[Dict]) -> Dict:
    """
    Calculate global value scores,
    given a dictionary of individual value scores
    per annotation.
    Returns a dictionary with a predefined template
    of evaluation scores.
    """
    val_scores = ValueMeasures().to_dict()

    for value_type in VALUE_TYPES:  # annotation type
        val_scores[value_type]['total_matching_attributes'] = sum(
            [val_dict[value_type]['total_matching_attributes'] for val_dict in val_dicts])
        val_scores[value_type]['perfect_value_match'] = sum(
            [val_dict[value_type]['perfect_value_match'] for val_dict in val_dicts]) / len(val_dicts)

    val_scores['global']["ratio_matching_attributes"] = sum(
        [val_dict['global']["ratio_matching_attributes"] for val_dict in val_dicts]) / len(
        val_dicts)
    val_scores['name']["levenstein"] = avg_min_max([val_dict['name']["levenstein"]['min'] for val_dict in val_dicts])
    val_scores['bbox']["intersect_over_union"] = avg_min_max(
        [val_dict['bbox']["intersect_over_union"]['min'] for val_dict in val_dicts])
    val_scores['tempex']["duration_overlap"] = avg_min_max(
        [val_dict['tempex']["duration_overlap"]['min'] for val_dict in val_dicts])
    val_scores['numeric']['value_offset'] = avg_min_max(
        [val_dict['numeric']['value_offset']['min'] for val_dict in val_dicts])
    val_scores['target']['matching_element'] = avg_min_max(
        [val_dict['target']['matching_element']['min'] for val_dict in val_dicts])

    return val_scores


def global_stats(stats_path: str, gold_path: str, test_path: str, out_path: str) -> None:
    """
    Calculate global statistics given a
    - statistics template file path that defines all the evaluation metrics
    - gold and test query annotations file paths
    - output file path
    Checks if all test queries have their gold defined,
    and calculates all metrics (data, span, attribute, value)
    and writes them using the statistics template to the output file
    """
    try:
        # open and copy the template file
        with open(stats_path, "r") as stats_f:
            template = json.load(stats_f)
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
        stats = template['global_stats']
        stats['gold_file'] = gold_path
        stats['test_file'] = test_path
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
        stats['data_measures'] = calc_global_data_scores(global_data)
        print("GLOBAL data measures:")
        pprint.pprint(stats['data_measures'])
        stats['span_measures'] = calc_global_span_scores(global_span)
        print("GLOBAL span measures: ")
        pprint.pprint(stats['span_measures'])
        stats['attribute_measures'] = calc_global_attr_scores(global_attr)
        print("GLOBAL attribute measures: ")
        pprint.pprint(stats['attribute_measures'])
        stats['value_measures'] = calc_global_val_scores(global_value)
        print("GLOBAL value measures: ")
        pprint.pprint(stats['value_measures'])

        # write results to out path
        with open(out_path, "w") as outf:
            json.dump(template, outf)


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    global_stats(os.path.join(path, "global_stats.json"), os.path.join(path, "gold_queries.json"),
                 os.path.join(path, "noisy_gold_queries.json"), os.path.join(path, "out.json"))
