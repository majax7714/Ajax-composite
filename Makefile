.PHONY: test lint check

test:
	python3 -m pytest -q

lint:
	ruff check src tests scripts

check: lint test
