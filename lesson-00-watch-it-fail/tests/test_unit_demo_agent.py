import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("demo_agent", ROOT / "demo_agent.py")
demo_agent = importlib.util.module_from_spec(spec)
sys.modules["demo_agent"] = demo_agent
spec.loader.exec_module(demo_agent)


class TestAgentLoop(unittest.TestCase):
    def setUp(self):
        self.workdir = Path(tempfile.mkdtemp())
        self.repo = self.workdir / "repo"
        shutil.copytree(ROOT / "fixtures" / "instances" / "repo_a", self.repo)

    def tearDown(self):
        shutil.rmtree(self.workdir, ignore_errors=True)

    def test_loop_stops_on_model_done(self):
        turns = [{"bash": "echo hi"}, {"done": True}]
        model = demo_agent.FixtureModelClient(turns)
        result = demo_agent.run_agent(model, self.repo, "irrelevant")
        self.assertEqual(result.stopped_reason, "model_done")
        self.assertEqual(result.turns_used, 1)

    def test_loop_stops_on_turn_cap(self):
        turns = [{"bash": "true"}] * (demo_agent.MAX_TURNS + 5)
        model = demo_agent.FixtureModelClient(turns)
        result = demo_agent.run_agent(model, self.repo, "irrelevant")
        self.assertEqual(result.stopped_reason, "turn_cap")
        self.assertEqual(result.turns_used, demo_agent.MAX_TURNS)

    def test_correct_patch_resolves(self):
        instance_a = json.loads((ROOT / "fixtures" / "instances" / "instance_a.json").read_text())
        model = demo_agent.FixtureModelClient(instance_a["fixture_turns"])
        result = demo_agent.run_agent(model, self.repo, instance_a["issue_text"])
        self.assertTrue(result.resolved)

    def test_wrong_patch_does_not_resolve(self):
        repo_b = self.workdir / "repo_b"
        shutil.copytree(ROOT / "fixtures" / "instances" / "repo_b", repo_b)
        instance_b = json.loads((ROOT / "fixtures" / "instances" / "instance_b.json").read_text())
        model = demo_agent.FixtureModelClient(instance_b["fixture_turns"])
        result = demo_agent.run_agent(model, repo_b, instance_b["issue_text"])
        self.assertFalse(result.resolved)

    def test_transcript_records_every_turn(self):
        turns = [{"bash": "echo one"}, {"bash": "echo two"}, {"done": True}]
        model = demo_agent.FixtureModelClient(turns)
        result = demo_agent.run_agent(model, self.repo, "irrelevant")
        tool_entries = [t for t in result.transcript if t.get("role") == "tool"]
        self.assertEqual(len(tool_entries), 2)
        self.assertIn("one", tool_entries[0]["content"]["output"])


class TestPredictionSeal(unittest.TestCase):
    def setUp(self):
        self.workdir = Path(tempfile.mkdtemp())
        self.seal_path = self.workdir / "predictions.txt"

    def tearDown(self):
        shutil.rmtree(self.workdir, ignore_errors=True)

    def test_predict_writes_once(self):
        args = demo_agent.argparse.Namespace(guess="wrong reasoning", out=str(self.seal_path))
        rc = demo_agent.cmd_predict(args)
        self.assertEqual(rc, 0)
        self.assertIn("wrong reasoning", self.seal_path.read_text())

    def test_predict_refuses_to_reseal(self):
        self.seal_path.write_text("already sealed\n")
        args = demo_agent.argparse.Namespace(guess="a different guess", out=str(self.seal_path))
        rc = demo_agent.cmd_predict(args)
        self.assertEqual(rc, 1)
        self.assertIn("already sealed", self.seal_path.read_text())


if __name__ == "__main__":
    unittest.main()
