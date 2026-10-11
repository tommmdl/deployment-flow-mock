.PHONY: test lint prepare deploy smoke remove
PYTHON ?= .venv/bin/python
lint:
	$(PYTHON) -m ruff check app scripts
	$(PYTHON) -m ruff format --check app scripts
test:
	$(PYTHON) -m pytest -q
prepare deploy remove:
	bash scripts/lab.sh $@
smoke:
	bash scripts/lab.sh verify
