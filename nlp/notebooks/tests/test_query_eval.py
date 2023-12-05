import unittest
from nlp.notebooks.nl2q_eval.query_eval import read_files, global_stats
from nlp.notebooks.nl2q_eval.MetricsClasses import SpanMeasures,\
    AttributeMeasures, DataMeasures, ValueMeasures, \
        ANNOTATION_TYPES, VALUE_TYPES

gold_file = "gold_queries.json"
test_file = "noisy_gold_queries.json"
annot_counts = {"property": 20, "location": 6, "tempex": 3, "target": 5, "global": 34}


class QueryEvalTests(unittest.TestCase):
    gold_queries = {}
    test_queries = {}
    nr_queries = 0
    eval_measures = {}
    span_measures = SpanMeasures()
    attr_measures = AttributeMeasures()
    data_measures = DataMeasures()
    val_measures = ValueMeasures()

    @classmethod
    def setUpClass(cls):
        """
        Set up unit tests.
        Read gold and test query annotations files,
        and call query_eval.global_stats to get all metrics.
        """
        cls.gold_queries, cls.test_queries = read_files(gold_file, test_file)
        cls.nr_queries = len(cls.test_queries)
        cls.eval_measures = global_stats(cls.gold_queries, cls.test_queries)
        cls.span_measures = cls.eval_measures.span_measures
        cls.attr_measures = cls.eval_measures.attribute_measures
        cls.val_measures = cls.eval_measures.value_measures
        cls.data_measures = cls.eval_measures.data_measures

    def test_setUp(self):
        """
        Check that setup was successful and we have
        non-empty query annotations and eval measures.
        """
        # make sure it's not empty
        self.assertNotEqual(self.gold_queries, {}, "Empty gold queries.")
        self.assertNotEqual(self.test_queries, {}, "Empty test queries.")
        self.assertNotEqual(self.nr_queries, 0, "Empty test queries.")
        self.assertNotEqual(self.eval_measures, {}, "Empty eval measures.")
        self.assertNotEqual(self.span_measures, {}, "Empty span measures.")
        self.assertNotEqual(self.attr_measures, {}, "Empty attribute measures.")
        self.assertNotEqual(self.val_measures, {}, "Empty value measures.")
        self.assertNotEqual(self.data_measures, {}, "Empty data measures.")

    def test_span_count(self):
        """
        Test annotation counts in span metrics
        for each type of annotation and global.
        Cross-check that the numbers correspond
        to data metrics counts.
        """
        for annot_type in ANNOTATION_TYPES:
            # check span count totals for each annotation type
            self.assertEqual(self.span_measures.get_span_metrics(annot_type).count,
                             annot_counts[annot_type])
            # check that span and data count values match
            self.assertEqual(self.span_measures.get_span_metrics(annot_type).count,
                             self.data_measures.get_data_metrics('test_data').get_metric(annot_type))
        # same for global
        self.assertEqual(self.span_measures.get_span_metrics('global').count,
                         annot_counts['global'])
        self.assertEqual(self.span_measures.get_span_metrics('global').count,
                         self.data_measures.get_data_metrics('test_data').total_annotation)

    def test_attr_count(self):
        """
        Test annotation counts in attribute metrics
        per annotation type and global
        """
        # check annotation count per annotation type and global
        for annot_type in ANNOTATION_TYPES:
            self.assertEqual(self.attr_measures.get_attribute_metrics(annot_type).count,
                             annot_counts[annot_type])
        self.assertEqual(self.attr_measures.get_attribute_metrics('global').count,
                         annot_counts['global'])

    def test_attr_total_span_type_match(self):
        """
        Test attribute total span type match
        per annotation type and global
        """
        total_span_type_match = 0
        for annot_type in ANNOTATION_TYPES:
            total_span_type_match += self.attr_measures.get_attribute_metrics(annot_type).total_span_type_match
        self.assertEqual(self.attr_measures.get_attribute_metrics('global').total_span_type_match,
                         total_span_type_match)

    def test_val_total_matching_attrs(self):
        """
        Test value measures: total matching attributes global
        """
        total_matching_attributes = 0
        for annot_type in VALUE_TYPES:
            total_matching_attributes += self.val_measures.get_value_metrics(annot_type).total_matching_attributes
        self.assertEqual(self.val_measures.get_value_metrics('global').total_matching_attributes,
                         total_matching_attributes)


if __name__ == "__main__":
    unittest.main()



