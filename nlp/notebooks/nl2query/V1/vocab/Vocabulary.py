import json
from typing import Any


class Vocabulary:
    def __init__(self, file: str = None):
        # map of var-values
        self.vocab = {}
        if file:
            with open(file, "r") as f:
                vocab = json.load(f)
            if vocab:
                for vals in vocab.values():
                    if "values" not in vals.keys() or \
                      "aliases" not in vals.keys():
                        raise Exception("Could not read vocabulary file. Missing key values.")
                # all is good
                self.vocab = vocab
                self.vars = self.get_vars_list()
                self.values = self.get_values_list()

    def get_vocab_dict(self):
        return self.vocab

    def get_vars_list(self):
        keys = []
        for key in self.vocab:
            keys.append(key)
            keys += self.vocab[key]['aliases']
        return keys

    def get_values_list(self):
        values = []
        for key in self.vocab:
            values += [x for x in self.vocab[key]['values'] if (type(x) == str and len(x) > 1)]
        return values

    def find_var_of_value(self, val: Any):
        for key in self.vocab:
            if type(self.vocab[key]['values']) == list and \
                    val in self.vocab[key]['values']:
                return key
            elif val == self.vocab[key]['values']:
                return key
        return None

    def find_value_of_var(self, var: str):
        if var in self.vocab:
            return self.vocab[var]['values']
        # key could be an alias
        else:
            for key in self.vocab:
                if var in self.vocab[key]['aliases']:
                    return self.vocab[key]['values']
        return None

    def add_var_value(self, var: str, val: Any):
        # add variable and a list of possible names (aliases) for it
        # and values as a list of possible values or type
        if var not in self.vocab.keys():
            if type(val) == list:
                self.vocab[var] = {"values": val, "aliases": []}
            else:
                self.vocab[var] = {"values": [val], "aliases": []}
        else:
            # handle adding under same key
            self.add_value_option(var, val)

    def add_variable_alias(self, var, alias):
        # find var in vocab
        if var not in self.vocab.keys():
            # new var, new alias, no value known
            self.add_var_value(var, [])
        # add alias
        if type(alias) == list:
            self.vocab[var]['aliases'] += alias
        else:
            self.vocab[var]['aliases'].append(alias)

    def add_value_option(self, var, newval):
        # find var in vocab, add new value option
        if var in self.vocab.keys():
            self.vocab[var]['values'].append(newval)
        else:
            # it's a new var entry
            self.add_var_value(var, newval)

    def stats(self):
        return {"Number of variable-value groups": len(self.vocab),
                "Number of variables with >1 alias": len([x for x in self.vocab.values() if len(x['aliases']) > 1])}
