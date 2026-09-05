# Lesson 5 — Reproduce the Gold Patches (Gate 0)

Cumulative through Lesson 5 of the *Autonomous Program Repair* course. This
lesson adds the grading harness itself: apply a patch, run the tests it's
supposed to affect, decide pass or fail — no mocked verdicts, real subprocess
`git apply` and real test execution against the five synthetic repos.

## 5-minute path to green

**Native:**
```bash
make setup
make verify
```

**Docker:**
```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm apr harness gold-empty
```

## What you should see

`make verify` ends with:
```
PASS: Lesson 5 verified — Gate 0: gold=100%, empty=0%, two runs identical
```

## Try it yourself

```bash
.venv/bin/apr harness gold-empty
# -> gold=5/5 empty=0/5
```

Run it twice — the output is byte-identical, because the harness purges every
stale cached module before each grading pass (see `apr.runner._purge_stale_modules`).

See `VERIFY.md` for exact pinned versions and expected timings.

## If your edits seem to do nothing

An editable install records an **absolute** path. Copy this directory with `.venv`
inside it and the copy will keep importing the original's `src/` — silently, with no
error. Run `make clean` before copying, or `make setup` again in the copy.

```bash
python -c "import apr; print(apr.__file__)"   # which tree am I actually running?
```
