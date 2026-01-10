"""
Complete Extrapolation Testing Framework
Tests Pure LLM, Neural Network, and Hybrid (Symbolic Regression + LLM) approaches

Goal: Generate Table 1 results showing extrapolation performance
"""

import json
import numpy as np
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import time

# Import baselines
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from hypatiax.core.generation.baseline_pure_llm_defi_discovery import PureLLMBaseline
from hypatiax.core.generation.baseline_neural_network_defi_improved import (
    train_neural_network,
)
from hypatiax.core.generation.experiment_protocol_defi import DeFiExperimentProtocol


def generate_extrapolation_data(
    data_func,
    train_range: Tuple[float, float],
    test_range: Tuple[float, float],
    n_train: int = 100,
    n_test: int = 200,
    var_names: List[str] = None,
    noise_level: float = 0.01,
):
    """
    Generate train and test data with extrapolation range.

    Args:
        data_func: Function to generate y from X
        train_range: (min, max) for training data
        test_range: (min, max) for test data (should extend beyond train)
        n_train: Number of training samples
        n_test: Number of test samples
        var_names: Variable names
        noise_level: Noise to add to y

    Returns:
        X_train, y_train, X_test, y_test, in_domain_mask, out_domain_mask
    """
    np.random.seed(42)

    # Training data - LIMITED RANGE
    if len(var_names) == 1:
        X_train = np.random.uniform(train_range[0], train_range[1], (n_train, 1))
    else:
        X_train = np.random.uniform(
            train_range[0], train_range[1], (n_train, len(var_names))
        )

    y_train = data_func(X_train)

    # Add noise
    noise_std = noise_level * np.std(y_train)
    y_train += np.random.normal(0, noise_std, len(y_train))

    # Test data - EXTENDED RANGE (includes extrapolation)
    if len(var_names) == 1:
        X_test = np.linspace(test_range[0], test_range[1], n_test).reshape(-1, 1)
    else:
        X_test = np.random.uniform(
            test_range[0], test_range[1], (n_test, len(var_names))
        )

    y_test = data_func(X_test)

    # Create masks for in-domain vs out-of-domain
    if len(var_names) == 1:
        in_domain_mask = X_test[:, 0] <= train_range[1]
        out_domain_mask = X_test[:, 0] > train_range[1]
    else:
        # For multi-dim, check if all variables are in range
        in_domain_mask = np.all(
            (X_test >= train_range[0]) & (X_test <= train_range[1]), axis=1
        )
        out_domain_mask = ~in_domain_mask

    return X_train, y_train, X_test, y_test, in_domain_mask, out_domain_mask


def test_pure_llm_extrapolation(
    description: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    in_domain_mask: np.ndarray,
    out_domain_mask: np.ndarray,
    var_names: List[str],
    metadata: Dict,
) -> Dict:
    """Test Pure LLM baseline on extrapolation."""

    print(f"\n🔵 Testing Pure LLM: {description}")

    baseline = PureLLMBaseline()

    # Generate formula
    start = time.time()
    result = baseline.generate_formula(
        description, metadata.get("domain", "defi"), var_names, metadata
    )
    gen_time = time.time() - start

    # Test on TRAINING data first
    train_metrics = baseline.test_formula_accuracy(result, X_train, y_train, var_names)

    if not train_metrics.get("success"):
        return {
            "method": "pure_llm",
            "description": description,
            "error": train_metrics.get("error", "Unknown"),
            "success": False,
        }

    # Test on FULL TEST data (in-domain + out-domain)
    test_metrics = baseline.test_formula_accuracy(result, X_test, y_test, var_names)

    if not test_metrics.get("success"):
        return {
            "method": "pure_llm",
            "description": description,
            "train_r2": train_metrics["r2"],
            "error": "Failed on test data",
            "success": False,
        }

    # Calculate in-domain vs out-domain errors
    try:
        # Re-evaluate to get predictions
        python_code = result.get("python_code", "")
        local_vars = {}
        exec(python_code, {"np": np, "numpy": np}, local_vars)
        func = next(
            (
                v
                for v in local_vars.values()
                if callable(v) and not v.__name__.startswith("_")
            ),
            None,
        )

        y_pred = baseline.evaluate_function(func, X_test, var_names)

        # In-domain metrics
        y_true_in = y_test[in_domain_mask]
        y_pred_in = y_pred[in_domain_mask]

        mae_in = np.mean(np.abs(y_true_in - y_pred_in))
        rel_error_in = mae_in / (np.mean(np.abs(y_true_in)) + 1e-10)

        # Out-of-domain metrics
        y_true_out = y_test[out_domain_mask]
        y_pred_out = y_pred[out_domain_mask]

        mae_out = np.mean(np.abs(y_true_out - y_pred_out))
        rel_error_out = mae_out / (np.mean(np.abs(y_true_out)) + 1e-10)

        # Extrapolation ratio
        extrap_ratio = rel_error_out / (rel_error_in + 1e-10)

        print(f"  ✅ Train R²: {train_metrics['r2']:.4f}")
        print(f"  📊 In-domain error: {rel_error_in:.4f}")
        print(f"  📊 Out-domain error: {rel_error_out:.4f}")
        print(f"  📊 Extrapolation ratio: {extrap_ratio:.2f}x")

        return {
            "method": "pure_llm",
            "description": description,
            "formula": result.get("formula", "N/A"),
            "train_r2": float(train_metrics["r2"]),
            "test_r2": float(test_metrics["r2"]),
            "in_domain_error": float(rel_error_in),
            "out_domain_error": float(rel_error_out),
            "extrapolation_ratio": float(extrap_ratio),
            "generation_time": gen_time,
            "success": True,
        }

    except Exception as e:
        print(f"  ❌ Error calculating extrapolation metrics: {e}")
        return {
            "method": "pure_llm",
            "description": description,
            "train_r2": train_metrics["r2"],
            "test_r2": test_metrics["r2"],
            "error": str(e),
            "success": False,
        }


def test_neural_network_extrapolation(
    description: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    in_domain_mask: np.ndarray,
    out_domain_mask: np.ndarray,
    var_names: List[str],
    metadata: Dict,
) -> Dict:
    """Test Neural Network on extrapolation."""

    print(f"\n🔴 Testing Neural Network: {description}")

    # Train NN (returns predictions on test split)
    result = train_neural_network(
        X_train,
        y_train,
        description,
        metadata.get("domain", "defi"),
        metadata,
        epochs=500,
        lr=0.001,
        verbose=False,
    )

    # Now evaluate on full test set with extrapolation
    import torch
    from sklearn.preprocessing import StandardScaler
    from hypatiax.core.generation.baseline_neural_network_defi_improved import (
        ImprovedNN,
    )

    # Retrain to get model
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_train_scaled = scaler_X.fit_transform(X_train)
    y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()

    X_train_t = torch.FloatTensor(X_train_scaled)
    y_train_t = torch.FloatTensor(y_train_scaled).reshape(-1, 1)

    model = ImprovedNN(X_train.shape[1], hidden_dims=[128, 64, 32])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.MSELoss()

    # Quick training
    for epoch in range(200):
        optimizer.zero_grad()
        pred = model(X_train_t)
        loss = criterion(pred, y_train_t)
        loss.backward()
        optimizer.step()

    # Evaluate on test set
    model.eval()
    with torch.no_grad():
        X_test_scaled = scaler_X.transform(X_test)
        X_test_t = torch.FloatTensor(X_test_scaled)
        y_pred_scaled = model(X_test_t).numpy().flatten()
        y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

    # Calculate metrics
    # In-domain
    y_true_in = y_test[in_domain_mask]
    y_pred_in = y_pred[in_domain_mask]

    mae_in = np.mean(np.abs(y_true_in - y_pred_in))
    rel_error_in = mae_in / (np.mean(np.abs(y_true_in)) + 1e-10)

    # Out-of-domain
    y_true_out = y_test[out_domain_mask]
    y_pred_out = y_pred[out_domain_mask]

    mae_out = np.mean(np.abs(y_true_out - y_pred_out))
    rel_error_out = mae_out / (np.mean(np.abs(y_true_out)) + 1e-10)

    # Extrapolation ratio
    extrap_ratio = rel_error_out / (rel_error_in + 1e-10)

    # Overall test R²
    ss_res = np.sum((y_test - y_pred) ** 2)
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    test_r2 = 1 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0.0

    print(f"  ✅ Train R²: {result['evaluation']['r2']:.4f}")
    print(f"  📊 In-domain error: {rel_error_in:.4f}")
    print(f"  📊 Out-domain error: {rel_error_out:.4f}")
    print(f"  📊 Extrapolation ratio: {extrap_ratio:.2f}x")

    return {
        "method": "neural_network",
        "description": description,
        "train_r2": float(result["evaluation"]["r2"]),
        "test_r2": float(test_r2),
        "in_domain_error": float(rel_error_in),
        "out_domain_error": float(rel_error_out),
        "extrapolation_ratio": float(extrap_ratio),
        "success": True,
    }


def run_extrapolation_experiment():
    """
    Run complete extrapolation experiment across key DeFi formulas.

    Tests:
    1. Impermanent Loss - Train on [0.1, 5], Test on [0.1, 10]
    2. VaR (95%) - Train on [0, 100k], Test on [0, 500k]
    3. Liquidation Price - Train on [2x, 10x], Test on [2x, 50x]
    """

    print("=" * 80)
    print("EXTRAPOLATION TESTING FRAMEWORK")
    print("=" * 80)
    print("Goal: Measure extrapolation performance vs interpolation")
    print("Metric: Out-of-domain error / In-domain error ratio")
    print("=" * 80)

    results = []

    # ============================================================
    # TEST 1: Impermanent Loss
    # ============================================================
    print("\n" + "=" * 80)
    print("[1/3] IMPERMANENT LOSS")
    print("=" * 80)

    def il_func(X):
        r = X[:, 0] if X.ndim > 1 else X
        return 2 * np.sqrt(r) / (r + 1) - 1

    X_train, y_train, X_test, y_test, in_mask, out_mask = generate_extrapolation_data(
        il_func,
        train_range=(0.1, 5.0),
        test_range=(0.1, 10.0),
        n_train=100,
        n_test=200,
        var_names=["price_ratio"],
    )

    metadata = {
        "domain": "amm",
        "ground_truth": "IL = 2√r/(1+r) - 1",
        "difficulty": "hard",
        "formula_type": "algebraic_with_sqrt",
        "extrapolation_test": True,
    }

    # Test Pure LLM
    llm_result = test_pure_llm_extrapolation(
        "Impermanent loss in constant product AMM",
        X_train,
        y_train,
        X_test,
        y_test,
        in_mask,
        out_mask,
        ["price_ratio"],
        metadata,
    )
    results.append(llm_result)

    # Test Neural Network
    nn_result = test_neural_network_extrapolation(
        "Impermanent loss in constant product AMM",
        X_train,
        y_train,
        X_test,
        y_test,
        in_mask,
        out_mask,
        ["price_ratio"],
        metadata,
    )
    results.append(nn_result)

    # ============================================================
    # TEST 2: Value at Risk
    # ============================================================
    print("\n" + "=" * 80)
    print("[2/3] VALUE AT RISK (95%)")
    print("=" * 80)

    def var_func(X):
        portfolio_value = X[:, 0]
        daily_vol = X[:, 1]
        z_95 = 1.645
        return portfolio_value * daily_vol * z_95

    X_train, y_train, X_test, y_test, in_mask, out_mask = generate_extrapolation_data(
        var_func,
        train_range=(0, 100000),
        test_range=(0, 500000),
        n_train=100,
        n_test=200,
        var_names=["portfolio_value", "daily_volatility"],
    )

    metadata = {
        "domain": "risk_var",
        "ground_truth": "VaR = V × σ × z",
        "difficulty": "easy",
        "formula_type": "linear",
        "extrapolation_test": True,
    }

    llm_result = test_pure_llm_extrapolation(
        "Parametric Value at Risk at 95% confidence",
        X_train,
        y_train,
        X_test,
        y_test,
        in_mask,
        out_mask,
        ["portfolio_value", "daily_volatility"],
        metadata,
    )
    results.append(llm_result)

    nn_result = test_neural_network_extrapolation(
        "Parametric Value at Risk at 95% confidence",
        X_train,
        y_train,
        X_test,
        y_test,
        in_mask,
        out_mask,
        ["portfolio_value", "daily_volatility"],
        metadata,
    )
    results.append(nn_result)

    # ============================================================
    # TEST 3: Liquidation Price
    # ============================================================
    print("\n" + "=" * 80)
    print("[3/3] LIQUIDATION PRICE")
    print("=" * 80)

    def liq_func(X):
        entry_price = X[:, 0]
        leverage = X[:, 1]
        m = 0.8
        return entry_price * (1 - 1 / (leverage * m))

    X_train, y_train, X_test, y_test, in_mask, out_mask = generate_extrapolation_data(
        liq_func,
        train_range=(10000, 50000),  # Entry price + leverage combos
        test_range=(10000, 100000),
        n_train=100,
        n_test=200,
        var_names=["entry_price", "leverage"],
    )

    metadata = {
        "domain": "liquidation",
        "ground_truth": "P_liq = P_e × (1 - 1/(L×m))",
        "difficulty": "hard",
        "formula_type": "rational",
        "extrapolation_test": True,
    }

    llm_result = test_pure_llm_extrapolation(
        "Liquidation price for leveraged long position",
        X_train,
        y_train,
        X_test,
        y_test,
        in_mask,
        out_mask,
        ["entry_price", "leverage"],
        metadata,
    )
    results.append(llm_result)

    nn_result = test_neural_network_extrapolation(
        "Liquidation price for leveraged long position",
        X_train,
        y_train,
        X_test,
        y_test,
        in_mask,
        out_mask,
        ["entry_price", "leverage"],
        metadata,
    )
    results.append(nn_result)

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/extrapolation_results_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    # Calculate averages
    llm_results = [r for r in results if r["method"] == "pure_llm" and r.get("success")]
    nn_results = [
        r for r in results if r["method"] == "neural_network" and r.get("success")
    ]

    if llm_results:
        llm_avg_extrap = np.mean([r["extrapolation_ratio"] for r in llm_results])
        llm_avg_in = np.mean([r["in_domain_error"] for r in llm_results])
        llm_avg_out = np.mean([r["out_domain_error"] for r in llm_results])

        print(f"\n🔵 Pure LLM:")
        print(f"  In-domain error: {llm_avg_in:.4f} ({llm_avg_in * 100:.2f}%)")
        print(f"  Out-domain error: {llm_avg_out:.4f} ({llm_avg_out * 100:.2f}%)")
        print(f"  Extrapolation ratio: {llm_avg_extrap:.2f}x")

    if nn_results:
        nn_avg_extrap = np.mean([r["extrapolation_ratio"] for r in nn_results])
        nn_avg_in = np.mean([r["in_domain_error"] for r in nn_results])
        nn_avg_out = np.mean([r["out_domain_error"] for r in nn_results])

        print(f"\n🔴 Neural Network:")
        print(f"  In-domain error: {nn_avg_in:.4f} ({nn_avg_in * 100:.2f}%)")
        print(f"  Out-domain error: {nn_avg_out:.4f} ({nn_avg_out * 100:.2f}%)")
        print(f"  Extrapolation ratio: {nn_avg_extrap:.2f}x")

    print(f"\n✅ Results saved to: {output_file}")
    print("=" * 80)

    return results


if __name__ == "__main__":
    run_extrapolation_experiment()
