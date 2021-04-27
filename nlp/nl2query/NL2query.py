from typing import TypedDict, List, Any

class Annotation(TypedDict):
    """ typed dict definition of one annotation.
    must include these fields """
    text: str
    position: List[int]
    type: str

class QueryAnnotationsDict(TypedDict):
    """ typed dict definition of all annotations for a query"""
    query: str
    annotations: List[Annotation]

class PropertyAnnotation(Annotation):
    """ typed dict definition for a property annotation
    must include Annotation superclass fields
    and additional ones defined here """
    name: str
    value: Any
    value_type: str
    operation: str

class LocationAnnotation(Annotation):
    """ typed dict definition for a location annotation
        must include Annotation superclass fields
        and additional ones defined here """
    matchingType: str
    name: str
    value: Any

class TemporalAnnotation(Annotation):
    """ typed dict definition for a temporal annotation
        must include Annotation superclass fields
        and additional ones defined here """
    tempex_type: str
    target: str
    value: Any

class TargetAnnotation(Annotation):
    """ typed dict definition for a target annotation
        must include Annotation superclass fields
        and additional ones defined here """
    name: List[str]


class NL2Query:
    """ class defining the minimal interface
    that any Nl2query module should implement
    """
    # one config file per nl2query implementation
    config = None

    def __init__(self, config: str = None):
        NL2Query.config = config

    def transform_nl2query(self, nlq: str) -> QueryAnnotationsDict:
        """
        Takes a natural language query string and
        transforms it into a structured query
        by calling the nl2query engine.
        Returns the equivalent structured query in a
        predefined query annotations dict format.
        """
        pass

    def create_property_annotation(self, annotation: Any) -> PropertyAnnotation:
        """
        Takes an annotation output by the nl2query engine and
        transforms it into a predefined typed dict for property annotation.
        The annotation object is specific to the nl2query engine implementation.
        """
        pass

    def create_location_annotation(self, annotation: Any) -> LocationAnnotation:
        """
        Takes an annotation output by the nl2query engine and
        transforms it into a predefined typed dict for location annotation.
        The annotation object is specific to the nl2query engine implementation.
        """
        pass

    def create_temporal_annotation(self, annotation: Any) -> TemporalAnnotation:
        """
        Takes an annotation output by the nl2query engine and
        transforms it into a predefined typed dict for temporal annotation.
        The annotation object is specific to the nl2query engine implementation.
        """
        pass

    def create_target_annotation(self, annotation: Any) -> TargetAnnotation:
        """
        Takes an annotation output by the nl2query engine and
        transforms it into a predefined typed dict for target annotation.
        The annotation object is specific to the nl2query engine implementation.
        """
        pass
