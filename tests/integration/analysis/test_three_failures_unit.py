# tests/unit/test_three_failures_unit.py
"""
Unit tests for the three previously failing cases: Kelly, Impermanent Loss, Expected Shortfall.

These tests DO NOT call the LLM. They use canonical deterministic implementations
of each formula (the same code the specialized prompts are intended to produce),
evaluate those implementations against the protocol test data, and train a neural
network baseline for comparison.

Run:
    pytest -q tests/unit/test_three_failures_unit.py
"""

import importlib
import sys
import types
import math
import numpy as np
import pytest

# Import protocol and neural baseline
from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol
from hypatiax.core.generation.baseline_neural_network_defi import NeuralNetworkBaseline


# Helper to execute parsed python code (string) safely and compute metrics
def evaluate_python_code(
    python_code: str, X: np.ndarray, y_true: np.ndarray, var_names=None
):
    """
    Execute python_code which defines a function (named 'formula' or any def).
    Returns metrics dict: {'r2','rmse','mae','mse','y_pred'}
    """
    # Prepare execution environment
    exec_globals = {"np": np, "numpy": np, "__name__": "__safe_exec__"}
    local_vars = {}

    # If the code contains 'def' we'll exec and find callable
    try:
        exec(python_code, exec_globals, local_vars)
    except Exception as e:
        raise RuntimeError(
            f"Failed to exec python code: {e}\nCode:\n{python_code[:400]}"
        )

    # find callable function
    func = None
    for v in local_vars.values():
        if callable(v):
            func = v
            break
    if func is None:
        # try to find in globals
        for v in exec_globals.values():
            if callable(v) and getattr(v, "__name__", "") != "np":
                func = v
                break
    if func is None:
        raise RuntimeError("No callable found in executed code")

    # Evaluate vectorized if possible
    n = X.shape[0]
    try:
        if X.ndim == 1 or X.shape[1] == 1:
            args = [X[:, 0]] if X.ndim > 1 else [X]
            y_pred = func(*args)
        else:
            args = [X[:, i] for i in range(X.shape[1])]
            y_pred = func(*args)
        y_pred = np.asarray(y_pred).flatten()
    except Exception:
        # fallback row-by-row
        y_pred = np.empty(n)
        for i in range(n):
            row = X[i, :]
            try:
                if row.size == 1:
                    y_pred[i] = float(func(row[0]))
                else:
                    y_pred[i] = float(func(*row))
            except Exception as e:
                raise RuntimeError(f"Function failed on row {i}: {e}")

    # metrics
    mse = float(np.mean((y_true - y_pred) ** 2))
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(mse))
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 1e-12 else 0.0

    return {"mse": mse, "mae": mae, "rmse": rmse, "r2": r2, "y_pred": y_pred}


@pytest.fixture(scope="module")
def protocol():
    return DeFiExperimentProtocol()


def find_case(protocol, domain, keyword):
    """Return the first case whose description contains keyword (case-insensitive)."""
    for desc, X, y, var_names, meta in protocol.load_test_data(domain, num_samples=100):
        if keyword.lower() in desc.lower():
            return desc, X, y, var_names, meta
    raise RuntimeError(
        f"Test case with keyword '{keyword}' not found in domain '{domain}'"
    )


def test_kelly_criterion_fits_perfectly(protocol):
    # canonical Kelly python code (vectorized)
    python_code = """
def formula(expected_fee_apy, il_risk):
    risk_aversion = 2.0
    f_star = expected_fee_apy / (risk_aversion * il_risk**2)
    return np.minimum(f_star, 1.0)
"""

    desc, X, y, var_names, meta = find_case(protocol, "liquidity", "kelly")
    print("\n--- Kelly test case:", desc)
    metrics = evaluate_python_code(python_code, X, y, var_names=var_names)
    print("Symbolic (LLM) metrics:", metrics)
    assert metrics["r2"] > 0.9999  # near-perfect fit
    # Train NN for comparison (will not match perfectly on extrapolation)
    nn = NeuralNetworkBaseline(hidden_dims=[64, 32], epochs=100)
    nn_result = nn.train_and_evaluate(
        X, y, description=desc, metadata=meta, verbose=False
    )
    print("NN metrics:", nn_result["metrics"])
    assert "r2" in nn_result["metrics"]


def test_impermanent_loss_fits_perfectly(protocol):
    python_code = """
def formula(price_ratio):
    il_fraction = 2.0 * np.sqrt(price_ratio) / (1.0 + price_ratio) - 1.0
    return il_fraction * 100.0
"""
    desc, X, y, var_names, meta = find_case(protocol, "amm", "impermanent loss")
    print("\n--- Impermanent Loss test case:", desc)
    metrics = evaluate_python_code(python_code, X, y, var_names=var_names)
    print("Symbolic (LLM) metrics:", metrics)
    assert metrics["r2"] > 0.9999
    nn = NeuralNetworkBaseline(hidden_dims=[64, 32], epochs=100)
    nn_result = nn.train_and_evaluate(
        X, y, description=desc, metadata=meta, verbose=False
    )
    print("NN metrics:", nn_result["metrics"])
    assert "r2" in nn_result["metrics"]


def test_expected_shortfall_fits_perfectly(protocol):
    python_code = """
def formula(position1_es, position2_es, correlation):
    return position1_es + position2_es + correlation * np.sqrt(position1_es * position2_es)
"""
    desc, X, y, var_names, meta = find_case(protocol, "risk", "expected shortfall")
    print("\n--- Expected Shortfall test case:", desc)
    metrics = evaluate_python_code(python_code, X, y, var_names=var_names)
    print("Symbolic (LLM) metrics:", metrics)
    # ES sometimes uses small floating discrepancies - allow small tolerance
    assert metrics["r2"] > 0.9999
    nn = NeuralNetworkBaseline(hidden_dims=[64, 32], epochs=100)
    nn_result = nn.train_and_evaluate(
        X, y, description=desc, metadata=meta, verbose=False
    )
    print("NN metrics:", nn_result["metrics"])
    assert "r2" in nn_result["metrics"]
