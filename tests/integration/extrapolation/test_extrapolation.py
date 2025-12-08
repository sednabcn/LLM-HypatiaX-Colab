"""
Extrapolation testing module for symbolic regression.

This module tests how well discovered formulas extrapolate beyond training data
by evaluating performance on in-domain and out-of-domain regions.
"""

import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hypatiax.tools.symbolic.symbolic_engine import DiscoveryConfig, SymbolicEngine


def test_extrapolation(formula_name, ground_truth_func, X_range, n_samples=100):
    """
    Test the discovered formula's extrapolation beyond training data.

    Args:
        formula_name: Name of the formula being tested
        ground_truth_func: Function that computes true values
        X_range: Tuple of (min, max) for training data
        n_samples: Number of training samples

    Returns:
        Dictionary with extrapolation metrics including:
        - formula: Name of the formula
        - discovered_expression: String representation of discovered formula
        - r2_train: R² score on training data
        - complexity: Complexity of discovered formula
        - in_domain_error: Relative error within training range
        - out_domain_error: Relative error beyond training range
        - extrapolation_ratio: Ratio of out-domain to in-domain error
        - training_range: Min/max of training data
        - test_range: Min/max of test data including extrapolation
    """
    print(f"\nTesting: {formula_name}")
    print("-" * 60)

    # Generate training data (limited range)
    np.random.seed(42)
    X_train = np.random.uniform(X_range[0], X_range[1], (n_samples, 1))
    y_train = ground_truth_func(X_train[:, 0])

    # Add small noise to make it realistic
    noise_std = 0.01 * np.std(y_train)
    y_train += np.random.normal(0, noise_std, n_samples)

    print(f"Training range: [{X_range[0]:.2f}, {X_range[1]:.2f}]")
    print(f"Training samples: {n_samples}")

    # Discover formula
    print("Running symbolic regression...")
    engine = SymbolicEngine(DiscoveryConfig(niterations=40, populations=15, population_size=50))
    result = engine.discover(X_train, y_train, variable_names=["x"])

    print(f"Discovered: {result['expression']}")
    print(f"R² on training: {result['r2_score']:.4f}")

    # Test extrapolation (2x beyond training range)
    X_test = np.linspace(X_range[0], X_range[1] * 2, 200).reshape(-1, 1)
    y_true = ground_truth_func(X_test[:, 0])

    # Evaluate discovered formula
    try:
        import sympy as sp

        x_sym = sp.Symbol("x")
        expr = result["sympy_expr"]

        # Vectorized evaluation
        y_pred = np.array([float(expr.subs(x_sym, float(x_val))) for x_val in X_test[:, 0]])
    except Exception as e:
        print(f"Error evaluating expression: {e}")
        return None

    # Calculate errors in different regions
    in_domain_mask = X_test[:, 0] <= X_range[1]
    out_domain_mask = X_test[:, 0] > X_range[1]

    # In-domain metrics
    in_domain_mae = np.mean(np.abs(y_true[in_domain_mask] - y_pred[in_domain_mask]))
    in_domain_relative = in_domain_mae / (np.mean(np.abs(y_true[in_domain_mask])) + 1e-10)

    # Out-of-domain metrics
    out_domain_mae = np.mean(np.abs(y_true[out_domain_mask] - y_pred[out_domain_mask]))
    out_domain_relative = out_domain_mae / (np.mean(np.abs(y_true[out_domain_mask])) + 1e-10)

    extrapolation_ratio = out_domain_relative / (in_domain_relative + 1e-10)

    print(f"In-domain error: {in_domain_relative:.4f} ({in_domain_relative*100:.2f}%)")
    print(f"Out-of-domain error: {out_domain_relative:.4f} ({out_domain_relative*100:.2f}%)")
    print(f"Extrapolation ratio: {extrapolation_ratio:.2f}x")

    # Create visualization
    plt.figure(figsize=(10, 6))

    # Training data
    plt.scatter(X_train, y_train, alpha=0.5, s=20, c="blue", label="Training data", zorder=3)

    # Ground truth
    plt.plot(X_test, y_true, "g-", label="Ground truth", linewidth=2.5, alpha=0.8, zorder=2)

    # Discovered formula
    plt.plot(X_test, y_pred, "r--", label="Discovered formula", linewidth=2, alpha=0.8, zorder=2)

    # Mark training boundary
    plt.axvline(X_range[1], color="black", linestyle=":", linewidth=2, label="Training boundary", zorder=1)

    # Shade extrapolation region
    plt.axvspan(X_range[1], X_range[1] * 2, alpha=0.1, color="red", label="Extrapolation region", zorder=0)

    plt.xlabel("X", fontsize=12)
    plt.ylabel("Y", fontsize=12)
    plt.title(
        f"Extrapolation Test: {formula_name}\n" f"Discovered: {result['expression']} (R²={result['r2_score']:.4f})",
        fontsize=11,
    )
    plt.legend(loc="best", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save plot
    os.makedirs("results", exist_ok=True)
    plot_path = f"results/extrapolation_{formula_name}.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Plot saved to {plot_path}")

    return {
        "formula": formula_name,
        "discovered_expression": result["expression"],
        "r2_train": float(result["r2_score"]),
        "complexity": result["complexity"],
        "in_domain_error": float(in_domain_relative),
        "out_domain_error": float(out_domain_relative),
        "extrapolation_ratio": float(extrapolation_ratio),
        "training_range": list(X_range),
        "test_range": [float(X_range[0]), float(X_range[1] * 2)],
    }


def run_all_extrapolation_tests():
    """Run extrapolation tests on multiple formulas.

    Tests include:
    1. Impermanent Loss - DeFi-specific formula
    2. Value at Risk (VaR) - Risk management metric
    3. Quadratic - Control test for baseline performance

    Returns:
        list: List of dictionaries containing test results for each formula
    """
    print("\n" + "=" * 80)
    print("EXTRAPOLATION TESTING")
    print("=" * 80)

    results = []

    # Test 1: Impermanent Loss
    print("\n[1/3] Impermanent Loss Formula")

    def il_func(x):
        """Compute the impermanent loss: 2*sqrt(x)/(x+1) - 1."""
        return 2 * np.sqrt(x) / (x + 1) - 1

    result = test_extrapolation("impermanent_loss", il_func, (0.1, 5.0))
    if result:
        results.append(result)

    # Test 2: Value at Risk (VaR)
    print("\n[2/3] Value at Risk (95% confidence)")

    def var_func(x):
        """Value at Risk at 95% confidence level."""
        mu, sigma = 0, 0.2
        return mu - 1.645 * sigma * np.sqrt(x)

    result = test_extrapolation("var_95", var_func, (1, 30))
    if result:
        results.append(result)

    # Test 3: Quadratic (control test)
    print("\n[3/3] Quadratic (Control)")

    def quad_func(x):
        """Solve simple quadratic function for baseline testing."""
        return x**2 + 2 * x + 1

    result = test_extrapolation("quadratic", quad_func, (-5, 5))
    if result:
        results.append(result)

    # Save results
    os.makedirs("results", exist_ok=True)
    output_path = "results/extrapolation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("EXTRAPOLATION SUMMARY")
    print("=" * 80)
    print(f"\n{'Formula':<20} {'R² Train':<12} {'Out/In Ratio':<15} {'Out Error':<12}")
    print("-" * 80)

    for r in results:
        print(
            f"{r['formula']:<20} {r['r2_train']:<12.4f} "
            f"{r['extrapolation_ratio']:<15.2f} {r['out_domain_error']:<12.4f}"
        )

    print("\n" + "=" * 80)
    print("Results saved to {}".format(output_path))
    print("=" * 80 + "\n")

    # Calculate average metrics
    if results:
        avg_r2 = np.mean([r["r2_train"] for r in results])
        avg_ratio = np.mean([r["extrapolation_ratio"] for r in results])

        print("\nAVERAGE METRICS:")
        print(f"  Mean R² (training): {avg_r2:.4f}")
        print(f"  Mean extrapolation ratio: {avg_ratio:.2f}x")
        print(f"  Interpretation: Discovered formulas have {avg_ratio:.1f}x higher error")
        print("                  when extrapolating vs interpolating\n")

    return results


if __name__ == "__main__":
    run_all_extrapolation_tests()
