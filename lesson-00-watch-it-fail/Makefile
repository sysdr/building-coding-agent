.PHONY: setup build run test verify demo clean

setup:
	python3 -m venv --system-site-packages .venv
	.venv/bin/pip install --upgrade pip==24.3.1 || true
	# demo_agent.py is stdlib-only, on purpose — this lesson has no package
	# to build, no scaffold, nothing to install. setup just gives you a venv
	# so `test`/`verify`/`demo` behave the same as every later lesson's.

build:
	@echo "Nothing to build — demo_agent.py is a single stdlib-only file. See README."

run:
	.venv/bin/python3 demo_agent.py demo --instance a --fixture

test:
	.venv/bin/python3 -m unittest discover -s tests -v

verify:
	bash scripts/verify.sh

demo:
	bash scripts/demo.sh

clean:
	rm -rf .venv .apr predictions.txt __pycache__ tests/__pycache__ .pytest_cache
