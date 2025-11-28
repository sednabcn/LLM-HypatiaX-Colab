10) How to run everything locally

Install dev deps:

pip install -r requirements-dev.txt


Run full test suite:

pytest -q


Run coverage:

make coverage
# or
pytest -q --cov=uniswap_v2_formulas_extended --cov-report=term-missing


Run benchmarks:

pytest -q tests/test_benchmarks.py --benchmark-only


Run Hypothesis tests (they are included in pytest run). To restrict Hypothesis examples or speed up locally:

pytest -q tests/test_property_based.py -k "not slow"


(You can also add Hypothesis settings in the test file, e.g. @settings(max_examples=100).)

11) Extra suggestions (optional)

Add python -m pip install pre-commit and a .pre-commit-config.yaml for linting.

Add tox.ini if you want a tox matrix locally.

If some Hypothesis tests are too heavy in CI, decorate them with @pytest.mark.slow and exclude -m "not slow" in CI.

