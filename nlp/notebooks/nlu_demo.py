import json
import os
from pprint import pprint

import ipywidgets as widgets
from ipywidgets import interact

from nl2query.V1.V1_pipeline import V1_pipeline
from nl2query.V2.V2_pipeline import V2_pipeline
from nl2query.V3.V3_pipeline import V3_pipeline
from stac_wrapper.query_handler import STAC_query_handler


class NLU_demo:
    """class to handle all necessary widgets and
    functions of the NLU demo notebook"""
    
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        # initialize pipelines
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.v1_config = os.path.join(self.path, "nl2query/V1/v1_config.cfg")
        self.v1_instance = None
        self.v2_config = os.path.join(self.path, "nl2query/V2/v2_config.cfg")
        self.v2_instance = None
        self.v3_instance = None
        self.stac_config = os.path.join(self.path, "stac_wrapper/stac_config.cfg")
        self.stac_handler = STAC_query_handler(self.stac_config)
        # Read gold queries
        gold_path = os.path.join(self.path, "nl2q_eval/ceda_gold_queries.json")
        with open(gold_path, 'r', encoding="utf-8") as qfile:
            goldq = json.load(qfile)
        self.gold_queries = goldq["queries"]
        self.query_list = [query['query'] for _,query in enumerate(self.gold_queries)]
        # setup visual widgets
        # NOTE: to ensure widgets render correctly, wrap them in 'interact' before returning them for the notebook
        self.select_query = widgets.Dropdown(
            options=self.query_list,
            value=self.query_list[11],
            description='Query:',
            disabled=False,
            layout={'width': 'max-content'}
            )
        self.write_query = widgets.Textarea(
            value='',
            placeholder='yearly precipitation over Ottawa between 2000 and 2020',
            description='Your query:',
            layout={'height':'auto', 'width': '800px'},
            disabled=False
            )
        self.select_version = widgets.Select(
            options=['V1', 'V2', 'V3'],
            value='V3',
            rows=3,
            description='System Version:',
            style={'description_width': 'initial'},
            disabled=False
            )
            
    def select_gold_query(self):
        """return select gold query dropdown"""
        return interact(self.select_query)

    def get_gold_annotations(self):
        """get the annotations for the selected gold query"""
        return self.gold_queries[self.select_query.index]

    def custom_query(self, value=""):
        """return textbox to write your own query"""
        if value:
            self.write_query.value = value
        return interact(self.write_query)

    def select_nlu_version(self):
        """return a selection widget for selecting the system version"""
        return interact(self.select_version)

    def nl2query(self):
        """takes the selected query (gold or custom),
        and executes the nl2query transformation
        with the selected NLU version (V1, V2 or V3).
        returns the annotated structured query"""
        # get nlq from gold or custom
        if len(self.write_query.value) > 1:
            self.nlq = self.write_query.value
        else:
            self.nlq = self.select_query.value
        if not self.nlq:
            raise ValueError(
                "Natural Language Query is empty. Cannot run the query pipeline. "
                "Either set the value with 'write_query' or 'select_query' widgets."
            )
        if self.select_version.value == "V1":
            if not self.v1_instance:
                #initialize V1
                self.v1_instance = V1_pipeline(self.v1_config)
            # run V1 pipeline on this query
            v1_structq = self.v1_instance.transform_nl2query(self.nlq, verbose=self.verbose)
            print("\nV1 structured query: ")
            self.struct_query = v1_structq.to_dict()
        elif self.select_version.value == "V2":
            # initialize V2
            if not self.v2_instance:
                self.v2_instance = V2_pipeline(self.v2_config)
            # run V2 pipeline on this query
            v2_structq = self.v2_instance.transform_nl2query(self.nlq, verbose=self.verbose)
            print("\nV2 structured query: ")
            self.struct_query = v2_structq.to_dict()
        else:
            if not self.v3_instance:
                # initialize V3
                self.v3_instance = V3_pipeline(self.v1_config, self.v2_config)
            # run V3 pipeline on query
            v3_structq = self.v3_instance.transform_nl2query(self.nlq, verbose=self.verbose)
            print("\nV3 structured query: ")
            self.struct_query = v3_structq.to_dict()
        return pprint(self.struct_query, sort_dicts=False)
        
    def select_stac_catalog(self):
        return self.stac_handler.select_catalog()
    
    def run_stac_query(self):
        if self.struct_query:
            return self.stac_handler.handle_query(self.struct_query, verbose=self.verbose)
        
    def run_custom_stac_query(self, params):
        return self.stac_handler.search_query(params=params)
