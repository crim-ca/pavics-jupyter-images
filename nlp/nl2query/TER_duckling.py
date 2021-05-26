from NL2QueryInterface import *
from duckling import *


class TER_duckling(NL2QueryInterface):
    """ Duckling implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        super().__init__(config)
        # start my Duckling engine
        try:
            self.duck = Duckling()
            print("Got Duckling at URL: ", self.duck.url)
            self.duck.locale = "en_GB"
            self.duck("")
        except Exception:
            print("Please make sure Docker is installed on your machine! "
                  "https://docs.docker.com/get-docker/.\n"
                  "Then run: \"docker pull rasa/duckling\""
                  "and \"docker run -p 8000:8000 rasa/duckling\"")

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typed annotation
        # filling in each slot as required

        # default
        val = annotation['value']
        if 'value' in val:
            val = val['value']
        elif 'to' in val:
            val = val['to']['value']
        if type(val) == int:
            val_type = "integer"
        else:
            val_type = "string"
        operation = "eq"

        return PropertyAnnotation(text=annotation['body'], position=[annotation['start'], annotation['end']],
                                  name="", value=val, value_type=val_type, operation=operation)

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        return LocationAnnotation(text=annotation.text,position=[annotation.start_char, annotation.end_char],
                                  matching_type="", name=annotation.text, value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        datetm = annotation['value']
        if 'value' in datetm:
            datetm = datetm['value']
        elif 'values' in datetm:
            datetm = datetm['values'][0]
        if type(datetm) == dict:
            datetm = {"start": datetm['from']['value'].split('.')[0]+"Z", "end": datetm['to']['value'].split('.')[0]+"Z"}
            t_type = "range"
        else:
            datetm = datetm.split('.')[0]+"Z"
            t_type = "point"
        return TemporalAnnotation(text=annotation['body'], position=[annotation['start'], annotation['end']],
                                  tempex_type=t_type, target="dataDate", value=datetm)

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation['text'], position=[annotation['start'], annotation['end']],
                                name=[""])

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        print("Query: \n", nlq)
        # collect annotations in a list of typed dicts
        annot_dicts = []
        # get annotations from my engine
        doc = self.duck(nlq)#, reference_time=str(datetime.datetime.today()))
        print("\nDuckling detected:")
        for d in doc:
            print(d['body'], d['value'], d['dim'])
            if d['dim'] == "time":
                annot_dicts.append(self.create_temporal_annotation(d))
            elif d['dim'] in ["number", "amount-of-money"]:
                annot_dicts.append(self.create_property_annotation(d))
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    # try 'last few years' in query!
    # You can define a config file if additional parameters required:
    # config_file = "duckling_config.cfg"
    # and pass it as: TER_duckling(config_file)
    # call my nl2query class
    my_instance = TER_duckling()
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("\nStructured query: ", structq)
