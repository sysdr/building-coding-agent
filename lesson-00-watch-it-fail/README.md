# Lesson 0 — Watch It Work. Then Watch It Fail.

The pinned, single-file agent from the article. No package, no scaffold, no dependency
on any later lesson — that's the point.

## 5-minute path

```bash
make setup
make test      # 7 unit tests, offline, ~1s
make verify    # mechanism check against the offline fixture backend, exit 0 = PASS
```

## The real demo

```bash
export APR_MODEL_API_KEY=...   # your own key; nothing below works without one
make demo
```

Without a key, `make demo` falls back to the same offline fixture backend `make verify`
uses — useful for seeing the shape of things, but it can't give you the genuine
uncertainty a live model run has, because the fixture agent's moves are scripted.

```bash
.venv/bin/python3 demo_agent.py predict "your one-sentence guess" > /dev/null
cat predictions.txt
```

## What's real here, and what isn't

- `demo_agent.py`'s loop, transcript capture, and prediction sealing are real and tested.
- The two prepared instances (`fixtures/instances/`) are small, real, self-contained repos
  with a real bug and a real failing test — not SWE-bench instances, since this zip ships
  with zero third-party dependencies and no network access at build time. They're built to
  demonstrate the same shape (one resolves, one doesn't, under the minimal scaffold) that
  the article's real SWE-bench instances demonstrate at course scale.
- `fixtures/reference_transcripts/` is captured from the fixture backend, not a live model —
  see its own README for why, and what that means for how much confusion it can actually give you.
- `AnthropicModelClient` is real, working code, unexercised by any test in this build.

See `VERIFY.md` for exact measured output and every correction made against the article's
original text.
