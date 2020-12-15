from intake import open_stac_catalog
import satsearch
import json
import ipywidgets as widgets

# STAC index public catalogs
# https://stacindex.org/catalogs?access=true&type=null
stac_catalogs = {
    'landsat8' : "https://raw.githubusercontent.com/sat-utils/sat-stac/master/test/catalog/catalog.json",
    'google_engine': "https://earthengine-stac.storage.googleapis.com/catalog/catalog.json",
    'pangeo_cmip6': "https://raw.githubusercontent.com/pangeo-data/pangeo-datastore/master/intake-catalogs/master.yaml",
    'nasa_cmr': "https://cmr.earthdata.nasa.gov/cmr-stac",
    'earth_aws':  "https://earth-search.aws.element84.com/v0"
}
data_sources = {
    'Climate': ['pangeo_cmip6'],
    'EO': ['landsat8', 'google_engine', 'nasa_cmr', 'earth_aws']
}
data_sources['All'] = data_sources['Climate'] + data_sources['EO']

# set the default catalog
catalog_URL = stac_catalogs['earth_aws']

# notebook interaction methods
def select_ds():
    select = widgets.Select(
        options=['catalog', 'domain'],
        value='catalog',  # Default
        rows=2,
        layout={'width': 'max-content'},
        description='Select:',
        disabled=False
    )
    return select

def select_c(svalue):
    ds = None
    if svalue == 'catalog':
        ds = widgets.Dropdown(
            options=['landsat8', 'google_engine', 'nasa_cmr', 'earth_aws', 'pangeo_cmip6'],
            value='earth_aws',
            description='Select catalog:',
            style={'description_width': 'initial'}
        )
    elif svalue == 'domain':
        ds = widgets.Dropdown(
            options=['All', 'EO', 'Climate'],
            description='Select domain:',
            style={'description_width': 'initial'}
        )
    return ds

def query_in():
    text = widgets.Textarea(
        value='',
        placeholder='Write your query here!',
        description='Input query:',
        disabled=False,
        rows=2,
        layout={'height': '90%', 'width': '100%'}
    )
    return text

# functionality methods
def inspect_catalog(catalog_URL):
    # open catalog
    catalog = open_stac_catalog(catalog_URL)
    return catalog

def eval_query(query_text, catalogue, query_structured=None):
    """
    Method to evaluate how correctly the natural language query
    was translated into a structured query.
    Score is calculated based on the parameters:
    collections, bbox, datetime, intersects and query
    It returns precision, recall and f1 scores
    """
    recall_score = 0
    precision_score = 0
    f1_score = 0
    if not query_structured:
        query_structured = nlp2query(query_text)
    with open('stac_wrapper/eval_queries.json', 'r') as f:
        eval_base = json.load(f)
    if query_text in eval_base[catalogue].keys():
        print("Found query in evaluation set.")
        gold_structured = eval_base[catalogue][query_text]
        print("Gold parameters: ", gold_structured)
        # parameter-wise comparison calculation of score
        # recall
        out_of = len(gold_structured.keys())
        for param in gold_structured.keys():
            inner_score = 0
            if param in query_structured.keys():
                gold_values = gold_structured[param]
                query_values = query_structured[param]
                if type(gold_values) == list and type(query_values) == list:
                    nr_values = len(gold_values)
                    for value in gold_values:
                        # strict match values
                        if value in query_values:
                            inner_score += 1/nr_values
                elif str(gold_values) == str(query_values):
                    inner_score += 1
            recall_score += inner_score / out_of
        # precision
        out_of = len(query_structured.keys())
        for param in query_structured.keys():
            inner_score = 0
            if param in gold_structured.keys():
                query_values = query_structured[param]
                gold_values = gold_structured[param]
                if type(gold_values) == list and type(query_values) == list:
                    nr_values = len(query_values)
                    for value in query_values:
                        # strict match values
                        if value in gold_values:
                            inner_score += 1 / nr_values
                elif str(gold_values) == str(query_values):
                    inner_score += 1
                precision_score += inner_score / out_of
    else:
        print("Query not found in evaluation set.")

    if precision_score:
        f1_score = (2 * precision_score * recall_score) / (precision_score + recall_score)
    return {"precision": precision_score, "recall": recall_score, "f1": f1_score}


def nlp2query(query_text):
    """
    Handle a NL query into a structured query
    returns parameters used for faceted search.
    """
    # initialize parameters
    params = {}
    # extract from the text query the structured query parameters

    # fill in parameters of structured query
    if query_text == "Sentinel-2 over Ottawa from april to september 2018 with cloud cover lower than 10%":
        params['collections'] = ['sentinel-s2-l2a']
        params['bbox'] = [-110, 39.5, -105, 40.5]
        params['datetime'] = '2018-04-01T00:00:00Z/2018-09-30T00:00:00Z'
        params['query'] = ["eo:cloud_cover<10"]
    print("Created structured query with parameters: ", params)
    return params


def handle_query(query_text, data_source='All'):
    """
    Takes an NL query, transforms it into a structured one,
    and performs a search against the given or default catalog.
    Returns result items or None.
    """
    print("Received query: ", query_text)
    params = nlp2query(query_text)
    # query a collection
    if type(data_source) == list and data_source in data_sources:
        for ds in data_sources[data_source]:
            # TODO! remove this condition for full version.
            #  This is demo query on earth_aws. Ignoring any other type of query for now.
            if ds == 'earth_aws':
                print("Querying data source: %s (%s)" % (ds, stac_catalogs[ds]))
                search_query(params, stac_catalogs[ds])
    # query a single catalog
    elif data_source in data_sources['All']:
        # TODO! remove this condition for full version.
        #  This is demo query on earth_aws. Ignoring any other type of query for now.
        if data_source == 'earth_aws':
            print("Querying data source: %s (%s)" % (data_source, stac_catalogs[data_source]))
            search_query(params, stac_catalogs[data_source])

def search_query(params, catalog_URL):
    """
    Search a specific catalog with with given search parameters
    return result items or None.
    """
    results = satsearch.Search.search(url=catalog_URL,
                                      bbox=params['bbox'],
                                      datetime=params['datetime'],
                                      query=params['query'],
                                      collections=params['collections'])
    print("Searching catalog: ", catalog_URL)
    print('Found %s items' % results.found())
    items = results.items(limit=10)
    print('Summary: %s' % items.summary())

    print('%s collections' % len(items._collections))
    col = items._collections[0]
    print('Collection: %s' % col)

    return items

