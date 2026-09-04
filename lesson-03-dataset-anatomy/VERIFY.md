# Verification record — Lesson 3

Measured on the reference build machine (Ubuntu, network available during
`make setup`).

## Versions
- Python: 3.12.3 (course floor: 3.11+, checked by `apr doctor`)
- git: 2.43.0
- pip: 24.3.1
- setuptools: 68.1.2 (pinned in `pyproject.toml` `[build-system]`)
- wheel: 0.42.0 (pinned in `pyproject.toml` `[build-system]`)
- Docker: 29.7.2 — present on the reference machine but not required until
  the image-pipeline lesson, `lesson-25-image-build-pipeline`.
- Base image (docker path): `python:3.11.10-slim`, pinned by tag. Pin the
  digest yourself after your first pull — see the comment in
  `docker/Dockerfile` for the exact `docker inspect` command. This file
  ships without a fabricated digest on purpose: a digest that wasn't
  pulled and checked is worse than no digest at all.

## Measured timings (native path)
- `make setup`: ~15s (with network — pulls tiktoken/regex wheels)
- `bash scripts/verify.sh`: ~0.4s (after setup)
- Total disk footprint: `.venv` 20 MB, `src/` 120 KB, `tests/` 56 KB,
  `fixtures/` 160 KB

## Expected `make verify` output (abridged — exact wording matters for the
last several lines; the doctor block's exact byte free count will vary)
```
-- unit tests --
...
Ran 32 tests in 0.311s

OK
-- environment doctor --
[PASS] python: found 3.12, need >= 3.11
[PASS] git: git version 2.43.0
[PASS] docker: Docker version 29.7.2, build a7dcaa6
[PASS] disk_space: 909.1 GB free, need >= 5.0 GB
PASS: environment doctor all critical checks green
-- version check --
apr --version -> 0.1.0
PASS: apr --version prints package version (0.1.0)
-- claim rejection (must fail) --
PASS: claims ledger rejects a non-falsifiable claim (REJECTED: missing required field(s): would_disprove)
-- claim acceptance (must succeed) --
RECORDED [........]: A minimal single-agent bash-and-edit scaffold resolves...
PASS: claims.json valid against schema (1 recorded claim, well-formed JSON)
-- dev slice: determinism --
PASS: dev slice byte-identical across two runs at seed=42, 5 repos covered
-- dev slice: rejects a corrupt record --
PASS: dev slice refuses a corrupt record (REJECTED: line 6: instance record missing required field(s): repo)

===================================================
PASS: Lesson 3 verified — scaffold, claims ledger, and dev slice all green
===================================================
```
The `[....]` claim ID is a random 8-char hex — it will differ every run
by design (see `Claim.id` in `src/apr/claims.py`).

## Known environment variance
- On a machine with a global `setuptools`/`wheel` older than the pins
  above, the `--no-build-isolation` fallback in `make setup` will use
  whatever is installed system-wide rather than the pinned versions.
- `disk_space` in the doctor output reflects free space on the volume
  containing the current working directory, not the whole machine.
- The five synthetic repos under `fixtures/dataset/repos/` are this
  course's stand-in for real SWE-bench repos — see the scope note in
  `lesson-03-article.md`. `gold.patch` and `test.patch` per repo were
  generated with Python's `difflib.unified_diff` and confirmed to apply
  cleanly with `git apply -p1` before being committed to this zip.
