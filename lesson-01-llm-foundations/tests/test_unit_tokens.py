"""Unit tests for token accounting. Fast, no network, no model calls."""
import json
import unittest
from pathlib import Path

from apr import tokens as tok

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
PAYLOADS = FIXTURES / "payloads"
MODELS = Path(__file__).resolve().parent.parent / "configs" / "models.json"


class TestHeuristic(unittest.TestCase):
    def test_heuristic_is_deterministic(self):
        text = "def f(x):\n    return x + 1\n"
        self.assertEqual(tok.estimate_heuristic(text), tok.estimate_heuristic(text))

    def test_heuristic_scales_with_length(self):
        self.assertGreater(tok.estimate_heuristic("a" * 400),
                           tok.estimate_heuristic("a" * 100))

    def test_pretoken_estimate_beats_chars4_on_terminal_output(self):
        """The pretokeniser is closer on whitespace-dense text -- but see the
        gate: closer is not close enough to budget against."""
        text = (PAYLOADS / "observation.txt").read_text()
        truth = tok.load_reference_counts(FIXTURES / "reference_counts.json")
        true_n = truth["observation.txt"]
        chars4_err = abs(tok.estimate_heuristic(text) - true_n) / true_n
        pretok_err = abs(tok.estimate_pretokens(text) - true_n) / true_n
        self.assertLess(pretok_err, chars4_err)


class TestReferenceCounts(unittest.TestCase):
    def test_every_payload_has_a_reference_count(self):
        truth = tok.load_reference_counts(FIXTURES / "reference_counts.json")
        on_disk = {p.name for p in PAYLOADS.iterdir()}
        self.assertEqual(on_disk, set(truth))

    def test_reference_counts_are_positive_ints(self):
        truth = tok.load_reference_counts(FIXTURES / "reference_counts.json")
        for name, n in truth.items():
            self.assertIsInstance(n, int, name)
            self.assertGreater(n, 0, name)


class TestPricing(unittest.TestCase):
    def setUp(self):
        self.models = tok.load_models(MODELS)

    def test_table_loads_three_tiers(self):
        self.assertEqual(set(self.models), {"frontier", "workhorse", "small"})

    def test_cost_is_linear_in_tokens(self):
        m = self.models["workhorse"]
        self.assertAlmostEqual(m.cost(2000, 0), 2 * m.cost(1000, 0), places=12)

    def test_cached_input_costs_less_than_fresh(self):
        m = self.models["workhorse"]
        self.assertLess(m.cost(1000, 0, cached_in=1000), m.cost(1000, 0))

    def test_spread_exceeds_five_times(self):
        _, _, ratio = tok.price_spread(self.models, 10_000, 500)
        self.assertGreater(ratio, 5.0)


class TestLoop(unittest.TestCase):
    def setUp(self):
        self.model = tok.load_models(MODELS)["workhorse"]

    def test_stable_prefix_is_cheaper_than_mutated(self):
        stable = tok.simulate_loop(self.model, turns=10, stable_prefix=True)
        churn = tok.simulate_loop(self.model, turns=10, stable_prefix=False)
        self.assertLess(stable.total_usd, churn.total_usd)

    def test_identical_token_volume_either_way(self):
        """The saving is not fewer tokens -- it is the same tokens, priced
        differently. If these ever diverge the simulation is lying."""
        stable = tok.simulate_loop(self.model, turns=10, stable_prefix=True)
        churn = tok.simulate_loop(self.model, turns=10, stable_prefix=False)
        self.assertEqual(stable.total_tokens_in, churn.total_tokens_in)

    def test_first_turn_is_never_cached(self):
        one = tok.simulate_loop(self.model, turns=1, stable_prefix=True)
        self.assertEqual(one.cached_tokens_in, 0)


class TestExactCounter(unittest.TestCase):
    def test_exact_matches_reference_when_available(self):
        truth = tok.load_reference_counts(FIXTURES / "reference_counts.json")
        try:
            got = tok.count_exact((PAYLOADS / "source.py").read_text())
        except tok.TokenizerUnavailable:
            self.skipTest("tiktoken not installed; covered by the offline gate")
        self.assertEqual(got, truth["source.py"])

    def test_count_falls_back_and_reports_method(self):
        n, method = tok.count("hello world", exact=False)
        self.assertEqual(method, "heuristic")
        self.assertGreater(n, 0)


if __name__ == "__main__":
    unittest.main()
