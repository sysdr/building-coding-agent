"""Workspace preparation and test execution. See lesson-05-reproduce-gold-patches.

Applies a candidate patch and the instance's test_patch into a fresh copy of
the repo, then runs the FAIL_TO_PASS / PASS_TO_PASS tests and reports a
verdict per test id.
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

REPOS_DIR = Path("fixtures/dataset/repos")


class PatchApplyError(Exception):
    """A patch failed `git apply --check` — malformed, not just unresolved."""


def make_workspace(repo: str, tmp_root: Path) -> Path:
    src = REPOS_DIR / repo
    dst = tmp_root / repo
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    subprocess.run(["git", "init", "-q"], cwd=dst, check=True)
    return dst


def apply_patch_or_raise(workspace: Path, patch_text: str) -> None:
    if not patch_text.strip():
        return
    patch_file = workspace / "_incoming.patch"
    patch_file.write_text(patch_text)
    check = subprocess.run(["git", "apply", "-p1", "--check", str(patch_file)],
                            cwd=workspace, capture_output=True, text=True)
    if check.returncode != 0:
        patch_file.unlink(missing_ok=True)
        raise PatchApplyError(check.stderr.strip() or "patch failed to apply")
    apply = subprocess.run(["git", "apply", "-p1", str(patch_file)],
                            cwd=workspace, capture_output=True, text=True)
    patch_file.unlink(missing_ok=True)
    if apply.returncode != 0:
        raise PatchApplyError(apply.stderr.strip() or "patch failed to apply")


def _purge_stale_modules(workspace: Path) -> None:
    """Purge before every single run, no exceptions -- Python caches imports
    in sys.modules by name, so grading the same instance twice (gold, then
    empty) would otherwise import the module once and silently reuse the
    FIRST run's version for the SECOND run's verdict."""
    stale = [m for m in list(sys.modules) if (workspace / f"{m}.py").exists()]
    for m in stale:
        del sys.modules[m]


def run_tests(workspace: Path, module_name: str, test_ids: list[str]) -> dict[str, str]:
    """Run each `test_file::test_name` id and return {test_id: 'passed'|'failed'}."""
    sys.path.insert(0, str(workspace))
    try:
        results: dict[str, str] = {}
        by_file: dict[str, list[str]] = {}
        for test_id in test_ids:
            file_part, name = test_id.split("::")
            by_file.setdefault(file_part, []).append(name)
        for file_part, names in by_file.items():
            _purge_stale_modules(workspace)
            mod_name = file_part.removesuffix(".py")
            test_mod = importlib.import_module(mod_name)
            for name in names:
                test_id = f"{file_part}::{name}"
                func = getattr(test_mod, name, None)
                if func is None:
                    results[test_id] = "failed"
                    continue
                try:
                    func()
                    results[test_id] = "passed"
                except AssertionError:
                    results[test_id] = "failed"
                except Exception:
                    results[test_id] = "failed"
        return results
    finally:
        sys.path.remove(str(workspace))
