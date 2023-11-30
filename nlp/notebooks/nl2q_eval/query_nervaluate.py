from nervaluate import Evaluator
import os
import json
from MetricsClasses import ANNOTATION_TYPES

def read_files(gold_path, test_path):
    """read the two files and
    perform sanity check
    return the list of queries"""
    try:
        gold_qs, test_qs = [], []
        # open the two files
        with open(gold_path) as f:
            gold_file = json.load(f)
        with open(test_path) as f:
            test_file = json.load(f)
        if gold_file and test_file:
            # the root key is 'queries'
            if 'queries' in gold_file.keys() and 'queries' in test_file.keys():
                gold_qs = gold_file['queries']
                test_qs = test_file['queries']
                # sanity checks if all queries are there
                if len(gold_qs) != len(test_qs):
                    print("Error: Number of queries different in gold and test! ")
            else:
                print("Error: JSON format not as expected. No 'queries' key! ")
        return gold_qs, test_qs
    except Exception as exc:
        print("Encountered an error while reading input files. "
              "Please check the correct file paths!")
        print(exc)
        return None, None


def get_span_list(queries_list):
    """takes a list of queries and their annotations
    and extracts span begin, end and annotation type as label
    in prodi.gy style required by nervaluate"""
    span_list = []
    for i, query in enumerate(queries_list):
        span_list.append([])
        for annot in query['annotations']:
            # if split annotation, take first and last
            if type(annot['position'][0]) == list:
                start = annot['position'][0][0]
                end = annot['position'][-1][-1]
            else:
                start = annot['position'][0]
                end = annot['position'][1]
            span_list[i].append({'label': annot['type'],
                                 'start': start,
                                 'end': end})
    return span_list


def nervaluate_performance(gold_path, test_path):
    """Take a gold and a test annotations file
    and calculate nervaluate performance metrics"""
    gold_qs, test_qs = read_files(gold_path, test_path)
    if not (gold_qs and test_qs):
        print("Problem reading annotation files or empty.")
        return
    # transform annotations in span lists
    gold_spans = get_span_list(gold_qs)
    test_spans = get_span_list(test_qs)
    # call Nervaluate
    evaluator = Evaluator(gold_spans, test_spans, tags=ANNOTATION_TYPES)
    results, results_per_tag = evaluator.evaluate()
    # return results
    return results, results_per_tag


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__)) #"misc/data23-bs/DACCS/wp15/CEDA/gold/v2/"
    res, res_per_tag = nervaluate_performance(gold_path=os.path.join(path, "ceda_gold_queries.json"),
                                              test_path=os.path.join(path, "v1_ceda_test_clean.json"))
    print(res)
    print(res_per_tag)
    out_path = os.path.join(path, "v1_ceda_clean_nervaluate_out.json")
    with open(out_path, "w") as outf:
        json.dump({"nervaluate": res, "nervaluate_per_tag": res_per_tag}, outf)
