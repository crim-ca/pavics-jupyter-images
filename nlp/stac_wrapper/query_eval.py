"""
Evaluates a set of natural language query test annotations
given their equivalent gold annotations.
Calculates several evaluation metrics (data, span, attribute, value)
and fills in predefined metrics template dictionaries defined in json file.
"""
import pprint
import copy
import json
import datetime
import os
from MetricsClasses import *
from shapely.geometry import Polygon
from Levenshtein import distance
from typing import List, Dict, Any

DATA_TYPES = ['gold_data', 'test_data']
ANNOTATION_TYPES = ["property", "location", "tempex", "target"]
VALUE_TYPES = ["global", "type", "name", "bbox", "tempex", "numeric", "target"]

# results collection JSON structure templates
attr_measure_template = {
    "count": 0,
    "total_span_type_match": 0,
    "per_annotation_span_perfect_match_precision": 0.0,
    "per_annotation_overlapping_span_perfect_match": 0.0,
    "per_annotation_attribute_match": {
        "avg": 0.0,
        "min": 0,
        "max": 0
    }}
val_measure_template = {
    "total_matching_attributes": 0,
    "perfect_value_match": 0.0}


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

    # annotation counts
    gold_annotations = gold['annotations']
    # annotation count per type
    gold_types = [ann['type'] for ann in gold_annotations]
    # create data metrics class instance
    gold_data = DataMetrics.create_data_metrics(total_ann=len(gold_annotations),
                                                total_prop=gold_types.count('property'),
                                                total_loc=gold_types.count('location'),
                                                total_temp=gold_types.count('tempex'),
                                                total_targ=gold_types.count('target'))
    # we will count averages and global values outside this function
    # same structure for test
    test_annotations = test['annotations']
    test_types = [ann['type'] for ann in test_annotations]
    test_data = DataMetrics.create_data_metrics(total_ann=len(test_annotations),
                                                total_prop=test_types.count('property'),
                                                total_loc=test_types.count('location'),
                                                total_temp=test_types.count('tempex'),
                                                total_targ=test_types.count('target'))
    # create measures dictionary
    data_measures = DataMeasures(gold_data, test_data)

    return data_measures.to_dict()


def eval_span(gold: Dict, test: Dict) -> Dict:
    """
    Calculate span measures for one query test annotations
    given the gold equivalent query annotations.
    Return a dictionary with a predefined template for the results.
    """
    # create measures dictionary
    span_measures = SpanMeasures.get_span_measures()

    # calculate span measures
    gold_types = [ann['type'] for ann in gold['annotations']]
    gold_spans = [ann['position'] for ann in gold['annotations']]
    test_types = [ann['type'] for ann in test['annotations']]
    test_spans = [ann['position'] for ann in test['annotations']]

    # print(gold_spans)
    # print(test_spans)
    # TODO! if gold_spans is only length 1, the result has an empty item in the list?
    for idx, span in enumerate(test_spans):
        # update count
        span_measures[test_types[idx]]['count'] += 1
        # perfect match
        if span in gold_spans:
            # exact match
            # update type-specific count
            # check for type match
            gold_idx = gold_spans.index(span)  # we do not presume the test and gold are aligned
            if test_types[idx] == gold_types[gold_idx]:
                span_measures[test_types[idx]]['perfect_match']['type_match'] += 1
            else:
                span_measures[test_types[idx]]['perfect_match']['no_type_match'] += 1
        else:
            # not perfect match
            # check for some kind of overlap
            # overlapping spans
            overlap_count = 0
            type_match_count = 0
            for gidx, gspan in enumerate(gold_spans):
                if range(max(span[0], gspan[0]), min(span[-1], gspan[-1])):
                    # includes perfect end and begin
                    if test_types[idx] == gold_types[gidx]:
                        span_measures[test_types[idx]]['overlapping_span']['type_match']['min'] += 1
                        type_match_count += 1
                    else:
                        span_measures[test_types[idx]]['overlapping_span']['no_type_match']['min'] += 1
                    # perfect begin
                    if span[0] == gold_spans[gidx][0]:
                        # begin match (including exact match)
                        # update type-specific count
                        if test_types[idx] == gold_types[gidx]:
                            span_measures[test_types[idx]]['perfect_begin']['type_match'] += 1
                        else:
                            span_measures[test_types[idx]]['perfect_begin']['no_type_match'] += 1
                    # perfect end
                    if span[1] == gold_spans[gidx][1]:
                        # end match (including exact match)
                        # update type-specific count
                        if test_types[idx] == gold_types[gidx]:
                            span_measures[test_types[idx]]['perfect_end']['type_match'] += 1
                        else:
                            span_measures[test_types[idx]]['perfect_end']['no_type_match'] += 1
                    overlap_count += 1
                if overlap_count > 1:
                    # this test span matches several gold spans = split-test
                    if overlap_count == type_match_count:
                        span_measures[test_types[idx]]['split_test_span']['type_match'] += 1
                    else:
                        span_measures[test_types[idx]]['split_test_span']['no_type_match'] += 1

    # split gold
    for gidx, gspan in enumerate(gold_spans):
        split_count = 0
        type_match_count = 0
        for tspan in test_spans:
            if range(max(gspan[0], tspan[0]), min(gspan[-1], tspan[-1])):
                split_count += 1
                if gold_types[gidx] == test_types[test_spans.index(tspan)]:
                    type_match_count += 1

        if split_count > 1:
            # we have split gold span
            if split_count == type_match_count:
                span_measures[gold_types[gidx]]['split_gold_span']['type_match'] += 1
            else:
                span_measures[gold_types[gidx]]['split_gold_span']['no_type_match'] += 1
    return span_measures


def eval_attribute(gold: Dict, test: Dict) -> Dict:
    """
    Calculate attribute measures for one query test annotations
    given the gold equivalent query annotations.
    Return a dictionary with a predefined template for the results.
    """
    # create measures dictionary
    attribute_measures = {
        "property": copy.deepcopy(attr_measure_template),
        "location": copy.deepcopy(attr_measure_template),
        "tempex": copy.deepcopy(attr_measure_template),
        "target": copy.deepcopy(attr_measure_template)
    }
    gold_spans = [gspan['position'] for gspan in gold['annotations']]
    gold_types = [gspan['type'] for gspan in gold['annotations']]
    gold_ann = list(gold['annotations'])
    # count of annotations per types
    count = {}
    for annot_type in ANNOTATION_TYPES:
        count[annot_type] = len([x for x in test['annotations'] if x['type'] == annot_type])

    for ann in test['annotations']:
        # count how many attributes in test
        # obligatory for property, tempex, location: type, position, name, value
        # obligatory for target: type, position, name
        test_type = ann['type']
        attribute_measures[test_type]['count'] += len(ann)
        test_span = ann['position']
        # exact span match
        if test_span in gold_spans:
            gidx = gold_spans.index(test_span)
            # per_annotation_span_perfect_match_precision
            # % of annotation having all attribute matched when span is same
            if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                attribute_measures[test_type]['per_annotation_span_perfect_match_precision'] += 1
        else:
            # no exact span match, find overlapping span match
            for gidx, gspan in enumerate(gold_spans):
                # overlapping span
                if range(max(gspan[0], test_span[0]), min(gspan[-1], test_span[-1])):
                    # total_span_type_match
                    # nr of attributes where matching span+type
                    # the same as in the measures overlapping_span:type_match
                    # but as a count instead of %
                    # exact type match
                    if test_type == gold_types[gidx]:
                        attribute_measures[test_type]['total_span_type_match'] += 1
                    # per_annotation_overlapping_span_perfect_match
                    # % of annotation having all attribute matched, for overlapping span
                    if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                        attribute_measures[test_type]['per_annotation_overlapping_span_perfect_match'] += 1
                    # per_annotation_attribute_match
                    # % of matching attribute name / total number of attribute in an annotation
                    # compared to overlapping spans
                    attribute_measures[test_type]['per_annotation_attribute_match']['min'] = \
                        len(set(ann.keys()).intersection(gold_ann[gidx].keys())) / len(ann)

    for annot_type in ANNOTATION_TYPES:
        # count of annotations of all attributes matched for exact span / nr of annots of that type
        attribute_measures[annot_type]['per_annotation_span_perfect_match_precision'] = \
            attribute_measures[annot_type]['per_annotation_span_perfect_match_precision'] / count[annot_type] if count[annot_type] else 0
        # per_annotation_overlapping_span_perfect_match
        attribute_measures[annot_type]['per_annotation_overlapping_span_perfect_match'] = \
            attribute_measures[annot_type]['per_annotation_overlapping_span_perfect_match'] / count[annot_type] if count[annot_type] else 0

    # print("Attribute measures: ")
    # pprint.pprint(attribute_measures)
    return attribute_measures


def levenshtein(str1: str, str2: str) -> int:
    """
    Calculate the Levenshtein distance
    between two strings
    """
    return distance(str1, str2)


def intersect_over_union(bbox1: Dict, bbox2: Dict) -> float:
    """
    Calculate intersect over union of two geojson features
    that are either polygons or points.
    """
    # polygons require min 3 coordinate tuples
    if 'coordinates' in bbox1 and 'coordinates' in bbox2 and \
            len(bbox1['coordinates']) > 2 and len(bbox2['coordinates']) > 2:
        poly1 = Polygon(bbox1['coordinates'])
        poly2 = Polygon(bbox2['coordinates'])
        polygon_intersection = poly1.intersection(poly2).area
        polygon_union = poly1.union(poly2).area
        iou = polygon_intersection / polygon_union
        return iou
    # how to calculate for points?
    if bbox1['type'] == "Point" and bbox2['type'] == "Point":
        if bbox1['coordinates'] == bbox2['coordinates']:
            return 1
    return 0


def duration_overlap(dur1, dur2) -> int:
    """
    Function to calculate the overlap (in number of days)
    of two date ranges given in a specific format
    Returns 0 if no overlap found.
    """
    dformat = '%Y-%m-%dT%H:%M:%SZ'
    # datarange {'start': startdate, 'end': enddate}
    if len(dur1) == 2 and len(dur2) == 2 and 'start' in dur1 and 'start' in dur2:
        r1_start = datetime.datetime.strptime(dur1['start'], dformat)
        r1_end = datetime.datetime.strptime(dur1['end'], dformat)
        r2_start = datetime.datetime.strptime(dur2['start'], dformat)
        r2_end = datetime.datetime.strptime(dur2['end'], dformat)
        overlap = min(r1_end - r2_start, r2_end - r1_start).days + 1
        return overlap if overlap > 0 else 0
    # datetime strings
    if dur1 == dur2:
        return 1
    return 0


def isnumeric(str_value: Any) -> bool:
    """
    Simple function to check if the passed parameter can be
    converted into a numeric value or not.
    Returns boolean true if yes, false otherwise.
    """
    try:
        if type(str_value) == dict:
            return False
        float(str_value)
        return True
    except ValueError:
        # we don't treat here the exception
        # it's enough to know that it's not numeric
        return False


def eval_value(gold: Dict, test: Dict) -> Dict:
    """
    Calculate value measures for one test query annotations
    given the gold equivalent query annotations.
    Return a dictionary with a predefined template for the results.
    """
    # create measures dictionary
    value_measures = {
        "global": copy.deepcopy(val_measure_template),
        "type": copy.deepcopy(val_measure_template),
        "name": copy.deepcopy(val_measure_template),
        "bbox": copy.deepcopy(val_measure_template),
        "tempex": copy.deepcopy(val_measure_template),
        "numeric": copy.deepcopy(val_measure_template),
        "target": copy.deepcopy(val_measure_template)
    }
    # add special keys
    value_measures['global']["ratio_matching_attributes"] = 0.0
    value_measures['name']["levenstein"] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['bbox']["intersect_over_union"] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['tempex']["duration_overlap"] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['numeric']['value_offset'] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['target']['matching_element'] = {"avg": 0.0, "min": 0, "max": 0}

    gold_spans = [gspan['position'] for gspan in gold['annotations']]
    gold_types = [gspan['type'] for gspan in gold['annotations']]
    gold_ann = list(gold['annotations'])
    for ann in test['annotations']:
        test_type = ann['type']
        test_span = ann['position']
        # how many location/tempex attributes we have
        if test_type == 'location':
            value_measures['bbox']['total_matching_attributes'] += 1
        if test_type == 'tempex':
            value_measures['tempex']['total_matching_attributes'] += 1
        if test_type == 'target':
            value_measures['target']['total_matching_attributes'] += 1
        if 'name' in ann.keys():
            value_measures['name']['total_matching_attributes'] += 1
        if 'value' in ann.keys() and type(ann['value']) == str:
            #print(ann['value'])
            if isnumeric(ann['value']):
                value_measures['numeric']['total_matching_attributes'] += 1
        for gidx, gspan in enumerate(gold_spans):
            # overlapping span
            if range(max(gspan[0], test_span[0]), min(gspan[-1], test_span[-1])):
                # all attributes match
                if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                    value_measures['global']['total_matching_attributes'] += 1
                #  for matching attribute type
                if gold_types[gidx] == test_type:
                    value_measures['type']['perfect_value_match'] += 1
                    if test_type == 'location':
                        if ann['value'] == gold_ann[gidx]['value']:
                            value_measures['bbox']['perfect_value_match'] += 1
                        value_measures['bbox']["intersect_over_union"]['min'] = \
                            intersect_over_union(ann['value'], gold_ann[gidx]['value'])
                    if test_type == 'tempex':
                        if ann['value'] == gold_ann[gidx]['value']:
                            value_measures['tempex']['perfect_value_match'] += 1
                        value_measures['tempex']["duration_overlap"]['min'] = \
                            duration_overlap(ann['value'],gold_ann[gidx]['value'])
                    if test_type == 'target':
                        if ann['name'] == gold_ann[gidx]['name']:
                            value_measures['target']['perfect_value_match'] += 1
                        value_measures['target']['matching_element']['min'] = \
                            len(set(ann['name']).intersection(gold_ann[gidx]['name']))
                    if test_type != 'tempex':
                        if gold_ann[gidx]['name'] == ann['name']:
                            value_measures['name']['perfect_value_match'] += 1
                        if test_type != 'target':
                            value_measures['name']["levenstein"]['min'] = \
                                levenshtein(ann['name'].lower(), gold_ann[gidx]['name'].lower())
                    if 'value' in gold_ann[gidx].keys() and isnumeric(gold_ann[gidx]['value']) \
                            and isnumeric(ann['value']):
                        if gold_ann[gidx]['value'] == ann['value']:
                            value_measures['numeric']['perfect_value_match'] += 1
                        value_measures['numeric']['value_offset']['min'] = \
                            abs(float(ann['value']) - float(gold_ann[gidx]['value']))
    # there are as many type attribute counts, as many annotations
    value_measures['type']['total_matching_attributes'] = len(test['annotations'])
    for value_type in VALUE_TYPES:
        if value_measures[value_type]['total_matching_attributes']:
            value_measures[value_type]['perfect_value_match'] = \
                value_measures[value_type]['perfect_value_match'] \
                / value_measures[value_type]['total_matching_attributes']

    value_measures['global']['ratio_matching_attributes'] = \
        value_measures['global']['total_matching_attributes'] / len(test['annotations'])

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


def calc_global_span_scores(span_dicts: List[Dict]) -> Dict:
    """
   Calculates global span evaluation scores
   given a dictionary of individual span scores
   per annotation.
   Returns a dictionary with a predefined template.
   """
    span_measures = SpanMeasures.get_span_measures()
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


def calc_global_data_scores(data_dicts: List[Dict]) -> Dict:
    """
    Calculates global data evaluation scores
    given a dictionary of individual data scores
    per annotation.
    Returns a dictionary with a predefined template.
    """
    # a list of data dicts
    # a data dict is one 'data_measurements' dict
    data_scores = DataMeasures.get_data_measures()

    for data_type in DATA_TYPES:
        data_scores[data_type]['total_annotation'] = sum(
            [data_dict[data_type]['total_annotation'] for data_dict in data_dicts])
        data_scores[data_type]['annotation_per_query'] = avg_min_max(
            [data_dict[data_type]['total_annotation'] for data_dict in data_dicts])
        for annot_type in ANNOTATION_TYPES:
            data_scores[data_type]['total_annotation_per_type'][annot_type] = sum(
                [data_dict[data_type]['total_annotation_per_type'][annot_type] for data_dict in data_dicts])

    return data_scores


def calc_global_attr_scores(attr_dicts: List[Dict]) -> Dict:
    """
    Calculates global attribute evaluation scores
    given a dictionary of individual attribute scores
    per annotation.
    Returns a dictionary with a predefined template.
    """

    attr_scores = {
        "global": copy.deepcopy(attr_measure_template),
        "property": copy.deepcopy(attr_measure_template),
        "location": copy.deepcopy(attr_measure_template),
        "tempex": copy.deepcopy(attr_measure_template),
        "target": copy.deepcopy(attr_measure_template)
    }

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
    val_scores = {
        "global": copy.deepcopy(val_measure_template),
        "type": copy.deepcopy(val_measure_template),
        "name": copy.deepcopy(val_measure_template),
        "bbox": copy.deepcopy(val_measure_template),
        "tempex": copy.deepcopy(val_measure_template),
        "numeric": copy.deepcopy(val_measure_template),
        "target": copy.deepcopy(val_measure_template)
    }
    val_scores['global']["ratio_matching_attributes"] = 0.0

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
