# Lesson 1 — LLM Foundations for Agentic Coding

Five minutes from unzip to green.

```bash
make setup     # venv + editable install (+ tiktoken if the network allows)
make verify    # the gate — exit 0 means the lesson passed
```

Expected last line:

```
PASS: Lesson 1 verified — scaffold, doctor, and token accounting all green
```

## What this ships

- `apr` — the package namespace, stable across all 54 lessons
- `apr doctor` — environment checks (python, git, docker)
- `apr tokens count` — exact vs heuristic token counts on any file
- `apr tokens price` — one payload across your model table
- `apr tokens loop` — a 10-turn tool loop, cached prefix vs mutated prefix

## Other targets

| Target | What it does |
|---|---|
| `make build` | editable install only |
| `make run` | counts tokens in the sample source payload |
| `make test` | 19 fast unit tests, no network |
| `make verify` | the full lesson gate |
| `make demo` | the same payload counted two ways, then priced three ways |
| `make clean` | remove venv and build artifacts |

## Known gap

The Docker path ships but was verified only by inspection — the reference machine's Docker
CLI cannot reach WSL paths. See `VERIFY.md`. The native path is fully verified.

## Before you trust the numbers

`configs/models.json` contains **illustrative** prices, not any vendor's real
rates. Replace them with your provider's current published prices before you
budget anything. See `VERIFY.md` for exactly what this lesson's numbers do and
do not establish.

## If your edits seem to do nothing

An editable install records an **absolute** path. Copy this directory with `.venv`
inside it and the copy will keep importing the original's `src/` — silently, with no
error. Run `make clean` before copying, or `make setup` again in the copy.

```bash
python -c "import apr; print(apr.__file__)"   # which tree am I actually running?
```
