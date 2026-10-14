import unittest

from isha import align_hypergraphs, evaluate_alignment
from isha.core import _select_matches
import scipy.sparse as sp


class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.source = [{0, 1}, {1, 2}]
        self.target = [{10, 11}, {11, 12}]
        self.seeds = [(self.source[0], self.target[0])]

    def test_distinct_node_ids_and_one_to_one_matches(self):
        self.assertEqual(align_hypergraphs(self.source, self.target, self.seeds), {0: 10, 1: 11, 2: 12})

    def test_iteration_recovers_nodes_outside_the_seed_edges(self):
        first = align_hypergraphs(self.source, self.target, self.seeds, max_rounds=1)
        full = align_hypergraphs(self.source, self.target, self.seeds)
        self.assertNotIn(2, first)
        self.assertEqual(full[2], 12)
        self.assertGreater(len(full), len(first))

    def test_no_seed_hyperedges(self):
        self.assertEqual(align_hypergraphs(self.source, self.target, []), {})

    def test_empty_input(self):
        self.assertEqual(align_hypergraphs([], self.target, []), {})

    def test_determinism(self):
        first = align_hypergraphs(self.source, self.target, self.seeds)
        for _ in range(5):
            self.assertEqual(first, align_hypergraphs(self.source, self.target, self.seeds))

    def test_unknown_seed_edge_is_rejected(self):
        with self.assertRaises(ValueError):
            align_hypergraphs(self.source, self.target, [({0, 2}, {10, 11})])

    def test_negative_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            align_hypergraphs([{-1, 0}], self.target, [])

    def test_invalid_round_count_is_rejected(self):
        with self.assertRaises(ValueError):
            align_hypergraphs(self.source, self.target, self.seeds, max_rounds=0)

    def test_mutual_selection_rejects_a_one_sided_best_candidate(self):
        evidence = sp.csr_matrix([[1.0, 0.5], [0.8, 0.1]])
        selected = _select_matches([0, 1], {0, 1}, evidence, {0: 2, 1: 2}, {0: 2, 1: 2})
        self.assertEqual(set(selected), {0})
        self.assertEqual(selected[0][0], 0)


class MetricTests(unittest.TestCase):
    def test_explicit_ground_truth_not_equal_ids(self):
        values = evaluate_alignment({0: 10, 1: 12}, {0: 10, 1: 11, 2: 12})
        self.assertEqual(values["precision"], 0.5)
        self.assertEqual(values["recall"], 1 / 3)
        self.assertEqual(values["f1"], 0.4)
        self.assertEqual(values["correct_matches"], 1)

    def test_seed_edge_nodes_remain_in_the_evaluation(self):
        values = evaluate_alignment({0: 10}, {0: 10, 1: 11, 2: 12})
        self.assertEqual(values["ground_truth_total"], 3)
        self.assertEqual(values["recall"], 1 / 3)

    def test_empty_predictions(self):
        values = evaluate_alignment({}, {0: 10})
        self.assertEqual([values[key] for key in ("precision", "recall", "f1")], [0, 0, 0])

    def test_perfect_matches(self):
        values = evaluate_alignment({0: 10}, {0: 10})
        self.assertEqual([values[key] for key in ("precision", "recall", "f1")], [1, 1, 1])

    def test_noninjective_predictions_are_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_alignment({0: 10, 1: 10}, {0: 10})

    def test_noninjective_ground_truth_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_alignment({}, {0: 10, 1: 10})


if __name__ == "__main__":
    unittest.main()
