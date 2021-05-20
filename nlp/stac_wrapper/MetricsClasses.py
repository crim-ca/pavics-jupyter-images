

ANNOTATION_TYPES = ["property", "location", "tempex", "target"]

class DataMetrics:

    def __init__(self, total_ann: int = 0, total_prop: int = 0, total_loc: int = 0,
                 total_temp: int= 0, total_targ: int = 0,
                 annot_avg: float = 0.0, annot_min: int = 0, annot_max: int = 0):
        self.total_annotation = total_ann
        self.total_annotation_property = total_prop
        self.total_annotation_location = total_loc
        self.total_annotation_tempex = total_temp
        self.total_annotation_target = total_targ
        self.annotation_per_query_avg = annot_avg
        self.annotation_per_query_min = annot_min
        self.annotation_per_query_max = annot_max


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


    @staticmethod
    def create_data_metrics(total_ann: int = 0, total_prop: int = 0, total_loc: int = 0,
                 total_temp: int= 0, total_targ: int = 0,
                 annot_avg: float = 0.0, annot_min: int = 0, annot_max: int = 0):
        return {"total_annotation": total_ann,
                "total_annotation_per_type": {
                    "property": total_prop,
                    "location": total_loc,
                    "tempex": total_temp,
                    "target": total_targ
                },
                "annotation_per_query": {"avg": annot_avg,
                                         "min": annot_min,
                                         "max": annot_max}
                }


class DataMeasures:
    def __init__(self, gold_metrics: DataMetrics = None, test_metrics: DataMetrics = None):
        self.gold_metrics = gold_metrics
        self.test_metrics = test_metrics

    def to_dict(self):
        return {"gold_data": self.gold_metrics.to_dict(),
                "test_data": self.test_metrics.to_dict()}

    @staticmethod
    def get_data_measures():
        return {"gold_data": DataMetrics.create_data_metrics(),
                "test_data": DataMetrics.create_data_metrics()}


class SpanMetrics:
    def __init__(self, count: int = 0, perfect_match_type: float = 0.0,
                 perfect_match_no_type: float = 0.0,
                 perfect_begin_type: float = 0.0, perfect_begin_no_type: float = 0.0,
                 perfect_end_type: float = 0.0, perfect_end_no_type: float = 0.0,
                 split_gold_type: int = 0, split_gold_no_type: int = 0,
                 split_test_type: int = 0, split_test_no_type: int = 0,
                 overlapping_no_type_avg: float = 0.0, overlapping_no_type_min: int = 0,
                 overlapping_no_type_max: int = 0, overlapping_type_avg: float = 0.0,
                 overlapping_type_min: int = 0, overlapping_type_max: int = 0):
        self.count = count
        self.perfect_match_type_match = perfect_match_type
        self.perfect_match_no_type_match = perfect_match_no_type
        self.perfect_begin_type_match = perfect_begin_type
        self.perfect_begin_no_type_match = perfect_begin_no_type
        self.perfect_end_type_match = perfect_end_type
        self.perfect_end_no_type_match = perfect_end_no_type
        self.split_gold_type_match = split_gold_type
        self.split_gold_no_type_match = split_gold_no_type
        self.split_test_type_match = split_test_type
        self.split_test_type_no_type_match = split_test_no_type
        self.overlapping_span_no_type_match_avg = overlapping_no_type_avg
        self.overlapping_span_no_type_match_min = overlapping_no_type_min
        self.overlapping_span_no_type_match_max = overlapping_no_type_max
        self.overlapping_span_type_match_avg = overlapping_type_avg
        self.overlapping_span_type_match_min = overlapping_type_min
        self.overlapping_span_type_match_max = overlapping_type_max

    def to_dict(self):
        return {"count": self.count,
                "perfect_match": {"no_type_match": self.perfect_match_no_type_match,
                                  "type_match": self.perfect_match_type_match},
                "perfect_begin": {"no_type_match": self.perfect_begin_no_type_match,
                                  "type_match": self.perfect_begin_type_match},
                "perfect_end": {"no_type_match": self.perfect_end_no_type_match,
                                "type_match": self.perfect_end_type_match},
                "split_gold_span": {"no_type_match": self.split_gold_no_type_match,
                                    "type_match": self.split_gold_type_match},
                "split_test_span": {"no_type_match": self.split_test_type_no_type_match,
                                    "type_match": self.split_test_type_match},
                "overlapping_span": {
                     "no_type_match": {"avg": self.overlapping_span_no_type_match_avg,
                                       "min": self.overlapping_span_no_type_match_min,
                                       "max": self.overlapping_span_no_type_match_max},
                     "type_match": {"avg": self.overlapping_span_type_match_avg,
                                    "min": self.overlapping_span_type_match_min,
                                    "max": self.overlapping_span_type_match_max}
                 }
                }

    @staticmethod
    def get_span_metrics(count: int = 0, perfect_match_type: float = 0.0,
                         perfect_match_no_type: float = 0.0,
                         perfect_begin_type: float = 0.0,
                         perfect_begin_no_type: float = 0.0,
                         perfect_end_type: float = 0.0,
                         perfect_end_no_type: float = 0.0,
                         split_gold_type: int = 0,
                         split_gold_no_type: int = 0,
                         split_test_type: int = 0,
                         split_test_no_type: int = 0,
                         overlapping_no_type_avg: float = 0.0,
                         overlapping_no_type_min: int = 0,
                         overlapping_no_type_max: int = 0,
                         overlapping_type_avg: float = 0.0,
                         overlapping_type_min: int = 0,
                         overlapping_type_max: int = 0):
        return {"count": count,
                "perfect_match": {"no_type_match": perfect_match_no_type,
                                  "type_match": perfect_match_type},
                "perfect_begin": {"no_type_match": perfect_begin_no_type,
                                  "type_match": perfect_begin_type},
                "perfect_end": {"no_type_match": perfect_end_no_type,
                                "type_match": perfect_end_type},
                "split_gold_span": {"no_type_match": split_gold_no_type,
                                    "type_match": split_gold_type},
                "split_test_span": {"no_type_match": split_test_no_type,
                                    "type_match": split_test_type},
                "overlapping_span": {
                     "no_type_match": {"avg": overlapping_no_type_avg,
                                       "min": overlapping_no_type_min,
                                       "max": overlapping_no_type_max},
                     "type_match": {"avg": overlapping_type_avg,
                                    "min": overlapping_type_min,
                                    "max": overlapping_type_max}
                 }
                }


class SpanMeasures:

    @staticmethod
    def get_span_measures():
        return {"global": SpanMetrics.get_span_metrics(),
                "property": SpanMetrics.get_span_metrics(),
                "location": SpanMetrics.get_span_metrics(),
                "tempex": SpanMetrics.get_span_metrics(),
                "target": SpanMetrics.get_span_metrics()
                }


class AttributeMetrics:

    @staticmethod
    def get_attribute_metrics():
        return {}


class ValueMetrics:
    @staticmethod
    def get_value_metrics():
        return {}