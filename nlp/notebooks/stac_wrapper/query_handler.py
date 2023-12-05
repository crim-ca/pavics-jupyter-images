import json
import os
import datetime
import ipywidgets as widgets
from configparser import ConfigParser
from pystac_client import Client


class STAC_query_handler():
    """ class to handle running a stac query"""
    
    def __init__(self, config_file:str="stac_config.cfg"):
        # parse the config file
        if os.path.exists(config_file):
            print("Reading config file: ", config_file)
            self.config = ConfigParser()
            self.config.read(config_file)
        else:
            raise Exception("Config file not found! "+ config_file)
        
        if "catalogs" in self.config.sections():
            self.catalogs = dict(self.config.items('catalogs'))
        
        # datasource
        self.datasource = None
        self.response_text = widgets.Output()
   

    def select_catalog(self):
        options = list(self.catalogs.keys())
        self.datasource = widgets.Dropdown(
            options=options,
            value=options[0],
            description='Select catalog:',
            style={'description_width': 'initial'}
        )
        return self.datasource


    def query2stac(self, struct_query:dict, verbose=False):
        """
        Transform a structured query into STAC API parameters.
        return parameters used for faceted search.
        """
        # initialize parameters
        params = {'bbox': [], 'datetime':[], 'query':[], 'collections':[]}
        # extract from the structured query the stac query parameters

        for annotation in struct_query['annotations']:    
        # fill in parameters of stac query
            if annotation['type'] == 'location':
                coords = annotation['value']['coordinates']
                # it might be nested
                if len(coords) > 1:
                    params['bbox'] = coords
                elif isinstance(coords, list) and len(coords) > 1:
                    params['bbox'] = coords
                elif len(coords)==1 and isinstance(coords[0], list) and len(coords[0]) > 1:
                    params['bbox'] = coords[0]
                elif len(coords[0])==1 and isinstance(coords[0][0], list) and len(coords[0][0]) > 1:
                    params['bbox'] = coords[0][0]
            elif annotation['type'] == 'tempex':
                if isinstance(annotation['value'], str):
                    params['datetime'] = annotation['value']
                else:
                    start = annotation['value']['start']
                    if start == "#-infinity":
                        start = ".."
                    # transform currentdate to actual date
                    elif start == "#currentdate":
                        start = (datetime.datetime.today().date()).strftime("%Y-%m-%dT%H:%M:%S") +"Z"
                    end = annotation['value']['end']
                    if end == "#currentdate":
                        end = (datetime.datetime.today().date()).strftime("%Y-%m-%dT%H:%M:%S") +"Z"
                    elif end == "#+infinity":
                        end = ".."
                    params['datetime'] = [start, end]
            elif annotation['type'] == 'property':
                if annotation['name'] and annotation['value']:
                    # by default operator is 'eq' 
                    op = "="
                    # we currently do not generate any other operator
                    # TODO! extend here in future to handle other operators
                    prop_string = str(annotation['name']) + op + str(annotation['value'])
                    params['query'] = [prop_string]
            elif annotation['type'] == 'target':
                params['query'] = annotation['name']
        if verbose:
            print("Created STAC query with the parameters:\n", params)
        return params
   

    def search_query(self, params:dict, verbose:bool=False):
        """
        Search a specific catalog with the given search parameters
        return a visual results list or None.
        """
        try:
            catalog_URL = self.catalogs[self.datasource.value]
            client = Client.open(catalog_URL)
            print("Opening catalog: ", client.title)
            if not client.conforms_to("ITEM_SEARCH"):
                print("Catalog does not conform to item search functionality. Quitting.")
                return None
            if 'max_items' in params:
                max_items = params['max_items']
            else:
                max_items = 10
            response = client.search(bbox=params['bbox'],
                                    datetime=params['datetime'],
                                    query=params['query'],
                                    collections=params['collections'],
                                    max_items=max_items,
                                    method="GET")
            items = response.items()
            if verbose:
                print("Searching catalog: ", catalog_URL)
                # print('Found %s items' % response.matched())
                print(f"QUERY: {vars(response)}")
            results = [item for item in items]
            # return visual repr of results list
            return VisualList(results)
        except Exception as e:
            print("During searching the STAC catalog, the following error occured:\n", str(e))
            return

    
    def handle_query(self, struct_query, verbose=False):
        """
        Takes an NL query, transforms it into a structured one,
        and performs a search against the given or default catalog.
        Returns result items or None.
        """
        params = self.query2stac(struct_query, verbose)
        return self.search_query(params, verbose)



class VisualList(list):
    """class to visualize STAC API response as a visual list using
    https://github.com/Open-EO/openeo-vue-components/tree/master"""

    def __init__(self, data: list):
        list.__init__(self, data)

    def _repr_html_(self):
        # Construct HTML, but load Vue Components source files only if the
        # openEO HTML tag is not yet defined
        return """
        <script>
        if (!window.customElements || !window.customElements.get('openeo-items')) {{
            var el = document.createElement('script');
            el.src = "https://cdn.jsdelivr.net/npm/@openeo/vue-components@2/assets/openeo.min.js";
            document.head.appendChild(el);
        }}
        </script>
        <openeo-items>
            <script type="application/json">{props}</script>
        </openeo-items>
        """.format(
            props=json.dumps({'items': [i.to_dict() for i in self], 'show-map': True}, indent=2)
        )
