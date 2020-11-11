from intake import open_stac_catalog
import satsearch

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
    'All': stac_catalogs.keys(),
    'Climate': ['pangeo_cmip6'],
    'EO': ['landsat8', 'google_engine', 'nasa_cmr', 'earth_aws']
}

# set the default catalog
catalog_URL = stac_catalogs['earth_aws']

def inspect_catalog(catalog_URL):
    # open catalog
    catalog = open_stac_catalog(catalog_URL)



def query_nlp(query_text):
    """
    Handle a NL query into a structured query
    returns parameters used for faceted search.
    """
    # initialize parameters
    params = {}
    # extract from the text query the structured query parameters

    # fill in parameters of structured query
    params['bbox'] = [-110, 39.5, -105, 40.5]
    params['datetime'] = '2018-02-12T00:00:00Z/2018-03-18T12:31:12Z'
    params['query'] = ["eo:cloud_cover<10"]
    params['collections'] = ['sentinel-s2-l2a']
    print("Created structured query with parameters: ", params)
    return params

def handle_query(query_text, data_source='All'):
    """
    Takes an NL query, transforms it into a structured one,
    and performs a search against the given or default catalog.
    Returns result items or None.
    """
    print("Received query: ", query_text)
    params = query_nlp(query_text)
    for ds in data_sources[data_source]:
        search_query(params, ds)
    return


def search_query(params, catalog_URL):
    """
    Search a specific catalog with with given search parameters
    return result items or None.
    """
    results = satsearch.Search.search(url=catalog_URL,
                                      bbox = params['bbox'],
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

