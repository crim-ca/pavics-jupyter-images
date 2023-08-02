from nlp.notebooks.nl2query.NL2QueryInterface import *
import json
from NER_spacy import NER_spacy
from NER_flair import NER_flair
from TER_heideltime import TER_heideltime
from Vars_values_textsearch import Vars_values_textsearch


class Combined_NL2Query(NL2QueryInterface):
    """ Combined implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        super().__init__(config)

        # Getting model from a config file, otherwise use the default model
        if self.config.get("spacy","config_file", fallback=None) :
            self.spacy_instance = NER_spacy(self.config.get("spacy","config_file"))
        else:
            self.spacy_instance = None
            
        if self.config.get("flair","config_file", fallback=None) :
            self.flair_instance = NER_flair(self.config.get("flair","config_file"))
        else:
            self.flair_instance = None

        if self.config.get("heideltime","config_file", fallback=None) :
            self.heideltime_instance = TER_heideltime(self.config.get("heideltime","config_file"))
        else:
            self.heideltime_instance = None
            
        if self.config.get("varval","config_file", fallback=None) :
            self.varval_instance = Vars_values_textsearch(self.config.get("varval","config_file"))
        else:
            self.varval_instance = None
            
    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required

        return PropertyAnnotation(text=annotation.text, position=[annotation.start_char, annotation.end_char],
                                  name="", value="", value_type="", operation="")

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        return LocationAnnotation(text=annotation.text, position=[annotation.start_char, annotation.end_char],
                                  matching_type="", name=annotation.text, value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        return TemporalAnnotation(text=annotation['text'],  position=[annotation['start_pos'], annotation['end_pos']],
                                  tempex_type="", target="", value={})

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation['text'],  position=[annotation['start'], annotation['end']],
                                name=[""])
         
        
    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        
        combined_annotations = []
        if self.spacy_instance:
            spacy_query_annotation_dict = self.spacy_instance.transform_nl2query(nlq)
            # if Heideltime is instanciated, removing temporal annotation
            if self.heideltime_instance:
                spacy_query_annotation_dict.annotations = \
                        [a for a in spacy_query_annotation_dict.annotations if type(a) is not TemporalAnnotation]
            combined_annotations = spacy_query_annotation_dict.annotations
               
       
        if self.flair_instance:
            flair_query_annotation_dict = self.flair_instance.transform_nl2query(nlq)
            
            combined_annotations.extend([a for a in flair_query_annotation_dict.annotations 
                                         if a.position not in 
                                         [b.position for b in spacy_query_annotation_dict.annotations]])

        if self.heideltime_instance:
            heideltime_query_annotation_dict = self.heideltime_instance.transform_nl2query(nlq)
            heideltime_annotations = heideltime_query_annotation_dict.annotations.copy()
            # Deleting dates when inside a range
            range_annotations = [a for a in heideltime_annotations  if a.tempex_type == "range"]
            if range_annotations :
                for a in heideltime_query_annotation_dict.annotations:
                    if a.tempex_type != "range" :
                        for b in range_annotations:
                            if a.position[0] >= b.position[0] and a.position[1] <= b.position[1]:
                                heideltime_annotations.remove(a)
                                break
            combined_annotations.extend(heideltime_annotations)
            
        if self.varval_instance:
            varval_query_annotation_dict = self.varval_instance.transform_nl2query(nlq)
            combined_annotations.extend(varval_query_annotation_dict.annotations)
 
        combined_annotations.sort(key=lambda a:a.position[0])
        return QueryAnnotationsDict(query=nlq, annotations=combined_annotations)

if __name__ == "__main__":
    # query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    config_file = "combined_config.cfg"
    # call my nl2query class
    my_instance = Combined_NL2Query(config_file)
    # get the structured query from the nl query
    # structq = my_instance.transform_nl2query(query)
    # print("Structured query: ", structq)

    qfile = "ceda_gold_queries.json"
    ofile = "ceda_test_results.json"
    struct_results = []
    with open(qfile, 'r') as f:
        qs = json.load(f)
        if 'queries' in qs.keys():
            qlist = qs['queries']
            # iterate over queries
            for q in qlist:
                print(q)
                res = my_instance.transform_nl2query(q['query'])
                print(res)
                struct_results.append(res.to_dict())
        print(struct_results)
        with open(ofile, 'w') as f:
            json.dump({'queries': struct_results}, f)
