"""
Risk Management Formula Discovery Dataset Generator
Class-based structure with comprehensive risk metrics
"""

import os
from datetime import datetime
from typing import Tuple

import numpy as np
from scipy import stats

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class RiskFormulaGenerator:
    """Generate risk management formulas with validation."""

    def __init__(self, domain: str = "risk", seed: int = 42, noise_level: float = 0.01):
        """
        Initialize the risk formula generator.

        Args:
            domain: Domain for validation
            seed: Random seed for reproducibility
            noise_level: Relative noise level for realistic data
        """
        self.system = HybridDiscoverySystem(domain=domain, max_results=100)
        self.seed = seed
        self.noise_level = noise_level
        np.random.seed(seed)
        self.results = []

    def generate_formula(self, formula_num: int, n_samples: int = 200):
        """
        Generate data for each risk formula (1-8).

        Args:
            formula_num: Formula number (1-8)
            n_samples: Number of samples to generate
        """

        if formula_num == 1:  # VaR 95%
            print("\n1. Value at Risk (95% confidence)")
            mu = np.random.uniform(-0.1, 0.15, n_samples)
            sigma = np.random.uniform(0.05, 0.5, n_samples)
            t = np.random.uniform(1, 252, n_samples)

            X = np.column_stack([mu, sigma, t])

            # Correct 95% confidence: z = 1.96
            var_95 = mu - 1.96 * sigma * np.sqrt(t)
            var_95 += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=var_95,
                variable_names=["mu", "sigma", "t"],
                variable_descriptions={
                    "mu": "Expected return",
                    "sigma": "Volatility (annualized)",
                    "t": "Time horizon in days",
                },
                variable_units={"mu": "dimensionless", "sigma": "dimensionless", "t": "dimensionless"},
                description="Value at Risk at 95% confidence level",
                validate_first=False,
            )

        elif formula_num == 2:  # Sharpe Ratio
            print("\n2. Sharpe Ratio")
            returns = np.random.uniform(-0.1, 0.3, n_samples)
            risk_free = np.random.uniform(0.01, 0.05, n_samples)
            vol = np.random.uniform(0.05, 0.3, n_samples)

            X = np.column_stack([returns, risk_free, vol])

            sharpe = (returns - risk_free) / vol
            sharpe += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=sharpe,
                variable_names=["returns", "risk_free", "volatility"],
                variable_descriptions={
                    "returns": "Portfolio returns (annualized)",
                    "risk_free": "Risk-free rate (annualized)",
                    "volatility": "Return volatility (annualized)",
                },
                variable_units={
                    "returns": "dimensionless",
                    "risk_free": "dimensionless",
                    "volatility": "dimensionless",
                },
                description="Sharpe ratio - risk-adjusted return measure",
                validate_first=False,
            )

        elif formula_num == 3:  # CVaR
            print("\n3. Conditional VaR (Expected Shortfall)")
            mu = np.random.uniform(-0.1, 0.15, n_samples)
            sigma = np.random.uniform(0.05, 0.5, n_samples)
            t = np.random.uniform(1, 252, n_samples)

            X = np.column_stack([mu, sigma, t])

            # CVaR formula for normal distribution at 95%
            phi_inv = stats.norm.pdf(1.96) / (1 - 0.95)  # ≈ 2.063
            cvar_95 = mu - phi_inv * sigma * np.sqrt(t)
            cvar_95 += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=cvar_95,
                variable_names=["mu", "sigma", "t"],
                variable_descriptions={
                    "mu": "Expected return",
                    "sigma": "Volatility (annualized)",
                    "t": "Time horizon in days",
                },
                variable_units={"mu": "dimensionless", "sigma": "dimensionless", "t": "dimensionless"},
                description="Conditional VaR (Expected Shortfall) at 95% confidence",
                validate_first=False,
            )

        elif formula_num == 4:  # Beta
            print("\n4. Beta (Systematic Risk)")
            cov_im = np.random.uniform(-0.1, 0.3, n_samples)
            var_m = np.random.uniform(0.01, 0.2, n_samples)

            X = np.column_stack([cov_im, var_m])

            beta = cov_im / var_m
            beta += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=beta,
                variable_names=["cov_im", "var_m"],
                variable_descriptions={"cov_im": "Covariance between asset and market", "var_m": "Market variance"},
                variable_units={"cov_im": "dimensionless", "var_m": "dimensionless"},
                description="Beta - measure of systematic risk relative to market",
                validate_first=False,
            )

        elif formula_num == 5:  # Sortino Ratio
            print("\n5. Sortino Ratio")
            returns = np.random.uniform(-0.1, 0.3, n_samples)
            target = np.random.uniform(0, 0.05, n_samples)
            downside_dev = np.random.uniform(0.05, 0.25, n_samples)

            X = np.column_stack([returns, target, downside_dev])

            sortino = (returns - target) / downside_dev
            sortino += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=sortino,
                variable_names=["returns", "target", "downside_dev"],
                variable_descriptions={
                    "returns": "Portfolio returns (annualized)",
                    "target": "Target or required return",
                    "downside_dev": "Downside deviation",
                },
                variable_units={"returns": "dimensionless", "target": "dimensionless", "downside_dev": "dimensionless"},
                description="Sortino ratio - downside risk-adjusted return",
                validate_first=False,
            )

        elif formula_num == 6:  # Information Ratio
            print("\n6. Information Ratio")
            active_return = np.random.uniform(-0.05, 0.15, n_samples)
            tracking_error = np.random.uniform(0.02, 0.15, n_samples)

            X = np.column_stack([active_return, tracking_error])

            info_ratio = active_return / tracking_error
            info_ratio += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=info_ratio,
                variable_names=["active_return", "tracking_error"],
                variable_descriptions={
                    "active_return": "Portfolio return minus benchmark return",
                    "tracking_error": "Standard deviation of active returns",
                },
                variable_units={"active_return": "dimensionless", "tracking_error": "dimensionless"},
                description="Information ratio - active management skill measure",
                validate_first=False,
            )

        elif formula_num == 7:  # Maximum Drawdown
            print("\n7. Maximum Drawdown")
            peak = np.random.uniform(100, 1000, n_samples)
            trough = peak * np.random.uniform(0.5, 0.95, n_samples)

            X = np.column_stack([peak, trough])

            max_dd = (trough - peak) / peak
            max_dd += np.random.normal(0, self.noise_level / 10, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=max_dd,
                variable_names=["peak", "trough"],
                variable_descriptions={"peak": "Peak portfolio value", "trough": "Trough portfolio value"},
                variable_units={"peak": "dimensionless", "trough": "dimensionless"},
                description="Maximum Drawdown - largest peak-to-trough decline",
                validate_first=False,
            )

        elif formula_num == 8:  # Treynor Ratio
            print("\n8. Treynor Ratio")
            returns = np.random.uniform(-0.1, 0.3, n_samples)
            risk_free = np.random.uniform(0.01, 0.05, n_samples)
            beta = np.random.uniform(0.5, 2.0, n_samples)

            X = np.column_stack([returns, risk_free, beta])

            treynor = (returns - risk_free) / beta
            treynor += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=treynor,
                variable_names=["returns", "risk_free", "beta"],
                variable_descriptions={
                    "returns": "Portfolio returns (annualized)",
                    "risk_free": "Risk-free rate (annualized)",
                    "beta": "Systematic risk (beta)",
                },
                variable_units={"returns": "dimensionless", "risk_free": "dimensionless", "beta": "dimensionless"},
                description="Treynor ratio - return per unit of systematic risk",
                validate_first=False,
            )

    def run_all_formulas(self, n_samples: int = 200):
        """Generate all 8 risk management formulas."""
        print("\n" + "#" * 70)
        print("# Risk Management Formula Discovery (8 Formulas)")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print(f"# Noise level: {self.noise_level}")
        print("#" * 70)

        for i in range(1, 9):
            try:
                print(f"\n{'='*70}")
                print(f"Processing Formula {i}/8")
                print(f"{'='*70}")
                self.generate_formula(i, n_samples)
                print(f"✅ Formula {i} completed")
            except Exception as e:
                print(f"❌ Error in Formula {i}: {str(e)}")
                import traceback

                traceback.print_exc()

    def save_results(self, output_dir: str = "hypatiax/data/finance/risk"):
        """
        Save results to files.

        Args:
            output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_path = os.path.join(output_dir, f"risk_comprehensive_{timestamp}.json")
        csv_path = os.path.join(output_dir, f"risk_comprehensive_{timestamp}.csv")

        self.system.export_results(json_path, format="json")

        try:
            self.system.export_results(csv_path, format="csv")
        except Exception as e:
            print(f"   Warning: Using fallback CSV export... ({e})")
            self._export_csv_safe(csv_path)

        return json_path, csv_path

    def _export_csv_safe(self, filepath: str):
        """Safely export to CSV with None handling."""
        import csv

        results_list = list(self.system.results)

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
                        self.system.domain,
                    ]
                )

        print(f"   CSV exported safely: {filepath}")

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("FINAL SUMMARY - RISK MANAGEMENT FORMULAS (8 Total)")
        print("=" * 70)

        stats = self.system.get_statistics()
        print(f"\nOverall Statistics:")
        print(f"  Total formulas: {stats['total_runs']}")
        print(f"  Valid formulas: {stats['valid_count']}")
        print(f"  Invalid formulas: {stats['invalid_count']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average R2 score: {stats['average_r2']:.4f}")
        print(f"  Average validation score: {stats['average_validation_score']:.1f}/100")

        # Individual results
        print("\n" + "-" * 70)
        print("Individual Formula Results:")
        print("-" * 70)

        for i, result in enumerate(self.system.get_results(), 1):
            discovery = result.get("discovery", {})
            validation = result.get("validation", {})

            valid_symbol = "✅" if validation.get("valid") else "❌"

            print(f"\n{i}. {result.get('description', 'Unknown')}")
            print(
                f"   {valid_symbol} R2: {discovery.get('r2_score', 0):.4f} | "
                f"Valid: {validation.get('valid', False)} | "
                f"Score: {validation.get('total_score', 0):.1f}/100"
            )
            print(f"   Expression: {discovery.get('expression', 'N/A')[:80]}")

        print("\n" + "=" * 70)


def main():
    """Main execution function."""
    generator = RiskFormulaGenerator(domain="risk", seed=42, noise_level=0.01)

    # Run all formulas
    generator.run_all_formulas(n_samples=200)

    # Save results
    json_path, csv_path = generator.save_results()
    print(f"\n📁 Results saved:")
    print(f"   JSON: {json_path}")
    print(f"   CSV: {csv_path}")

    # Print summary
    generator.print_summary()


if __name__ == "__main__":
    main()
