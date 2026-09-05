"""Gate 0: the harness that decides pass/fail. See lesson-05-reproduce-gold-patches.

resolved = every FAIL_TO_PASS test passes AND every PASS_TO_PASS test still
passes. No partial credit.
"""
from __future__ import annotations

import enum
import json
import tempfile
from pathlib import Path

from apr import runner
from apr.slice import load_instances


class Verdict(enum.Enum):
    PASSED = "passed"
    FAILED = "failed"


def grade_instance(instance: dict, patch_text: str) -> dict:
    """Apply `patch_text` (gold, empty, or otherwise) plus the instance's own
    test_patch, run F2P and P2P, and return a verdict dict. Never raises for a
    normal grading outcome -- only PatchApplyError propagates, for a genuinely
    malformed patch."""
    repo = instance["repo"]
    module_name = repo

    with tempfile.TemporaryDirectory() as td:
        workspace = runner.make_workspace(repo, Path(td))

        test_patch_path = Path(instance["test_patch_file"]).name
        test_patch_dir = Path("fixtures/dataset") / instance["test_patch_file"]
        test_patch_text = test_patch_dir.read_text()
        runner.apply_patch_or_raise(workspace, test_patch_text)

        if patch_text.strip():
            runner.apply_patch_or_raise(workspace, patch_text)

        f2p = instance["FAIL_TO_PASS"]
        p2p = instance["PASS_TO_PASS"]
        f2p_map = runner.run_tests(workspace, module_name, f2p)
        p2p_map = runner.run_tests(workspace, module_name, p2p)

    resolved = (
        all(v == Verdict.PASSED.value for v in f2p_map.values())
        and all(v == Verdict.PASSED.value for v in p2p_map.values())
    )
    return {
        "instance_id": instance["instance_id"],
        "resolved": resolved,
        "f2p": f2p_map,
        "p2p": p2p_map,
    }


def _gold_patch_text(instance: dict) -> str:
    return (Path("fixtures/dataset") / instance["gold_patch_file"]).read_text()


def gold_empty_check(dataset_path: Path = Path("fixtures/dataset/instances.jsonl")) -> dict:
    instances = load_instances(dataset_path)
    gold_results = [grade_instance(inst, _gold_patch_text(inst)) for inst in instances]
    empty_results = [grade_instance(inst, "") for inst in instances]
    gold_resolved = sum(1 for r in gold_results if r["resolved"])
    empty_resolved = sum(1 for r in empty_results if r["resolved"])
    return {
        "n": len(instances),
        "gold_resolved": gold_resolved,
        "empty_resolved": empty_resolved,
        "gold_results": gold_results,
        "empty_results": empty_results,
    }


def write_jsonl(results: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in results:
            f.write(json.dumps(r, sort_keys=True) + "\n")
