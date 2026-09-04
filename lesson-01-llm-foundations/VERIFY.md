# Verification record — Lesson 1

Measured on the reference machine (Ubuntu 24.04 under WSL2, 8 cores).

## Versions
- Python: 3.12.3 (course floor: 3.11+, checked by `apr doctor`)
- git: 2.43.0
- Docker: 29.7.2 (present here, but NOT required until lesson-25)
- tiktoken: 0.14.0 (optional `[exact]` extra)
- setuptools 68.1.2 / wheel 0.42.0 (pinned in `pyproject.toml`)
- Base image (docker path): `python:3.11.10-slim`, pinned by tag. Pin the
  digest yourself after your first pull — see the comment in
  `docker/Dockerfile`. This file ships without a fabricated digest on purpose.

## Measured timings
- `make setup`: ~25 s with network (fetches tiktoken), ~7 s without
- `make test`: 0.39 s — 19 tests
- `make verify`: 0.86 s
- Disk: `.venv` 20 MB, `src/` 80 KB, `tests/` 36 KB, `fixtures/` 32 KB

## Ground truth
`fixtures/reference_counts.json` holds REAL counts produced by tiktoken 0.14.0,
encoding `cl100k_base`, on this machine. They are reproducible: with the
`[exact]` extra installed the gate recomputes all five and requires exact
equality.

**What they do not establish:** a provider's billed usage. An API's reported
`usage` also counts message framing, system prompt scaffolding and tool
schemas, none of which these bare payloads contain. This lesson measures the
tokeniser, not your invoice. A later lesson wires the live comparison.

## Prices
`configs/models.json` ships ILLUSTRATIVE prices under tier names (`frontier`,
`workhorse`, `small`) — deliberately not any vendor's product names or real
published rates, so nothing here can go stale into a wrong number that looks
authoritative. Replace them before budgeting. The gate's 30.0x spread is a
property of that example table, not a claim about the market.

## Expected `make verify` output
Exact wording matters for the PASS lines; the per-payload numbers are fixed by
the fixtures and must reproduce byte-identically.

```
-- unit tests --
Ran 19 tests in 0.326s

OK

-- exact counter vs recorded reference --
[PASS] issue.md           exact=227   reference=227
[PASS] observation.txt    exact=242   reference=242
[PASS] patch.diff         exact=290   reference=290
[PASS] source.py          exact=420   reference=420
[PASS] traceback.txt      exact=317   reference=317
PASS: exact counter reproduces all 5 reference counts

-- heuristic error (the point of the lesson) --
payload             chars/4   true    error
issue.md                260    227   +14.5%
observation.txt         158    242   -34.7%
patch.diff              323    290   +11.4%
source.py               456    420    +8.6%
traceback.txt           375    317   +18.3%

PASS: chars/4 off by >=8.0% on 5/5 payloads, in BOTH directions (+18.3% .. -34.7%)
      no single correction factor rescues a 53.0-point spread

-- model price spread --
payload source.py: 420 input tokens, 500 output tokens assumed
cheapest $0.001460   dearest $0.043800   spread 30.0x
PASS: model table spans 30.0x on an identical payload

-- cached vs uncached tool loop --
identical work, 10 turns, 97500 input tokens either way
stable prefix     $0.240300  (36000 cached)
mutated prefix    $0.337500  (0 cached)
PASS: stable prefix costs 28.8% less for identical token volume

===================================================
PASS: Lesson 1 verified — scaffold, doctor, and token accounting all green
===================================================
```

## Offline path — verified, not assumed
Installed without the `[exact]` extra (`pip install -e .`), the gate:
- skips the exact-counter section with an explicit SKIP and why,
- skips 1 unit test (19 run, 1 skipped),
- still PASSES the heuristic, spread and cache sections against recorded truth,
- prices `source.py` at 456 input tokens instead of 420 — the heuristic's own
  error leaking into the cost estimate, which is the lesson in miniature.

Exit code is 0 on both paths.

## What was NOT verified

**The Docker path was not run.** The reference machine is WSL2, where the `docker` on
PATH is the Windows Docker Desktop CLI (`npipe:////./pipe/dockerDesktopLinuxEngine`). It
translates `/tmp/...` to `C:\tmp\...` and cannot see the WSL filesystem, so
`docker compose build` fails with `The system cannot find the path specified` before
reaching the Dockerfile.

That is an environment limitation, not a defect in `docker/Dockerfile` — but it means the
article's Docker command block is **unverified**, and the honest thing is to say so rather
than let a green native run imply both paths work. Run it yourself on a native Linux or
macOS Docker install before trusting it, and open an issue if it fails.

Verified here: native path only, on both the `[exact]` and offline installs, from a fresh
unzip of the release asset.
