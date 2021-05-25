from jpype._jvmfinder import JVMNotFoundException
from NL2QueryInterface import *
from duckling import DucklingWrapper

class TER_duckling(NL2QueryInterface):
    """ Duckling implementation of the NL2query interface"""

    def __init__(self, config: str = None):
        super().__init__(config)
        # start my Duckling engine
        try:
            self.duck = DucklingWrapper()
        except JVMNotFoundException:
            print("Please install a Java Virtual Machine (JVM) on your machine "
                  "to run the Duckling temporal expression recognizer!")

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required

        # default
        val = annotation['value']['value']
        if annotation['dim'] in ["number", "quantity"]:
            val_type = "integer"
        else:
            val_type = "string"
        operation = "eq"

        return PropertyAnnotation(text=annotation['text'], position=[annotation['start'], annotation['end']],
                                  name="", value=val, value_type=val_type, operation=operation)

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        # get gejson of location
        geojson = {}
        return LocationAnnotation(text=annotation.text,position=[annotation.start_char, annotation.end_char],
                                  matching_type="", name=annotation.text, value=geojson)

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        # get standard dateformat from text
        datetm = annotation['value']['value']
        if type(datetm) == dict:
            datetm = {"start": datetm['from'].split('.')[0]+"Z", "end": datetm['to'].split('.')[0]+"Z"}
            t_type = "range"
        else:
            datetm = datetm.split('.')[0]+"Z"
            t_type = "point"
        return TemporalAnnotation(text=annotation['text'], position=[annotation['start'], annotation['end']],
                                  tempex_type=t_type, target="dataDate", value=datetm)

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation['text'], position=[annotation['start'], annotation['end']],
                                name=[""])

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        # collect annotations in a list of typed dicts
        annot_dicts = []
        # get annotations from my engine
        doc1 = self.duck.parse_time(nlq)#, reference_time=str(datetime.datetime.today()))
        doc2 = self.duck.parse_duration(nlq)
        for d in doc1+doc2:
            print(d)
            annot_dicts.append(self.create_temporal_annotation(d))
        doc1 = self.duck.parse_number(nlq)
        doc2 = self.duck.parse_quantity(nlq)
        for d in doc1+doc2:
            print(d)
            annot_dicts.append(self.create_property_annotation(d))
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    config_file = "duckling_config.cfg"
    # call my nl2query class
    my_instance = TER_duckling(config_file)
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query: ", structq)
