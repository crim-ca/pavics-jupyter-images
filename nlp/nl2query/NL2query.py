from typing import TypedDict, List, Any
from configparser import ConfigParser
import os
import json


class Annotation:
    """class definition of one annotation.
    must include these fields """
    def __init__(self, text: str, position: List[int], annot_type: str):
        self.text = text
        self.position = position
        if annot_type in ["property", "location", "tempex", "target"]:
            self.annot_type = annot_type
        else:
            raise Exception("Unknown annotation type! "
                            "Must be one of: [property, location, tempex, target]")

    def to_dict(self):
        return {"text": self.text, "position": self.position, "type": self.annot_type}

    def __repr__(self):
        return json.dumps(self.to_dict())


class QueryAnnotationsDict:
    """ class definition of all annotations for a query"""
    def __init__(self, query: str, annotations: List[Annotation]):
        self.query = query
        self.annotations = annotations

    def to_dict(self):
        return {"query": self.query,
                "annotations": [annot.to_dict() for annot in self.annotations]}

    def __repr__(self):
        return json.dumps(self.to_dict())


class PropertyAnnotation(Annotation):
    """ class definition for a property annotation
    must include Annotation superclass fields
    and additional ones defined here """
    def __init__(self, text: str, position: List[int], name: str,
                 value: Any, value_type: str, operation: str):
        super().__init__(text, position, "property")
        self.name = name
        self.value = value
        if value_type in ["string", "percentage", "integer"]:
            self.value_type = value_type
        else:
            raise Exception("Unknown value type for property annotation! "
                            "Must be one of: [string, percentage, integer]")
        if operation in ["eq", "lt", "gt", "diff", "let", "get", "sort"]:
            self.operation = operation
        else:
            raise Exception("Unknown operation for property annotation! "
                            "Must be one of: [eq, lt, gt, diff, let, get, sort]")

    def to_dict(self):
        return {"text": self.text, "position": self.position, "type": "property",
                "name": self.name, "value": self.value, "value_type": self.value_type}

    def __repr__(self):
        return json.dumps(self.to_dict())


class LocationAnnotation(Annotation):
    """ class definition for a location annotation
        must include Annotation superclass fields
        and additional ones defined here """
    def __init__(self, text: str, position: List[int], name: str, value: Any, matching_type: str):
        super().__init__(text, position, "location")
        self.name = name
        self.value = value
        if matching_type in ["overlap", "intersect"]:
            self.matching_type = matching_type
        else:
            raise Exception("Unknown matching type for location annotation! "
                            "Must be one of: [overlap, intersect]")

    def to_dict(self):
        return {"text": self.text, "position": self.position, "type": "location",
                "name": self.name, "value": self.value, "matchingType": self.matching_type}

    def __repr__(self):
        return json.dumps(self.to_dict())


class TemporalAnnotation(Annotation):
    """ class definition for a temporal annotation
        must include Annotation superclass fields
        and additional ones defined here """
    def __init__(self, text: str, position: List[int], tempex_type: str, target: str, value: Any):
        super().__init__(text, position, "tempex")
        if tempex_type in ["range", "point"]:
            self.tempex_tye = tempex_type
        else:
            raise Exception("Unknown tempex type for temporal annotation! "
                            "Must be one of: [range, point]")
        if target in ["dataDate", "publishedDate"]:
            self.target = target
        else:
            raise Exception("Unknown target for temporal annotation! "
                            "Must be one of: [dataDate, publishedDate]")
        self.value = value

    def to_dict(self):
        return {"text": self.text, "position": self.position, "type": "tempex",
                "tempex_type": self.tempex_tye, "target": self.target}

    def __repr__(self):
        return json.dumps(self.to_dict())


class TargetAnnotation(Annotation):
    """ class definition for a target annotation
        must include Annotation superclass fields
        and additional ones defined here """
    def __init__(self, text: str, position: List[int], name: List[str]):
        super().__init__(text, position, "target")
        self.name = name

    def to_dict(self):
        return {"text": self.text, "position": self.position,
                "type": "target", "name": self.name}

    def __repr__(self):
        return json.dumps(self.to_dict())


class NL2Query:
    """ class defining the minimal interface
    that any Nl2query module should implement
    """

    def __init__(self, config_file: str = None):
        self.config = None
        if config_file:
            # parse the config file
            if os.path.exists(config_file):
                print("Reading config file: ", config_file)
                self.config = ConfigParser()
                self.config.read(config_file)
            else:
                print("Config file not found!")


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
