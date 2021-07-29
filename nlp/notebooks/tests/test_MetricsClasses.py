import unittest
from nlp.nl2q_eval.query_eval import read_files
from nlp.nl2q_eval.MetricsClasses import *

gold_file = "gold_queries.json"
test_file = "noisy_gold_queries.json"


class MetricsClassesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Set up unit tests.
        Read gold and test query annotations files
        """
        cls.gold_queries, cls.test_queries = read_files(gold_file, test_file)
        if not cls.gold_queries:
            print("Empty gold queries read during setup! Aborting.")
            assert False
        if not cls.test_queries:
            print("Empty test queries read during setup! Aborting.")
            assert False

    def test_data(self):
        """
        Test DataMeasures.get_data_measures method to evaluate data metrics for first query
        no global or avg-min-max values calculated
        """
        data_measures = DataMeasures.get_data_measures(self.gold_queries["queries"][0]['annotations'],
                                                       self.test_queries["queries"][0]['annotations'])
        self.assertEqual(4, data_measures.gold_metrics.total_annotation)
        self.assertEqual(1, data_measures.gold_metrics.total_annotation_location)
        self.assertEqual(2, data_measures.gold_metrics.total_annotation_property)
        self.assertEqual(0, data_measures.gold_metrics.total_annotation_target)
        self.assertEqual(1, data_measures.gold_metrics.total_annotation_tempex)
        self.assertDictEqual({"avg": 0.0, "max": 0, "min": 0},
                             data_measures.gold_metrics.annotation_per_query.to_dict())

    def test_span(self):
        """
        Test SpanMeasures.get_span_measures method to evaluate span metrics for first query,
        no global or avg-min-max values calculated
        """
        span_measures = SpanMeasures.get_span_measures(self.gold_queries["queries"][0]['annotations'],
                                                       self.test_queries["queries"][0]['annotations'])
        self.assertEqual(2.0, span_measures.property_span.perfect_match_type_match)
        self.assertEqual(1.0, span_measures.location_span.perfect_match_type_match)
        self.assertEqual(1.0, span_measures.tempex_span.perfect_end_type_match)

    def test_attr(self):
        """
        Test AttributeMeasures.get_attribute_measures to evaluate attribute metrics
        for first query only,
        no global or avg-min-max values
        """
        attr_measures = AttributeMeasures.get_attribute_measures(self.gold_queries["queries"][0]['annotations'],
                                                                 self.test_queries["queries"][0]['annotations'])
        self.assertEqual(1.0, attr_measures.property_attribute.perfect_match_precision)
        self.assertEqual(1.0, attr_measures.location_attribute.perfect_match_precision)
        self.assertEqual(1, attr_measures.tempex_attribute.total_span_type_match)
        self.assertEqual(1.0, attr_measures.tempex_attribute.overlapping_perfect_match)

    def test_val(self):
        """
        Test ValueMeasures.get_value_measures method to evaluate value metrics for first query,
        no global or avg-min-max values calculated
        """
        val_measures = ValueMeasures.get_value_measures(self.gold_queries["queries"][0]['annotations'],
                                                        self.test_queries["queries"][0]['annotations'])
        self.assertEqual(1.0, val_measures.type_value.perfect_value_match)
        self.assertEqual(1.0, val_measures.name_value.perfect_value_match)
        self.assertEqual(1.0, val_measures.numeric_value.perfect_value_match)


if __name__ == "__main__":
    unittest.main()
