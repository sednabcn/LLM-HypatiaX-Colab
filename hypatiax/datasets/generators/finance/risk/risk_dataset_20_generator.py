"""
Risk Management Formula Discovery Dataset Generator - 20 Formulas
Class-based structure with comprehensive risk metrics
"""

import os
from datetime import datetime

import numpy as np
from scipy import stats

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class RiskFormula20Generator:
    """Generate 20 risk management formulas with validation."""

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
        Generate data for each risk formula (1-20).

        Args:
            formula_num: Formula number (1-20)
            n_samples: Number of samples to generate
        """

        if formula_num == 1:  # VaR 95%
            print("\n1. Value at Risk (95% confidence)")
            mu = np.random.uniform(-0.1, 0.15, n_samples)
            sigma = np.random.uniform(0.05, 0.5, n_samples)
            t = np.random.uniform(1, 252, n_samples)
            X = np.column_stack([mu, sigma, t])
            var_95 = mu - 1.96 * sigma * np.sqrt(t)
            var_95 += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=var_95,
                variable_names=["mu", "sigma", "t"],
                variable_descriptions={
                    "mu": "Expected return",
                    "sigma": "Volatility",
                    "t": "Time horizon",
                },
                variable_units={
                    "mu": "dimensionless",
                    "sigma": "dimensionless",
                    "t": "dimensionless",
                },
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
                    "returns": "Portfolio returns",
                    "risk_free": "Risk-free rate",
                    "volatility": "Return volatility",
                },
                variable_units={
                    "returns": "dimensionless",
                    "risk_free": "dimensionless",
                    "volatility": "dimensionless",
                },
                description="Sharpe ratio - risk-adjusted return measure",
                validate_first=False,
            )

        elif formula_num == 3:  # CVaR 95%
            print("\n3. Conditional VaR (Expected Shortfall 95%)")
            mu = np.random.uniform(-0.1, 0.15, n_samples)
            sigma = np.random.uniform(0.05, 0.5, n_samples)
            t = np.random.uniform(1, 252, n_samples)
            X = np.column_stack([mu, sigma, t])
            phi_inv = stats.norm.pdf(1.96) / (1 - 0.95)
            cvar_95 = mu - phi_inv * sigma * np.sqrt(t)
            cvar_95 += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=cvar_95,
                variable_names=["mu", "sigma", "t"],
                variable_descriptions={
                    "mu": "Expected return",
                    "sigma": "Volatility",
                    "t": "Time horizon",
                },
                variable_units={
                    "mu": "dimensionless",
                    "sigma": "dimensionless",
                    "t": "dimensionless",
                },
                description="Conditional VaR (Expected Shortfall) at 95%",
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
                variable_descriptions={
                    "cov_im": "Covariance between asset and market",
                    "var_m": "Market variance",
                },
                variable_units={"cov_im": "dimensionless", "var_m": "dimensionless"},
                description="Beta - measure of systematic risk",
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
                    "returns": "Portfolio returns",
                    "target": "Target return",
                    "downside_dev": "Downside deviation",
                },
                variable_units={
                    "returns": "dimensionless",
                    "target": "dimensionless",
                    "downside_dev": "dimensionless",
                },
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
                    "active_return": "Portfolio return minus benchmark",
                    "tracking_error": "Std dev of active returns",
                },
                variable_units={
                    "active_return": "dimensionless",
                    "tracking_error": "dimensionless",
                },
                description="Information ratio - active management skill",
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
                variable_descriptions={
                    "peak": "Peak portfolio value",
                    "trough": "Trough portfolio value",
                },
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
                    "returns": "Portfolio returns",
                    "risk_free": "Risk-free rate",
                    "beta": "Systematic risk (beta)",
                },
                variable_units={
                    "returns": "dimensionless",
                    "risk_free": "dimensionless",
                    "beta": "dimensionless",
                },
                description="Treynor ratio - return per unit of systematic risk",
                validate_first=False,
            )

        elif formula_num == 9:  # Calmar Ratio
            print("\n9. Calmar Ratio")
            annual_return = np.random.uniform(-0.1, 0.3, n_samples)
            max_drawdown = np.random.uniform(0.05, 0.5, n_samples)
            X = np.column_stack([annual_return, max_drawdown])
            calmar = annual_return / max_drawdown
            calmar += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=calmar,
                variable_names=["annual_return", "max_drawdown"],
                variable_descriptions={
                    "annual_return": "Annualized return",
                    "max_drawdown": "Maximum drawdown",
                },
                variable_units={
                    "annual_return": "dimensionless",
                    "max_drawdown": "dimensionless",
                },
                description="Calmar ratio - return relative to maximum drawdown",
                validate_first=False,
            )

        elif formula_num == 10:  # Omega Ratio
            print("\n10. Omega Ratio")
            gains = np.random.uniform(0, 0.3, n_samples)
            losses = np.random.uniform(0, 0.2, n_samples)
            X = np.column_stack([gains, losses])
            omega = (gains + 0.01) / (losses + 0.01)
            omega += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=omega,
                variable_names=["gains", "losses"],
                variable_descriptions={
                    "gains": "Expected gains above threshold",
                    "losses": "Expected losses below threshold",
                },
                variable_units={"gains": "dimensionless", "losses": "dimensionless"},
                description="Omega ratio - probability weighted gains vs losses",
                validate_first=False,
            )

        elif formula_num == 11:  # VaR 99%
            print("\n11. Value at Risk (99% confidence)")
            mu = np.random.uniform(-0.1, 0.15, n_samples)
            sigma = np.random.uniform(0.05, 0.5, n_samples)
            t = np.random.uniform(1, 252, n_samples)
            X = np.column_stack([mu, sigma, t])
            var_99 = mu - 2.576 * sigma * np.sqrt(t)
            var_99 += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=var_99,
                variable_names=["mu", "sigma", "t"],
                variable_descriptions={
                    "mu": "Expected return",
                    "sigma": "Volatility",
                    "t": "Time horizon",
                },
                variable_units={
                    "mu": "dimensionless",
                    "sigma": "dimensionless",
                    "t": "dimensionless",
                },
                description="Value at Risk at 99% confidence level",
                validate_first=False,
            )

        elif formula_num == 12:  # Modified Sharpe Ratio
            print("\n12. Modified Sharpe Ratio")
            returns = np.random.uniform(-0.1, 0.3, n_samples)
            risk_free = np.random.uniform(0.01, 0.05, n_samples)
            vol = np.random.uniform(0.05, 0.3, n_samples)
            skew = np.random.uniform(-0.5, 0.5, n_samples)
            X = np.column_stack([returns, risk_free, vol, skew])
            mod_sharpe = (returns - risk_free) / (vol * (1 + skew / 6))
            mod_sharpe += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=mod_sharpe,
                variable_names=["returns", "risk_free", "volatility", "skewness"],
                variable_descriptions={
                    "returns": "Portfolio returns",
                    "risk_free": "Risk-free rate",
                    "volatility": "Volatility",
                    "skewness": "Return skewness",
                },
                variable_units={
                    "returns": "dimensionless",
                    "risk_free": "dimensionless",
                    "volatility": "dimensionless",
                    "skewness": "dimensionless",
                },
                description="Modified Sharpe ratio adjusting for skewness",
                validate_first=False,
            )

        elif formula_num == 13:  # Ulcer Index
            print("\n13. Ulcer Index")
            dd_squared_sum = np.random.uniform(0.01, 0.5, n_samples)
            periods = np.random.uniform(10, 252, n_samples)
            X = np.column_stack([dd_squared_sum, periods])
            ulcer = np.sqrt(dd_squared_sum / periods)
            ulcer += np.random.normal(0, self.noise_level / 10, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=ulcer,
                variable_names=["dd_squared_sum", "periods"],
                variable_descriptions={
                    "dd_squared_sum": "Sum of squared drawdowns",
                    "periods": "Number of periods",
                },
                variable_units={
                    "dd_squared_sum": "dimensionless",
                    "periods": "dimensionless",
                },
                description="Ulcer Index - downside volatility measure",
                validate_first=False,
            )

        elif formula_num == 14:  # Martin Ratio
            print("\n14. Martin Ratio")
            returns = np.random.uniform(-0.1, 0.3, n_samples)
            ulcer_idx = np.random.uniform(0.05, 0.3, n_samples)
            X = np.column_stack([returns, ulcer_idx])
            martin = returns / ulcer_idx
            martin += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=martin,
                variable_names=["returns", "ulcer_index"],
                variable_descriptions={
                    "returns": "Portfolio returns",
                    "ulcer_index": "Ulcer Index",
                },
                variable_units={
                    "returns": "dimensionless",
                    "ulcer_index": "dimensionless",
                },
                description="Martin ratio - return per unit of Ulcer Index",
                validate_first=False,
            )

        elif formula_num == 15:  # Kappa Ratio (3rd order)
            print("\n15. Kappa 3 Ratio")
            returns = np.random.uniform(-0.1, 0.3, n_samples)
            lpm3 = np.random.uniform(0.001, 0.1, n_samples)
            X = np.column_stack([returns, lpm3])
            kappa3 = returns / np.power(lpm3, 1 / 3)
            kappa3 += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=kappa3,
                variable_names=["returns", "lpm3"],
                variable_descriptions={
                    "returns": "Portfolio returns",
                    "lpm3": "Lower partial moment (3rd order)",
                },
                variable_units={"returns": "dimensionless", "lpm3": "dimensionless"},
                description="Kappa 3 ratio - return per unit of downside risk",
                validate_first=False,
            )

        elif formula_num == 16:  # Gain-Loss Ratio
            print("\n16. Gain-Loss Ratio")
            avg_gain = np.random.uniform(0.01, 0.1, n_samples)
            avg_loss = np.random.uniform(0.01, 0.1, n_samples)
            X = np.column_stack([avg_gain, avg_loss])
            gainloss = avg_gain / avg_loss
            gainloss += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=gainloss,
                variable_names=["avg_gain", "avg_loss"],
                variable_descriptions={
                    "avg_gain": "Average gain per winning trade",
                    "avg_loss": "Average loss per losing trade",
                },
                variable_units={
                    "avg_gain": "dimensionless",
                    "avg_loss": "dimensionless",
                },
                description="Gain-Loss ratio - average win to average loss",
                validate_first=False,
            )

        elif formula_num == 17:  # Upside Potential Ratio
            print("\n17. Upside Potential Ratio")
            upside_potential = np.random.uniform(0.05, 0.3, n_samples)
            downside_risk = np.random.uniform(0.03, 0.2, n_samples)
            X = np.column_stack([upside_potential, downside_risk])
            upr = upside_potential / downside_risk
            upr += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=upr,
                variable_names=["upside_potential", "downside_risk"],
                variable_descriptions={
                    "upside_potential": "Expected upside above MAR",
                    "downside_risk": "Downside deviation below MAR",
                },
                variable_units={
                    "upside_potential": "dimensionless",
                    "downside_risk": "dimensionless",
                },
                description="Upside Potential Ratio",
                validate_first=False,
            )

        elif formula_num == 18:  # Sterling Ratio
            print("\n18. Sterling Ratio")
            annual_return = np.random.uniform(-0.1, 0.3, n_samples)
            avg_dd = np.random.uniform(0.05, 0.4, n_samples)
            X = np.column_stack([annual_return, avg_dd])
            sterling = (annual_return - 0.1) / avg_dd
            sterling += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=sterling,
                variable_names=["annual_return", "avg_drawdown"],
                variable_descriptions={
                    "annual_return": "Annualized return",
                    "avg_drawdown": "Average drawdown",
                },
                variable_units={
                    "annual_return": "dimensionless",
                    "avg_drawdown": "dimensionless",
                },
                description="Sterling ratio - excess return per unit of average drawdown",
                validate_first=False,
            )

        elif formula_num == 19:  # Burke Ratio
            print("\n19. Burke Ratio")
            excess_ret = np.random.uniform(-0.05, 0.25, n_samples)
            sqrt_sum_dd = np.random.uniform(0.1, 0.6, n_samples)
            X = np.column_stack([excess_ret, sqrt_sum_dd])
            burke = excess_ret / sqrt_sum_dd
            burke += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=burke,
                variable_names=["excess_return", "sqrt_sum_dd"],
                variable_descriptions={
                    "excess_return": "Return above risk-free rate",
                    "sqrt_sum_dd": "Square root of sum of squared drawdowns",
                },
                variable_units={
                    "excess_return": "dimensionless",
                    "sqrt_sum_dd": "dimensionless",
                },
                description="Burke ratio - return per unit of drawdown magnitude",
                validate_first=False,
            )

        elif formula_num == 20:  # Pain Ratio
            print("\n20. Pain Ratio")
            returns = np.random.uniform(-0.1, 0.3, n_samples)
            pain_index = np.random.uniform(0.02, 0.3, n_samples)
            X = np.column_stack([returns, pain_index])
            pain_ratio = returns / pain_index
            pain_ratio += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=pain_ratio,
                variable_names=["returns", "pain_index"],
                variable_descriptions={
                    "returns": "Portfolio returns",
                    "pain_index": "Average drawdown over period",
                },
                variable_units={
                    "returns": "dimensionless",
                    "pain_index": "dimensionless",
                },
                description="Pain ratio - return per unit of pain index",
                validate_first=False,
            )

    def run_all_formulas(self, n_samples: int = 200):
        """Generate all 20 risk management formulas."""
        print("\n" + "#" * 70)
        print("# Risk Management Formula Discovery (20 Formulas)")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print(f"# Noise level: {self.noise_level}")
        print("#" * 70)

        for i in range(1, 21):
            try:
                print(f"\n{'=' * 70}")
                print(f"Processing Formula {i}/20")
                print(f"{'=' * 70}")
                self.generate_formula(i, n_samples)
                print(f"✅ Formula {i} completed")
            except Exception as e:
                print(f"❌ Error in Formula {i}: {str(e)}")
                import traceback

                traceback.print_exc()

    def save_results(self, output_dir: str = "hypatiax/data/finance/risk"):
        """Save results to files."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_path = os.path.join(output_dir, f"risk_comprehensive_20_{timestamp}.json")
        csv_path = os.path.join(output_dir, f"risk_comprehensive_20_{timestamp}.csv")

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
                        (
                            interpretation.get("interpretation", "")[:100]
                            if interpretation
                            else ""
                        ),
                        metadata.get("llm_provider", ""),
                        self.system.domain,
                    ]
                )

        print(f"   CSV exported safely: {filepath}")

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("FINAL SUMMARY - RISK MANAGEMENT FORMULAS (20 Total)")
        print("=" * 70)

        stats = self.system.get_statistics()
        print(f"\nOverall Statistics:")
        print(f"  Total formulas: {stats['total_runs']}")
        print(f"  Valid formulas: {stats['valid_count']}")
        print(f"  Invalid formulas: {stats['invalid_count']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average R2 score: {stats['average_r2']:.4f}")
        print(
            f"  Average validation score: {stats['average_validation_score']:.1f}/100"
        )

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
    generator = RiskFormula20Generator(domain="risk", seed=42, noise_level=0.01)

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
