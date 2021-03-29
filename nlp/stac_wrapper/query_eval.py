import pprint
import copy

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
        "ratio_matching_attributes": 0.0,
        "perfect_value_match": 0.0,}

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

    print(gold_spans)
    print(test_spans)
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

    for ann in test['annotations']:
        # count how many attributes in test
        # obligatory for property, tempex, location: type, position, name, value
        # obligatory for target: type, position, name
        test_type = ann['type']
        attribute_measures[test_type]['count'] += len(ann)
        test_span = ann['position']
        if test_span in gold_spans:
            idx = gold_spans.index(test_span)
            # total_span_type_match
            # nr of attributes where matching span+type
            if test_type == gold_types[idx]:
                attribute_measures[test_type]['total_span_type_match'] += len(ann)
            # per_annotation_span_perfect_match
            # % of annotation having all attribute matched when span is same
            attribute_measures[test_type]['per_annotation_span_perfect_match'] = \
                (1.0 * len(set(ann.keys()).intersection(gold_ann[idx].keys()))) / len(ann)
    # per_annotation_overlapping_span_perfect_match
    # % of annotation having all attribute matched, for overlapping span
        else:
            for gspan in gold_spans:
                if range(max(gspan[0], test_span[0]), min(gspan[-1], test_span[-1])):
                    gidx = gold_spans.index(gspan)
                    attribute_measures[test_type]['per_annotation_overlapping_span_perfect_match'] = \
                        (1.0 * len(set(ann.keys()).intersection(gold_ann[gidx].keys()))) / len(ann)
    # per_annotation_attribute_match
    # % of matching attribute name / total number of attribute in an annotation
    # compared to what? gidx = ?
    attribute_measures[test_type]['per_annotation_attribute_match'] = \
        (1.0 * len(set(ann.keys()).intersection(gold_ann[gidx].keys()))) / len(ann)

    print("Attribute measures: ")
    pprint.pprint(attribute_measures)
    return attribute_measures

def eval_val(gold, test):
    # create measures dictionary
    value_measures = {
        "type": copy.deepcopy(val_measure_template),
        "name": copy.deepcopy(val_measure_template),
        "bbox": copy.deepcopy(val_measure_template),
        "tempex": copy.deepcopy(val_measure_template),
        "numeric": copy.deepcopy(val_measure_template),
        "target": copy.deepcopy(val_measure_template)
    }
    # add special keys
    value_measures['type']["perfect_type_match"] = 0.0
    value_measures['name']["levenstein"] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['bbox']["intersect_over_union"] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['tempex']["duration_overlap"] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['numeric']['value_offset'] = {"avg": 0.0, "min": 0, "max": 0}
    value_measures['target']['matching_element'] = {"avg": 0.0, "min": 0, "max": 0}


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
    return 1.0 * sum(data_list)/len(data_list), min(data_list), max(data_list)

def calc_global_span_scores(span_dicts):

    span_measures = {
        "global": copy.deepcopy(span_measure_template),
        "property": copy.deepcopy(span_measure_template),
        "location": copy.deepcopy(span_measure_template),
        "tempex": copy.deepcopy(span_measure_template),
        "target": copy.deepcopy(span_measure_template)
    }

    count_prop, count_loc, count_temp, count_targ = 0, 0, 0, 0
    begin_prop, begin_loc, begin_temp, begin_targ = 0, 0, 0, 0
    begin_prop_m, begin_loc_m, begin_temp_m, begin_targ_m = 0, 0, 0, 0
    exact_prop, exact_loc, exact_temp, exact_targ = 0, 0, 0, 0
    exact_prop_t, exact_loc_t, exact_temp_t, exact_targ_t = 0, 0, 0, 0
    overlap_prop, overlap_loc, overlap_temp, overlap_targ = [], [], [], []
    overlap_prop_t, overlap_loc_t, overlap_temp_t, overlap_targ_t = [], [], [], []
    end_prop, end_loc, end_temp, end_targ = 0, 0, 0, 0
    end_prop_m, end_loc_m, end_temp_m, end_targ_m = 0, 0, 0, 0
    split_t_prop, split_t_loc, split_t_temp, split_t_targ = 0, 0, 0, 0
    split_t_prop_m, split_t_loc_m, split_t_temp_m, split_t_targ_m = 0, 0, 0, 0
    split_g_prop, split_g_loc, split_g_temp, split_g_targ = 0, 0, 0, 0
    split_g_prop_m, split_g_loc_m, split_g_temp_m, split_g_targ_m = 0, 0, 0, 0
    # count global measures
    for span_dict in span_dicts:
        # total span counts per type
        count_prop += span_dict['property']['count']
        count_loc += span_dict['location']['count']
        count_temp += span_dict['tempex']['count']
        count_targ += span_dict['target']['count']
        # add up first
        begin_prop += span_dict['property']['perfect_begin']['no_match']
        begin_prop_m += span_dict['property']['perfect_begin']['type_match']
        begin_loc += span_dict['location']['perfect_begin']['no_match']
        begin_loc_m += span_dict['location']['perfect_begin']['type_match']
        begin_temp += span_dict['tempex']['perfect_begin']['no_match']
        begin_temp_m += span_dict['tempex']['perfect_begin']['type_match']
        begin_targ += span_dict['target']['perfect_begin']['no_match']
        begin_targ_m += span_dict['target']['perfect_begin']['type_match']

        end_prop += span_dict['property']['perfect_end']['no_match']
        end_prop_m += span_dict['property']['perfect_end']['type_match']
        end_loc += span_dict['location']['perfect_end']['no_match']
        end_loc_m += span_dict['location']['perfect_end']['type_match']
        end_temp += span_dict['tempex']['perfect_end']['no_match']
        end_temp_m += span_dict['tempex']['perfect_end']['type_match']
        end_targ += span_dict['target']['perfect_end']['no_match']
        end_targ_m += span_dict['target']['perfect_end']['type_match']

        exact_prop += span_dict['property']['perfect_match']['no_match']
        exact_prop_t += span_dict['property']['perfect_match']['type_match']
        exact_loc += span_dict['location']['perfect_match']['no_match']
        exact_loc_t += span_dict['location']['perfect_match']['type_match']
        exact_temp += span_dict['tempex']['perfect_match']['no_match']
        exact_temp_t += span_dict['tempex']['perfect_match']['type_match']
        exact_targ += span_dict['target']['perfect_match']['no_match']
        exact_targ_t += span_dict['target']['perfect_match']['type_match']

        overlap_prop.append(span_dict['property']['overlapping_span']['no_match']['min'])
        overlap_prop_t.append(span_dict['property']['overlapping_span']['type_match']['min'])
        overlap_loc.append(span_dict['location']['overlapping_span']['no_match']['min'])
        overlap_loc_t.append(span_dict['location']['overlapping_span']['type_match']['min'])
        overlap_temp.append(span_dict['tempex']['overlapping_span']['no_match']['min'])
        overlap_temp_t.append(span_dict['tempex']['overlapping_span']['type_match']['min'])
        overlap_targ.append(span_dict['target']['overlapping_span']['no_match']['min'])
        overlap_targ_t.append(span_dict['target']['overlapping_span']['type_match']['min'])

        split_g_prop += span_dict['property']['split_gold_span']['no_match']
        split_g_prop_m += span_dict['property']['split_gold_span']['type_match']
        split_g_loc += span_dict['location']['split_gold_span']['no_match']
        split_g_loc_m += span_dict['location']['split_gold_span']['type_match']
        split_g_temp += span_dict['tempex']['split_gold_span']['no_match']
        split_g_temp_m += span_dict['tempex']['split_gold_span']['type_match']
        split_g_targ += span_dict['target']['split_gold_span']['no_match']
        split_g_targ_m += span_dict['target']['split_gold_span']['type_match']

        split_t_prop += span_dict['property']['split_test_span']['no_match']
        split_t_prop_m += span_dict['property']['split_test_span']['type_match']
        split_t_loc += span_dict['location']['split_test_span']['no_match']
        split_t_loc_m += span_dict['location']['split_test_span']['type_match']
        split_t_temp += span_dict['tempex']['split_test_span']['no_match']
        split_t_temp_m += span_dict['tempex']['split_test_span']['type_match']
        split_t_targ += span_dict['target']['split_test_span']['no_match']
        split_t_targ_m += span_dict['target']['split_test_span']['type_match']


    global_count = count_prop + count_loc + count_temp + count_targ
    span_measures['global']['count'] = global_count
    span_measures['property']['count'] = count_prop
    span_measures['location']['count'] = count_loc
    span_measures['tempex']['count'] = count_temp
    span_measures['target']['count'] = count_targ

    # calculate percentage of test
    avg, min, max = avg_min_max(overlap_prop + overlap_loc + overlap_temp + overlap_targ)
    span_measures['global']['overlapping_span']['no_match']['avg'] = avg
    span_measures['global']['overlapping_span']['no_match']['min'] = min
    span_measures['global']['overlapping_span']['no_match']['max'] = max
    avg, min, max = avg_min_max(overlap_prop_t + overlap_loc_t + overlap_temp_t + overlap_targ_t)
    span_measures['global']['overlapping_span']['type_match']['avg'] = avg
    span_measures['global']['overlapping_span']['type_match']['min'] = min
    span_measures['global']['overlapping_span']['type_match']['max'] = max
    avg, min, max = avg_min_max(overlap_prop)
    span_measures['property']['overlapping_span']['no_match']['avg'] = avg
    span_measures['property']['overlapping_span']['no_match']['min'] = min
    span_measures['property']['overlapping_span']['no_match']['max'] = max
    avg, min, max = avg_min_max(overlap_prop_t)
    span_measures['property']['overlapping_span']['type_match']['avg'] = avg
    span_measures['property']['overlapping_span']['type_match']['min'] = min
    span_measures['property']['overlapping_span']['type_match']['max'] = max
    avg, min, max = avg_min_max(overlap_loc)
    span_measures['location']['overlapping_span']['no_match']['avg'] = avg
    span_measures['location']['overlapping_span']['no_match']['min'] = min
    span_measures['location']['overlapping_span']['no_match']['max'] = max
    avg, min, max = avg_min_max(overlap_loc_t)
    span_measures['location']['overlapping_span']['type_match']['avg'] = avg
    span_measures['location']['overlapping_span']['type_match']['min'] = min
    span_measures['location']['overlapping_span']['type_match']['max'] = max
    avg, min, max = avg_min_max(overlap_temp)
    span_measures['tempex']['overlapping_span']['no_match']['avg'] = avg
    span_measures['tempex']['overlapping_span']['no_match']['min'] = min
    span_measures['tempex']['overlapping_span']['no_match']['max'] = max
    avg, min, max = avg_min_max(overlap_temp_t)
    span_measures['tempex']['overlapping_span']['type_match']['avg'] = avg
    span_measures['tempex']['overlapping_span']['type_match']['min'] = min
    span_measures['tempex']['overlapping_span']['type_match']['max'] = max
    avg, min, max = avg_min_max(overlap_targ)
    span_measures['target']['overlapping_span']['no_match']['avg'] = avg
    span_measures['target']['overlapping_span']['no_match']['min'] = min
    span_measures['target']['overlapping_span']['no_match']['max'] = max
    avg, min, max = avg_min_max(overlap_targ_t)
    span_measures['target']['overlapping_span']['type_match']['avg'] = avg
    span_measures['target']['overlapping_span']['type_match']['min'] = min
    span_measures['target']['overlapping_span']['type_match']['max'] = max

    span_measures['global']['perfect_begin']['no_match'] = (1.0 * (begin_prop + begin_loc + begin_temp + begin_targ)) / global_count
    span_measures['global']['perfect_begin']['type_match'] = (1.0 * (begin_prop_m + begin_loc_m + begin_temp_m + begin_targ_m)) / global_count
    span_measures['property']['perfect_begin']['no_match'] = (1.0 * begin_prop) / count_prop
    span_measures['property']['perfect_begin']['type_match'] = (1.0 * begin_prop_m) / count_prop
    span_measures['location']['perfect_begin']['no_match'] = (1.0 * begin_loc) / count_loc
    span_measures['location']['perfect_begin']['type_match'] = (1.0 * begin_loc_m) / count_loc
    span_measures['tempex']['perfect_begin']['no_match'] = (1.0 * begin_temp) / count_temp
    span_measures['tempex']['perfect_begin']['type_match'] = (1.0 * begin_temp_m) / count_temp
    span_measures['target']['perfect_begin']['no_match'] = (1.0 * begin_targ) / count_targ
    span_measures['target']['perfect_begin']['type_match'] = (1.0 * begin_targ_m) / count_targ

    span_measures['global']['perfect_end']['no_match'] = (1.0 * (
                end_prop + end_loc + end_temp + end_targ)) / global_count
    span_measures['global']['perfect_end']['type_match'] = (1.0 * (
                end_prop_m + end_loc_m + end_temp_m + end_targ_m)) / global_count
    span_measures['property']['perfect_end']['no_match'] = (1.0 * end_prop) / count_prop
    span_measures['property']['perfect_end']['type_match'] = (1.0 * end_prop_m) / count_prop
    span_measures['location']['perfect_end']['no_match'] = (1.0 * end_loc) / count_loc
    span_measures['location']['perfect_end']['type_match'] = (1.0 * end_loc_m) / count_loc
    span_measures['tempex']['perfect_end']['no_match'] = (1.0 * end_temp) / count_temp
    span_measures['tempex']['perfect_end']['type_match'] = (1.0 * end_temp_m) / count_temp
    span_measures['target']['perfect_end']['no_match'] = (1.0 * end_targ) / count_targ
    span_measures['target']['perfect_end']['type_match'] = (1.0 * end_targ_m) / count_targ

    span_measures['property']['perfect_match']['type_match'] = (1.0 * exact_prop_t) / count_prop
    span_measures['property']['perfect_match']['no_match'] = (1.0 * exact_prop) / count_prop
    span_measures['location']['perfect_match']['no_match'] = (1.0 * exact_loc) / count_loc
    span_measures['location']['perfect_match']['type_match'] = (1.0 * exact_loc_t) / count_loc
    span_measures['tempex']['perfect_match']['no_match'] = (1.0 * exact_temp) / count_temp
    span_measures['tempex']['perfect_match']['type_match'] = (1.0 * exact_temp_t) / count_temp
    span_measures['target']['perfect_match']['no_match'] = (1.0 * exact_targ) / count_targ
    span_measures['target']['perfect_match']['type_match'] = (1.0 * exact_targ_t) / count_targ

    span_measures['global']['split_gold_span']['no_match'] = (1.0 * (
                split_g_prop + split_g_loc + split_g_temp + split_g_targ)) / global_count
    span_measures['global']['split_gold_span']['type_match'] = (1.0 * (
                split_g_prop_m + split_g_loc_m + split_g_temp_m + split_g_targ_m)) / global_count
    span_measures['property']['split_gold_span']['no_match'] = (1.0 * split_g_prop) / count_prop
    span_measures['property']['split_gold_span']['type_match'] = (1.0 * split_g_prop_m) / count_prop
    span_measures['location']['split_gold_span']['no_match'] = (1.0 * split_g_loc) / count_loc
    span_measures['location']['split_gold_span']['type_match'] = (1.0 * split_g_loc_m) / count_loc
    span_measures['tempex']['split_gold_span']['no_match'] = (1.0 * split_g_temp) / count_temp
    span_measures['tempex']['split_gold_span']['type_match'] = (1.0 * split_g_temp_m) / count_temp
    span_measures['target']['split_gold_span']['no_match'] = (1.0 * split_g_targ) / count_targ
    span_measures['target']['split_gold_span']['type_match'] = (1.0 * split_g_targ_m) / count_targ

    span_measures['global']['split_test_span']['no_match'] = (1.0 * (
            split_t_prop + split_t_loc + split_t_temp + split_t_targ)) / global_count
    span_measures['global']['split_test_span']['type_match'] = (1.0 * (
            split_t_prop_m + split_t_loc_m + split_t_temp_m + split_t_targ_m)) / global_count
    span_measures['property']['split_test_span']['no_match'] = (1.0 * split_t_prop) / count_prop
    span_measures['property']['split_test_span']['type_match'] = (1.0 * split_t_prop_m) / count_prop
    span_measures['location']['split_test_span']['no_match'] = (1.0 * split_t_loc) / count_loc
    span_measures['location']['split_test_span']['type_match'] = (1.0 * split_t_loc_m) / count_loc
    span_measures['tempex']['split_test_span']['no_match'] = (1.0 * split_t_temp) / count_temp
    span_measures['tempex']['split_test_span']['type_match'] = (1.0 * split_t_temp_m) / count_temp
    span_measures['target']['split_test_span']['no_match'] = (1.0 * split_t_targ) / count_targ
    span_measures['target']['split_test_span']['type_match'] = (1.0 * split_t_targ_m) / count_targ
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
    avg, min, max = avg_min_max(gold_annot_counts)
    data_scores['gold_data']['annotation_per_query']['avg'] = avg
    data_scores['gold_data']['annotation_per_query']['min'] = min
    data_scores['gold_data']['annotation_per_query']['max'] = max
    avg, min, max = avg_min_max(test_annot_counts)
    data_scores['test_data']['annotation_per_query']['avg'] = avg
    data_scores['test_data']['annotation_per_query']['min'] = min
    data_scores['test_data']['annotation_per_query']['max'] = max
    return data_scores

def calc_global_attr_scores(attr_dicts):

    attr_scores = {
        "global": copy.deepcopy(attr_measure_template),
        "property": copy.deepcopy(attr_measure_template),
        "location": copy.deepcopy(attr_measure_template),
        "tempex": copy.deepcopy(attr_measure_template),
        "target": copy.deepcopy(attr_measure_template)
    }
    return attr_scores


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

    # write results to out path
    with open(out_path, "w") as outf:
        json.dump(template, outf)




global_stats("gold_queries.json", "noisy_gold_queries.json", "out.json")

