.PHONY: install-dev test coverage bench clean ci

PY = python3
PIP = pip
REQS = requirements-dev.txt
MODULE = uniswap_v2_formulas_extended

install-dev:
	$(PIP) install -r $(REQS)

test:
	pytest -q

coverage:
	pytest -q --maxfail=1 --cov=$(MODULE) --cov-report=term-missing

coverage-html:
	pytest -q --cov=$(MODULE) --cov-report=html

bench:
	pytest -q -m "benchmark or benchmark" --benchmark-only

ci: install-dev coverage

clean:
	rm -rf .pytest_cache .cache htmlcov .coverage __pycache__
