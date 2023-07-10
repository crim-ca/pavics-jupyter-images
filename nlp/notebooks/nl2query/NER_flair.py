import requests
import json
from NL2QueryInterface import *
from flair.data import Sentence
from flair.models import SequenceTagger


class NER_flair(NL2QueryInterface):
    """ Flair NLP implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        super().__init__(config)
        # start my NL2query engine
        default = "ner-large"
        # Passing a config containing the local path to the model, otherwise it will download the model
        self.model_file = self.config.get("model_file","ner-large", fallback=default) if self.config else default
        # load the NER tagger
        self.tagger = SequenceTagger.load(self.model_file)

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required
        return PropertyAnnotation(text=annotation['text'], position=[annotation['start_pos'], annotation['end_pos']],
                                  name="", value="", value_type="string", operation="eq")

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        # use geogratis - only for Canada
        req = requests.get('http://geogratis.gc.ca/services/geolocation/en/locate?q=' + annotation['text'])
        if req.status_code == 200:
            result = json.loads(req.text)
            # take the first best match
            # TODO: develop a better heuristic than the first best match
            if result:
                if 'bbox' in result[0]:
                    # create polygon feature from bbox
                    geojson = {"type": "Polygon", "coordinates":
                               [[[result[0]['bbox'][i], result[0]['bbox'][i + 1]]
                                for i in range(0, len(result[0]['bbox']), 2)]]}
                elif 'geometry' in result[0]:
                    # point feature
                    geojson = result[0]['geometry']
        return LocationAnnotation(text=annotation['text'], position=[annotation['start_pos'], annotation['end_pos']],
                                  matching_type="overlap", name=annotation['text'], value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        return TemporalAnnotation(text=annotation['text'],  position=[annotation['start_pos'], annotation['end_pos']],
                                  tempex_type="", target="", value={})

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation['text'], position=[annotation['start_pos'], annotation['end_pos']],
                                name=[""])

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        # collect annotations in a list of typed dicts
        annot_dicts = []
        # get annotations from my engine
        # make a sentence
        sentence = Sentence(nlq)
        # run NER over sentence
        self.tagger.predict(sentence)
        for entity in sentence.to_dict(tag_type='ner')['entities']:
            # iterate over entities and print
            print(entity)
            # check the type and create appropriate annotation type
            if "LOC" in entity['labels'][0].value:
                annot_dicts.append(self.create_location_annotation(entity))
            else:
                annot_dicts.append(self.create_property_annotation(entity))
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    config_file = "flair_config.cfg"
    # call my nl2query class
    my_instance = NER_flair(config_file)
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query: ", structq)
