# Verification record — Lesson 2

Measured on the reference build machine (Ubuntu 24.04, 8 cores, no network
during `make setup`'s fallback path).

## Versions
- Python: 3.12.3 (course floor: 3.11+, checked by `apr doctor`)
- git: 2.43.0
- pip: 24.0
- setuptools: 68.1.2 (pinned in `pyproject.toml` `[build-system]`)
- wheel: 0.42.0 (pinned in `pyproject.toml` `[build-system]`)
- Docker: not installed on the reference machine — this is fine. Lesson 2
  treats Docker as non-critical because nothing needs a container until
  the image-pipeline lesson, lesson-25-image-build-pipeline (per-instance image builds).
- Base image (docker path): `python:3.11.10-slim`, pinned by tag. Pin the
  digest yourself after your first pull — see the comment in
  `docker/Dockerfile` for the exact `docker inspect` command. This file
  ships without a fabricated digest on purpose: a digest that wasn't
  pulled and checked is worse than no digest at all.

## Measured timings (native path)
- `make setup`: 7.0s (offline fallback via `--no-build-isolation`; expect
  a few seconds longer with network, since pip then fetches the pinned
  setuptools/wheel from PyPI instead of reusing system copies)
- `bash scripts/verify.sh`: 0.4s
- Total disk footprint: `.venv` 16 MB, `src/` 48 KB, `tests/` 24 KB,
  `fixtures/` 12 KB

## Expected `make verify` output (abridged, exact wording matters for the
last three lines — everything else may vary slightly by environment)
```
-- unit tests --
...
Ran 9 tests in 0.017s

OK
-- environment doctor --
[PASS] python: found 3.12, need >= 3.11
[PASS] git: git version 2.43.0
[WARN] docker: docker not found on PATH (not required until lesson-25)
[PASS] disk_space: 10.0 GB free, need >= 5.0 GB
PASS: environment doctor all critical checks green
-- version check --
apr --version -> 0.1.0
PASS: apr --version prints package version (0.1.0)
-- claim rejection (must fail) --
PASS: claims ledger rejects a non-falsifiable claim (REJECTED: missing required field(s): would_disprove)
-- claim acceptance (must succeed) --
RECORDED [........]: A minimal single-agent bash-and-edit scaffold resolves...
PASS: claims.json valid against schema (1 recorded claim, well-formed JSON)

===================================================
PASS: Lesson 2 verified — scaffold, doctor, and claims ledger all green
===================================================
```
The `[....]` claim ID is a random 8-char hex — it will differ every run
by design (see `Claim.id` in `src/apr/claims.py`).

## Known environment variance
- On a machine with a global `setuptools`/`wheel` older than the pins
  above, the `--no-build-isolation` fallback in `make setup` will use
  whatever is installed system-wide rather than the pinned versions.
  This only matters for reproducing this exact file's byte-for-byte
  build log — it does not change `apr`'s behavior, since Lesson 2 has
  zero runtime dependencies.
- `disk_space` in the doctor output reflects free space on the volume
  containing the current working directory, not the whole machine.
