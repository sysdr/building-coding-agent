"""Environment doctor: fail loudly now rather than silently in Phase 3.

Later phases build per-instance Docker images (lesson-25-image-build-pipeline
alone needs tens of GB). Checking here, in Lesson 1, is cheaper than
discovering it thirty lessons later.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass

MIN_PYTHON = (3, 11)

# Docker is not needed until lesson-25-image-build-pipeline, so a missing
# docker is a warning here, never a failure.
NON_CRITICAL = ("docker",)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str

    @property
    def critical(self) -> bool:
        return self.name not in NON_CRITICAL

    def render(self) -> str:
        if self.ok:
            tag = "PASS"
        else:
            tag = "FAIL" if self.critical else "WARN"
        return f"[{tag}] {self.name}: {self.detail}"


def _tool_version(binary: str) -> str | None:
    try:
        out = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=10
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() or out.stderr.strip() or None


def check_python() -> CheckResult:
    found = sys.version_info[:2]
    ok = found >= MIN_PYTHON
    need = ".".join(str(p) for p in MIN_PYTHON)
    return CheckResult(
        "python", ok, f"found {found[0]}.{found[1]}, need >= {need}"
    )


def check_git() -> CheckResult:
    version = _tool_version("git")
    return CheckResult("git", version is not None, version or "git not found on PATH")


def check_docker() -> CheckResult:
    version = _tool_version("docker")
    return CheckResult(
        "docker",
        version is not None,
        version or "docker not found on PATH (not required until lesson-25)",
    )


def run_all() -> list[CheckResult]:
    return [check_python(), check_git(), check_docker()]


def all_critical_pass(results: list[CheckResult]) -> bool:
    return all(r.ok for r in results if r.critical)
