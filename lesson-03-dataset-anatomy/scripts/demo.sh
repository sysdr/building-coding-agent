#!/usr/bin/env bash
# One command, visible result: watch the ledger reject a hand-wavy claim,
# then accept a real one.
set -euo pipefail
cd "$(dirname "$0")/.."
APR=".venv/bin/apr"

echo ">>> apr claim new --statement 'the swarm will be better' --would-disprove ''"
"$APR" claim new --statement "the swarm will be better" --would-disprove "" || true

echo ""
echo ">>> apr claim new --statement '...' --would-disprove '...' (a real falsifiable claim)"
"$APR" claim new \
  --statement "A minimal single-agent scaffold resolves at least as many dev-slice instances as a three-role swarm at equal cost." \
  --would-disprove "The swarm resolves strictly more instances than the single agent at equal or lower cost, on the same slice."

echo ""
echo ">>> apr claim list"
"$APR" claim list

echo ""
echo ">>> apr slice build --seed 42"
"$APR" slice build --seed 42
