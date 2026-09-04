# Lesson 3 — Dataset Anatomy

Cumulative through Lesson 3 of the *Autonomous Program Repair* course: the `apr`
package, an environment doctor, a claims ledger, and a validated, deterministic
dev-slice builder over a five-repo synthetic dataset.

## 5-minute path to green

**Native:**
```bash
make setup
make verify
```

**Docker:**
```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm apr slice build --seed 42
```

## What you should see

`make verify` ends with:
```
PASS: Lesson 3 verified — scaffold, claims ledger, and dev slice all green
```

## Try it yourself

```bash
.venv/bin/apr slice build --seed 42
# -> wrote 5 instance(s) across 5 repo(s) to .apr/dev_slice.jsonl (seed=42)
#      jsonutils
#      listutils
#      mathutils
#      strutils
#      timeutils
```

See `VERIFY.md` for exact pinned versions and expected timings.

## If your edits seem to do nothing

An editable install records an **absolute** path. Copy this directory with `.venv`
inside it and the copy will keep importing the original's `src/` — silently, with no
error. Run `make clean` before copying, or `make setup` again in the copy.

```bash
python -c "import apr; print(apr.__file__)"   # which tree am I actually running?
```
