import json
import difflib


def eval_query(test, gold):
    nr_types = 4  #['property', 'tempex', 'location', 'target']

    # sanity check
    if test['query'] != gold['query']:
        print("Test and gold queries are different!")
        return

    test_annotations = test['annotations']
    gold_annotations = gold['annotations']

    test_span_count = 0
    gold_span_count = 0
    test_property_count = 0
    gold_property_count = 0
    test_tempex_count = 0
    gold_tempex_count = 0
    test_location_count = 0
    gold_location_count = 0
    test_target_count = 0
    gold_target_count = 0

    print("#################  DATA  #################")
    test_spans = [ann['text'] for ann in test_annotations]
    test_types = [ann['type'] for ann in test_annotations]
    test_span_count = len(test_annotations)
    for t in test_annotations:
        test_type = t['type']
        if test_type == "property":
            test_property_count += 1
        elif test_type == "tempex":
            test_tempex_count += 1
        elif test_type == "location":
            test_location_count += 1
        elif test_type == "target":
            test_target_count += 1
    print("Test annot count: ", test_span_count)
    print("Test spans: ", test_spans)
    print("Test types: ", test_types)

    golden_spans = [ann['text'] for ann in gold_annotations]
    golden_types = [ann['type'] for ann in gold_annotations]
    gold_span_count = len(gold_annotations)
    for t in gold_annotations:
        gold_type = t['type']
        if gold_type == "property":
            gold_property_count += 1
        elif gold_type == "tempex":
            gold_tempex_count += 1
        elif gold_type == "location":
            gold_location_count += 1
        elif gold_type == "target":
            gold_target_count += 1

    print("Gold annot count: ", gold_span_count)
    print("Gold spans: ", golden_spans)
    print("Gold types: ", golden_types)

    calc_score("precision", test_annotations, test_span_count,
               test_property_count, test_tempex_count,
               test_location_count, test_target_count,
               gold_annotations, golden_spans, golden_types)
    calc_score("recall", gold_annotations, gold_span_count,
               gold_property_count, gold_tempex_count,
               gold_location_count, gold_target_count,
               test_annotations, test_spans, test_types)


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
