import unittest

from apr import harness
from apr.runner import PatchApplyError
from apr.slice import load_instances


class TestHarness(unittest.TestCase):
    def test_gold_resolves_all_five(self):
        result = harness.gold_empty_check()
        self.assertEqual(result["gold_resolved"], 5)
        self.assertEqual(result["n"], 5)

    def test_empty_resolves_none(self):
        result = harness.gold_empty_check()
        self.assertEqual(result["empty_resolved"], 0)

    def test_two_runs_are_byte_identical(self):
        a = harness.gold_empty_check()
        b = harness.gold_empty_check()
        self.assertEqual(a["gold_results"], b["gold_results"])
        self.assertEqual(a["empty_results"], b["empty_results"])

    def test_malformed_patch_raises(self):
        instances = load_instances()
        inst = instances[0]
        with self.assertRaises(PatchApplyError):
            harness.grade_instance(inst, "not a real diff at all\n@@garbage@@\n")

    def test_p2p_still_passes_on_empty(self):
        instances = load_instances()
        inst = instances[0]
        result = harness.grade_instance(inst, "")
        self.assertTrue(all(v == "passed" for v in result["p2p"].values()))


if __name__ == "__main__":
    unittest.main()
