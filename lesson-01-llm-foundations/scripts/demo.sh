#!/usr/bin/env bash
# 60-second demo: the same file, counted two ways, then priced three ways.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3

echo "== the same payload, counted two ways =="
$PY -m apr.cli tokens count fixtures/payloads/observation.txt
echo
echo "== what one turn of it costs, three ways =="
$PY -m apr.cli tokens price fixtures/payloads/observation.txt
