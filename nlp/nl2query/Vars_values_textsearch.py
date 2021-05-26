from NL2QueryInterface import *

class Vars_values_textsearch(NL2QueryInterface):

    def __init__(self, config:str = None):
        super().__init__(config)

    def create_location_annotation(self, annotation: Any) -> LocationAnnotation:
        return {}

    def create_property_annotation(self, annotation: Any) -> PropertyAnnotation:
        return {}

    def create_target_annotation(self, annotation: Any) -> TargetAnnotation:
        return {}

    def create_temporal_annotation(self, annotation: Any) -> TemporalAnnotation:
        return {}

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        return {}

if __name__ == "__main__":
    myvarval = Vars_values_textsearch()
    nlquery = "Sentinel-2 over Ottawa from april to september 2020 with cloud cover lower than 10%"
    structq = myvarval.transform_nl2query(nlq=nlquery)
    print("Structured query: ", structq)