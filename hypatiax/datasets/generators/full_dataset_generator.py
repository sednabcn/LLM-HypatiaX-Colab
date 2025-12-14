"""
Full Dataset Generator - Synthetic Formulas
Generates additional formulas to reach dataset targets:
  - DeFi Domain: 40 formulas
  - Risk Domain: 50 formulas
Total: 90 additional formulas
"""

import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class SyntheticFormulaGenerator:
    """Generate synthetic formulas for DeFi and Risk domains."""

    def __init__(self, seed: int = 42):
        """
        Initialize the synthetic formula generator.

        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        np.random.seed(seed)
        self.defi_system = None
        self.risk_system = None

    def generate_defi_formulas(self, n_formulas: int = 40):
        """
        Generate synthetic DeFi formulas.

        Args:
            n_formulas: Number of formulas to generate
        """
        print("\n" + "#" * 70)
        print(f"# DEFI DOMAIN: Generating {n_formulas} Synthetic Formulas")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print("#" * 70)

        self.defi_system = HybridDiscoverySystem(domain="defi", max_results=100)

        for i in range(n_formulas):
            print(f"\n{'='*70}")
            print(f"Processing DeFi Formula {i+1}/{n_formulas}")
            print(f"{'='*70}")

            try:
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
                    var_units = {"x": "dimensionless"}

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
                    var_units = {"x1": "dimensionless", "x2": "dimensionless"}

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
                    var_units = {"x1": "dimensionless", "x2": "dimensionless", "x3": "dimensionless"}

                # Add realistic noise
                noise_level = np.random.uniform(0.01, 0.1)
                y += np.random.normal(0, noise_level * np.std(y), n_samples)

                self.defi_system.discover_validate_interpret(
                    X=X,
                    y=y,
                    variable_names=var_names,
                    variable_descriptions=var_desc,
                    variable_units=var_units,
                    description=f"DeFi synthetic formula {i+1}",
                    validate_first=False,
                )
                print(f"✅ Formula {i+1} completed")

            except Exception as e:
                print(f"❌ Error in Formula {i+1}: {str(e)}")
                import traceback

                traceback.print_exc()

    def generate_risk_formulas(self, n_formulas: int = 50):
        """
        Generate synthetic Risk formulas.

        Args:
            n_formulas: Number of formulas to generate
        """
        print("\n" + "#" * 70)
        print(f"# RISK DOMAIN: Generating {n_formulas} Synthetic Formulas")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print("#" * 70)

        self.risk_system = HybridDiscoverySystem(domain="risk", max_results=100)

        for i in range(n_formulas):
            print(f"\n{'='*70}")
            print(f"Processing Risk Formula {i+1}/{n_formulas}")
            print(f"{'='*70}")

            try:
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
                    var_units = {"mu": "dimensionless", "sigma": "dimensionless"}

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

                self.risk_system.discover_validate_interpret(
                    X=X,
                    y=y,
                    variable_names=var_names,
                    variable_descriptions=var_desc,
                    variable_units=var_units,
                    description=f"Risk synthetic formula {i+1}",
                    validate_first=False,
                )
                print(f"✅ Formula {i+1} completed")

            except Exception as e:
                print(f"❌ Error in Formula {i+1}: {str(e)}")
                import traceback

                traceback.print_exc()

    def save_results(self, output_dir: str = "hypatiax/data/synthetic"):
        """Save results to files."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        saved_files = {}

        # Save DeFi results
        if self.defi_system:
            defi_json = os.path.join(output_dir, f"defi_synthetic_{timestamp}.json")
            defi_csv = os.path.join(output_dir, f"defi_synthetic_{timestamp}.csv")

            self.defi_system.export_results(defi_json, format="json")

            try:
                self.defi_system.export_results(defi_csv, format="csv")
            except Exception as e:
                print(f"   Warning: Using fallback CSV export for DeFi... ({e})")
                self._export_csv_safe(self.defi_system, defi_csv)

            saved_files["defi"] = {"json": defi_json, "csv": defi_csv}

        # Save Risk results
        if self.risk_system:
            risk_json = os.path.join(output_dir, f"risk_synthetic_{timestamp}.json")
            risk_csv = os.path.join(output_dir, f"risk_synthetic_{timestamp}.csv")

            self.risk_system.export_results(risk_json, format="json")

            try:
                self.risk_system.export_results(risk_csv, format="csv")
            except Exception as e:
                print(f"   Warning: Using fallback CSV export for Risk... ({e})")
                self._export_csv_safe(self.risk_system, risk_csv)

            saved_files["risk"] = {"json": risk_json, "csv": risk_csv}

        return saved_files

    def _export_csv_safe(self, system, filepath: str):
        """Safely export to CSV with None handling."""
        import csv

        results_list = list(system.results)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Timestamp",
                    "Expression",
                    "R2_Score",
                    "Complexity",
                    "Validation_Score",
                    "Valid",
                    "Interpretation",
                    "Provider",
                    "Domain",
                ]
            )

            for result in results_list:
                discovery = result.get("discovery", {})
                validation = result.get("validation", {})
                interpretation = result.get("interpretation") or {}
                metadata = result.get("metadata", {})

                writer.writerow(
                    [
                        result.get("timestamp", ""),
                        discovery.get("expression", ""),
                        discovery.get("r2_score", 0),
                        discovery.get("complexity", 0),
                        validation.get("total_score", 0),
                        validation.get("valid", False),
                        interpretation.get("interpretation", "")[:100] if interpretation else "",
                        metadata.get("llm_provider", ""),
                        system.domain,
                    ]
                )

        print(f"   CSV exported safely: {filepath}")

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("FINAL SUMMARY - SYNTHETIC FORMULA GENERATION")
        print("=" * 70)

        # DeFi Summary
        if self.defi_system:
            defi_stats = self.defi_system.get_statistics()
            print(f"\nDeFi Domain Statistics:")
            print(f"  Total formulas: {defi_stats['total_runs']}")
            print(f"  Valid formulas: {defi_stats['valid_count']}")
            print(f"  Invalid formulas: {defi_stats['invalid_count']}")
            print(f"  Success rate: {defi_stats['success_rate']:.1%}")
            print(f"  Average R2 score: {defi_stats['average_r2']:.4f}")
            print(f"  Average validation score: {defi_stats['average_validation_score']:.1f}/100")

        # Risk Summary
        if self.risk_system:
            risk_stats = self.risk_system.get_statistics()
            print(f"\nRisk Domain Statistics:")
            print(f"  Total formulas: {risk_stats['total_runs']}")
            print(f"  Valid formulas: {risk_stats['valid_count']}")
            print(f"  Invalid formulas: {risk_stats['invalid_count']}")
            print(f"  Success rate: {risk_stats['success_rate']:.1%}")
            print(f"  Average R2 score: {risk_stats['average_r2']:.4f}")
            print(f"  Average validation score: {risk_stats['average_validation_score']:.1f}/100")

        # Combined Summary
        if self.defi_system and self.risk_system:
            total_formulas = defi_stats["total_runs"] + risk_stats["total_runs"]
            total_valid = defi_stats["valid_count"] + risk_stats["valid_count"]
            combined_rate = (total_valid / total_formulas * 100) if total_formulas > 0 else 0

            print(f"\nCombined Statistics:")
            print(f"  Total formulas: {total_formulas}")
            print(f"  Total valid: {total_valid}")
            print(f"  Overall success rate: {combined_rate:.1%}")

        print("\n" + "=" * 70)

    def run_all(self, n_defi: int = 40, n_risk: int = 50):
        """Generate all synthetic formulas."""
        print("\n" + "=" * 70)
        print("GENERATING FULL SYNTHETIC DATASET")
        print("=" * 70 + "\n")

        # Generate DeFi formulas
        self.generate_defi_formulas(n_defi)

        # Generate Risk formulas
        self.generate_risk_formulas(n_risk)


def main():
    """Main execution function."""
    generator = SyntheticFormulaGenerator(seed=42)

    # Generate all formulas
    generator.run_all(n_defi=40, n_risk=50)

    # Save results
    saved_files = generator.save_results()

    print(f"\n📁 Results saved:")
    if "defi" in saved_files:
        print(f"   DeFi JSON: {saved_files['defi']['json']}")
        print(f"   DeFi CSV: {saved_files['defi']['csv']}")
    if "risk" in saved_files:
        print(f"   Risk JSON: {saved_files['risk']['json']}")
        print(f"   Risk CSV: {saved_files['risk']['csv']}")

    # Print summary
    generator.print_summary()


if __name__ == "__main__":
    try:
        main()
        print("\n✅ Dataset generation completed successfully!\n")
    except Exception as e:
        print(f"\n❌ Error during dataset generation: {e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
