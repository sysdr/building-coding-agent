.PHONY: setup build run test verify demo clean

setup:
	python3 -m venv --system-site-packages .venv
	.venv/bin/pip install --upgrade pip==24.3.1 || true
	.venv/bin/pip install -e ".[exact]" || .venv/bin/pip install -e . || .venv/bin/pip install --no-build-isolation -e .
	# --system-site-packages + the --no-build-isolation fallback let this
	# install from the machine's existing setuptools/wheel when PyPI isn't
	# reachable (see VERIFY.md). With network access, the first line succeeds
	# and pulls the pinned setuptools==68.1.2 / wheel==0.42.0 from PyPI instead.

build:
	.venv/bin/pip install -e .

run:
	.venv/bin/apr doctor

test:
	.venv/bin/python -m unittest discover -s tests -v

verify:
	bash scripts/verify.sh

demo:
	bash scripts/demo.sh

clean:
	rm -rf .venv dist build src/*.egg-info .apr .pytest_cache
