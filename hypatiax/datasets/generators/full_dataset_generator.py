import os
import sys
from pathlib import Path

import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.hybrid_system import HybridDiscoverySystem


def generate_remaining_formulas():
    """
    Generate remaining formulas to reach 150 total.
    Current: ~60, Need: 90 more
    Target breakdown:
    - DeFi: 40 more formulas
    - Risk: 50 more formulas
    """

    print("\n" + "=" * 80)
    print("GENERATING FULL DATASET (150 FORMULAS)")
    print("=" * 80 + "\n")

    # ========================================================================
    # DeFi Domain: 40 additional formulas
    # ========================================================================
    print("=" * 80)
    print("DEFI DOMAIN: Generating 40 formulas")
    print("=" * 80 + "\n")

    defi_system = HybridDiscoverySystem(domain="defi")

    np.random.seed(42)  # For reproducibility

    for i in range(40):
        print(f"\n[DeFi {i+1}/40] Generating formula...")

        # Vary complexity across formulas
        n_vars = np.random.randint(1, 4)
        n_samples = np.random.randint(80, 120)

        X = np.random.uniform(0.1, 100, (n_samples, n_vars))

        # Generate formulas based on common DeFi patterns
        if n_vars == 1:
            # Single variable patterns
            patterns = [
                lambda x: x**0.5,  # Square root (price impact)
                lambda x: 1 / x,  # Inverse (exchange rate)
                lambda x: np.log(x + 1),  # Logarithmic (diminishing returns)
                lambda x: x / (x + 1),  # Bounded ratio
                lambda x: 2 * x**0.5 / (x + 1),  # IL-like pattern
            ]
            pattern = np.random.choice(patterns)
            y = pattern(X[:, 0])

            var_names = ["x"]
            var_desc = {"x": "Input variable"}
            var_units = {"x": "tokens"}

        elif n_vars == 2:
            # Two variable patterns
            patterns = [
                lambda x1, x2: x1 / (x2 + 1),  # Ratio with offset
                lambda x1, x2: (x1 * x2) ** 0.5,  # Geometric mean
                lambda x1, x2: x1 / (x1 + x2),  # Share calculation
                lambda x1, x2: x1 * np.log(x2 + 1),  # Weighted log
                lambda x1, x2: (x1 - x2) / (x1 + x2),  # Relative difference
            ]
            pattern = np.random.choice(patterns)
            y = pattern(X[:, 0], X[:, 1])

            var_names = ["x1", "x2"]
            var_desc = {"x1": "Numerator term", "x2": "Denominator term"}
            var_units = {"x1": "tokens", "x2": "tokens"}

        else:  # n_vars == 3
            # Three variable patterns
            patterns = [
                lambda x1, x2, x3: (x1 * x2) / (x3 + 1),  # Product ratio
                lambda x1, x2, x3: x1 / (x2 + x3),  # Sum denominator
                lambda x1, x2, x3: (x1 + x2) / (x3 + 1),  # Sum ratio
                lambda x1, x2, x3: x1 * x2 * x3**0.5,  # Mixed product
            ]
            pattern = np.random.choice(patterns)
            y = pattern(X[:, 0], X[:, 1], X[:, 2])

            var_names = ["x1", "x2", "x3"]
            var_desc = {"x1": "Factor 1", "x2": "Factor 2", "x3": "Divisor"}
            var_units = {"x1": "tokens", "x2": "tokens", "x3": "tokens"}

        # Add realistic noise
        noise_level = np.random.uniform(0.01, 0.1)
        y += np.random.normal(0, noise_level * np.std(y), n_samples)

        try:
            defi_system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=var_names,
                variable_descriptions=var_desc,
                variable_units=var_units,
                description=f"DeFi synthetic formula {i+1}",
            )
            print(f"  ✓ Successfully generated formula {i+1}")
        except Exception as e:
            print(f"  ✗ Error generating formula {i+1}: {e}")

    # Save DeFi results
    os.makedirs("data", exist_ok=True)
    defi_output = "data/defi_synthetic_batch.json"
    defi_system.save_results(defi_output)
    print(f"\n✓ DeFi batch saved: {len(defi_system.results)} formulas → {defi_output}")

    # ========================================================================
    # Risk Domain: 50 additional formulas
    # ========================================================================
    print("\n" + "=" * 80)
    print("RISK DOMAIN: Generating 50 formulas")
    print("=" * 80 + "\n")

    risk_system = HybridDiscoverySystem(domain="risk")

    for i in range(50):
        print(f"\n[Risk {i+1}/50] Generating formula...")

        n_vars = np.random.randint(2, 5)
        n_samples = np.random.randint(80, 120)

        # Risk metrics often involve standardized variables
        X = np.random.uniform(-2, 2, (n_samples, n_vars))

        # Risk-specific patterns
        if n_vars == 2:
            # VaR-like patterns
            patterns = [
                lambda mu, sig: mu - 1.96 * sig,  # 95% VaR
                lambda mu, sig: mu - 1.645 * sig,  # 90% VaR
                lambda mu, sig: mu - 2.576 * sig,  # 99% VaR
                lambda mu, sig: sig / (mu + 0.1),  # Coefficient of variation
                lambda mu, sig: mu / (sig + 0.1),  # Sharpe-like ratio
            ]
            pattern = np.random.choice(patterns)
            y = pattern(X[:, 0], X[:, 1])

            var_names = ["mu", "sigma"]
            var_desc = {"mu": "Expected return", "sigma": "Volatility"}
            var_units = {"mu": "percent", "sigma": "percent"}

        elif n_vars == 3:
            # Portfolio metrics
            patterns = [
                lambda w1, w2, w3: w1**2 + w2**2 + w3**2,  # Variance (uncorrelated)
                lambda w1, w2, w3: (w1 + w2 + w3) / 3,  # Equal weight
                lambda w1, w2, w3: w1 * w2 / (w3 + 0.1),  # Risk-adjusted return
            ]
            pattern = np.random.choice(patterns)
            y = pattern(X[:, 0], X[:, 1], X[:, 2])

            var_names = ["w1", "w2", "w3"]
            var_desc = {f"w{j+1}": f"Asset {j+1} weight" for j in range(3)}
            var_units = {f"w{j+1}": "dimensionless" for j in range(3)}

        else:  # n_vars == 4
            # Complex portfolio patterns
            y = np.sum(X**2, axis=1)  # Sum of squares

            var_names = [f"w{j+1}" for j in range(n_vars)]
            var_desc = {f"w{j+1}": f"Asset {j+1} weight" for j in range(n_vars)}
            var_units = {f"w{j+1}": "dimensionless" for j in range(n_vars)}

        # Add realistic noise
        noise_level = np.random.uniform(0.01, 0.05)
        y += np.random.normal(0, noise_level * np.std(y), n_samples)

        try:
            risk_system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=var_names,
                variable_descriptions=var_desc,
                variable_units=var_units,
                description=f"Risk synthetic formula {i+1}",
            )
            print(f"  ✓ Successfully generated formula {i+1}")
        except Exception as e:
            print(f"  ✗ Error generating formula {i+1}: {e}")

    # Save Risk results
    risk_output = "data/risk_synthetic_batch.json"
    risk_system.save_results(risk_output)
    print(f"\n✓ Risk batch saved: {len(risk_system.results)} formulas → {risk_output}")

    # ========================================================================
    # Final Summary
    # ========================================================================
    print("\n" + "=" * 80)
    print("DATASET GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated:")
    print(f"  - DeFi formulas: {len(defi_system.results)}")
    print(f"  - Risk formulas: {len(risk_system.results)}")
    print(f"  - Total new: {len(defi_system.results) + len(risk_system.results)}")

    # Calculate success rates
    defi_valid = sum(1 for r in defi_system.results if r.get("validation", {}).get("valid", False))
    risk_valid = sum(1 for r in risk_system.results if r.get("validation", {}).get("valid", False))

    defi_rate = (defi_valid / len(defi_system.results) * 100) if defi_system.results else 0
    risk_rate = (risk_valid / len(risk_system.results) * 100) if risk_system.results else 0

    print(f"\nValidation rates:")
    print(f"  - DeFi: {defi_valid}/{len(defi_system.results)} ({defi_rate:.1f}%)")
    print(f"  - Risk: {risk_valid}/{len(risk_system.results)} ({risk_rate:.1f}%)")

    print("\n" + "=" * 80)
    print("Next step: Run dataset validation")
    print("  python scripts/validate_dataset.py")
    print("=" * 80 + "\n")

    return {
        "defi": {"total": len(defi_system.results), "valid": defi_valid, "rate": defi_rate},
        "risk": {"total": len(risk_system.results), "valid": risk_valid, "rate": risk_rate},
    }


if __name__ == "__main__":
    try:
        results = generate_remaining_formulas()
        print("\n✓ Dataset generation completed successfully!\n")
    except Exception as e:
        print(f"\n✗ Error during dataset generation: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
