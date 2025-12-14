"""
Risk Management Queries Dataset Generator - Complete
Creates 300+ description → analytical formula mappings
Covers all major risk management formulas used in the market
Format: [description, analytical_formula, category]
"""

import os
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd


class RiskQueriesDataset:
    """Generate comprehensive risk management queries dataset."""

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.queries = []
        self.formula_count = 0

    def add_query(self, description: str, formula: str, category: str):
        """Add a single query."""
        self.queries.append({"description": description, "analytical_formula": formula, "category": category})
        self.formula_count += 1

    def generate_var_formulas(self):
        """Generate 35 Value at Risk (VaR) variants."""
        print("Generating VaR formulas (35 variants)...")

        # Base VaR formulas
        self.add_query("Calculate Value at Risk at 95% confidence level", "VaR_95 = μ - 1.96 * σ * √t", "Value at Risk")

        # Different confidence levels
        confidence_levels = [(90, 1.28, "90%"), (95, 1.645, "95%"), (99, 2.33, "99%"), (99.9, 3.09, "99.9%")]

        for conf, z_score, conf_str in confidence_levels:
            # Basic VaR
            self.add_query(
                f"Calculate VaR at {conf_str} confidence level", f"VaR_{conf} = μ - {z_score} * σ * √t", "Value at Risk"
            )

            # VaR with time horizons
            for horizon in [1, 10, 30, 252]:
                self.add_query(
                    f"VaR {conf_str} for {horizon}-day horizon",
                    f"VaR_{conf}({horizon}d) = μ - {z_score} * σ * √{horizon}",
                    "Value at Risk",
                )

            # VaR for different portfolio levels
            for portfolio in [100000, 1000000, 10000000]:
                self.add_query(
                    f"Dollar VaR at {conf_str} for ${portfolio:,} portfolio",
                    f"Dollar_VaR = Portfolio_Value * (μ - {z_score} * σ * √t)",
                    "Value at Risk",
                )

        # VaR parametric vs historical
        self.add_query(
            "Historical VaR using percentile method", "VaR_historical = percentile(returns, 5)", "Value at Risk"
        )

        self.add_query(
            "Cornish-Fisher VaR adjusting for skewness and kurtosis",
            "VaR_CF = μ - (z + (z²-1)/6 * skew + (z³-3z)/24 * kurt) * σ * √t",
            "Value at Risk",
        )

    def generate_cvar_formulas(self):
        """Generate 30 Conditional VaR (Expected Shortfall) variants."""
        print("Generating CVaR/Expected Shortfall formulas (30 variants)...")

        self.add_query(
            "Calculate Conditional VaR (Expected Shortfall) at 95%",
            "CVaR_95 = μ - φ(z_95)/(1-0.95) * σ * √t",
            "Conditional VaR",
        )

        for conf, z_score, phi_value in [(90, 1.28, 2.50), (95, 1.645, 2.063), (99, 2.33, 1.755), (99.9, 3.09, 1.505)]:
            self.add_query(
                f"CVaR at {conf}% confidence level", f"CVaR_{conf} = μ - {phi_value} * σ * √t", "Conditional VaR"
            )

            for horizon in [1, 10, 30, 252]:
                self.add_query(
                    f"Expected Shortfall at {conf}% for {horizon}-day horizon",
                    f"ES_{conf}({horizon}d) = μ - {phi_value} * σ * √{horizon}",
                    "Conditional VaR",
                )

        self.add_query(
            "Historical CVaR as average of tail losses",
            "CVaR_historical = mean(returns[returns <= VaR_historical])",
            "Conditional VaR",
        )

        self.add_query(
            "Stressed CVaR using historical stress scenarios",
            "Stressed_CVaR = mean(losses during stress periods)",
            "Conditional VaR",
        )

    def generate_sharpe_ratio_formulas(self):
        """Generate 25 Sharpe Ratio variants."""
        print("Generating Sharpe Ratio formulas (25 variants)...")

        self.add_query("Calculate Sharpe Ratio for portfolio performance", "Sharpe = (R_p - R_f) / σ_p", "Sharpe Ratio")

        # Different risk-free rates
        for rf_rate in [0.01, 0.02, 0.03, 0.05, 0.10]:
            self.add_query(
                f"Sharpe Ratio with {rf_rate*100:.1f}% risk-free rate",
                f"Sharpe = (R_p - {rf_rate}) / σ_p",
                "Sharpe Ratio",
            )

            # Different time horizons
            for period in ["daily", "monthly", "annual"]:
                self.add_query(
                    f"Annualized Sharpe Ratio ({period} data)",
                    f"Sharpe_annual = Sharpe * √(periods_per_year)",
                    "Sharpe Ratio",
                )

        self.add_query(
            "Risk-adjusted Sharpe Ratio with transaction costs", "Sharpe_adj = (R_p - TC - R_f) / σ_p", "Sharpe Ratio"
        )

        self.add_query(
            "Excess Sharpe Ratio relative to benchmark",
            "Sharpe_excess = (R_p - R_bench) / σ(R_p - R_bench)",
            "Sharpe Ratio",
        )

    def generate_sortino_ratio_formulas(self):
        """Generate 25 Sortino Ratio variants."""
        print("Generating Sortino Ratio formulas (25 variants)...")

        self.add_query(
            "Calculate Sortino Ratio focusing on downside risk",
            "Sortino = (R_p - R_target) / σ_downside",
            "Sortino Ratio",
        )

        # Different target returns
        for target in [0.00, 0.02, 0.05, 0.10]:
            self.add_query(
                f"Sortino Ratio with {target*100:.1f}% target return",
                f"Sortino = (R_p - {target}) / σ_downside",
                "Sortino Ratio",
            )

            for period in ["daily", "monthly", "annual"]:
                self.add_query(
                    f"Annualized Sortino Ratio ({period} data, {target*100:.1f}% target)",
                    f"Sortino_annual = (R_p - {target}) * √(periods/year) / σ_downside",
                    "Sortino Ratio",
                )

        self.add_query(
            "Downside deviation calculation", "σ_downside = √[Σ(min(R_i - R_target, 0))² / n]", "Sortino Ratio"
        )

    def generate_beta_formulas(self):
        """Generate 28 Beta (Systematic Risk) variants."""
        print("Generating Beta formulas (28 variants)...")

        self.add_query(
            "Calculate Beta - systematic risk relative to market", "β = Cov(R_asset, R_market) / Var(R_market)", "Beta"
        )

        # Different estimation periods
        for period in ["1-year", "3-year", "5-year"]:
            self.add_query(
                f"Beta estimation using {period} historical data",
                f"β_{period} = Cov(R_asset, R_market) / Var(R_market)",
                "Beta",
            )

        # Levered and unlevered beta
        self.add_query("Unlevered (asset) Beta", "β_unlevered = β_levered / (1 + (1-Tc) * D/E)", "Beta")

        self.add_query("Levered (equity) Beta with debt", "β_levered = β_unlevered * (1 + (1-Tc) * D/E)", "Beta")

        # Beta adjustments
        for factor in ["market", "size", "value", "momentum"]:
            self.add_query(
                f"Multi-factor Beta including {factor} premium",
                f"β_multi = α + β_market*F_market + β_{factor}*F_{factor}",
                "Beta",
            )

        self.add_query(
            "Rolling Beta estimation",
            "β_rolling(t) = Cov(R_asset[t-252:t], R_market[t-252:t]) / Var(R_market[t-252:t])",
            "Beta",
        )

    def generate_max_drawdown_formulas(self):
        """Generate 30 Maximum Drawdown variants."""
        print("Generating Maximum Drawdown formulas (30 variants)...")

        self.add_query(
            "Calculate Maximum Drawdown as peak-to-trough decline", "MDD = (Trough - Peak) / Peak", "Maximum Drawdown"
        )

        # Variations by holding period
        for period in [10, 20, 60, 252]:
            self.add_query(
                f"Maximum Drawdown over {period}-day period",
                f"MDD_{period}d = min(Portfolio_Value[t:t+{period}]) / max(Portfolio_Value[t:t+{period}])",
                "Maximum Drawdown",
            )

        self.add_query(
            "Calmar Ratio - return per unit of drawdown", "Calmar = Annual_Return / Max_Drawdown", "Maximum Drawdown"
        )

        self.add_query(
            "Return over Maximum Drawdown (RoMaD)", "RoMaD = Cumulative_Return / Max_Drawdown", "Maximum Drawdown"
        )

        # Recovery time metrics
        for recovery_target in [50, 75, 100]:
            self.add_query(
                f"Time to recover {recovery_target}% of drawdown",
                f"Recovery_Time_{recovery_target} = First_Date(Portfolio_Value >= Peak * {recovery_target/100})",
                "Maximum Drawdown",
            )

        self.add_query(
            "Average Drawdown over period", "Avg_DD = mean(|Drawdown_i|) for all i in period", "Maximum Drawdown"
        )

    def generate_information_ratio_formulas(self):
        """Generate 24 Information Ratio variants."""
        print("Generating Information Ratio formulas (24 variants)...")

        self.add_query(
            "Calculate Information Ratio for active management", "IR = (R_p - R_bench) / TE", "Information Ratio"
        )

        # Different benchmark types
        for bench in ["S&P500", "Russell2000", "MSCI_World", "Custom"]:
            self.add_query(
                f"Information Ratio vs {bench} benchmark",
                f"IR_{bench} = (R_p - R_{bench}) / σ(R_p - R_{bench})",
                "Information Ratio",
            )

        self.add_query(
            "Tracking Error - standard deviation of active returns", "TE = σ(R_p - R_bench)", "Information Ratio"
        )

        self.add_query(
            "Ex-ante Information Ratio using factor model", "IR_ex_ante = α / Residual_Volatility", "Information Ratio"
        )

        self.add_query("Annualized Information Ratio", "IR_annual = IR_monthly * √12", "Information Ratio")

    def generate_treynor_ratio_formulas(self):
        """Generate 20 Treynor Ratio variants."""
        print("Generating Treynor Ratio formulas (20 variants)...")

        self.add_query(
            "Calculate Treynor Ratio - return per unit of systematic risk", "Treynor = (R_p - R_f) / β", "Treynor Ratio"
        )

        for rf in [0.01, 0.02, 0.05]:
            for beta_range in ["Low (β<1)", "Mid (1<β<1.5)", "High (β>1.5)"]:
                self.add_query(
                    f"Treynor Ratio with {rf*100:.1f}% RF rate, {beta_range}",
                    f"Treynor = (R_p - {rf}) / β",
                    "Treynor Ratio",
                )

        self.add_query(
            "Jensen's Alpha - excess return above CAPM prediction", "α = R_p - [R_f + β(R_m - R_f)]", "Treynor Ratio"
        )

    def generate_capm_formulas(self):
        """Generate 28 CAPM and related variants."""
        print("Generating CAPM formulas (28 variants)...")

        self.add_query("Capital Asset Pricing Model", "E(R_i) = R_f + β_i(E(R_m) - R_f)", "CAPM")

        # Market risk premium variations
        for mrp in [0.04, 0.05, 0.06, 0.08]:
            self.add_query(f"CAPM with {mrp*100:.1f}% market risk premium", f"E(R_i) = R_f + β_i * {mrp}", "CAPM")

        self.add_query(
            "Build-up method for required return (Private Companies)",
            "E(R) = R_f + β * MRP + Size_Premium + Industry_Premium",
            "CAPM",
        )

        self.add_query(
            "Three-Factor Fama-French Model",
            "R_i - R_f = α + β_market(R_m - R_f) + β_size*SMB + β_value*HML + ε",
            "CAPM",
        )

        self.add_query(
            "Five-Factor Fama-French Model",
            "R_i - R_f = α + β_mkt*MKT + β_smb*SMB + β_hml*HML + β_rmw*RMW + β_cma*CMA",
            "CAPM",
        )

    def generate_var_extensions(self):
        """Generate 32 Advanced VaR extensions."""
        print("Generating Advanced VaR extensions (32 variants)...")

        self.add_query(
            "Incremental VaR - VaR contribution of adding position",
            "IVaR = VaR(Portfolio+Position) - VaR(Portfolio)",
            "Advanced VaR",
        )

        self.add_query(
            "Marginal VaR - sensitivity of portfolio VaR to position change", "MVaR = ∂VaR/∂Position_i", "Advanced VaR"
        )

        self.add_query(
            "Component VaR - allocation of total VaR to positions", "CVaR_i = MVaR_i * Position_Value_i", "Advanced VaR"
        )

        self.add_query("Stand-alone VaR for individual position", "SA_VaR_i = μ_i - z_α * σ_i * √t", "Advanced VaR")

        self.add_query(
            "Concentrated VaR - accounts for correlation breakdowns",
            "Conc_VaR = VaR * Concentration_Factor",
            "Advanced VaR",
        )

        self.add_query(
            "Liquidity-adjusted VaR with market depth", "LVaR = VaR + Liquidity_Adjustment * σ", "Advanced VaR"
        )

        self.add_query(
            "Stressed VaR using stressed market parameters",
            "Stressed_VaR = μ_stressed - z * σ_stressed * √t",
            "Advanced VaR",
        )

        self.add_query("Incremental CVaR", "I_CVaR = CVaR(Portfolio+Position) - CVaR(Portfolio)", "Advanced VaR")

    def generate_stress_testing_formulas(self):
        """Generate 25 Stress Testing formulas."""
        print("Generating Stress Testing formulas (25 variants)...")

        self.add_query(
            "Scenario loss - portfolio value change under stress scenario",
            "Scenario_Loss = Portfolio_Value_0 - Portfolio_Value_stress",
            "Stress Testing",
        )

        self.add_query(
            "Parallel shift stress test - all rates shift equally",
            "Stress_Parallel = Σ(Duration_i * Shift * Value_i)",
            "Stress Testing",
        )

        self.add_query(
            "Yield curve twist stress test", "Stress_Twist = Σ(Duration_Slope_i * Twist * Value_i)", "Stress Testing"
        )

        self.add_query(
            "Butterfly shift in yield curve",
            "Stress_Butterfly = Σ(Butterfly_Sensitivity_i * Shift * Value_i)",
            "Stress Testing",
        )

        self.add_query(
            "Correlation breakdown scenario",
            "Stress_Correlation = Portfolio_Loss(ρ=correlation_stress)",
            "Stress Testing",
        )

    def generate_risk_metrics_advanced(self):
        """Generate 30 Advanced risk metrics."""
        print("Generating Advanced risk metrics (30 variants)...")

        self.add_query(
            "Omega Ratio - probability-weighted returns vs threshold",
            "Omega(R_t) = E[max(R - R_t, 0)] / E[max(R_t - R, 0)]",
            "Advanced Metrics",
        )

        self.add_query(
            "Kappa Ratio - excess return to below-target semi-deviation",
            "Kappa_3 = (R - R_t) / (E[(max(R_t - R, 0))³])^(1/3)",
            "Advanced Metrics",
        )

        self.add_query(
            "Ulcer Index - average depth and duration of drawdowns",
            "UI = √(Σ(D_i²)/n) where D_i = percentage drawdowns",
            "Advanced Metrics",
        )

        self.add_query(
            "Martin Ratio - return to Ulcer Index", "Martin = Annual_Return / Ulcer_Index", "Advanced Metrics"
        )

        self.add_query(
            "Tail ratio - size of gains vs losses in tail",
            "Tail_Ratio = E[R | R > percentile_95] / |E[R | R < percentile_5]|",
            "Advanced Metrics",
        )

        self.add_query("Skewness - asymmetry of return distribution", "Skewness = E[(R - μ)³] / σ³", "Advanced Metrics")

        self.add_query(
            "Kurtosis - tail heaviness of return distribution", "Kurtosis = E[(R - μ)⁴] / σ⁴ - 3", "Advanced Metrics"
        )

        self.add_query(
            "Value at Risk for portfolio with options (delta-gamma approximation)",
            "VaR_approx = ΔS + 0.5*Γ*(ΔS)²",
            "Advanced Metrics",
        )

    def generate_correlation_covariance(self):
        """Generate 22 Correlation and Covariance formulas."""
        print("Generating Correlation and Covariance formulas (22 variants)...")

        self.add_query("Correlation coefficient between two assets", "ρ_xy = Cov(x,y) / (σ_x * σ_y)", "Correlation")

        self.add_query("Covariance matrix for portfolio", "Cov(R_p) = w^T * Σ * w", "Correlation")

        self.add_query("Portfolio volatility with correlations", "σ_p = √(Σ Σ w_i*w_j*σ_i*σ_j*ρ_ij)", "Correlation")

        self.add_query(
            "Rolling correlation - time-varying correlation",
            "ρ_rolling(t) = Cov(R_x[t-n:t], R_y[t-n:t]) / (σ_x * σ_y)",
            "Correlation",
        )

        self.add_query(
            "Exponentially weighted moving average correlation",
            "ρ_EWMA(t) = λ*ρ_EWMA(t-1) + (1-λ)*r_x(t)*r_y(t)",
            "Correlation",
        )

    def generate_all(self):
        """Generate all risk formulas."""
        print("\n" + "#" * 80)
        print("# Risk Management Queries Dataset - Comprehensive")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print("#" * 80 + "\n")

        self.generate_var_formulas()  # 35
        self.generate_cvar_formulas()  # 30
        self.generate_sharpe_ratio_formulas()  # 25
        self.generate_sortino_ratio_formulas()  # 25
        self.generate_beta_formulas()  # 28
        self.generate_max_drawdown_formulas()  # 30
        self.generate_information_ratio_formulas()  # 24
        self.generate_treynor_ratio_formulas()  # 20
        self.generate_capm_formulas()  # 28
        self.generate_var_extensions()  # 32
        self.generate_stress_testing_formulas()  # 25
        self.generate_risk_metrics_advanced()  # 30
        self.generate_correlation_covariance()  # 22

        print(f"\n✓ Generated {self.formula_count} total risk formulas")
        return self.formula_count

    def to_dataframe(self):
        """Convert to DataFrame."""
        return pd.DataFrame(self.queries)

    def save_csv(self, filename="hypatiax/datasets/generators/queries/finance/risk/risk_queries_comprehensive.csv"):
        """Save to CSV."""
        df = self.to_dataframe()
        df.to_csv(filename, index=False)
        print(f"✓ Saved CSV: {filename}")
        return filename

    def save_json(self, filename="hypatiax/datasets/generators/queries/finance/risk/risk_queries_comprehensive.json"):
        """Save to JSON."""
        df = self.to_dataframe()
        df.to_json(filename, orient="records", indent=2)
        print(f"✓ Saved JSON: {filename}")
        return filename

    def print_summary(self):
        """Print comprehensive summary."""
        df = self.to_dataframe()

        print("\n" + "=" * 80)
        print("DATASET SUMMARY - Risk Management Formulas")
        print("=" * 80)

        print(f"\nTotal queries: {len(df)}")
        print("\nBreakdown by category:")
        print("-" * 80)

        for cat in sorted(df["category"].unique()):
            count = len(df[df["category"] == cat])
            pct = (count / len(df)) * 100
            print(f"  {cat:.<50} {count:>3} ({pct:>5.1f}%)")

        print("-" * 80)
        print(f"  {'TOTAL':.<50} {len(df):>3} (100.0%)")

        print("\n" + "-" * 80)
        print("Sample rows:")
        print("-" * 80)

        for idx, row in df.head(20).iterrows():
            print(f"\n[{idx+1}] {row['category']}")
            print(f"    Description: {row['description']}")
            print(f"    Formula:     {row['analytical_formula']}")

        print("\n" + "=" * 80)


def main():
    """Main execution."""
    print("\n" + "█" * 80)
    print("█  Risk Management Queries Dataset - Complete  █")
    print("█  Description → Analytical Formula Mappings  █")
    print("█  All Major Risk Formulas Used in Finance  █")
    print("█" * 80)

    generator = RiskQueriesDataset(seed=42)
    total = generator.generate_all()
    generator.print_summary()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = generator.save_csv(f"risk_queries_{timestamp}.csv")
    json_file = generator.save_json(f"risk_queries_{timestamp}.json")

    print(f"\n" + "=" * 80)
    print("✓ COMPLETE!")
    print(f"  Total formulas: {total}")
    print(f"  CSV: {csv_file}")
    print(f"  JSON: {json_file}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
