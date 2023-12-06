from nl2query.NL2QueryInterface import (
    LocationAnnotation,
    NL2QueryInterface,
    PropertyAnnotation,
    QueryAnnotationsDict,
    TargetAnnotation,
    TemporalAnnotation
)


class MyEngine:
    """ mockup class of an annotator engine """
    def __init__(self, config):
        # read config file and set necessary parameters
        return

    def get_annotations(self, nlq: str):
        # call the engine to annotate the nl query
        # and return a list of engine-specific annotations
        return [["geoname", "some identified location", 20, 40],
                ["named entity", "some text", 13, 28],
                ["time", "from x to y", 55, 66],
                ["var", 'cmpi6', 70, 75]]


class MyNL2query(NL2QueryInterface):
    """ mockup class to try out NL2query interface"""

    def __init__(self, config_file: str = None):
        # call super's implementation of init
        # to handle config file reading
        super().__init__(config_file)
        print("Config contents:", self.config)
        # start my NL2query engine
        # self.config being a dict created by NL2Query.__init__
        self.engine = MyEngine(self.config)

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate annotation class
        # filling in each slot as required
        return PropertyAnnotation(text=annotation[1], position=[annotation[2], annotation[3]],
                                  name="", value=annotation[1], value_type="string", operation="eq")

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        return LocationAnnotation(text=annotation[1], position=[annotation[2], annotation[3]],
                                  name="", value={}, matching_type="overlap")

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        return TemporalAnnotation(text=annotation[1], position=[annotation[2], annotation[3]],
                                  tempex_type="range", target="dataDate", value=("x", "y"))

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation[1], position=[annotation[2], annotation[3]],
                                name=[annotation[1]])

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        # get annotations from my engine
        engine_results = self.engine.get_annotations(nlq)
        # collect annotations in a list of typed dicts
        annot_dicts = []
        for result in engine_results:
            print(result)
            # check the type and create appropriate annotatation type
            if result[0] == "named entity":
                annot_dicts.append(self.create_property_annotation(result))
            elif result[0] == "geoname":
                annot_dicts.append(self.create_location_annotation(result))
            elif result[0] == "time":
                annot_dicts.append(self.create_temporal_annotation(result))
            elif result[0] == "var":
                annot_dicts.append(self.create_target_annotation(result))
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    config_f = "config.ini"
    # call my nl2query class
    my_instance = MyNL2query(config_f)
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query as Dict: ", structq.to_dict())
    print("Structured query as string: ", structq)
