# Lesson 2 — The Landscape, Honestly

Scaffold for the *Autonomous Program Repair* course: the `apr` package, an
environment doctor, and a claims ledger that rejects any claim that doesn't
say what would prove it wrong.

## 5-minute path to green

**Native:**
```bash
make setup
make verify
```

**Docker:**
```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm apr doctor
```

## What you should see

`make verify` ends with:
```
PASS: Lesson 2 verified — scaffold, doctor, and claims ledger all green
```

## Try it yourself

```bash
.venv/bin/apr claim new --statement "..." --would-disprove ""
# -> REJECTED: missing required field(s): would_disprove

.venv/bin/apr claim new \
  --statement "A single agent matches the swarm at equal cost." \
  --would-disprove "The swarm resolves strictly more instances at equal or lower cost."
# -> RECORDED [a1b2c3d4]: A single agent matches the swarm at equal cost.
```

See `VERIFY.md` for exact pinned versions and expected timings.

## If your edits seem to do nothing

An editable install records an **absolute** path. Copy this directory with `.venv`
inside it and the copy will keep importing the original's `src/` — silently, with no
error. Run `make clean` before copying, or `make setup` again in the copy.

```bash
python -c "import apr; print(apr.__file__)"   # which tree am I actually running?
```
