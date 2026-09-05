"""Environment-layer inspection. See lesson-04-environment-reality.

Predicts Docker layer reuse from a manifest of (interpreter, pins) per
instance, before any image is actually built.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

DEFAULT_MANIFEST = Path("fixtures/environments/environments.json")


@dataclass(frozen=True)
class Environment:
    repo: str
    instance_id: str
    interpreter: str
    pins: tuple[str, ...]
    toolchain: str | None

    @property
    def layer_key(self) -> tuple[str, tuple[str, ...]]:
        """interpreter + pin set. Toolchain differences don't split the
        layer; pin differences do."""
        return (self.interpreter, self.pins)


def load_environments(path: Path = DEFAULT_MANIFEST) -> list[Environment]:
    records = json.loads(Path(path).read_text())
    return [
        Environment(
            repo=r["repo"],
            instance_id=r["instance_id"],
            interpreter=r["interpreter"],
            pins=tuple(sorted(r["pins"])),
            toolchain=r.get("toolchain"),
        )
        for r in records
    ]


def layer_reuse_rate(envs: list[Environment]) -> float:
    counts = Counter(e.layer_key for e in envs)
    shared = sum(1 for e in envs if counts[e.layer_key] > 1)
    return shared / len(envs) if envs else 0.0


def distinct_layers(envs: list[Environment]) -> dict[tuple[str, tuple[str, ...]], list[Environment]]:
    layers: dict[tuple[str, tuple[str, ...]], list[Environment]] = {}
    for e in envs:
        layers.setdefault(e.layer_key, []).append(e)
    return layers


def summarize_by_repo(envs: list[Environment]) -> list[dict]:
    """One row per repo: interpreter, pins, toolchain, instance count.
    Assumes (as this course's fixture does) that all instances of one repo
    share one environment -- real datasets should assert this, not assume it."""
    by_repo: dict[str, list[Environment]] = {}
    for e in envs:
        by_repo.setdefault(e.repo, []).append(e)
    rows = []
    for repo in sorted(by_repo):
        group = by_repo[repo]
        first = group[0]
        rows.append({
            "repo": repo,
            "interpreter": first.interpreter,
            "pins": ", ".join(first.pins) if first.pins else "-",
            "toolchain": first.toolchain or "-",
            "n": len(group),
        })
    return rows
