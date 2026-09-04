#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Load .env if present so `make demo` picks up APR_MODEL_API_KEY without a manual export.
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

if [ -n "${APR_MODEL_API_KEY:-}" ] && [ "${APR_MODEL_API_KEY}" != "YOUR_API_KEY_HERE" ]; then
    echo "APR_MODEL_API_KEY is set — running the real two-instance demo."
    .venv/bin/python3 demo_agent.py demo --instance a
    .venv/bin/python3 demo_agent.py demo --instance b
else
    echo "No APR_MODEL_API_KEY set — running the offline fixture backend instead."
    echo "This shows the mechanism, not the genuine surprise the article describes;"
    echo "set a real key and rerun for the actual experience."
    .venv/bin/python3 demo_agent.py demo --instance a --fixture
    .venv/bin/python3 demo_agent.py demo --instance b --fixture
fi

echo
echo "Read both transcripts in .apr/demo/ before moving on."
