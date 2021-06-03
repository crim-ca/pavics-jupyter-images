import json
import os
import re
from xml.etree import ElementTree as ET
from Vocabulary import Vocabulary

def process_cf_standard_names(path:str):
    my_vocab = Vocabulary()
    tree = ET.parse(path)
    if tree.getroot():
        print("Successfully read XML file.")
    for entry in tree.getroot():
        if entry.tag == "entry":
            # extract id
            var = (entry.attrib['id']).replace("_", " ")
            units = entry.find('.//canonical_units')
            if units.text in [1, "day", "month", "year"]:
                my_vocab.add_var_value(var, 'int')
            else:
                my_vocab.add_var_value(var, 'float')
            # extract from description?
        elif entry.tag == "alias":
            alias = entry.attrib['id'].replace("_", " ")
            var = entry.find('./entry_id').text.replace("_", " ")
            my_vocab.add_variable_alias(var, alias)
            my_vocab.add_variable_alias(alias, var)
    print("First 5 items of the vocabulary: ", list(my_vocab.get_vocab_dict().items())[:5])
    print("Generated vocabulary with: ", my_vocab.stats())
    return my_vocab

def process_copernicus(file:str):
    my_vocab = Vocabulary()
    with open(file, "r") as f:
        cop_file = json.load(f)
    if cop_file:
        print("Read copernicus raw vocabulary file.")
        for key in cop_file["copernicus"]:
            val = cop_file["copernicus"][key]
            if type(val) == dict:
                aggregated_vals = set()
                for v in val.values():
                    # nested nested dict
                    if type(v) == dict:
                        for k2, v2 in v.items():
                            aggregated_vals.add(k2)
                            aggregated_vals.add(v2)
                    elif type(v) == list:
                        for v2 in v:
                            aggregated_vals.add(v2)
                val = list(aggregated_vals)
            my_vocab.add_var_value(key.replace("_", " "), val)

    print("First 5 items of the vocabulary: ", list(my_vocab.get_vocab_dict().items())[:5])
    print("Generated vocabulary with: ", my_vocab.stats())
    return my_vocab


def process_peps(file: str):
    my_vocab = Vocabulary()
    with open(file, "r") as f:
        peps_file = json.load(f)
    if peps_file:
        print("Read peps raw vocabulary file.")
        for key in peps_file['peps']['all']:
            val = peps_file['peps']['all'][key]
            if type(val) == dict:
                for key2, val2 in val.items():
                    my_vocab.add_var_value(key2, val2)
            else:
                my_vocab.add_var_value(key, val)
    print("First 5 items of the vocabulary: ", list(my_vocab.get_vocab_dict().items())[:5])
    print("Generated vocabulary with: ", my_vocab.stats())
    return my_vocab

def process_cmip6(file: str):
    my_vocab = Vocabulary()
    with open(file, "r") as f:
        cmip6_file = json.load(f)
    if cmip6_file:
        print("Read CMIP6 raw vocabulary file.")
        for key in cmip6_file['cmip6']:
            val = cmip6_file['cmip6'][key]
            if type(val) == dict:
                # adding values as possible value
                vals = list(val.keys())
                # add value of val if length < 30 -> possible label, not long description
                vals += [v for v in val.values() if len(v) < 30]
                vals += [v.replace("-", " ") for v in val.keys() if "-" in v]
                my_vocab.add_var_value(key.replace("_", " "), vals)
            else:
                my_vocab.add_var_value(key.replace("_", " "), val)
    print("First 5 items of the vocabulary: ", list(my_vocab.get_vocab_dict().items())[:5])
    print("Generated vocabulary with: ", my_vocab.stats())
    return my_vocab


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def process_paviccs(file: str):
    my_vocab = Vocabulary()
    with open(file, "r") as f:
        paviccs_file = json.load(f)
    if paviccs_file:
        print("Read PAVICCS raw vocabulary file.")
        for key in paviccs_file:
            val = paviccs_file[key]
            if key == "variables":
                for v in val[0]:
                    newvar = v.replace("_", " ")
                    alias = set()
                    if 'long_name' in val[0][v]:
                        alias.add(val[0][v]['long_name'].replace("_", " "))
                    if 'standard_name' in val[0][v]:
                        alias.add(val[0][v]['standard_name'].replace("_", " "))
                    if 'units' in val[0][v]:
                        my_vocab.add_var_value(newvar, val[0][v]['units'])
                    else:
                        my_vocab.add_var_value(newvar, [])
                    my_vocab.add_variable_alias(newvar, list(alias))
            else:
                newval = []
                for v in val:
                    if v.isdigit():
                        newval.append(int(v))
                    elif isfloat(v):
                        newval.append(float(v))
                    else:
                        newval.append(v)
                newkey = key.lower().replace("_", " ")
                # de-camelcase
                newkey = " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', newkey)).split())
                my_vocab.add_var_value(newkey, newval)

    print("First 5 items of the vocabulary: ", list(my_vocab.get_vocab_dict().items())[:5])
    print("Generated vocabulary with: ", my_vocab.stats())
    return my_vocab

if __name__ == "__main__":
    path = "/misc/data23-bs/DACCS/wp15/metadata/vocab/"
    cf_standard_name = "cf-standard-name-table.xml"
    cf_vocab = process_cf_standard_names(os.path.join(path, cf_standard_name))
    with open("proc_vocab_cf_standard_names.json", "w") as f:
        json.dump(cf_vocab.get_vocab_dict(), f)
    print("Vocabulary written to file. ")

    copernicus_file = "vocab_copernicus.json"
    cop_vocab = process_copernicus(os.path.join(path, copernicus_file))
    with open("proc_vocab_copernicus.json", "w") as f:
        json.dump(cop_vocab.get_vocab_dict(), f)
    print("Vocabulary written to file. ")

    peps_file = "vocab_peps.json"
    peps_vocab = process_peps(os.path.join(path, peps_file))
    with open("proc_vocab_peps.json", "w") as f:
        json.dump(peps_vocab.get_vocab_dict(), f)
    print("Vocabulary written to file. ")

    cmip6_file = "vocab_cmip6.json"
    cmip6_vocab = process_cmip6(os.path.join(path, cmip6_file))
    with open("proc_vocab_cmip6.json", "w") as f:
        json.dump(cmip6_vocab.get_vocab_dict(), f)
    print("Vocabulary written to file. ")

    paviccs_file = "PAVICCS/all_key_vals.json"
    paviccs_vocab = process_paviccs(os.path.join(path, paviccs_file))
    with open("proc_vocab_paviccs.json", "w") as f:
        json.dump(paviccs_vocab.get_vocab_dict(), f)
    print("Vocabulary written to file. ")