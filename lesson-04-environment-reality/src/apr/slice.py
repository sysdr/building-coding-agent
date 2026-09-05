"""Dataset loading and dev-slice selection. See lesson-03-dataset-anatomy."""
from __future__ import annotations

import json
import random
from pathlib import Path

REQUIRED_FIELDS = (
    "instance_id", "repo", "base_commit", "problem_statement",
    "FAIL_TO_PASS", "PASS_TO_PASS", "gold_patch_file", "test_patch_file",
)

DEFAULT_DATASET = Path("fixtures/dataset/instances.jsonl")
DEV_SLICE_OUT = Path(".apr/dev_slice.jsonl")


class DatasetError(Exception):
    """Raised when a dataset record fails validation, naming the line and field."""


def _validate(record: dict) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in record]
    if missing:
        raise DatasetError(
            f"instance record missing required field(s): {', '.join(missing)}"
        )


def load_instances(path: Path = DEFAULT_DATASET) -> list[dict]:
    """Read a JSONL dataset, validating every record before returning any of them."""
    records = []
    for lineno, line in enumerate(Path(path).read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        try:
            _validate(record)
        except DatasetError as exc:
            raise DatasetError(f"line {lineno}: {exc}") from None
        records.append(record)
    return records


def build_dev_slice(records: list[dict], seed: int, size: int | None = None) -> list[dict]:
    """Round-robin across repos, shuffled once by seed, so the same seed always
    produces the same slice and every repo is represented before any repeats."""
    by_repo: dict[str, list[dict]] = {}
    for r in records:
        by_repo.setdefault(r["repo"], []).append(r)

    rng = random.Random(seed)
    repos = list(by_repo.keys())
    rng.shuffle(repos)
    for r in repos:
        rng.shuffle(by_repo[r])

    if size is None:
        size = len(records)

    out: list[dict] = []
    indices = {r: 0 for r in repos}
    while len(out) < size:
        progressed = False
        for r in repos:
            if len(out) >= size:
                break
            i = indices[r]
            if i < len(by_repo[r]):
                out.append(by_repo[r][i])
                indices[r] = i + 1
                progressed = True
        if not progressed:
            break  # dataset exhausted; return fewer than `size`, not repeats
    return out


def write_dev_slice(instances: list[dict], out_path: Path = DEV_SLICE_OUT) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for inst in instances:
            f.write(json.dumps(inst, sort_keys=True) + "\n")
    return out_path
