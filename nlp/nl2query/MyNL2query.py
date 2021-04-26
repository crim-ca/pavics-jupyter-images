from NL2query import *


class MyEngine:
    """ mockup class of an annotator engine """
    def __init__(self, config):
        # read config file and set necessary parameters
        return

    def get_annotations(self, nlq: str):
        # call the engine to annotate the nl query
        # and return a list of engine-specific annotations
        return [["geoname", "some identified text"], ["named entity", "some other text"]]


class MyNL2query(NL2Query):
    """ mockup class to try out NL2query interface"""
    engine = None

    def __init__(self, config: str = None):
        NL2Query.__init__(self, config)
        # start my NL2query engine
        self.engine = MyEngine(config)

    def create_property_annotation(self, annotation) -> PropertyAnnotation:
        # take annotation given by the engine
        # and create appropriate typeddict annotation
        # filling in each slot as required
        return PropertyAnnotation(text=annotation[1], type="property", position=[],
                                  name="", value="", value_type="", operation="")

    def create_location_annotation(self, annotation) -> LocationAnnotation:
        return LocationAnnotation(text=annotation[1], type="location", position=[],
                                  matchingType="", name="", value={})

    def create_temporal_annotation(self, annotation) -> TemporalAnnotation:
        return TemporalAnnotation(text=annotation[1], type="tempex", position=[],
                                  tempex_type="", target="", value={})

    def create_target_annotation(self, annotation) -> TargetAnnotation:
        return TargetAnnotation(text=annotation[1], type="target", position=[],
                                name="")

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        # get annotations from my engine
        engine_results = self.engine.get_annotations(nlq)
        # collect annotations in a list of typed dicts
        annot_dicts = []
        for result in engine_results:
            # check the type and create appropriate annotatation type
            if result[0] == "named entity":
                annot_dicts.append(self.create_property_annotation(result))
            elif result[0] == "geoname":
                annot_dicts.append(self.create_location_annotation(result))
            # elif etc...
        # return a query annotations typed dict as required
        return QueryAnnotationsDict(query=nlq, annotations=annot_dicts)


if __name__ == "__main__":
    query = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    config_file = "config.ini"
    # call my nl2query class
    my_instance = MyNL2query(config_file)
    # get the structured query from the nl query
    structq = my_instance.transform_nl2query(query)
    print("Structured query: ", structq)
