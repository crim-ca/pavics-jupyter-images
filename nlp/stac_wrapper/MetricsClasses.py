from typing import List, Dict, Any
from shapely.geometry import Polygon
from Levenshtein import distance
import datetime

ANNOTATION_TYPES = ["property", "location", "tempex", "target"]
VALUE_TYPES = ["global", "type", "name", "bbox", "tempex", "numeric", "target"]


class DataMetrics:

    def __init__(self, total_ann: int = 0, total_prop: int = 0, total_loc: int = 0,
                 total_temp: int = 0, total_targ: int = 0,
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
    def create_data_metrics(annotations: List[Dict]) -> DataMetrics:
        if annotations:
            ann_types = [ann['type'] for ann in annotations]
            # create data metrics class instance
            return DataMetrics(total_ann=len(annotations), total_prop=ann_types.count('property'),
                               total_loc=ann_types.count('location'), total_temp=ann_types.count('tempex'),
                               total_targ=ann_types.count('target'))
        else:
            return DataMetrics()


class DataMeasures:
    def __init__(self, gold_metrics: DataMetrics = None, test_metrics: DataMetrics = None):
        if gold_metrics:
            self.gold_metrics = gold_metrics
        else:
            self.gold_metrics = DataMetrics()
        if test_metrics:
            self.test_metrics = test_metrics
        else:
            self.test_metrics = DataMetrics()

    def to_dict(self):
        return {"gold_data": self.gold_metrics.to_dict(),
                "test_data": self.test_metrics.to_dict()}

    @staticmethod
    def get_data_measures(gold: List[Dict], test: List[Dict]) -> Dict:
        return DataMeasures(DataMetrics.create_data_metrics(gold),
                            DataMetrics.create_data_metrics(test)).to_dict()


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


class SpanMeasures:

    def __init__(self, global_span: SpanMetrics = None, prop_span: SpanMetrics = None,
                 loc_span: SpanMetrics = None,
                 temp_span: SpanMetrics = None, targ_span: SpanMetrics = None):
        if global_span:
            self.global_span = global_span
        else:
            self.global_span = SpanMetrics()
        if prop_span:
            self.property_span = prop_span
        else:
            self.property_span = SpanMetrics()
        if loc_span:
            self.location_span = loc_span
        else:
            self.location_span = SpanMetrics()
        if temp_span:
            self.tempex_span = temp_span
        else:
            self.tempex_span = SpanMetrics()
        if targ_span:
            self.target_span = targ_span
        else:
            self.target_span = SpanMetrics()

    def to_dict(self):
        return {"global": self.global_span.to_dict(),
                "property": self.property_span.to_dict(),
                "location": self.location_span.to_dict(),
                "tempex": self.tempex_span.to_dict(),
                "target": self.target_span.to_dict()
                }

    @staticmethod
    def get_span_measures(gold: List[Dict], test: List[Dict]) -> Dict:
        span_measures = SpanMeasures().to_dict()

        gold_types = [ann['type'] for ann in gold]
        gold_spans = [ann['position'] for ann in gold]
        test_types = [ann['type'] for ann in test]
        test_spans = [ann['position'] for ann in test]

        # print(gold_spans)
        # print(test_spans)
        # TODO! if gold_spans is only length 1, the result has an empty item in the list?
        for idx, span in enumerate(test_spans):
            # update count
            span_measures[test_types[idx]]['count'] += 1
            # perfect match
            if span in gold_spans:
                # exact match
                # update type-specific count
                # check for type match
                gold_idx = gold_spans.index(span)  # we do not presume the test and gold are aligned
                if test_types[idx] == gold_types[gold_idx]:
                    span_measures[test_types[idx]]['perfect_match']['type_match'] += 1
                else:
                    span_measures[test_types[idx]]['perfect_match']['no_type_match'] += 1
            else:
                # not perfect match
                # check for some kind of overlap
                # overlapping spans
                overlap_count = 0
                type_match_count = 0
                for gidx, gspan in enumerate(gold_spans):
                    if range(max(span[0], gspan[0]), min(span[-1], gspan[-1])):
                        # includes perfect end and begin
                        if test_types[idx] == gold_types[gidx]:
                            span_measures[test_types[idx]]['overlapping_span']['type_match']['min'] += 1
                            type_match_count += 1
                        else:
                            span_measures[test_types[idx]]['overlapping_span']['no_type_match']['min'] += 1
                        # perfect begin
                        if span[0] == gold_spans[gidx][0]:
                            # begin match (including exact match)
                            # update type-specific count
                            if test_types[idx] == gold_types[gidx]:
                                span_measures[test_types[idx]]['perfect_begin']['type_match'] += 1
                            else:
                                span_measures[test_types[idx]]['perfect_begin']['no_type_match'] += 1
                        # perfect end
                        if span[1] == gold_spans[gidx][1]:
                            # end match (including exact match)
                            # update type-specific count
                            if test_types[idx] == gold_types[gidx]:
                                span_measures[test_types[idx]]['perfect_end']['type_match'] += 1
                            else:
                                span_measures[test_types[idx]]['perfect_end']['no_type_match'] += 1
                        overlap_count += 1
                    if overlap_count > 1:
                        # this test span matches several gold spans = split-test
                        if overlap_count == type_match_count:
                            span_measures[test_types[idx]]['split_test_span']['type_match'] += 1
                        else:
                            span_measures[test_types[idx]]['split_test_span']['no_type_match'] += 1

        # split gold
        for gidx, gspan in enumerate(gold_spans):
            split_count = 0
            type_match_count = 0
            for tspan in test_spans:
                if range(max(gspan[0], tspan[0]), min(gspan[-1], tspan[-1])):
                    split_count += 1
                    if gold_types[gidx] == test_types[test_spans.index(tspan)]:
                        type_match_count += 1

            if split_count > 1:
                # we have split gold span
                if split_count == type_match_count:
                    span_measures[gold_types[gidx]]['split_gold_span']['type_match'] += 1
                else:
                    span_measures[gold_types[gidx]]['split_gold_span']['no_type_match'] += 1
        return span_measures


class AttributeMetrics:

    def __init__(self, count: int = 0, total_span_type_match: int = 0,
                 perfect_match_precision: float = 0.0, overlapping_perfect_match: float = 0.0,
                 attribute_match_avg: float = 0.0, attribute_match_min: int = 0, attribute_match_max: int = 0):
        self.count = count
        self.total_span_type_match = total_span_type_match
        self.perfect_match_precision = perfect_match_precision
        self.overlapping_perfect_match = overlapping_perfect_match
        self.attribute_match_avg = attribute_match_avg
        self.attribute_match_min = attribute_match_min
        self.attribute_match_max = attribute_match_max

    def to_dict(self):
        return {"count": self.count,
                "total_span_type_match": self.total_span_type_match,
                "per_annotation_span_perfect_match_precision": self.perfect_match_precision,
                "per_annotation_overlapping_span_perfect_match": self.overlapping_perfect_match,
                "per_annotation_attribute_match": {
                    "avg": self.attribute_match_avg,
                    "min": self.attribute_match_min,
                    "max": self.attribute_match_max
                }}


class AttributeMeasures:

    def __init__(self, prop_attr: AttributeMetrics = None, loc_attr: AttributeMetrics = None,
                 temp_attr: AttributeMetrics = None, targ_attr: AttributeMetrics = None):
        if prop_attr:
            self.property_attribute = prop_attr
        else:
            self.property_attribute = AttributeMetrics()
        if loc_attr:
            self.location_attribute = loc_attr
        else:
            self.location_attribute = AttributeMetrics()
        if temp_attr:
            self.tempex_attribute = temp_attr
        else:
            self.tempex_attribute = AttributeMetrics()
        if targ_attr:
            self.target_attribute = targ_attr
        else:
            self.target_attribute = AttributeMetrics()

    def to_dict(self):
        return {
            "property": self.property_attribute.to_dict(),
            "location": self.location_attribute.to_dict(),
            "tempex": self.tempex_attribute.to_dict(),
            "target": self.target_attribute.to_dict()
        }

    @staticmethod
    def get_attribute_measures(gold: List[Dict], test: List[Dict]) -> Dict:
        # create measures dictionary
        attribute_measures = AttributeMeasures().to_dict()
        gold_spans = [gspan['position'] for gspan in gold]
        gold_types = [gspan['type'] for gspan in gold]
        gold_ann = list(gold)
        # count of annotations per types
        count = {}
        for annot_type in ANNOTATION_TYPES:
            count[annot_type] = len([x for x in test if x['type'] == annot_type])

        for ann in test:
            # count how many attributes in test
            # obligatory for property, tempex, location: type, position, name, value
            # obligatory for target: type, position, name
            test_type = ann['type']
            attribute_measures[test_type]['count'] += len(ann)
            test_span = ann['position']
            # exact span match
            if test_span in gold_spans:
                gidx = gold_spans.index(test_span)
                # per_annotation_span_perfect_match_precision
                # % of annotation having all attribute matched when span is same
                if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                    attribute_measures[test_type]['per_annotation_span_perfect_match_precision'] += 1
            else:
                # no exact span match, find overlapping span match
                for gidx, gspan in enumerate(gold_spans):
                    # overlapping span
                    if range(max(gspan[0], test_span[0]), min(gspan[-1], test_span[-1])):
                        # total_span_type_match
                        # nr of attributes where matching span+type
                        # the same as in the measures overlapping_span:type_match
                        # but as a count instead of %
                        # exact type match
                        if test_type == gold_types[gidx]:
                            attribute_measures[test_type]['total_span_type_match'] += 1
                        # per_annotation_overlapping_span_perfect_match
                        # % of annotation having all attribute matched, for overlapping span
                        if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                            attribute_measures[test_type]['per_annotation_overlapping_span_perfect_match'] += 1
                        # per_annotation_attribute_match
                        # % of matching attribute name / total number of attribute in an annotation
                        # compared to overlapping spans
                        attribute_measures[test_type]['per_annotation_attribute_match']['min'] = \
                            len(set(ann.keys()).intersection(gold_ann[gidx].keys())) / len(ann)

        for annot_type in ANNOTATION_TYPES:
            # count of annotations of all attributes matched for exact span / nr of annots of that type
            attribute_measures[annot_type]['per_annotation_span_perfect_match_precision'] = \
                attribute_measures[annot_type]['per_annotation_span_perfect_match_precision'] / count[annot_type] if \
                count[annot_type] else 0
            # per_annotation_overlapping_span_perfect_match
            attribute_measures[annot_type]['per_annotation_overlapping_span_perfect_match'] = \
                attribute_measures[annot_type]['per_annotation_overlapping_span_perfect_match'] / count[annot_type] if \
                count[annot_type] else 0

        return attribute_measures


def levenshtein(str1: str, str2: str) -> int:
    """
    Calculate the Levenshtein distance
    between two strings
    """
    return distance(str1, str2)


def intersect_over_union(bbox1: Dict, bbox2: Dict) -> float:
    """
    Calculate intersect over union of two geojson features
    that are either polygons or points.
    """
    # polygons require min 3 coordinate tuples
    if 'coordinates' in bbox1 and 'coordinates' in bbox2 and \
            len(bbox1['coordinates']) > 2 and len(bbox2['coordinates']) > 2:
        poly1 = Polygon(bbox1['coordinates'])
        poly2 = Polygon(bbox2['coordinates'])
        polygon_intersection = poly1.intersection(poly2).area
        polygon_union = poly1.union(poly2).area
        iou = polygon_intersection / polygon_union
        return iou
    # how to calculate for points?
    if bbox1['type'] == "Point" and bbox2['type'] == "Point":
        if bbox1['coordinates'] == bbox2['coordinates']:
            return 1
    return 0


def duration_overlap(dur1, dur2) -> int:
    """
    Function to calculate the overlap (in number of days)
    of two date ranges given in a specific format
    Returns 0 if no overlap found.
    """
    dformat = '%Y-%m-%dT%H:%M:%SZ'
    # datarange {'start': startdate, 'end': enddate}
    if len(dur1) == 2 and len(dur2) == 2 and 'start' in dur1 and 'start' in dur2:
        r1_start = datetime.datetime.strptime(dur1['start'], dformat)
        r1_end = datetime.datetime.strptime(dur1['end'], dformat)
        r2_start = datetime.datetime.strptime(dur2['start'], dformat)
        r2_end = datetime.datetime.strptime(dur2['end'], dformat)
        overlap = min(r1_end - r2_start, r2_end - r1_start).days + 1
        return overlap if overlap > 0 else 0
    # datetime strings
    if dur1 == dur2:
        return 1
    return 0


def isnumeric(str_value: Any) -> bool:
    """
    Simple function to check if the passed parameter can be
    converted into a numeric value or not.
    Returns boolean true if yes, false otherwise.
    """
    try:
        if type(str_value) == dict:
            return False
        float(str_value)
        return True
    except ValueError:
        # we don't treat here the exception
        # it's enough to know that it's not numeric
        return False


class ValueMeasures:
    def __init__(self):
        self.global_smth = 0

    def to_dict(self):
        return {"global":  {"total_matching_attributes": 0, "perfect_value_match": 0.0,
                            "ratio_matching_attributes": 0.0},
                "type": {"total_matching_attributes": 0, "perfect_value_match": 0.0},
                "name": {"total_matching_attributes": 0, "perfect_value_match": 0.0,
                         "levenstein": {"avg": 0.0, "min": 0, "max": 0}},
                "bbox": {"total_matching_attributes": 0, "perfect_value_match": 0.0,
                         "intersect_over_union": {"avg": 0.0, "min": 0, "max": 0}},
                "tempex": {"total_matching_attributes": 0, "perfect_value_match": 0.0,
                           "duration_overlap": {"avg": 0.0, "min": 0, "max": 0}},
                "numeric": {"total_matching_attributes": 0, "perfect_value_match": 0.0,
                            "value_offset": {"avg": 0.0, "min": 0, "max": 0}},
                "target": {"total_matching_attributes": 0, "perfect_value_match": 0.0,
                           "matching_element": {"avg": 0.0, "min": 0, "max": 0}}
                }

    @staticmethod
    def get_value_measures(gold: List[Dict], test: List[Dict]) -> Dict:
        # create measures dictionary
        value_measures = ValueMeasures().to_dict()
        # add special keys

        gold_spans = [gspan['position'] for gspan in gold]
        gold_types = [gspan['type'] for gspan in gold]
        gold_ann = list(gold)
        for ann in test:
            test_type = ann['type']
            test_span = ann['position']
            # how many location/tempex attributes we have
            if test_type == 'location':
                value_measures['bbox']['total_matching_attributes'] += 1
            if test_type == 'tempex':
                value_measures['tempex']['total_matching_attributes'] += 1
            if test_type == 'target':
                value_measures['target']['total_matching_attributes'] += 1
            if 'name' in ann.keys():
                value_measures['name']['total_matching_attributes'] += 1
            if 'value' in ann.keys() and type(ann['value']) == str:
                # print(ann['value'])
                if isnumeric(ann['value']):
                    value_measures['numeric']['total_matching_attributes'] += 1
            for gidx, gspan in enumerate(gold_spans):
                # overlapping span
                if range(max(gspan[0], test_span[0]), min(gspan[-1], test_span[-1])):
                    # all attributes match
                    if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                        value_measures['global']['total_matching_attributes'] += 1
                    #  for matching attribute type
                    if gold_types[gidx] == test_type:
                        value_measures['type']['perfect_value_match'] += 1
                        if test_type == 'location':
                            if ann['value'] == gold_ann[gidx]['value']:
                                value_measures['bbox']['perfect_value_match'] += 1
                            value_measures['bbox']["intersect_over_union"]['min'] = \
                                intersect_over_union(ann['value'], gold_ann[gidx]['value'])
                        if test_type == 'tempex':
                            if ann['value'] == gold_ann[gidx]['value']:
                                value_measures['tempex']['perfect_value_match'] += 1
                            value_measures['tempex']["duration_overlap"]['min'] = \
                                duration_overlap(ann['value'], gold_ann[gidx]['value'])
                        if test_type == 'target':
                            if ann['name'] == gold_ann[gidx]['name']:
                                value_measures['target']['perfect_value_match'] += 1
                            value_measures['target']['matching_element']['min'] = \
                                len(set(ann['name']).intersection(gold_ann[gidx]['name']))
                        if test_type != 'tempex':
                            if gold_ann[gidx]['name'] == ann['name']:
                                value_measures['name']['perfect_value_match'] += 1
                            if test_type != 'target':
                                value_measures['name']["levenstein"]['min'] = \
                                    levenshtein(ann['name'].lower(), gold_ann[gidx]['name'].lower())
                        if 'value' in gold_ann[gidx].keys() and isnumeric(gold_ann[gidx]['value']) \
                                and isnumeric(ann['value']):
                            if gold_ann[gidx]['value'] == ann['value']:
                                value_measures['numeric']['perfect_value_match'] += 1
                            value_measures['numeric']['value_offset']['min'] = \
                                abs(float(ann['value']) - float(gold_ann[gidx]['value']))
        # there are as many type attribute counts, as many annotations
        value_measures['type']['total_matching_attributes'] = len(test)
        for value_type in VALUE_TYPES:
            if value_measures[value_type]['total_matching_attributes']:
                value_measures[value_type]['perfect_value_match'] = \
                    value_measures[value_type]['perfect_value_match'] \
                    / value_measures[value_type]['total_matching_attributes']

        value_measures['global']['ratio_matching_attributes'] = \
            value_measures['global']['total_matching_attributes'] / len(test)

        return value_measures
