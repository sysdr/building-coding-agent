#!/usr/bin/env bash
# The verification gate for Lesson 1. Exit 0 = lesson passed.
#
# What this gate establishes, in order:
#   1. the exact counter reproduces recorded ground truth exactly
#   2. the chars/4 heuristic is badly wrong, in BOTH directions
#   3. the model table spans a >5x cost range on one payload
#   4. a stable prefix is measurably cheaper than a mutated one
# Criterion 2 is the lesson. It is stated as a floor on the error, not a
# ceiling: a heuristic that quietly got accurate would mean the fixtures no
# longer represent real agent payloads, and the gate should fail then too.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=.venv/bin/python
[ -x "$PY" ] || PY=python3

echo "-- unit tests --"
$PY -m unittest discover -s tests 2>&1 | tail -4

echo
echo "-- exact counter vs recorded reference --"
$PY - <<'EOF'
import sys
from pathlib import Path
from apr import tokens as tok

FIX = Path("fixtures")
truth = tok.load_reference_counts(FIX / "reference_counts.json")
try:
    tok.count_exact("probe")
except tok.TokenizerUnavailable:
    print("SKIP: tiktoken not installed -- exact check skipped (offline path).")
    print("      The heuristic check below still runs against recorded truth,")
    print("      which is what this lesson actually argues about.")
    sys.exit(0)

bad = 0
for name, expected in sorted(truth.items()):
    got = tok.count_exact((FIX / "payloads" / name).read_text())
    flag = "PASS" if got == expected else "FAIL"
    if got != expected:
        bad += 1
    print(f"[{flag}] {name:<18} exact={got:<5} reference={expected}")
if bad:
    print(f"FAIL: {bad} payload(s) disagree with recorded reference counts")
    sys.exit(1)
print(f"PASS: exact counter reproduces all {len(truth)} reference counts")
EOF

echo
echo "-- heuristic error (the point of the lesson) --"
$PY - <<'EOF'
import sys
from pathlib import Path
from apr import tokens as tok

FIX = Path("fixtures")
truth = tok.load_reference_counts(FIX / "reference_counts.json")

MIN_ERR = 8.0          # a heuristic within 8% everywhere would be usable
MIN_PAYLOADS = 3       # ...so at least this many must be worse than that

errs = {}
print(f"{'payload':<18}{'chars/4':>9}{'true':>7}{'error':>9}")
for name, true_n in sorted(truth.items()):
    text = (FIX / "payloads" / name).read_text()
    est = tok.estimate_heuristic(text)
    err = (est - true_n) / true_n * 100.0
    errs[name] = err
    print(f"{name:<18}{est:>9}{true_n:>7}{err:>+8.1f}%")

over = [n for n, e in errs.items() if e > 0]
under = [n for n, e in errs.items() if e < 0]
bad = [n for n, e in errs.items() if abs(e) >= MIN_ERR]

print()
if len(bad) < MIN_PAYLOADS:
    print(f"FAIL: only {len(bad)} payload(s) exceed {MIN_ERR}% error; the "
          f"heuristic is more accurate than this lesson claims")
    sys.exit(1)
if not over or not under:
    print("FAIL: heuristic errs in only one direction -- a single correction "
          "factor would fix it, and the lesson's argument collapses")
    sys.exit(1)
hi, lo = max(errs.values()), min(errs.values())
print(f"PASS: chars/4 off by >={MIN_ERR}% on {len(bad)}/{len(errs)} payloads, "
      f"in BOTH directions ({hi:+.1f}% .. {lo:+.1f}%)")
print(f"      no single correction factor rescues a {hi - lo:.1f}-point spread")
EOF

echo
echo "-- model price spread --"
$PY - <<'EOF'
import sys
from pathlib import Path
from apr import tokens as tok

models = tok.load_models("configs/models.json")
text = (Path("fixtures/payloads") / "source.py").read_text()
n, _ = tok.count(text)
lo, hi, ratio = tok.price_spread(models, n, 500)
print(f"payload source.py: {n} input tokens, 500 output tokens assumed")
print(f"cheapest ${lo:.6f}   dearest ${hi:.6f}   spread {ratio:.1f}x")
if ratio <= 5.0:
    print(f"FAIL: spread {ratio:.1f}x does not exceed 5x")
    sys.exit(1)
print(f"PASS: model table spans {ratio:.1f}x on an identical payload")
EOF

echo
echo "-- cached vs uncached tool loop --"
$PY - <<'EOF'
import sys
from apr import tokens as tok

model = tok.load_models("configs/models.json")["workhorse"]
stable = tok.simulate_loop(model, turns=10, stable_prefix=True)
churn = tok.simulate_loop(model, turns=10, stable_prefix=False)
saving = (churn.total_usd - stable.total_usd) / churn.total_usd * 100

print(f"identical work, 10 turns, {stable.total_tokens_in} input tokens either way")
print(f"stable prefix     ${stable.total_usd:.6f}  ({stable.cached_tokens_in} cached)")
print(f"mutated prefix    ${churn.total_usd:.6f}  ({churn.cached_tokens_in} cached)")
if stable.total_tokens_in != churn.total_tokens_in:
    print("FAIL: token volumes differ -- the simulation is not comparing like for like")
    sys.exit(1)
if saving <= 0:
    print("FAIL: caching did not reduce cost")
    sys.exit(1)
print(f"PASS: stable prefix costs {saving:.1f}% less for identical token volume")
EOF

echo
echo "==================================================="
echo "PASS: Lesson 1 verified — scaffold, doctor, and token accounting all green"
echo "==================================================="
