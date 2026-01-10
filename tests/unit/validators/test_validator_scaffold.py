#!/usr/bin/env python3
"""
Unit tests and Hypothesis-based numeric stability test for validator_scaffold.

Run with:
    pytest tests/unit/validators/test_validator_scaffold.py -q

Requires:
    - sympy, numpy, pytest, hypothesis
"""

import numpy as np
import pytest
import sympy as sp

# Hypothesis for property-based numeric stability test
from hypothesis import given, settings
from hypothesis import strategies as st

from hypatiax.tools.validation.validator_scaffold import (
    ValidatorScaffold,
    find_denominator_bases,
    lambdify_and_eval,
    safe_sympify,
)


def test_safe_sympify_parses_with_locals():
    expr = safe_sympify("(r - rf) / sigma", var_names=["r", "rf", "sigma"])
    assert isinstance(expr, sp.Basic)
    syms = {str(s) for s in expr.free_symbols}
    assert syms == {"r", "rf", "sigma"}


def test_find_denominator_detects_pow_minus_one():
    expr = safe_sympify("1 / (x + 1) + a * b**-1", var_names=["x", "a", "b"])
    denoms = find_denominator_bases(expr)
    denoms_str = [str(d) for d in denoms]
    # both (x + 1) and b should appear as denominator bases (order may vary)
    assert any("x" in s for s in denoms_str)
    assert any(s == "b" for s in denoms_str)


def test_lambdify_and_eval_basic_success():
    expr = safe_sympify("(r - rf) / sigma", var_names=["r", "rf", "sigma"])
    # scalar numpy arrays
    test_data = {
        "r": np.array([0.10]),
        "rf": np.array([0.02]),
        "sigma": np.array([0.15]),
    }
    out = lambdify_and_eval(expr, test_data, symbol_order=["r", "rf", "sigma"])
    assert out["success"] is True
    assert out["value"] is not None
    assert np.all(np.isfinite(out["value"]))


def test_lambdify_and_eval_missing_data():
    expr = safe_sympify("x / y", var_names=["x", "y"])
    out = lambdify_and_eval(expr, {"x": np.array([1.0])}, symbol_order=["x", "y"])
    assert out["success"] is False
    assert out["error"] is not None
    assert "Missing test_data for symbol 'y'" in out["error"]


# Hypothesis-based test: generate sigma near zero to check numeric stability handling.
# We expect either evaluation to succeed with finite values, or the scaffold to capture the error.
@settings(max_examples=50)
@given(
    sigma=st.floats(
        min_value=-1e-6, max_value=1e-6, allow_nan=False, allow_infinity=False
    )
)
def test_numerical_stability_sharpe(sigma):
    """
    For expression (r - rf) / sigma, we generate small sigma values (including negative and zero)
    and assert that the lambdify_and_eval function captures exceptions or returns a finite/finite-array result.
    """
    expr = safe_sympify("(r - rf) / sigma", var_names=["r", "rf", "sigma"])
    # Choose scalar arrays for r and rf to keep shape simple
    r = np.array([0.10])
    rf = np.array([0.02])
    sigma_arr = np.array([sigma])

    out = lambdify_and_eval(
        expr, {"r": r, "rf": rf, "sigma": sigma_arr}, symbol_order=["r", "rf", "sigma"]
    )

    # If success, value must be finite OR non_finite flagged True (we accept either but must not raise)
    if out["success"]:
        # if non_finite True, that indicates np.isfinite found inf/nan — acceptable outcome
        if out.get("non_finite", False):
            assert np.any(~np.isfinite(out["value"]))
        else:
            # all values should be finite
            assert np.all(np.isfinite(out["value"]))
    else:
        # If not successful, we should have captured an error message
        assert out["error"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-q"])


"""
Notes:

The scaffold is intentionally small and focused on safety and diagnostics rather than domain-specific policy decisions.
The Hypothesis test focuses on the numeric stability of (r - rf) / sigma under small sigma perturbations. It asserts that the numeric evaluator either returns a finite value or captures the failure without raising uncaught exceptions.
You can extend ValidatorScaffold with:
unit/dimensional checks (pint integration),
richer AST pattern matching (e.g., detect sqrt of negative),
caching of lambdified functions for repeated evaluations.
If you want, I can:
add a pint-based dimensional checker integrated into the scaffold,
add caching for lambdified functions,
provide a PR with these files committed into your repository.
Ask anything

Nice — the scaffold and tests look good: all 5 tests passed (with a few runtime warnings from the Hypothesis numeric runs), so the validator scaffolding is working correctly in your environment.

What I did

Provided a small ValidatorScaffold module (tools/validation/validator_scaffold.py) that:
safely parses expressions with explicit SymPy locals,
inspects expression structure (free symbols, denominator bases),
lambdifies and evaluates numerically with robust error capture.
Added unit tests and a Hypothesis-based numeric-stability test (tests/unit/validators/test_validator_scaffold.py).
The tests exercise parsing, denominator detection, lambdify errors for missing data, and numeric stability around sigma ≈ 0.
What the test output shows

All tests passed (5 passed). Hypothesis generated some small/edge sigma values which produced runtime warnings (divide-by-zero / overflow) during numeric evaluation — those are expected and handled by the scaffold (the evaluator flags non-finite results rather than crashing).
No failing tests remain related to the scaffold.
Recommended next steps you can pick from

Add the scaffold to your repo (if not already committed) and import it from your EnhancedDomainValidator to consolidate parsing/inspection logic.
Add the scaffold and hypothesis to your dev dependencies (requirements-dev.txt or pyproject.toml) so CI installs them.
Integrate the Hypothesis test into CI; set settings(max_examples=...) lower for CI to control runtime.
Add a pint-based dimensional checker extension to the scaffold if you need unit/dimensional validation.
Add caching for lambdified functions keyed by (normalized expression, symbol order) to speed repeated evaluations.
Add a debug/verbose mode to the scaffold that appends the decision path to validation results (useful in production debugging).
If you want, I can create a PR adding the files to a branch, add entries to requirements-dev, and add a GitHub Actions workflow that runs pytest.
If you want any of those done now, tell me which one (e.g., "add pint integration", "create PR branch fix/validator-scaffold", or "add CI workflow") and I’ll prepare the changes.



"""
