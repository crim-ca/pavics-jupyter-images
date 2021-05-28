import json
from typing import Any


class Vocabulary:
    def __init__(self):
        # map of var-values
        self.vocab = {}

    def read_vocabulary(self, file: str):
        with open(file, "r") as f:
            vocab = json.load(f)
        if vocab:
            for vals in vocab.values():
                if "values" not in vals.keys() or \
                  "aliases" not in vals.keys():
                    raise Exception("Could not read vocabulary file. Missing key values.")
            # all is good
            self.vocab = vocab

    def get_vocab_dict(self):
        return self.vocab

    def add_var_val(self, var: str, val: Any):
        # add variable and a list of possible names (aliases) for it
        # and values as a list of possible values or type
        if var not in self.vocab.keys():
            self.vocab[var] = {"values": val, "aliases": []}
        else:
            # handle adding under same key
            self.add_value_option(var, val)

    def add_variable_alias(self, var, alias):
        # find var in vocab
        if var not in self.vocab.keys():
            # new var, new alias, no value known
            self.add_var_val(var, [])
        # add alias
        self.vocab[var]['aliases'] += alias

    def add_value_option(self, var, newval):
        # find var in vocab, add new value option
        if var in self.vocab.keys():
            if not type(self.vocab[var]['values']) == list:
                self.vocab[var]['values'] = [self.vocab[var]['values']]
            self.vocab[var]['values'].append(newval)
        else:
            # it's a new var entry
            self.add_var_val(var, newval)

    def stats(self):
        return {"Number of variable-value groups": len(self.vocab),
                "Number of variables with >1 alias": len([x for x in self.vocab.values() if len(x['aliases']) > 1])}
