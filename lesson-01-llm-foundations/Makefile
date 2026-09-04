.PHONY: setup build run test verify demo clean

setup:
	python3 -m venv --system-site-packages .venv
	.venv/bin/pip install --upgrade pip==24.3.1 || true
	.venv/bin/pip install -e ".[exact]" \
	  || .venv/bin/pip install -e . \
	  || .venv/bin/pip install --no-build-isolation -e .
	# Three fallbacks, narrowing as the network gets worse: with PyPI reachable
	# the first line installs the exact tokeniser; without it the package still
	# installs and the gate falls back to recorded reference counts.

build:
	.venv/bin/pip install -e .

run:
	.venv/bin/apr tokens count fixtures/payloads/source.py

test:
	.venv/bin/python -m unittest discover -s tests -v

verify:
	bash scripts/verify.sh

demo:
	bash scripts/demo.sh

clean:
	rm -rf .venv dist build src/*.egg-info .apr .pytest_cache __pycache__
