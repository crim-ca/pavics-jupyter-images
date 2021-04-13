import pprint
import copy
import json
import datetime
from shapely.geometry import box, Polygon
from Levenshtein import distance

annot_types = [ "property", "location", "tempex", "target"]
# results collection JSON structure templates
data_measure_template = {"total_annotation": 0,
                         "total_annotation_per_type": {
                             "property": 0,
                             "location": 0,
                             "tempex": 0,
                             "target": 0
                         },
                         "annotation_per_query": {"avg": 0.0, "min": 0,"max": 0}
                         }
span_measure_template = {"count": 0,
                         "perfect_match": {"no_match": 0.0, "type_match": 0.0},
                         "perfect_begin": {"no_match": 0.0, "type_match": 0.0},
                         "perfect_end": {"no_match": 0.0, "type_match": 0.0},
                         "split_gold_span": {"no_match": 0, "type_match": 0},
                         "split_test_span": {"no_match": 0, "type_match": 0},
                         "overlapping_span": {
                             "no_match": {"avg": 0.0, "min": 0, "max": 0},
                             "type_match": {"avg": 0.0, "min": 0, "max": 0}
                         }}

attr_measure_template = {
        "count": 0,
        "total_span_type_match": 0,
        "per_annotation_span_perfect_match": 0.0,
        "per_annotation_overlapping_span_perfect_match": 0.0,
        "per_annotation_attribute_match": {
          "avg": 0.0,
          "min": 0,
          "max": 0
        }}
val_measure_template = {
        "total_matching_attributes": 0,
        "perfect_value_match": 0.0}

def eval_query(gold, test):
    return eval_data(gold, test), eval_span(gold, test), \
           eval_attr(gold, test), eval_val(gold, test)

def eval_data(gold, test):
    # create measures dictionary

    data_measures = {'gold_data': copy.deepcopy(data_measure_template),
                     'test_data': copy.deepcopy(data_measure_template)}

    # annotation counts
    gold_annotations = gold['annotations']
    gold_span_count = len(gold_annotations)
    data_measures['gold_data']['total_annotation'] = gold_span_count
    # for now set the min and max both equal to the count.
    # we will count averages and global values outside this function
    test_annotations = test['annotations']
    test_span_count = len(test_annotations)
    data_measures['test_data']['total_annotation'] = test_span_count

    # annotation count per type
    gold_types = [ann['type'] for ann in gold_annotations]
    gold_property_count = gold_types.count('property')
    data_measures['gold_data']['total_annotation_per_type']['property'] = gold_property_count
    gold_tempex_count = gold_types.count('tempex')
    data_measures['gold_data']['total_annotation_per_type']['tempex'] = gold_tempex_count
    gold_location_count = gold_types.count('location')
    data_measures['gold_data']['total_annotation_per_type']['location'] = gold_location_count
    gold_target_count = gold_types.count('target')
    data_measures['gold_data']['total_annotation_per_type']['target'] = gold_target_count

    test_types = [ann['type'] for ann in test_annotations]
    test_property_count = test_types.count('property')
    data_measures['test_data']['total_annotation_per_type']['property'] = test_property_count
    test_tempex_count = test_types.count('tempex')
    data_measures['test_data']['total_annotation_per_type']['tempex'] = test_tempex_count
    test_location_count = test_types.count('location')
    data_measures['test_data']['total_annotation_per_type']['location'] = test_location_count
    test_target_count = test_types.count('target')
    data_measures['test_data']['total_annotation_per_type']['target'] = test_target_count

    return data_measures

def eval_span(gold, test):
    # create measures dictionary
    span_measures = {
        "property": copy.deepcopy(span_measure_template),
        "location": copy.deepcopy(span_measure_template),
        "tempex": copy.deepcopy(span_measure_template),
        "target": copy.deepcopy(span_measure_template)
    }

    # calculate span measures
    gold_types = [ann['type'] for ann in gold['annotations']]
    gold_spans = [ann['position'] for ann in gold['annotations']]
    test_types = [ann['type'] for ann in test['annotations']]
    test_spans = [ann['position'] for ann in test['annotations']]

    # print(gold_spans)
    # print(test_spans)
    gold_begins = list(zip(*gold_spans))[0]
    gold_ends = list(zip(*gold_spans))[1]
    #TODO! if gold_spans is only length 1, the result has an empty item in the list?
    idx = 0
    for span in test_spans:
        # update count
        span_measures[test_types[idx]]['count'] += 1
        # perfect match
        if span in gold_spans:
            # exact match
            # update type-specific count
            # check for type match
            gold_idx = gold_spans.index(span) # we do not presume the test and gold are aligned
            if test_types[idx] == gold_types[gold_idx]:
                span_measures[test_types[idx]]['perfect_match']['type_match'] += 1
            else:
                span_measures[test_types[idx]]['perfect_match']['no_match'] += 1
        else:
            # not perfect match
            # check for some kind of overlap
            # overlapping spans
            overlap_count = 0
            type_match_count = 0
            gidx = 0
            for gspan in gold_spans:
                if range(max(span[0], gspan[0]), min(span[-1], gspan[-1])):
                # includes perfect end and begin
                    if test_types[idx] == gold_types[gidx]:
                        span_measures[test_types[idx]]['overlapping_span']['type_match']['min'] += 1
                        type_match_count += 1
                    else:
                        span_measures[test_types[idx]]['overlapping_span']['no_match']['min'] += 1
                    # perfect begin
                    if span[0] == gold_spans[gidx][0]:
                        # begin match (including exact match)
                        # update type-specific count
                        if test_types[idx] == gold_types[gidx]:
                            span_measures[test_types[idx]]['perfect_begin']['type_match'] += 1
                        else:
                            span_measures[test_types[idx]]['perfect_begin']['no_match'] += 1
                    # perfect end
                    if span[1] == gold_spans[gidx][1]:
                        # end match (including exact match)
                        # update type-specific count
                        if test_types[idx] == gold_types[gidx]:
                            span_measures[test_types[idx]]['perfect_end']['type_match'] += 1
                        else:
                            span_measures[test_types[idx]]['perfect_end']['no_match'] += 1
                    overlap_count += 1
                if overlap_count > 1:
                    # this test span matches several gold spans = split-test
                    if overlap_count == type_match_count:
                        span_measures[test_types[idx]]['split_test_span']['type_match'] += 1
                    else:
                        span_measures[test_types[idx]]['split_test_span']['no_match'] += 1
                gidx += 1

        idx += 1

    # split gold
    idx = 0
    for gspan in gold_spans:
        split_count = 0
        type_match_count = 0
        for tspan in test_spans:
            if range(max(gspan[0], tspan[0]), min(gspan[-1], tspan[-1])):
                split_count += 1
                if gold_types[idx] == test_types[test_spans.index(tspan)]:
                    type_match_count += 1

        if split_count > 1:
            # we have split gold span
            if split_count == type_match_count:
                span_measures[gold_types[idx]]['split_gold_span']['type_match'] += 1
            else:
                span_measures[gold_types[idx]]['split_gold_span']['no_match'] += 1
        idx += 1
    return span_measures

def eval_attr(gold, test):
    # create measures dictionary
    attribute_measures = {
        "property": copy.deepcopy(attr_measure_template),
        "location": copy.deepcopy(attr_measure_template),
        "tempex": copy.deepcopy(attr_measure_template),
        "target": copy.deepcopy(attr_measure_template)
    }
    gold_spans = [gspan['position'] for gspan in gold['annotations']]
    gold_types = [gspan['type'] for gspan in gold['annotations']]
    gold_ann = [gspan for gspan in gold['annotations']]
    # count of annotations per types
    nr_prop = len([x for x in test['annotations'] if x['type'] == "property"])
    nr_loc = len([x for x in test['annotations'] if x['type'] == "location"])
    nr_temp = len([x for x in test['annotations'] if x['type'] == "tempex"])
    nr_targ = len([x for x in test['annotations'] if x['type'] == "target"])

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
            # per_annotation_span_perfect_match
            # % of annotation having all attribute matched when span is same
            if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                attribute_measures[test_type]['per_annotation_span_perfect_match'] += 1
        else:
            for gspan in gold_spans:
                # overlapping span
                if range(max(gspan[0], test_span[0]), min(gspan[-1], test_span[-1])):
                    gidx = gold_spans.index(gspan)
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
                        (1.0 * len(set(ann.keys()).intersection(gold_ann[gidx].keys()))) / len(ann)

    # count of annotations of all attributes matched for exact span / nr of annots of that type
    attribute_measures['property']['per_annotation_span_perfect_match'] = (1 * attribute_measures['property'][
        'per_annotation_span_perfect_match']) / nr_prop if nr_prop else 0
    attribute_measures['location']['per_annotation_span_perfect_match'] = (1 * attribute_measures['location'][
        'per_annotation_span_perfect_match']) / nr_loc if nr_loc else 0
    attribute_measures['tempex']['per_annotation_span_perfect_match'] = (1 * attribute_measures['tempex'][
        'per_annotation_span_perfect_match']) / nr_temp if nr_temp else 0
    attribute_measures['target']['per_annotation_span_perfect_match'] = (1 * attribute_measures['target'][
        'per_annotation_span_perfect_match']) / nr_targ if nr_targ else 0

    #per_annotation_overlapping_span_perfect_match
    attribute_measures['property']['per_annotation_overlapping_span_perfect_match'] = (1 * attribute_measures['property'][
        'per_annotation_overlapping_span_perfect_match']) / nr_prop if nr_prop else 0
    attribute_measures['location']['per_annotation_overlapping_span_perfect_match'] = (1 * attribute_measures['location'][
        'per_annotation_overlapping_span_perfect_match']) / nr_loc if nr_loc else 0
    attribute_measures['tempex']['per_annotation_overlapping_span_perfect_match'] = (1 * attribute_measures['tempex'][
        'per_annotation_overlapping_span_perfect_match']) / nr_temp if nr_temp else 0
    attribute_measures['target']['per_annotation_overlapping_span_perfect_match'] = (1 * attribute_measures['target'][
        'per_annotation_overlapping_span_perfect_match']) / nr_targ if nr_targ else 0

    # print("Attribute measures: ")
    # pprint.pprint(attribute_measures)
    return attribute_measures

def levenshtein(str1, str2):
    return distance(str1, str2)

def intersect_union(bbox1, bbox2):
    # polygons require min 3 coordinate tuples
    if len(bbox1['coordinates']) > 2 and len(bbox2['coordinates']) > 2:
        poly1 = Polygon(bbox1['coordinates'])
        poly2 = Polygon(bbox2['coordinates'])
        polygon_intersection = poly1.intersection(poly2).area
        polygon_union = poly1.union(poly2).area
        iou = polygon_intersection / polygon_union
        return iou
    # how to calculate for points?
    if bbox1['type']=="Point" and bbox2['type']=="Point":
        if bbox1['coordinates']==bbox2['coordinates']:
            return 1
    return 0

def duration_overlap(dur1, dur2):
    format = '%Y-%m-%dT%H:%M:%SZ'
    # datarange
    if len(dur1) == 2 and len(dur2) == 2:
        r1_start = datetime.datetime.strptime(dur1['start'], format)
        r1_end = datetime.datetime.strptime(dur1['end'], format)
        r2_start = datetime.datetime.strptime(dur2['start'], format)
        r2_end = datetime.datetime.strptime(dur2['end'], format)
        overlap = min(r1_end - r2_start, r2_end - r1_start).days + 1
        return overlap
    # datetime
    if dur1 == dur2:
        return 1
    return 0

def isnumeric(str_value):
    try:
        float(str_value)
        return True
    except:
        return False

def eval_val(gold, test):
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
    gold_ann = [gspan for gspan in gold['annotations']]
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
        if 'value' in ann.keys() and isnumeric(ann['value']):
            value_measures['numeric']['total_matching_attributes'] += 1
        for gspan in gold_spans:
            # overlapping span
            if range(max(gspan[0], test_span[0]), min(gspan[-1], test_span[-1])):
                gidx = gold_spans.index(gspan)
                # all attributes match
                if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                    value_measures['global']['total_matching_attributes'] += 1
                #  for matching attribute type
                if gold_types[gidx] == test_type:
                    value_measures['type']['perfect_value_match'] += 1
                    if test_type == 'location':
                        if ann['value'] == gold_ann[gidx]['value']:
                            value_measures['bbox']['perfect_value_match'] += 1
                        value_measures['bbox']["intersect_over_union"]['min'] = intersect_union(ann['value'],
                                                                                                gold_ann[gidx]['value'])
                    if test_type == 'tempex':
                        if ann['value'] == gold_ann[gidx]['value']:
                            value_measures['tempex']['perfect_value_match'] += 1
                        value_measures['tempex']["duration_overlap"]['min'] = duration_overlap(ann['value'],
                                                                                               gold_ann[gidx]['value'])
                    if test_type == 'target':
                        if ann['name'] == gold_ann[gidx]['name']:
                            value_measures['target']['perfect_value_match'] += 1
                        value_measures['target']['matching_element']['min'] = len(set(ann['name']).
                                                                                  intersection(gold_ann[gidx]['name']))
                    if test_type != 'tempex':
                        if gold_ann[gidx]['name'] == ann['name']:
                            value_measures['name']['perfect_value_match'] += 1
                        if test_type != 'target': #TODO implement Levenshtein for target list of var names
                            value_measures['name']["levenstein"]['min'] = levenshtein(ann['name'].lower(),
                                                                                  gold_ann[gidx]['name'].lower())
                    if 'value' in gold_ann[gidx].keys() and isnumeric(gold_ann[gidx]['value']) \
                            and isnumeric(ann['value']):
                        if gold_ann[gidx]['value'] == ann['value']:
                            value_measures['numeric']['perfect_value_match'] += 1
                        value_measures['numeric']['value_offset']['min'] = abs(float(ann['value']) -
                                                                               float(gold_ann[gidx]['value']))

    value_measures['type']['total_matching_attributes'] = len(ann) # there are as many type attribute counts, as many annotations
    value_measures['type']['perfect_value_match'] = (1.0 * value_measures['type']['perfect_value_match'])\
                                                    / len(ann)
    value_measures['name']['perfect_value_match'] = (1.0 * value_measures['name']['perfect_value_match'])\
                                                    / len(ann)
    if value_measures['bbox']['total_matching_attributes']:
        value_measures['bbox']['perfect_value_match'] = (1.0 * value_measures['bbox']['perfect_value_match'])\
                                                    / value_measures['bbox']['total_matching_attributes']
    if value_measures['tempex']['total_matching_attributes']:
        value_measures['tempex']['perfect_value_match'] = (1.0 * value_measures['tempex']['perfect_value_match']) \
                                                    / value_measures['tempex']['total_matching_attributes']
    if value_measures['numeric']['total_matching_attributes']:
        value_measures['numeric']['perfect_value_match'] = (1.0 * value_measures['numeric']['perfect_value_match']) \
                                                      / value_measures['numeric']['total_matching_attributes']
    if value_measures['target']['total_matching_attributes']:
        value_measures['target']['perfect_value_match'] = (1.0 * value_measures['target']['perfect_value_match']) \
                                                    / value_measures['target']['total_matching_attributes']
    if value_measures['global']['total_matching_attributes']:
        value_measures['global']['perfect_value_match'] = (1.0 * value_measures['global']['perfect_value_match'])\
                                                       / value_measures['global']['total_matching_attributes']

    value_measures['global']['ratio_matching_attributes'] = (1.0 *
                                                             value_measures['global']['total_matching_attributes']) \
                                                            / len(test['annotations'])
    # print("Value measures: ")
    # pprint.pprint(value_measures)
    return value_measures

"""
>>>>>>> Stashed changes
def calc_score(score_type, test_annotations, test_span_count,
               test_property_count, test_tempex_count,
               test_location_count, test_target_count,
               gold_annotations, golden_spans, golden_types):
    span_p_strict = 0
    span_p_relaxed = 0
    # per types
    type_p = 0
    property_p = 0
    prop_name_p = 0
    prop_val_p = 0
    tempex_p = 0
    tempex_type_p = 0
    tempex_val_p = 0
    location_p = 0
    location_name_p = 0
    location_val_p = 0
    target_p = 0
    target_name_p = 0

    print("#################  " + score_type + "  #################")
    for annot in test_annotations:
        # span
        test_span = annot['text']
        # type
        test_type = annot['type']
        test_val = annot['value']
        type_match = False
        # strict span match
        if test_span in golden_spans:
            span_p_strict += 1
            #print("Strict span match: ", test_span)
            # type
            idx = golden_spans.index(test_span)
            if test_type == golden_types[idx]:
                type_match = True
        else:  # partial span match
            idx = 0
            for text in golden_spans:
                # relaxed match criteria: at least length 3
                test_pos = annot['position']
                gold_pos = gold_annotations[idx]['position']
                overlap = range(max(test_pos[0], gold_pos[0]), min(test_pos[-1], gold_pos[-1]) + 1)
                if overlap:
                    span_p_relaxed += 1
                    #print("Relaxed span match: ", test_span, text)
                    # type
                    if test_type == golden_types[idx]:
                        type_match = True
                        #print("Type match:", test_type)
                    break  # only take first relaxed match
                idx += 1
        # idx still holds the right index of match
        if type_match:
            type_p += 1
            if test_type == "property":
                property_p += 1
                # name
                if annot['name'] == gold_annotations[idx]['name']:
                    prop_name_p += 1
                # value
                if test_val == gold_annotations[idx]['value']:
                    prop_val_p += 1
            elif test_type == "tempex":
                tempex_p += 1
                # tempex_type
                if annot['tempex_type'] == gold_annotations[idx]['tempex_type']:
                    tempex_type_p += 1
                # value
                if test_val == gold_annotations[idx]['value']:
                    tempex_val_p += 1
            elif test_type == "location":
                location_p += 1
                # name
                if annot['name'] == gold_annotations[idx]['name']:
                    location_name_p += 1
                # value
                if test_val == gold_annotations[idx]['value']:
                    location_val_p += 1
            elif test_type == "target":
                target_p += 1
                # name
                if annot['name'] == gold_annotations[idx]['name']:
                    target_name_p += 1


    span_p_strict = span_p_strict * 1.0 / test_span_count
    # relaxed precision = strict matches + relaxed matches
    span_p_relaxed = (span_p_relaxed * 1.0 / test_span_count) + span_p_strict
    print("Span strict {0}: {1}".format(score_type, span_p_strict))
    print("Span relaxed {0}: {1}".format(score_type, span_p_relaxed))

    type_p = type_p * 1.0 / test_span_count
    print("Type {0}: {1}".format(score_type, type_p))
    # per type
    if test_property_count != 0:
        property_p = property_p * 1.0 / test_property_count
        prop_name_p = prop_name_p * 1.0 / test_property_count
        prop_val_p = prop_val_p * 1.0 / test_property_count
    if test_location_count != 0:
        location_p = location_p * 1.0 / test_location_count
        location_name_p = location_name_p * 1.0 / test_location_count
        location_val_p = location_val_p * 1.0 / test_location_count
    if test_tempex_count != 0:
        tempex_p = tempex_p * 1.0 / test_tempex_count
        tempex_type_p = tempex_type_p * 1.0 / test_tempex_count
        tempex_val_p = tempex_val_p * 1.0 / test_tempex_count
    if test_target_count != 0:
        target_p = target_p * 1.0 / test_target_count
        target_name_p = target_name_p * 1.0 / test_target_count

    print("Property type {0}: {1}".format(score_type, property_p))
    print("Property name {0}: {1}".format(score_type, prop_name_p))
    print("Property value {0}: {1}".format(score_type, prop_val_p))
    print("Location type {0}: {1}".format(score_type, location_p))
    print("Location name {0}: {1}".format(score_type, location_name_p))
    print("Location value {0}: {1}".format(score_type, location_val_p))
    print("Tempex type {0}: {1}".format(score_type, tempex_p))
    print("Tempex_type {0}: {1}".format(score_type, tempex_type_p))
    print("Tempex value {0}: {1}".format(score_type, tempex_val_p))
    print("Target {0}: {1}".format(score_type, target_p))
    print("Target name {0}: {1}".format(score_type, target_name_p))
<<<<<<< Updated upstream


def eval_queries(test_queries, gold_queries):
    global_span_p_strict = 0
    i = 0
    for test_query in test_queries:
        eval_query(test_query, gold_queries[i])
        i += 1



with open("gold_queries.json") as f:
    gold_file = json.load(f)
with open("noisy_gold_queries.json") as f:
    noisy_file = json.load(f)

idx = 1
test_q = noisy_file['noisy_queries'][idx]
gold_q = gold_file['golden_queries'][idx]
eval_query(test_q, gold_q)
=======
"""

def avg_min_max(data_list):
    return {'avg': (1.0 * sum(data_list)/len(data_list)), 'min': min(data_list), 'max': max(data_list)}

def calc_global_span_scores(span_dicts):

    span_measures = {
        "global": copy.deepcopy(span_measure_template),
        "property": copy.deepcopy(span_measure_template),
        "location": copy.deepcopy(span_measure_template),
        "tempex": copy.deepcopy(span_measure_template),
        "target": copy.deepcopy(span_measure_template)
    }

    count = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    begin = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    begin_m = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    exact = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    exact_t = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    overlap = {'property': [], 'location': [], 'tempex': [], 'target': []}
    overlap_t = {'property': [], 'location': [], 'tempex': [], 'target': []}
    end = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    end_m = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    split_t = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    split_t_m = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    split_g = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    split_g_m = {'property': 0, 'location': 0, 'tempex': 0, 'target': 0}
    # count global measures
    for span_dict in span_dicts:
        for key in annot_types:
            # total span counts per type
            count[key] += span_dict[key]['count']
            # add up first
            begin[key] += span_dict[key]['perfect_begin']['no_match']
            begin_m[key] += span_dict[key]['perfect_begin']['type_match']
            end[key] += span_dict[key]['perfect_end']['no_match']
            end_m[key] += span_dict[key]['perfect_end']['type_match']
            exact[key] += span_dict[key]['perfect_match']['no_match']
            exact_t[key] += span_dict[key]['perfect_match']['type_match']
            overlap[key].append(span_dict[key]['overlapping_span']['no_match']['min'])
            overlap_t[key].append(span_dict[key]['overlapping_span']['type_match']['min'])
            split_g[key] += span_dict[key]['split_gold_span']['no_match']
            split_g_m[key] += span_dict[key]['split_gold_span']['type_match']
            split_t[key] += span_dict[key]['split_test_span']['no_match']
            split_t_m[key] += span_dict[key]['split_test_span']['type_match']

    global_count = 0
    for key in annot_types:
        global_count += count[key]
        span_measures[key]['count'] = count[key]
        span_measures[key]['overlapping_span']['no_match'] = avg_min_max(overlap[key])
        span_measures[key]['overlapping_span']['type_match'] = avg_min_max(overlap_t[key])
        span_measures[key]['perfect_begin']['no_match'] = (1.0 * begin[key]) / count[key]
        span_measures[key]['perfect_begin']['type_match'] = (1.0 * begin_m[key]) / count[key]
        span_measures[key]['perfect_end']['no_match'] = (1.0 * end[key]) / count[key]
        span_measures[key]['perfect_end']['type_match'] = (1.0 * end_m[key]) / count[key]
        span_measures[key]['perfect_match']['type_match'] = (1.0 * exact_t[key]) / count[key]
        span_measures[key]['perfect_match']['no_match'] = (1.0 * exact[key]) / count[key]
        span_measures[key]['split_gold_span']['no_match'] = (1.0 * split_g[key]) / count[key]
        span_measures[key]['split_gold_span']['type_match'] = (1.0 * split_g_m[key]) / count[key]
        span_measures[key]['split_test_span']['no_match'] = (1.0 * split_t[key]) / count[key]
        span_measures[key]['split_test_span']['type_match'] = (1.0 * split_t_m[key]) / count[key]

    span_measures['global']['count'] = global_count

    # calculate percentage of test
    span_measures['global']['overlapping_span']['no_match'] = avg_min_max(sum(overlap.values(), []))
    span_measures['global']['overlapping_span']['type_match'] = avg_min_max(sum(overlap_t.values(), []))

    span_measures['global']['perfect_begin']['no_match'] = (1.0 * sum(begin.values())) / global_count
    span_measures['global']['perfect_begin']['type_match'] = (1.0 * sum(begin_m.values())) / global_count

    span_measures['global']['perfect_end']['no_match'] = (1.0 * sum(end.values())) / global_count
    span_measures['global']['perfect_end']['type_match'] = (1.0 * sum(end_m.values())) / global_count

    span_measures['global']['split_gold_span']['no_match'] = (1.0 * sum(split_g.values())) / global_count
    span_measures['global']['split_gold_span']['type_match'] = (1.0 * sum(split_g_m.values())) / global_count

    span_measures['global']['split_test_span']['no_match'] = (1.0 * sum(split_t.values())) / global_count
    span_measures['global']['split_test_span']['type_match'] = (1.0 * sum(split_t_m.values())) / global_count

    return span_measures

def calc_global_data_scores(data_dicts):
    #a list of data dicts
    # a data dict is one 'data_measurements' dict
    data_scores = {
      "gold_data": copy.deepcopy(data_measure_template),
      "test_data": copy.deepcopy(data_measure_template)
    }
    gold_total_annot = 0
    test_total_annot = 0
    gold_total_prop = 0
    gold_total_loc = 0
    gold_total_temp = 0
    gold_total_targ = 0
    test_total_prop = 0
    test_total_loc = 0
    test_total_temp = 0
    test_total_targ = 0
    gold_annot_counts = []
    test_annot_counts = []
    for data_dict in data_dicts:
        gold_total_annot += data_dict['gold_data']['total_annotation']
        test_total_annot += data_dict['test_data']['total_annotation']
        gold_total_prop += data_dict['gold_data']['total_annotation_per_type']['property']
        gold_total_temp += data_dict['gold_data']['total_annotation_per_type']['tempex']
        gold_total_loc += data_dict['gold_data']['total_annotation_per_type']['location']
        gold_total_targ += data_dict['gold_data']['total_annotation_per_type']['target']
        test_total_prop += data_dict['test_data']['total_annotation_per_type']['property']
        test_total_temp += data_dict['test_data']['total_annotation_per_type']['tempex']
        test_total_loc += data_dict['test_data']['total_annotation_per_type']['location']
        test_total_targ += data_dict['test_data']['total_annotation_per_type']['target']
        gold_annot_counts.append(data_dict['gold_data']['total_annotation'])
        test_annot_counts.append(data_dict['test_data']['total_annotation'])


    data_scores['gold_data']['total_annotation'] = gold_total_annot
    data_scores['test_data']['total_annotation'] = test_total_annot
    data_scores['gold_data']['total_annotation_per_type']['property'] = gold_total_prop
    data_scores['gold_data']['total_annotation_per_type']['tempex'] = gold_total_temp
    data_scores['gold_data']['total_annotation_per_type']['location'] = gold_total_loc
    data_scores['gold_data']['total_annotation_per_type']['target'] = gold_total_targ
    data_scores['test_data']['total_annotation_per_type']['property'] = test_total_prop
    data_scores['test_data']['total_annotation_per_type']['tempex'] = test_total_temp
    data_scores['test_data']['total_annotation_per_type']['location'] = test_total_loc
    data_scores['test_data']['total_annotation_per_type']['target'] = test_total_targ
    data_scores['gold_data']['annotation_per_query'] = avg_min_max(gold_annot_counts)
    data_scores['test_data']['annotation_per_query'] = avg_min_max(test_annot_counts)
    return data_scores

def calc_global_attr_scores(attr_dicts):

    attr_scores = {
        "global": copy.deepcopy(attr_measure_template),
        "property": copy.deepcopy(attr_measure_template),
        "location": copy.deepcopy(attr_measure_template),
        "tempex": copy.deepcopy(attr_measure_template),
        "target": copy.deepcopy(attr_measure_template)
    }
    per_annot_match = {'property': [], 'location': [], 'tempex': [], 'target': []}

    for attr_dict in attr_dicts:
        for key in attr_dict.keys(): # annotation type
            attr_scores[key]["count"] += attr_dict[key]['count']
            attr_scores[key]["total_span_type_match"] += attr_dict[key]["total_span_type_match"]
            attr_scores[key]["per_annotation_span_perfect_match"] += attr_dict[key]["per_annotation_span_perfect_match"]
            attr_scores[key]["per_annotation_overlapping_span_perfect_match"] += attr_dict[key]["per_annotation_overlapping_span_perfect_match"]
            per_annot_match[key].append(attr_dict[key]["per_annotation_attribute_match"]['min'])


    # global values
    for key in annot_types:
        attr_scores['global']["count"] += attr_scores[key]["count"]
        attr_scores['global']["total_span_type_match"] += attr_scores[key]["total_span_type_match"]
        attr_scores['global']["per_annotation_span_perfect_match"] += attr_scores[key]["per_annotation_span_perfect_match"]
        attr_scores['global']["per_annotation_overlapping_span_perfect_match"] += attr_scores[key]["per_annotation_overlapping_span_perfect_match"]
        attr_scores[key]["per_annotation_attribute_match"] = avg_min_max(per_annot_match[key])
        attr_scores[key]["per_annotation_span_perfect_match"] = (1.0 * attr_scores[key]["per_annotation_span_perfect_match"]) / len(attr_dicts)
        attr_scores[key]["per_annotation_overlapping_span_perfect_match"] = (1.0 * attr_scores[key][
            "per_annotation_overlapping_span_perfect_match"]) / len(attr_dicts)

    # add all per type values into a flat list
    per_annot_matches = []
    for l in per_annot_match.values():
        per_annot_matches += l
    attr_scores['global']["per_annotation_attribute_match"] = avg_min_max(per_annot_matches)
    return attr_scores

def calc_global_val_scores(val_dicts):

    val_scores = {
        "global": copy.deepcopy(val_measure_template),
        "type": copy.deepcopy(val_measure_template),
        "name": copy.deepcopy(val_measure_template),
        "bbox": copy.deepcopy(val_measure_template),
        "tempex": copy.deepcopy(val_measure_template),
        "numeric": copy.deepcopy(val_measure_template),
        "target": copy.deepcopy(val_measure_template)
    }
    templ = {"global": [], "type": [], "name": [], "bbox": [], "tempex": [], "numeric": [], "target": []}
    val_scores['global']["ratio_matching_attributes"] = 0.0

    for val_dict in val_dicts:
        for key in val_dict.keys(): # annotation type
            val_scores[key]['total_matching_attributes'] += val_dict[key]['total_matching_attributes']
            val_scores[key]['perfect_value_match'] += val_dict[key]['perfect_value_match']
        val_scores['global']["ratio_matching_attributes"] += val_dict['global']["ratio_matching_attributes"]
        templ['name'].append(val_dict['name']["levenstein"]['min'])
        templ['bbox'].append(val_dict['bbox']["intersect_over_union"]['min'])
        templ['tempex'].append(val_dict['tempex']["duration_overlap"]['min'])
        templ['numeric'].append(val_dict['numeric']['value_offset']['min'])
        templ['target'].append(val_dict['target']['matching_element']['min'])

    # global values
    for key in templ.keys():
        val_scores[key]['perfect_value_match'] = val_scores[key]['perfect_value_match'] / len(val_dicts)

    val_scores['global']["ratio_matching_attributes"] = val_scores['global']["ratio_matching_attributes"] / len(val_dicts)
    val_scores['name']["levenstein"] = avg_min_max(templ['name'])
    val_scores['bbox']["intersect_over_union"] = avg_min_max(templ['bbox'])
    val_scores['tempex']["duration_overlap"] = avg_min_max(templ['tempex'])
    val_scores['numeric']['value_offset'] = avg_min_max(templ['numeric'])
    val_scores['target']['matching_element'] = avg_min_max(templ['target'])

    return val_scores

def global_stats(gold_path, test_path, out_path):

    # open and copy the template file
    with open("global_stats.json") as tf:
        template_file = json.load(tf)
    template = template_file

    # open the two files
    with open(gold_path) as f:
        gold_file = json.load(f)
    with open(test_path) as f:
        test_file = json.load(f)

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
    nr_queries = len(gold_qs)

    # each query file consists of a list of {query: {}, annotations: {}} dicts
    gold_queries, _ = list(zip(*gold_qs))
    test_queries, _ = list(zip(*test_qs))
    for query in gold_queries:
        if query not in test_queries:
            print("Error: Query not found! ", query)
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
    print("Global data measures:")
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




global_stats("gold_queries.json", "noisy_gold_queries.json", "out.json")

