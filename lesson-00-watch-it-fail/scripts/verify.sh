#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Lesson 0 has no gate — this script checks the mechanism, not a resolve rate =="
echo

echo "-- unit tests --"
.venv/bin/python3 -m unittest discover -s tests -q

echo
echo "-- fixture-backend mechanism check (NOT a live-model claim) --"
rm -rf .apr
.venv/bin/python3 demo_agent.py demo --instance a --fixture
.venv/bin/python3 demo_agent.py demo --instance b --fixture

RESOLVED_A=$(.venv/bin/python3 -c "import json; print(json.load(open('.apr/demo/instance_a.json'))['resolved'])")
RESOLVED_B=$(.venv/bin/python3 -c "import json; print(json.load(open('.apr/demo/instance_b.json'))['resolved'])")

if [ "$RESOLVED_A" != "True" ] || [ "$RESOLVED_B" != "False" ]; then
    echo "FAIL: expected instance a resolved=True, instance b resolved=False (got a=$RESOLVED_A b=$RESOLVED_B)"
    exit 1
fi

echo
echo "-- prediction sealing --"
rm -f predictions.txt
.venv/bin/python3 demo_agent.py predict "the fixture agent misdiagnosed the bug as documentation, not logic"
test -f predictions.txt

echo
echo "PASS: mechanism verified — loop runs, both fixture transcripts written,"
echo "PASS: instance a resolves and instance b doesn't under the fixture backend,"
echo "PASS: prediction seals exactly once."
echo
echo "This does NOT verify the live two-instance demo described in the article —"
echo "that requires APR_MODEL_API_KEY and a real model call this environment"
echo "does not hold a key for. See VERIFY.md."
