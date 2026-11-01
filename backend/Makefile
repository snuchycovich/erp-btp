.PHONY: lint test

PYTHON ?= .venv/bin/python
PYRIGHT ?= .venv/bin/pyright

lint:
	$(PYTHON) -m ruff check app tests
	$(PYTHON) -m ruff format --check app tests
	$(PYRIGHT) app tests

fix:
	$(PYTHON) -m ruff check app tests --fix
	$(PYTHON) -m ruff format app tests

test:
	$(PYTHON) -m pytest -v
