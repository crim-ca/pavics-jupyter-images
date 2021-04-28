from NL2query import *
from flair.data import Sentence
from flair.models import SequenceTagger

class NER_flair(NL2Query):
    """ Flair NLP implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        NL2Query.__init__(self, config)
        # start my NL2query engine
        # load the NER tagger
        self.tagger = SequenceTagger.load('ner-large')

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required
        return PropertyAnnotation(text=annotation['text'], type="property", position=[annotation['start_pos'], annotation['end_pos']],
                                  name="", value="", value_type="", operation="")

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        return LocationAnnotation(text=annotation['text'], type="location", position=[annotation['start_pos'], annotation['end_pos']],
                                  matchingType="", name=annotation['text'], value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        return TemporalAnnotation(text=annotation['text'], type="tempex", position=[annotation['start_pos'], annotation['end_pos']],
                                  tempex_type="", target="", value={})

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation['text'], type="target", position=[annotation['start_pos'], annotation['end_pos']],
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
