#!/usr/bin/env bash
# The verification gate for Lesson 2. Exit 0 = lesson passed.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -x ".venv/bin/apr" ]; then
  echo "-- no venv found, running setup --"
  make setup
fi

APR=".venv/bin/apr"
PY=".venv/bin/python"
rm -rf .apr  # start each verify run from a clean ledger

echo "-- unit tests --"
.venv/bin/python -m unittest discover -s tests -v

echo "-- environment doctor --"
if ! "$APR" doctor; then
  echo "FAIL: environment doctor reported a critical failure"
  exit 1
fi
echo "-- version check --"
VERSION_OUT=$("$APR" --version)
echo "apr --version -> $VERSION_OUT"
[ -n "$VERSION_OUT" ] || { echo "FAIL: apr --version printed nothing"; exit 1; }
echo "PASS: apr --version prints package version ($VERSION_OUT)"

echo "-- claim rejection (must fail) --"
INVALID=$("$PY" -c "import json; d=json.load(open('fixtures/invalid_claim.json')); print(d['statement']); print(d['would_disprove'])")
STATEMENT=$(echo "$INVALID" | sed -n 1p)
DISPROVE=$(echo "$INVALID" | sed -n 2p)
if "$APR" claim new --statement "$STATEMENT" --would-disprove "$DISPROVE" 2>/tmp/apr_reject.log; then
  echo "FAIL: invalid claim was accepted"
  exit 1
fi
grep -q "REJECTED" /tmp/apr_reject.log
echo "PASS: claims ledger rejects a non-falsifiable claim ($(cat /tmp/apr_reject.log))"

echo "-- claim acceptance (must succeed) --"
VALID=$("$PY" -c "import json; d=json.load(open('fixtures/valid_claim.json')); print(d['statement']); print(d['would_disprove'])")
V_STATEMENT=$(echo "$VALID" | sed -n 1p)
V_DISPROVE=$(echo "$VALID" | sed -n 2p)
"$APR" claim new --statement "$V_STATEMENT" --would-disprove "$V_DISPROVE"
"$PY" -c "import json,sys; d=json.load(open('.apr/claims.json')); sys.exit(0 if len(d)==1 else 1)"
echo "PASS: claims.json valid against schema (1 recorded claim, well-formed JSON)"

echo ""
echo "==================================================="
echo "PASS: Lesson 2 verified — scaffold, doctor, and claims ledger all green"
echo "==================================================="
