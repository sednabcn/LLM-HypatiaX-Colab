import os

import numpy as np
from scipy import stats

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


def generate_risk_formulas(n_samples=200, noise_level=0.01):
    """
    Generate comprehensive risk management dataset.

    Args:
        n_samples: Number of samples per formula
        noise_level: Standard deviation of added noise
    """
    system = HybridDiscoverySystem(domain="risk")

    # Formula 1: VaR 95% (corrected z-score)
    print("Generating VaR 95% dataset...")
    mu = np.random.uniform(-0.1, 0.15, n_samples)
    sigma = np.random.uniform(0.05, 0.5, n_samples)
    t = np.random.uniform(1, 252, n_samples)  # 1 to 252 trading days
    X_var = np.column_stack([mu, sigma, t])
    # Correct 95% confidence: z = 1.96 (not 1.645)
    var_95 = mu - 1.96 * sigma * np.sqrt(t) + np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X_var,
        y=var_95,
        variable_names=["mu", "sigma", "t"],
        variable_descriptions={"mu": "Expected return", "sigma": "Volatility (annualized)", "t": "Time horizon"},
        variable_units={"mu": "percent", "sigma": "percent", "t": "dimensionless"},
        description="Value at Risk at 95% confidence level",
    )

    # Formula 2: Sharpe Ratio
    print("Generating Sharpe Ratio dataset...")
    returns = np.random.uniform(-0.1, 0.3, n_samples)
    risk_free = np.random.uniform(0.01, 0.05, n_samples)  # Variable risk-free rate
    vol = np.random.uniform(0.05, 0.3, n_samples)
    X_sharpe = np.column_stack([returns, risk_free, vol])
    sharpe = (returns - risk_free) / vol + np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X_sharpe,
        y=sharpe,
        variable_names=["returns", "risk_free", "volatility"],
        variable_descriptions={
            "returns": "Portfolio returns (annualized)",
            "risk_free": "Risk-free rate (annualized)",
            "volatility": "Return volatility (annualized)",
        },
        variable_units={"returns": "percent", "risk_free": "percent", "volatility": "percent"},
        description="Sharpe ratio - risk-adjusted return measure",
    )

    # Formula 3: CVaR (Conditional VaR / Expected Shortfall)
    print("Generating CVaR 95% dataset...")
    mu_cvar = np.random.uniform(-0.1, 0.15, n_samples)
    sigma_cvar = np.random.uniform(0.05, 0.5, n_samples)
    t_cvar = np.random.uniform(1, 252, n_samples)
    X_cvar = np.column_stack([mu_cvar, sigma_cvar, t_cvar])
    # CVaR formula for normal distribution at 95%
    phi_inv = stats.norm.pdf(1.96) / (1 - 0.95)  # ≈ 2.063
    cvar_95 = mu_cvar - phi_inv * sigma_cvar * np.sqrt(t_cvar) + np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X_cvar,
        y=cvar_95,
        variable_names=["mu", "sigma", "t"],
        variable_descriptions={"mu": "Expected return", "sigma": "Volatility (annualized)", "t": "Time horizon"},
        variable_units={"mu": "percent", "sigma": "percent", "t": "dimensionless"},
        description="Conditional VaR (Expected Shortfall) at 95% confidence",
    )

    # Formula 4: Beta (systematic risk)
    print("Generating Beta dataset...")
    cov_im = np.random.uniform(-0.1, 0.3, n_samples)  # Covariance with market
    var_m = np.random.uniform(0.01, 0.2, n_samples)  # Market variance
    X_beta = np.column_stack([cov_im, var_m])
    risk_beta = cov_im / var_m + np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X_beta,
        y=risk_beta,
        variable_names=["cov_im", "var_m"],
        variable_descriptions={"cov_im": "Covariance between asset and market", "var_m": "Market variance"},
        variable_units={"cov_im": "percent^2", "var_m": "percent^2"},
        description="Beta - measure of systematic risk relative to market",
    )

    # Formula 5: Sortino Ratio
    print("Generating Sortino Ratio dataset...")
    returns_sort = np.random.uniform(-0.1, 0.3, n_samples)
    target_return = np.random.uniform(0, 0.05, n_samples)
    downside_dev = np.random.uniform(0.05, 0.25, n_samples)
    X_sortino = np.column_stack([returns_sort, target_return, downside_dev])
    sortino = (returns_sort - target_return) / downside_dev + np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X_sortino,
        y=sortino,
        variable_names=["returns", "target", "downside_dev"],
        variable_descriptions={
            "returns": "Portfolio returns (annualized)",
            "target": "Target or required return",
            "downside_dev": "Downside deviation",
        },
        variable_units={"returns": "percent", "target": "percent", "downside_dev": "percent"},
        description="Sortino ratio - downside risk-adjusted return",
    )

    # Formula 6: Information Ratio
    print("Generating Information Ratio dataset...")
    active_return = np.random.uniform(-0.05, 0.15, n_samples)
    tracking_error = np.random.uniform(0.02, 0.15, n_samples)
    X_ir = np.column_stack([active_return, tracking_error])
    info_ratio = active_return / tracking_error + np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X_ir,
        y=info_ratio,
        variable_names=["active_return", "tracking_error"],
        variable_descriptions={
            "active_return": "Portfolio return minus benchmark return",
            "tracking_error": "Standard deviation of active returns",
        },
        variable_units={"active_return": "percent", "tracking_error": "percent"},
        description="Information ratio - active management skill measure",
    )

    # Formula 7: Maximum Drawdown (simplified)
    print("Generating Maximum Drawdown dataset...")
    peak_value = np.random.uniform(100, 1000, n_samples)
    trough_value = peak_value * np.random.uniform(0.5, 0.95, n_samples)
    X_mdd = np.column_stack([peak_value, trough_value])
    max_dd = (trough_value - peak_value) / peak_value + np.random.normal(0, noise_level / 10, n_samples)

    system.discover_validate_interpret(
        X=X_mdd,
        y=max_dd,
        variable_names=["peak", "trough"],
        variable_descriptions={"peak": "Peak portfolio value", "trough": "Trough portfolio value"},
        variable_units={"peak": "currency", "trough": "currency"},
        description="Maximum Drawdown - largest peak-to-trough decline",
    )

    # Formula 8: Treynor Ratio
    print("Generating Treynor Ratio dataset...")
    returns_trey = np.random.uniform(-0.1, 0.3, n_samples)
    risk_free_trey = np.random.uniform(0.01, 0.05, n_samples)
    beta_trey = np.random.uniform(0.5, 2.0, n_samples)
    X_treynor = np.column_stack([returns_trey, risk_free_trey, beta_trey])
    treynor = (returns_trey - risk_free_trey) / beta_trey + np.random.normal(0, noise_level, n_samples)

    system.discover_validate_interpret(
        X=X_treynor,
        y=treynor,
        variable_names=["returns", "risk_free", "risk_beta"],
        variable_descriptions={
            "returns": "Portfolio returns (annualized)",
            "risk_free": "Risk-free rate (annualized)",
            "risk_beta": "Systematic risk (beta)",
        },
        variable_units={"returns": "percent", "risk_free": "percent", "risk_beta": "dimensionless"},
        description="Treynor ratio - return per unit of systematic risk",
    )

    # Save results
    os.makedirs("hypatiax/data/finance/risk", exist_ok=True)
    system.export_results("hypatiax/data/finance/risk/risk_comprehensive.json", format="json")

    # Summary statistics
    valid = sum(1 for r in system.results if r["validation"]["valid"])
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  Total formulas: {len(system.results)}")
    print(f"  Validated: {valid}/{len(system.results)} ({100*valid/len(system.results):.1f}%)")
    print(f"  Samples per formula: {n_samples}")
    print(f"  Noise level: {noise_level}")
    print(f"  Output: hypatiax/data/finance/risk/risk_comprehensive.json")
    print(f"{'='*60}")

    return system


if __name__ == "__main__":
    # Generate with default parameters
    system = generate_risk_formulas(n_samples=200, noise_level=0.01)

    # Optional: Generate additional batch with more noise
    # system = generate_risk_formulas(n_samples=150, noise_level=0.02)
    # system.save_results('hypatiax/data/finance/risk/risk_batch2.json')
