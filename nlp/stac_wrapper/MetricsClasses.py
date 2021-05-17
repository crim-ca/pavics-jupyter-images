

class DataMetrics:

    def __init__(self, total_ann: int = 0, total_prop: int = 0, total_loc: int = 0,
                 total_temp: int= 0, total_targ: int = 0,
                 annot_avg: float = 0.0, annot_min: int = 0, annot_max: int = 0):
        self.total_annotation = total_ann
        self.total_annotation_property = total_prop
        self.total_annotation_location = total_loc
        self.total_annotation_tempex = total_temp
        self.total_annotation_target = total_targ
        self.total_annotation_per_type = [self.total_annotation_property,
                                          self.total_annotation_location,
                                          self.total_annotation_tempex,
                                          self.total_annotation_target]
        self.annotation_per_query_avg = annot_avg
        self.annotation_per_query_min = annot_min
        self.annotation_per_query_max = annot_max
        self.annotation_per_query = [self.annotation_per_query_avg,
                                     self.annotation_per_query_min,
                                     self.annotation_per_query_max]


    def to_dict(self):
        return {"total_annotation": self.total_annotation,
                "total_annotation_per_type": {
                     "property": self.total_annotation_property,
                     "location": self.total_annotation_location,
                     "tempex": self.total_annotation_tempex,
                     "target": self.total_annotation_target
                },
                "annotation_per_query": {"avg": self.annotation_per_query_avg,
                                         "min": self.annotation_per_query_min,
                                         "max": self.annotation_per_query_max}
                }


