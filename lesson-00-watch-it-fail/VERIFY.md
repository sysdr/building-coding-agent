# VERIFY.md — Lesson 0

## Environment

- Python 3.12.3, Linux x86_64
- pip 24.3.1
- Zero third-party dependencies (stdlib only)

## What was actually run

```
$ make setup && make test
Ran 7 tests in 0.761s
OK

$ make verify
== Lesson 0 has no gate — this script checks the mechanism, not a resolve rate ==
-- unit tests --  (7 passed)
-- fixture-backend mechanism check --
instance a [fixture backend]: RESOLVED in 3 turns (model_done)
instance b [fixture backend]: NOT RESOLVED in 3 turns (model_done)
-- prediction sealing --
prediction sealed to predictions.txt — unread until Lesson 9's failure taxonomy exists to check it.
PASS: mechanism verified — loop runs, both fixture transcripts written,
PASS: instance a resolves and instance b doesn't under the fixture backend,
PASS: prediction seals exactly once.
$ echo $?
0
```

Re-run from a clean unzip: `rm -rf .venv .apr predictions.txt && make setup && make test && make verify` — identical result.

## What was NOT run, disclosed rather than implied

- **The live, real-model two-instance demo.** This is the actual point of Lesson 0, and it
  is explicitly not verifiable in an automated build — the article itself argues that a
  scripted stand-in "would make this lesson safe, reproducible, and pointless." No
  `APR_MODEL_API_KEY` was available while building this zip, so `AnthropicModelClient` is
  real, working code that has never been executed against a live model in producing this
  artifact. Run `make demo` with your own key for the actual experience.
- **Docker path.** `docker/Dockerfile` and `docker/compose.yaml` are written and consistent
  with the native path, but were not built/run in this environment (no Docker daemon
  available at build time). Treat the Docker path as unverified until you run it yourself.

## Corrections made against the article's original text

1. The article originally said this lesson's code "hasn't been built yet" and gave the
   commands as "the design, not yet a working build." That's now false — `demo_agent.py`
   and its fixture-backed mechanism are built and verified above. Corrected the Status line
   and the "Get the code" section.
2. The article said `fixtures/reference_transcripts/` holds "real captured runs from the
   reference agent." No live model was available, so these are fixture-backend captures
   instead — corrected the wording, and the fixture's own README explains the gap in full.

## Illustrative vs. measured

Everything printed by `make verify` above was actually produced by running the commands
shown — none of it is a stated-but-unrun number. The two-instance "resolves / doesn't
resolve" split under the fixture backend is a designed property of the fixture repos in
`fixtures/instances/`, not a claim about model capability — it exists only to exercise the
loop, the transcript writer, and the prediction-sealing mechanism end to end.
