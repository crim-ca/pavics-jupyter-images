from NL2QueryInterface import *
import spacy
import requests
import re
import json

class NER_spacy(NL2QueryInterface):
    """ Spacy implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        super().__init__(config)
        # start my NL2query engine
        default = "en_core_web_trf"
        # Getting model from a config file, otherwise use the default model
        self.model = self.config.get("components.ner","source", fallback=default) if self.config else default
        self.spacy_engine = spacy.load(self.model)
#        self.spacy_engine = Language.from_config(self.config)

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required

        # default
        val = annotation.text
        val_type = "string"
        operation = "eq"

        # extract numerical value
        if annotation.label_ in ["QUANTITY", "CARDINAL", "PERCENT"]:
            val = re.search(r"[+-]?\d+", annotation.text).group(0)
            if val:
                val = int(val)
            else:
                val = re.search(r"[+-]?\d+(?:\.\d+)?", annotation.text).group(0)
                val = float(val)
            val_type = "integer"
            # extract operation ex: "less than" -> "lt"
            print("Need a parser to detect operation! ex: less than -> lt. Default is 'eq'.")
            operation = "eq"
        if annotation.label_ == "PERCENT":
            val_type = "percentage"
        return PropertyAnnotation(text=annotation.text, position=[annotation.start_char, annotation.end_char],
                                  name="", value=val, value_type=val_type, operation=operation)

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        # use geogratis - only for Canada
        req = requests.get('http://geogratis.gc.ca/services/geolocation/en/locate?q=' + annotation.text)
        if req.status_code == 200:
            result = json.loads(req.text)
            # take the first best match
            # TODO: develop a better heuristic than the first best match
            if result:
                if 'bbox' in result[0]:
                    # create polygon feature from bbox
                    geojson = {"type": "Polygon", "coordinates":
                               [[[result[0]['bbox'][i], result[0]['bbox'][i+1]]
                                for i in range(0, len(result[0]['bbox']), 2)]]}
                elif 'geometry' in result[0]:
                    # point feature
                    geojson = result[0]['geometry']
        return LocationAnnotation(text=annotation.text,  position=[annotation.start_char, annotation.end_char],
                                  matching_type="overlap", name=annotation.text, value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        datetime = {}
        print("Need a datestring parser to get the actual value. We don't know in what format the string date is!")
        return TemporalAnnotation(text=annotation.text, position=[annotation.start_char, annotation.end_char],
                                  tempex_type="range", target="dataDate", value=datetime)

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation.text, position=[annotation.start_char, annotation.end_char],
                                name=[""])

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        # get annotations from my engine
        doc = self.spacy_engine(nlq)
        # collect annotations in a list of typed dicts
        annot_dicts = []
        for ent in doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
            # check the type and create appropriate annotatation type
            if ent.label_ in ["PERCENT", "QUANTITY", "ORDINAL", "CARDINAL",
                              "PERSON", "NORP", "ORGANIZATION", "FACILITY"]:
                annot_dicts.append(self.create_property_annotation(ent))
            elif ent.label_ in ["GPE", "LOCATION"]:
                annot_dicts.append(self.create_location_annotation(ent))
            elif ent.label_ in ["DATE", "TIME"]:
                annot_dicts.append(self.create_temporal_annotation(ent))
            elif ent.label_ in []:
                annot_dicts.append(self.create_target_annotation(ent))
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    config_file = "spacy_config.cfg"
    # call my nl2query class
    my_instance = NER_spacy(config_file)
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query: ", structq)