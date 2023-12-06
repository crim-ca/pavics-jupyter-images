import datetime
import re
from typing import Any, Dict, List

from Levenshtein import distance
from shapely.geometry import Polygon

from typedefs import JSON, Number

# global variables
DATA_TYPES = ['gold_data', 'test_data']
ANNOTATION_TYPES = ["property", "location", "tempex", "target"]
VALUE_TYPES = ["type", "name", "bbox", "tempex", "numeric", "target"]


class MinMaxAvg:
    """
    Class that defines a minimum, a maximum and an average value
    calculated from a list of numeric values.
    """
    def __init__(self, minn: int = 0, maxx: int = 0, avg: float = 0.0):
        self.minn = minn
        self.maxx = maxx
        self.avg = avg

    def to_dict(self) -> Dict[str, Number]:
        """
        Serialize this class into a dictionary format.
        """
        return {"avg": self.avg, "min": self.minn, "max": self.maxx}

    @staticmethod
    def calc_avg_min_max(data_list: List):
        """
        Function that calculates average, min and max
        of a list of numeric values.
        Returns an instance of MinMaxAvg class.
        """
        if len(data_list) == 0:
            return MinMaxAvg(avg=0, minn=0, maxx=0)
        return MinMaxAvg(avg=sum(data_list) / len(data_list),
                         minn=min(data_list), maxx=max(data_list))


class DataMetrics:
    """Class that defines one data metrics,
    and calculates the data metrics from a list of annotations"""

    def __init__(self, total_ann: int = 0, total_prop: int = 0, total_loc: int = 0,
                 total_temp: int = 0, total_targ: int = 0, annot_query: MinMaxAvg = None):
        self.total_annotation = total_ann
        self.total_annotation_property = total_prop
        self.total_annotation_location = total_loc
        self.total_annotation_tempex = total_temp
        self.total_annotation_target = total_targ
        self.annotation_per_query = annot_query if annot_query else MinMaxAvg()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {
            "total_annotation": self.total_annotation,
            "total_annotation_per_type": {
                "property": self.total_annotation_property,
                "location": self.total_annotation_location,
                "tempex": self.total_annotation_tempex,
                "target": self.total_annotation_target
            },
            "annotation_per_query": self.annotation_per_query.to_dict()
        }

    def get_metric(self, name: str):
        """
        Function to access a specific parameter by its name.
        """
        if name == "global":
            return self.total_annotation
        elif name == "property":
            return self.total_annotation_property
        elif name == "location":
            return self.total_annotation_location
        elif name == "tempex":
            return self.total_annotation_tempex
        elif name == "target":
            return self.total_annotation_target
        return None

    def set_metric(self, name: str, value):
        """ Setter function for some variables
        specific by their name."""
        if name == "global":
            self.total_annotation = value
        elif name == "property":
            self.total_annotation_property = value
        elif name == "location":
            self.total_annotation_location = value
        elif name == "tempex":
            self.total_annotation_tempex = value
        elif name == "target":
            self.total_annotation_target = value

    @staticmethod
    def create_data_metrics(annotations: List[JSON]):
        """
        Function to calculate and create a DataMetrics instance
        from a list of dictionary annotations.
        """
        if annotations:
            ann_types = [ann['type'] for ann in annotations]
            # create data metrics class instance
            return DataMetrics(total_ann=len(annotations), total_prop=ann_types.count('property'),
                               total_loc=ann_types.count('location'), total_temp=ann_types.count('tempex'),
                               total_targ=ann_types.count('target'))
        else:
            return DataMetrics()


class DataMeasures:
    """Class that defines one data measures composed of data metrics,
        and calculates it from a list of annotations"""

    def __init__(self, gold_metrics: DataMetrics = None, test_metrics: DataMetrics = None):
        self.gold_metrics = gold_metrics if gold_metrics else DataMetrics()
        self.test_metrics = test_metrics if test_metrics else DataMetrics()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {"gold_data": self.gold_metrics.to_dict(),
                "test_data": self.test_metrics.to_dict()}

    def get_data_metrics(self, name: str):
        """
        Function to access a specific parameter by its name.
        """
        if name == "gold_data":
            return self.gold_metrics
        elif name == "test_data":
            return self.test_metrics
        return None

    @staticmethod
    def get_data_measures(gold: List[JSON], test: List[JSON]):
        """
        Function to calculate and create a DataMeasures instance
        from a list of gold and test dictionary annotations.
        """
        return DataMeasures(gold_metrics=DataMetrics.create_data_metrics(gold),
                            test_metrics=DataMetrics.create_data_metrics(test))


class SpanMetrics:
    """
    Class to defines a span metrics
    """
    def __init__(self, count: int = 0, perfect_match_type: float = 0.0,
                 perfect_match_no_type: float = 0.0,
                 perfect_begin_type: float = 0.0, perfect_begin_no_type: float = 0.0,
                 perfect_end_type: float = 0.0, perfect_end_no_type: float = 0.0,
                 split_gold_type: int = 0, split_gold_no_type: int = 0,
                 split_test_type: int = 0, split_test_no_type: int = 0,
                 overlapping_no_type: MinMaxAvg = None,
                 overlapping_type: MinMaxAvg = None):
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
        self.overlapping_span_no_type_match = overlapping_no_type if overlapping_no_type \
            else MinMaxAvg()
        self.overlapping_span_type_match = overlapping_type if overlapping_type else MinMaxAvg()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {
            "count": self.count,
            "perfect_match": {
                "no_type_match": self.perfect_match_no_type_match,
                "type_match": self.perfect_match_type_match
            },
            "perfect_begin": {
                "no_type_match": self.perfect_begin_no_type_match,
                "type_match": self.perfect_begin_type_match
            },
            "perfect_end": {
                "no_type_match": self.perfect_end_no_type_match,
                "type_match": self.perfect_end_type_match
            },
            "split_gold_span": {
                "no_type_match": self.split_gold_no_type_match,
                "type_match": self.split_gold_type_match
            },
            "split_test_span": {
                "no_type_match": self.split_test_type_no_type_match,
                "type_match": self.split_test_type_match
            },
            "overlapping_span": {
                 "no_type_match": self.overlapping_span_no_type_match.to_dict(),
                 "type_match": self.overlapping_span_type_match.to_dict()
            }
        }


class SpanMeasures:
    """
    Class to define span measures that include span metrics,
    and calculate the span measures from a list of annotations"""

    def __init__(self, global_span: SpanMetrics = None, prop_span: SpanMetrics = None,
                 loc_span: SpanMetrics = None,  temp_span: SpanMetrics = None,
                 targ_span: SpanMetrics = None):
        self.global_span = global_span if global_span else SpanMetrics()
        self.property_span = prop_span if prop_span else SpanMetrics()
        self.location_span = loc_span if loc_span else SpanMetrics()
        self.tempex_span = temp_span if temp_span else SpanMetrics()
        self.target_span = targ_span if targ_span else SpanMetrics()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {
            "global": self.global_span.to_dict(),
            "property": self.property_span.to_dict(),
            "location": self.location_span.to_dict(),
            "tempex": self.tempex_span.to_dict(),
            "target": self.target_span.to_dict()
        }

    def get_span_metrics(self, name: str):
        """
        Function to access a specific parameter by its name.
        """
        if name == "global":
            return self.global_span
        elif name == "property":
            return self.property_span
        elif name == "location":
            return self.location_span
        elif name == "tempex":
            return self.tempex_span
        elif name == "target":
            return self.target_span
        return None

    @staticmethod
    def span_overlap(gold_span, test_span):
        """takes the span positions of gold and test
        and checks if there is any overlap
        even in the split annotation cases"""
        if not (len(gold_span) == 2 and len(test_span) == 2):
            return False
        if isinstance(test_span[0], list):
            for split_tspan in test_span:
                if isinstance(gold_span[0], list):
                    for split_gspan in gold_span:
                        return range(max(split_gspan[0], split_tspan[0]), min(split_gspan[-1], split_tspan[-1]))
                else:
                    return range(max(gold_span[0], split_tspan[0]), min(gold_span[-1], split_tspan[-1]))
        else:
            if isinstance(gold_span[0], list):
                for split_gspan in gold_span:
                    return range(max(split_gspan[0], test_span[0]), min(split_gspan[-1], test_span[-1]))
            else:
                return range(max(gold_span[0], test_span[0]), min(gold_span[-1], test_span[-1]))
        return 0

    @staticmethod
    def span_begin_overlap(gold_span, test_span):
        """takes the span positions of gold and test
        and checks if there is any overlap
        even in the split annotation cases"""
        if not (len(gold_span) == 2 and len(test_span) == 2):
            return False
        if isinstance(test_span[0], list):
            for split_tspan in test_span:
                if isinstance(gold_span[0], list):
                    for split_gspan in gold_span:
                        if split_gspan[0] == split_tspan[0]:
                            return True
                else:
                    if gold_span[0] == split_tspan[0]:
                        return True
        else:
            if isinstance(gold_span[0], list):
                for split_gspan in gold_span:
                    if split_gspan[0] == test_span[0]:
                        return True
            elif gold_span[0] == test_span[0]:
                return True
        return False

    @staticmethod
    def span_end_overlap(gold_span, test_span):
        """takes the span positions of gold and test
        and checks if there is any overlap
        even in the split annotation cases"""
        if not (len(gold_span) == 2 and len(test_span) == 2):
            return False
        if isinstance(test_span[0], list):
            for split_tspan in test_span:
                if isinstance(gold_span[0], list):
                    for split_gspan in gold_span:
                        if split_gspan[-1] == split_tspan[-1]:
                            return True
                else:
                    if gold_span[-1] == split_tspan[-1]:
                        return True
        else:
            if isinstance(gold_span[0], list):
                for split_gspan in gold_span:
                    if split_gspan[-1] == test_span[-1]:
                        return True
            elif gold_span[-1] == test_span[-1]:
                return True
        return False

    @staticmethod
    def get_span_measures(gold: List[JSON], test: List[JSON]):
        """
        Function to calculate and create a SpanMeasures instance
        from a list of gold and test dictionary annotations.
        """
        span_measures = SpanMeasures()

        gold_types = [ann['type'] for ann in gold]
        gold_spans = [ann['position'] for ann in gold]
        test_types = [ann['type'] for ann in test]
        test_spans = [ann['position'] for ann in test]

        # print(gold_spans)
        # print(test_spans)
        # TODO! if gold_spans is only length 1, the result has an empty item in the list?
        for idx, span in enumerate(test_spans):
            # update count
            span_metric_test_type = span_measures.get_span_metrics(test_types[idx])
            span_metric_test_type.count += 1
            # perfect match
            if span in gold_spans:
                # exact match
                # update type-specific count
                # check for type match
                gold_idx = gold_spans.index(span)  # we do not presume the test and gold are aligned
                if test_types[idx] == gold_types[gold_idx]:
                    span_metric_test_type.perfect_match_type_match += 1
                else:
                    span_metric_test_type.perfect_match_no_type_match += 1
            else:
                # not perfect match
                # check for some kind of overlap
                # overlapping spans
                overlap_count = 0
                type_match_count = 0
                for gidx, gspan in enumerate(gold_spans):
                    overlap = SpanMeasures.span_overlap(span, gspan)
                    if overlap:
                        overlap_count += 1
                        if isinstance(span[0], list):
                            glength = 0
                            for s in span:
                                glength += s[1] - s[0]
                        else:
                            glength = span[1]-span[0]
                        ratio = (overlap.stop-overlap.start) / glength
                        # includes perfect end and begin
                        if test_types[idx] == gold_types[gidx]:
                            span_metric_test_type.overlapping_span_type_match.minn += ratio
                            type_match_count += 1
                        else:
                            span_metric_test_type.overlapping_span_no_type_match.minn += ratio
                        # perfect begin
                        if SpanMeasures.span_begin_overlap(span, gold_spans[gidx]):  # span[0] == gold_spans[gidx][0]:
                            # begin match (including exact match)
                            # update type-specific count
                            if test_types[idx] == gold_types[gidx]:
                                span_metric_test_type.perfect_begin_type_match += 1
                            else:
                                span_metric_test_type.perfect_begin_no_type_match += 1
                        # perfect end
                        if SpanMeasures.span_end_overlap(span, gold_spans[gidx]):  # span[1] == gold_spans[gidx][1]:
                            # end match (including exact match)
                            # update type-specific count
                            if test_types[idx] == gold_types[gidx]:
                                span_metric_test_type.perfect_end_type_match += 1
                            else:
                                span_metric_test_type.perfect_end_no_type_match += 1
                if overlap_count > 1:
                    # this test span matches several gold spans = split-test
                    if overlap_count == type_match_count:
                        span_metric_test_type.split_test_type_match += 1
                    else:
                        span_metric_test_type.split_test_type_no_type_match += 1

        # split gold
        for gidx, gspan in enumerate(gold_spans):
            split_count = 0
            type_match_count = 0
            for tspan in test_spans:
                if tspan not in gold_spans:
                    if SpanMeasures.span_overlap(gspan, tspan):
                        split_count += 1
                        if gold_types[gidx] == test_types[test_spans.index(tspan)]:
                            type_match_count += 1

            if split_count > 1:
                # we have split gold span
                if split_count == type_match_count:
                    span_measures.get_span_metrics(gold_types[gidx]).split_gold_type_match += 1
                else:
                    span_measures.get_span_metrics(gold_types[gidx]).split_gold_no_type_match += 1
        return span_measures


class AttributeMetrics:
    """Class that defines one attribute metrics"""

    def __init__(self, count: int = 0, total_span_type_match: int = 0,
                 perfect_match_precision: float = 0.0, overlapping_perfect_match: float = 0.0,
                 attribute_match: MinMaxAvg = None):
        self.count = count
        self.total_span_type_match = total_span_type_match
        self.perfect_match_precision = perfect_match_precision
        self.overlapping_perfect_match = overlapping_perfect_match
        self.attribute_match = attribute_match if attribute_match else MinMaxAvg()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {
            "count": self.count,
            "total_span_type_match": self.total_span_type_match,
            "per_annotation_span_perfect_match_precision": self.perfect_match_precision,
            "per_annotation_overlapping_span_perfect_match": self.overlapping_perfect_match,
            "per_annotation_attribute_match": self.attribute_match.to_dict()
        }


class AttributeMeasures:
    """Class that defines one attribute measures composed of attribute metrics,
    and calculates it from a list of annotations"""

    def __init__(self, global_attr: AttributeMetrics = None,
                 prop_attr: AttributeMetrics = None,
                 loc_attr: AttributeMetrics = None,
                 temp_attr: AttributeMetrics = None,
                 targ_attr: AttributeMetrics = None):
        self.global_attribute = global_attr if global_attr else AttributeMetrics()
        self.property_attribute = prop_attr if prop_attr else AttributeMetrics()
        self.location_attribute = loc_attr if loc_attr else AttributeMetrics()
        self.tempex_attribute = temp_attr if temp_attr else AttributeMetrics()
        self.target_attribute = targ_attr if targ_attr else AttributeMetrics()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {
            "global": self.global_attribute.to_dict(),
            "property": self.property_attribute.to_dict(),
            "location": self.location_attribute.to_dict(),
            "tempex": self.tempex_attribute.to_dict(),
            "target": self.target_attribute.to_dict()
        }

    def get_attribute_metrics(self, name: str):
        """
        Function to access a specific parameter by its name.
        """
        if name == "global":
            return self.global_attribute
        elif name == "property":
            return self.property_attribute
        elif name == "location":
            return self.location_attribute
        elif name == "tempex":
            return self.tempex_attribute
        elif name == "target":
            return self.target_attribute
        return None

    @staticmethod
    def get_attribute_measures(gold: List[JSON], test: List[JSON]):
        """
        Function to calculate and create an AttributeMeasures instance
        from a list of gold and test dictionary annotations.
        """
        # create measures dictionary
        attribute_measures = AttributeMeasures()
        gold_spans = [gspan['position'] for gspan in gold]
        gold_types = [gspan['type'] for gspan in gold]
        gold_ann = list(gold)
        # count of annotations per types
        count = {}
        for annot_type in ANNOTATION_TYPES:
            count[annot_type] = len([x for x in test if x['type'] == annot_type])
            attribute_measures.get_attribute_metrics(annot_type).count = count[annot_type]
        for ann in test:
            # count how many attributes in test
            # obligatory for property, tempex, location: type, position, name, value
            # obligatory for target: type, position, name
            test_type = ann['type']
            test_span = ann['position']
            # exact span match
            if test_span in gold_spans:
                gidx = gold_spans.index(test_span)
                # per_annotation_span_perfect_match_precision
                # % of annotation having all attribute matched when span is same
                if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                    attribute_measures.get_attribute_metrics(test_type).perfect_match_precision += 1
                # per_annotation_attribute_match
                # % of matching attribute name / total number of attribute in an annotation
                # compared to perfect matching spans
                attribute_measures.get_attribute_metrics(test_type).attribute_match.minn = 1.0
            else:
                # no exact span match, find overlapping span match
                for gidx, gspan in enumerate(gold_spans):
                    # overlapping span
                    if SpanMeasures.span_overlap(gspan, test_span):
                        # total_span_type_match
                        # nr of attributes where matching span+type
                        # the same as in the measures overlapping_span:type_match
                        # but as a count instead of %
                        # exact type match
                        if test_type == gold_types[gidx]:
                            attribute_measures.get_attribute_metrics(test_type).total_span_type_match += 1
                        # per_annotation_overlapping_span_perfect_match
                        # % of annotation having all attribute matched, for overlapping span
                        if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                            attribute_measures.get_attribute_metrics(test_type).overlapping_perfect_match += 1
                        # per_annotation_attribute_match
                        # % of matching attribute name / total number of attribute in an annotation
                        # compared to overlapping spans
                        attribute_measures.get_attribute_metrics(test_type).attribute_match.minn = \
                            len(set(ann.keys()).intersection(gold_ann[gidx].keys())) / len(ann)

        for annot_type in ANNOTATION_TYPES:
            # count of annotations of all attributes matched for exact span / nr of annots of that type
            attribute_measures.get_attribute_metrics(annot_type).perfect_match_precision = \
                attribute_measures.get_attribute_metrics(annot_type).perfect_match_precision / count[annot_type] if \
                count[annot_type] else 0
            # per_annotation_overlapping_span_perfect_match
            attribute_measures.get_attribute_metrics(annot_type).overlapping_perfect_match = \
                attribute_measures.get_attribute_metrics(annot_type).overlapping_perfect_match / count[annot_type] if \
                count[annot_type] else 0

        return attribute_measures


def levenshtein(str1: str, str2: str) -> int:
    """
    Calculate the Levenshtein distance
    between two strings
    """
    return distance(str1, str2)


def intersect_over_union(bbox1: JSON, bbox2: JSON) -> float:
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


def get_dateformat(time: str) -> datetime.datetime:
    """parse a  time date and
    return the actual dateformat relative to today"""
    dformat = '%Y-%m-%dT%H:%M:%SZ'
    new_time = time.strip()
    if new_time.startswith("#"):
        new_time = new_time.lower()
        if new_time == "#currentdate":
            new_time = datetime.datetime.now()
        elif new_time.startswith('#currentdate'):
            rex = re.search('#currentdate([+-])([0-9]+)([ymd])', new_time)
            if rex.group(1) and rex.group(2) and rex.group(3):
                quant = int(rex.group(2))
                calc = {'y': 365, 'm': 31, 'd': 1}
                days = quant * calc[rex.group(3)]
                if rex.group(1) == "-":
                    new_time = datetime.datetime.now() - datetime.timedelta(days=days)
                if rex.group(1) == "+":
                    new_time = datetime.datetime.now() + datetime.timedelta(days=days)
        elif new_time == '#-infinity':
            # smallest representable date value
            new_time = datetime.datetime.min
        elif new_time == '#+infinity':
            # largest representable date value
            new_time = datetime.datetime.max
        new_time = new_time.isoformat(timespec='seconds') + "Z"
    return datetime.datetime.strptime(new_time, dformat)


def duration_overlap(dur1, dur2) -> int:
    """
    Function to calculate the overlap (in number of days)
    of two date ranges given in a specific format
    Returns 0 if no overlap found.
    """
    # datarange {'start': startdate, 'end': enddate}
    if len(dur1) == 2 and len(dur2) == 2 and 'start' in dur1 and 'start' in dur2:
        try:
            r1_start = get_dateformat(dur1['start'])
            r1_end = get_dateformat(dur1['end'])
            r2_start = get_dateformat(dur2['start'])
            r2_end = get_dateformat(dur2['end'])
        except Exception:
            print("Error in transforming one of the dates:\n",
                  dur1['start'], dur1['end'], dur2['start'], dur2['end'])
            raise

        if r1_start and r1_end and r2_start and r2_end:
            overlap = min(r1_end - r2_start, r2_end - r1_start).days
            if overlap < 0:
                overlap = -overlap
            elif overlap > 0:
                overlap += 1
            return overlap
        else:
            return 0
    # datetime strings
    if dur1 == dur2:
        return 1
    # TODO! divide by total duration to get IOU, better metrics
    return 0


def isnumeric(str_value: Any) -> bool:
    """
    Simple function to check if the passed parameter can be
    converted into a numeric value or not.
    Returns boolean true if yes, false otherwise.
    """
    try:
        if isinstance(str_value, dict):
            return False
        float(str_value)
        return True
    except ValueError:
        # we don't treat here the exception
        # it's enough to know that it's not numeric
        return False


class ValueMetrics:
    """ Class to define one value metrics"""

    def __init__(self, total_matching_attr: int = 0, perfect_value_match: float = 0.0):
        self.total_matching_attributes = total_matching_attr
        self.perfect_value_match = perfect_value_match

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {"total_matching_attributes": self.total_matching_attributes,
                "perfect_value_match": self.perfect_value_match}


class ValueMeasures:
    """Class that defines one value measures composed of value metrics,
    and calculates it from a list of annotations"""

    def __init__(self, global_val: ValueMetrics = None,
                 type_val: ValueMetrics = None,
                 name_val: ValueMetrics = None,
                 bbx_val: ValueMetrics = None,
                 tempex_val: ValueMetrics = None,
                 numeric_val: ValueMetrics = None,
                 target_val: ValueMetrics = None,
                 global_ratio_matching_attr: float = 0.0,
                 name_levenstein: MinMaxAvg = None,
                 bbox_iou: MinMaxAvg = None,
                 tempex_dur_overlap: MinMaxAvg = None,
                 numeric_val_offset: MinMaxAvg = None,
                 target_match_elem: MinMaxAvg = None):
        self.global_value = global_val if global_val else ValueMetrics()
        self.type_value = type_val if type_val else ValueMetrics()
        self.name_value = name_val if name_val else ValueMetrics()
        self.bbox_value = bbx_val if bbx_val else ValueMetrics()
        self.tempex_value = tempex_val if tempex_val else ValueMetrics()
        self.numeric_value = numeric_val if numeric_val else ValueMetrics()
        self.target_value = target_val if target_val else ValueMetrics()
        self.global_ratio_matching_attribute = global_ratio_matching_attr
        self.name_levenstein = name_levenstein if name_levenstein else MinMaxAvg()
        self.bbox_iou = bbox_iou if bbox_iou else MinMaxAvg()
        self.tempex_duration_overlap = tempex_dur_overlap if tempex_dur_overlap else MinMaxAvg()
        self.numeric_value_offset = numeric_val_offset if numeric_val_offset else MinMaxAvg()
        self.target_matching_element = target_match_elem if target_match_elem else MinMaxAvg()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {
            "global":  {
                "total_matching_attributes": self.global_value.total_matching_attributes,
                "perfect_value_match": self.global_value.perfect_value_match,
                "ratio_matching_attributes": self.global_ratio_matching_attribute
            },
            "type": self.type_value.to_dict(),
            "name": {
                "total_matching_attributes": self.name_value.total_matching_attributes,
                "perfect_value_match": self.name_value.perfect_value_match,
                "levenshtein": self.name_levenstein.to_dict()
            },
            "bbox": {
                "total_matching_attributes": self.bbox_value.total_matching_attributes,
                "perfect_value_match": self.bbox_value.perfect_value_match,
                "intersect_over_union": self.bbox_iou.to_dict()
            },
            "tempex": {
                "total_matching_attributes": self.tempex_value.total_matching_attributes,
                "perfect_value_match": self.tempex_value.perfect_value_match,
                "duration_overlap": self.tempex_duration_overlap.to_dict()
            },
            "numeric": {
                "total_matching_attributes": self.numeric_value.total_matching_attributes,
                "perfect_value_match": self.numeric_value.perfect_value_match,
                "value_offset": self.numeric_value_offset.to_dict()
            },
            "target": {
                "total_matching_attributes": self.target_value.total_matching_attributes,
                "perfect_value_match": self.target_value.perfect_value_match,
                "matching_element": self.target_matching_element.to_dict()
            }
        }

    def get_value_metrics(self, name: str):
        """
        Function to access a specific parameter by its name.
        """
        if name == "global":
            return self.global_value
        elif name == "type":
            return self.type_value
        elif name == "name":
            return self.name_value
        elif name == "bbox":
            return self.bbox_value
        elif name == "tempex":
            return self.tempex_value
        elif name == "target":
            return self.target_value
        elif name == "numeric":
            return self.numeric_value
        return None

    @staticmethod
    def get_value_measures(gold: List[JSON], test: List[JSON]):
        """
        Function to calculate and create a ValueMeasures instance
        from a list of gold and test dictionary annotations.
        """
        # create measures dictionary
        value_measures = ValueMeasures()

        gold_spans = [gspan['position'] for gspan in gold]
        gold_types = [gspan['type'] for gspan in gold]
        gold_ann = list(gold)
        for ann in test:
            test_type = ann['type']
            test_span = ann['position']
            # how many location/tempex attributes we have
            if test_type == 'location':
                value_measures.get_value_metrics('bbox').total_matching_attributes += 1
            if test_type == 'tempex':
                value_measures.get_value_metrics('tempex').total_matching_attributes += 1
            if test_type == 'target':
                value_measures.get_value_metrics('target').total_matching_attributes += 1
            if 'name' in ann.keys():
                value_measures.get_value_metrics('name').total_matching_attributes += 1
            if 'value' in ann.keys() and isinstance(ann['value'], str):
                # print(ann['value'])
                if isnumeric(ann['value']):
                    value_measures.get_value_metrics('numeric').total_matching_attributes += 1
            for gidx, gspan in enumerate(gold_spans):
                # overlapping span
                if SpanMeasures.span_overlap(gspan, test_span):
                    # all attributes match
                    if len(set(ann.keys()).intersection(gold_ann[gidx].keys())) == len(ann):
                        value_measures.get_value_metrics('global').total_matching_attributes += 1
                    #  for matching attribute type
                    if gold_types[gidx] == test_type:
                        value_measures.get_value_metrics('type').perfect_value_match += 1
                        if test_type == 'location':
                            if ann['value'] == gold_ann[gidx]['value']:
                                value_measures.get_value_metrics('bbox').perfect_value_match += 1
                            value_measures.bbox_iou.minn = \
                                intersect_over_union(ann['value'], gold_ann[gidx]['value'])
                        if test_type == 'tempex':
                            if ann['value'] == gold_ann[gidx]['value']:
                                value_measures.get_value_metrics('tempex').perfect_value_match += 1
                            value_measures.tempex_duration_overlap.minn = \
                                duration_overlap(ann['value'], gold_ann[gidx]['value'])
                        if test_type == 'target':
                            if ann['name'] == gold_ann[gidx]['name']:
                                value_measures.get_value_metrics('target').perfect_value_match += 1
                            value_measures.target_matching_element.minn = \
                                len(set(ann['name']).intersection(gold_ann[gidx]['name']))
                        if test_type != 'tempex':
                            if gold_ann[gidx]['name'] == ann['name']:
                                value_measures.get_value_metrics('name').perfect_value_match += 1
                            if test_type != 'target':
                                value_measures.name_levenstein.minn = \
                                    levenshtein(ann['name'].lower(), gold_ann[gidx]['name'].lower())
                        if 'value' in gold_ann[gidx].keys() and isnumeric(gold_ann[gidx]['value']) \
                                and isnumeric(ann['value']):
                            if gold_ann[gidx]['value'] == ann['value']:
                                value_measures.get_value_metrics('numeric').perfect_value_match += 1
                            value_measures.numeric_value_offset.minn = \
                                abs(float(ann['value']) - float(gold_ann[gidx]['value']))
        # there are as many type attribute counts, as many annotations
        value_measures.get_value_metrics('type').total_matching_attributes = len(test)
        for value_type in VALUE_TYPES:
            value_measures.get_value_metrics(value_type).perfect_value_match = \
                value_measures.get_value_metrics(value_type).perfect_value_match \
                / value_measures.get_value_metrics(value_type).total_matching_attributes \
                if value_measures.get_value_metrics(value_type).total_matching_attributes > 0 else 0

        value_measures.global_ratio_matching_attribute = \
            value_measures.get_value_metrics('global').total_matching_attributes / len(test) \
            if len(test) else 0
        return value_measures


class EvalMeasures:
    """ Class that defines the final valuation measures,
    including a data, span, attribute and value measures instances"""
    def __init__(self, data_measures: DataMeasures = None, span_measures: SpanMeasures = None,
                 attr_measures: AttributeMeasures = None, val_measures: ValueMeasures = None):
        if data_measures:
            self.data_measures = data_measures
        else:
            self.data_measures = DataMeasures()
        if span_measures:
            self.span_measures = span_measures
        else:
            self.span_measures = SpanMeasures()
        if attr_measures:
            self.attribute_measures = attr_measures
        else:
            self.attribute_measures = AttributeMeasures()
        if val_measures:
            self.value_measures = val_measures
        else:
            self.value_measures = ValueMeasures()

    def to_dict(self) -> JSON:
        """
        Serialize this class into a dictionary format.
        """
        return {
            'global_stats': {
                'data_measures': self.data_measures.to_dict(),
                'span_measures': self.span_measures.to_dict(),
                'attribute_measures': self.attribute_measures.to_dict(),
                'value_measures': self.value_measures.to_dict(),
            }
        }
