import unittest
from pathlib import Path

from apr import image as image_mod

MANIFEST = Path("fixtures/environments/environments.json")


class TestImage(unittest.TestCase):
    def test_loads_thirteen_instances(self):
        envs = image_mod.load_environments(MANIFEST)
        self.assertEqual(len(envs), 13)

    def test_five_distinct_layers(self):
        envs = image_mod.load_environments(MANIFEST)
        layers = image_mod.distinct_layers(envs)
        self.assertEqual(len(layers), 5)

    def test_reuse_rate_is_92_3_percent(self):
        envs = image_mod.load_environments(MANIFEST)
        rate = image_mod.layer_reuse_rate(envs)
        self.assertAlmostEqual(rate, 12 / 13, places=6)

    def test_singleton_repo_is_not_counted_as_reused(self):
        envs = image_mod.load_environments(MANIFEST)
        listutils = [e for e in envs if e.repo == "listutils"]
        self.assertEqual(len(listutils), 1)
        layers = image_mod.distinct_layers(envs)
        self.assertEqual(len(layers[listutils[0].layer_key]), 1)


if __name__ == "__main__":
    unittest.main()
