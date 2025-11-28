your_project/
├─ uniswap_v2_formulas_extended.py
├─ requirements-dev.txt
├─ pytest.ini
├─ .coveragerc
├─ Makefile
├─ run_tests.py
├─ tests/
│  ├─ test_defi_formulas.py                # existing unit tests (you already have)
│  ├─ test_defi_formulas_coverage.py       # coverage-optimized/fast subset
│  ├─ test_property_based.py               # Hypothesis property-based tests
│  └─ test_benchmarks.py                   # pytest-benchmark benchmarks
└─ .github/
   └─ workflows/
      └─ ci.yml
