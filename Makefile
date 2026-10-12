.PHONY: check test run install-hooks

PYTHON ?= python3

check:
	$(PYTHON) -m compileall -q src tests
	$(PYTHON) -m unittest discover -s tests -t .

test:
	$(PYTHON) -m unittest discover -s tests -t .

run:
	$(PYTHON) -m src

install-hooks:
	git config core.hooksPath .githooks
