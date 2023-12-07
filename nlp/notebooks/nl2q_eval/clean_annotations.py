import json
import os


def clean_incomplete_annotations(dataset:list):
    """given a list of annotations,
    remove all that are incomplete
    (missing any attribute values)"""
    new_annots = []
    total = 0
    removed = 0
    prop = 0
    targ = 0
    loc = 0
    temp = 0
    print("Queries:", len(dataset))
    for query in dataset:
        # print(query)
        newq = {}
        newq['query'] = query['query']
        newq['annotations'] = []
        total += len(query['annotations'])
        for annot in query['annotations']:
            complete = True
            for k,v in annot.items():
                if v == "" or v == [] or v=={}:
                    complete = False
                    # print("Incomplete:",k,v)
                    removed += 1
                    if annot['type'] == 'property':
                        prop+=1
                    elif annot['type'] == 'location':
                        loc+=1
                    elif annot['type'] == 'tempex':
                        temp+=1
                    elif annot['type'] == 'target':
                        targ+=1
                    break
            if complete:
                newq['annotations'].append(annot)
        new_annots.append(newq)
    print("Removed: ", removed, " out of total: ",total)
    print("Removed percentage: ", removed/total)
    print("Breakdown of removed annotations by type:\nProperty: ", prop)
    print("Location: ", loc)
    print("Temporal: ", temp)
    print("Target: ", targ)
    return new_annots
    
    
if __name__ == "__main__":
    this_path=  os.path.dirname(os.path.realpath(__file__))
    file_to_clean = os.path.join(this_path, "v3_ceda_test_results.json")
    out_file = os.path.join(this_path, "v3_ceda_test_clean.json")
    with open(file_to_clean, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    if 'queries' in dataset.keys():
        new_dataset = clean_incomplete_annotations(dataset['queries'])
        with open(out_file, "w", encoding="utf-8") as outf:
            json.dump({"queries":new_dataset}, outf, indent=2)
    else:
        print("Error: JSON format not as expected. No 'queries' key! ")