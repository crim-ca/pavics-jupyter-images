
def nlq_ner(nlq):
    """
    Named entity recognition module over a
    natural language query.
    Returns a list of detected NEs.
    """
    return []

def nlq_ter(nlq):
    """
    Temporal expression recognition module over a
    natural language query.
    Returns a list of detected TEs.
    """
    return []

def nlq_var_val(nlq):
    """
    Variable and value recognition module over a
    natural language query.
    Returns a list of detected variable names and their values.
    """
    return []

def nl2query(nlq):
    """
    Takes a natural language query and
    processes it with different NLP modules:
    - named entity recognition (NER)
    - temporal expression recognition (TER)
    - variable name and value detection (Var&Val)
    Returns the equivalent structured query in a dict format.
    """
    struct_q = {}
    struct_q['ner'] = nlq_ner(nlq)
    struct_q['ter'] = nlq_ter(nlq)
    struct_q['var_val'] = nlq_var_val(nlq)
    return struct_q
