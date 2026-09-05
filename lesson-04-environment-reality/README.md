# Lesson 4 — Environment Reality

Cumulative through Lesson 4 of the *Autonomous Program Repair* course: the `apr`
package, environment doctor, claims ledger, dev-slice builder, and an
environment/image-layer inspector that predicts Docker layer reuse before any
image is built.

## 5-minute path to green

**Native:**
```bash
make setup
make verify
```

**Docker:**
```bash
docker compose -f docker/compose.yaml build
docker compose -f docker/compose.yaml run --rm apr image inspect
```

## What you should see

`make verify` ends with:
```
PASS: Lesson 4 verified — scaffold, claims ledger, dev slice, and environment inspector all green
```

## Try it yourself

```bash
.venv/bin/apr image inspect
# -> repo table + "5 distinct environment layer(s) across 13 instance(s)"
# -> "layer reuse rate: 92.3%"
```

See `VERIFY.md` for exact pinned versions and expected timings.

## If your edits seem to do nothing

An editable install records an **absolute** path. Copy this directory with `.venv`
inside it and the copy will keep importing the original's `src/` — silently, with no
error. Run `make clean` before copying, or `make setup` again in the copy.

```bash
python -c "import apr; print(apr.__file__)"   # which tree am I actually running?
```
