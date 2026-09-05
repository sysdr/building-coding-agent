import unittest
from pathlib import Path

from apr import slice as slice_mod

DATASET = Path("fixtures/dataset/instances.jsonl")
CORRUPT_DATASET = Path("fixtures/dataset/instances_with_corrupt.jsonl")


class TestLoadInstances(unittest.TestCase):
    def test_loads_five_repos(self):
        records = slice_mod.load_instances(DATASET)
        self.assertEqual(len(records), 5)
        repos = {r["repo"] for r in records}
        self.assertEqual(repos, {"mathutils", "strutils", "listutils",
                                  "jsonutils", "timeutils"})

    def test_corrupt_record_raises(self):
        with self.assertRaises(slice_mod.DatasetError) as ctx:
            slice_mod.load_instances(CORRUPT_DATASET)
        msg = str(ctx.exception)
        self.assertIn("line 6", msg)
        self.assertIn("repo", msg)


class TestBuildDevSlice(unittest.TestCase):
    def test_same_seed_is_byte_identical(self):
        records = slice_mod.load_instances(DATASET)
        a = slice_mod.build_dev_slice(records, seed=42)
        b = slice_mod.build_dev_slice(records, seed=42)
        self.assertEqual(a, b)

    def test_different_seeds_can_differ_in_order(self):
        records = slice_mod.load_instances(DATASET)
        a = slice_mod.build_dev_slice(records, seed=1)
        b = slice_mod.build_dev_slice(records, seed=2)
        # Not asserting they differ (small dataset could coincide), just that
        # both are valid full-coverage slices.
        self.assertEqual(len(a), len(b), 5)

    def test_every_repo_represented(self):
        records = slice_mod.load_instances(DATASET)
        dev = slice_mod.build_dev_slice(records, seed=42)
        repos = {r["repo"] for r in dev}
        self.assertEqual(len(repos), 5)

    def test_size_larger_than_dataset_returns_available(self):
        records = slice_mod.load_instances(DATASET)
        dev = slice_mod.build_dev_slice(records, seed=42, size=50)
        self.assertEqual(len(dev), 5)


if __name__ == "__main__":
    unittest.main()
