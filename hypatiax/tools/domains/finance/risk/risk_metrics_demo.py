#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete demo for RiskMetrics class
Demonstrates all major features of the risk analytics system
"""

import numpy as np
from risk_metrics import Asset, RiskLevel, RiskMetrics, StressScenario, TimeHorizon


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_dict(d, indent=0):
    """Pretty print dictionary"""
    for key, value in d.items():
        if isinstance(value, dict):
            print("  " * indent + f"{key}:")
            print_dict(value, indent + 1)
        elif isinstance(value, (list, np.ndarray)) and len(str(value)) > 100:
            print("  " * indent + f"{key}: [array of length {len(value)}]")
        elif isinstance(value, float):
            print("  " * indent + f"{key}: {value:.6f}")
        else:
            print("  " * indent + f"{key}: {value}")


def demo_risk_metrics():
    """Comprehensive demonstration of RiskMetrics capabilities"""

    print("\n" + "=" * 80)
    print("  RiskMetrics Demo - Comprehensive Portfolio Risk Analysis")
    print("=" * 80)
    print("\nThis demo showcases a complete risk management workflow:")
    print("  - Portfolio construction with multiple assets")
    print("  - Core risk metrics calculation")
    print("  - Risk-adjusted performance analysis")
    print("  - Correlation and diversification analysis")
    print("  - Risk attribution and budgeting")
    print("  - Stress testing and scenario analysis")
    print("  - Real-time risk monitoring")

    # ========================================================================
    # 1. Portfolio Construction
    # ========================================================================
    print_section("1. Portfolio Construction")

    np.random.seed(42)

    # Initialize risk metrics calculator
    rm = RiskMetrics(risk_free_rate=0.03)

    # Create a diversified portfolio with realistic characteristics
    print("\nCreating portfolio with 5 assets:")

    # Tech stock - high volatility, high return
    aapl_returns = np.random.normal(0.0008, 0.025, 252)
    rm.add_asset(
        Asset(
            "AAPL",
            aapl_returns,
            weight=0.25,
            market_value=250000,
            beta=1.2,
            sector="Technology",
        )
    )
    print("  - AAPL: 25% weight, $250k, Tech sector, β=1.2")

    # Financial stock - moderate volatility
    jpm_returns = np.random.normal(0.0005, 0.020, 252)
    rm.add_asset(
        Asset(
            "JPM",
            jpm_returns,
            weight=0.20,
            market_value=200000,
            beta=1.1,
            sector="Financials",
        )
    )
    print("  - JPM:  20% weight, $200k, Financials, β=1.1")

    # Consumer goods - lower volatility
    pg_returns = np.random.normal(0.0004, 0.015, 252)
    rm.add_asset(
        Asset(
            "PG",
            pg_returns,
            weight=0.20,
            market_value=200000,
            beta=0.8,
            sector="Consumer",
        )
    )
    print("  - PG:   20% weight, $200k, Consumer, β=0.8")

    # Healthcare - moderate volatility
    jnj_returns = np.random.normal(0.0005, 0.018, 252)
    rm.add_asset(
        Asset(
            "JNJ",
            jnj_returns,
            weight=0.20,
            market_value=200000,
            beta=0.9,
            sector="Healthcare",
        )
    )
    print("  - JNJ:  20% weight, $200k, Healthcare, β=0.9")

    # Bonds - low volatility, low return
    bonds_returns = np.random.normal(0.0002, 0.008, 252)
    rm.add_asset(
        Asset(
            "AGG",
            bonds_returns,
            weight=0.15,
            market_value=150000,
            beta=0.3,
            sector="Fixed Income",
        )
    )
    print("  - AGG:  15% weight, $150k, Fixed Income, β=0.3")

    # Set benchmark (S&P 500)
    benchmark_returns = np.random.normal(0.0006, 0.020, 252)
    rm.set_benchmark(benchmark_returns)
    print("\n  Benchmark: S&P 500 (simulated)")

    total_value = sum(a.market_value for a in rm.assets)
    print(f"\n  Total Portfolio Value: ${total_value:,.0f}")

    # ========================================================================
    # 2. Core Risk Metrics
    # ========================================================================
    print_section("2. Core Risk Metrics")

    portfolio_returns = rm.get_portfolio_returns()
    print(f"\nPortfolio has {len(portfolio_returns)} daily return observations")

    # Volatility
    print("\n[Volatility Analysis]")
    vol = rm.volatility()
    print(f"  Annualized Volatility: {vol['volatility_pct']:.2f}%")
    print(f"  Variance: {vol['variance']:.6f}")

    # Value at Risk
    print("\n[Value at Risk - Multiple Methods]")
    var_hist = rm.value_at_risk(confidence=0.95, method="historical")
    print(f"  Historical VaR (95%): {var_hist['var_pct']:.2f}%")

    var_param = rm.value_at_risk(confidence=0.95, method="parametric")
    print(f"  Parametric VaR (95%): {var_param['var_pct']:.2f}%")

    var_cf = rm.value_at_risk(confidence=0.95, method="cornish_fisher")
    print(f"  Cornish-Fisher VaR (95%): {var_cf['var_pct']:.2f}%")

    # Conditional VaR
    print("\n[Conditional Value at Risk]")
    cvar = rm.conditional_var(confidence=0.95)
    print(f"  CVaR (95%): {cvar['cvar_pct']:.2f}%")
    print(f"  Tail observations: {cvar['tail_observations']}")
    print(f"  Expected loss in worst 5% of days: {cvar['cvar_pct']:.2f}%")

    # Downside Deviation
    print("\n[Downside Risk]")
    downside = rm.downside_deviation(mar=0.0)
    print(f"  Downside Deviation: {downside['downside_deviation_pct']:.2f}%")
    print(f"  Downside Frequency: {downside['downside_frequency'] * 100:.1f}%")
    print(
        f"  Negative return days: {downside['downside_periods']}/{downside['total_periods']}"
    )

    # ========================================================================
    # 3. Risk-Adjusted Performance
    # ========================================================================
    print_section("3. Risk-Adjusted Performance Metrics")

    # Sharpe Ratio
    print("\n[Sharpe Ratio]")
    sharpe = rm.sharpe_ratio()
    print(f"  Sharpe Ratio: {sharpe['sharpe']:.3f}")
    print(f"  Mean Excess Return: {sharpe['mean_excess_return']:.6f}")
    print(
        f"  Interpretation: {'Excellent' if sharpe['sharpe'] > 2 else 'Good' if sharpe['sharpe'] > 1 else 'Moderate' if sharpe['sharpe'] > 0.5 else 'Poor'}"
    )

    # Sortino Ratio
    print("\n[Sortino Ratio]")
    sortino = rm.sortino_ratio()
    print(f"  Sortino Ratio: {sortino['sortino']:.3f}")
    print(f"  Downside Deviation: {sortino['downside_deviation']:.6f}")
    print(f"  (Sortino focuses on downside risk only)")

    # Calmar Ratio
    print("\n[Calmar Ratio]")
    calmar = rm.calmar_ratio()
    print(f"  Calmar Ratio: {calmar['calmar']:.3f}")
    print(f"  Annual Return: {calmar['annual_return'] * 100:.2f}%")
    print(f"  Max Drawdown: {calmar['max_drawdown'] * 100:.2f}%")

    # ========================================================================
    # 4. Drawdown Analysis
    # ========================================================================
    print_section("4. Drawdown Analysis")

    dd = rm.drawdown_analysis()
    print(f"\n  Maximum Drawdown: {dd['max_drawdown_pct']:.2f}%")
    print(f"  Max DD Duration: {dd['max_drawdown_length']} days")
    print(f"  Longest Drawdown Period: {dd['longest_drawdown_length']} days")
    print(f"  Number of Drawdown Periods: {dd['num_drawdown_periods']}")
    print(f"  Average Drawdown Depth: {dd['avg_drawdown_depth'] * 100:.2f}%")
    print(f"  Average Drawdown Length: {dd['avg_drawdown_length']:.1f} days")
    print(f"  Current Drawdown: {dd['current_drawdown'] * 100:.2f}%")
    print(f"  Time Underwater: {dd['time_underwater_pct']:.1f}%")

    # ========================================================================
    # 5. Correlation & Diversification
    # ========================================================================
    print_section("5. Correlation & Diversification Analysis")

    # Correlation matrix
    print("\n[Correlation Matrix]")
    corr = rm.correlation_matrix()
    print(f"\n  Assets: {', '.join(corr['symbols'])}")
    print(f"  Average Correlation: {corr['average_correlation']:.3f}")
    print(f"  Max Correlation: {corr['max_correlation']:.3f}")
    print(f"  Min Correlation: {corr['min_correlation']:.3f}")

    print("\n  Correlation Matrix:")
    matrix = corr["correlation_matrix"]
    symbols = corr["symbols"]

    # Print header
    print("        ", end="")
    for sym in symbols:
        print(f"{sym:>8}", end="")
    print()

    # Print matrix
    for i, sym in enumerate(symbols):
        print(f"  {sym:>5}", end="")
        for j in range(len(symbols)):
            print(f"{matrix[i, j]:>8.3f}", end="")
        print()

    # Diversification ratio
    print("\n[Diversification Ratio]")
    div = rm.diversification_ratio()
    print(f"  Diversification Ratio: {div['diversification_ratio']:.3f}")
    print(f"  Weighted Avg Volatility: {div['weighted_avg_volatility']:.6f}")
    print(f"  Portfolio Volatility: {div['portfolio_volatility']:.6f}")
    print(f"  Diversification Benefit: {div['diversification_benefit']:.2f}%")
    print(f"\n  Interpretation: DR > 1 indicates diversification benefit")
    print(
        f"  Your portfolio reduces risk by {div['diversification_benefit']:.1f}% through diversification"
    )

    # ========================================================================
    # 6. Risk Attribution & Budgeting
    # ========================================================================
    print_section("6. Risk Attribution & Budgeting")

    # Component VaR
    print("\n[Component VaR Analysis]")
    comp_var = rm.component_var(confidence=0.95)
    print("\n  Asset     Weight    Marginal VaR    Component VaR    % of Total")
    print("  " + "-" * 70)

    total_comp_var = sum(abs(c["component_var"]) for c in comp_var)
    for comp in comp_var:
        pct_of_total = (
            abs(comp["component_var"]) / total_comp_var * 100
            if total_comp_var > 0
            else 0
        )
        print(
            f"  {comp['asset']:>5}   {comp['weight']:>6.1%}    {comp['marginal_var']:>11.6f}    "
            f"{comp['component_var']:>13.6f}    {pct_of_total:>7.1f}%"
        )

    # Risk Budget Analysis
    print("\n[Risk Budget Analysis]")
    target_budgets = {
        "AAPL": 25.0,  # Target: 25% of risk
        "JPM": 20.0,  # Target: 20% of risk
        "PG": 20.0,  # Target: 20% of risk
        "JNJ": 20.0,  # Target: 20% of risk
        "AGG": 15.0,  # Target: 15% of risk
    }

    risk_budgets = rm.risk_budget_analysis(target_budgets)

    print("\n  Asset    Allocated    Actual    Utilization    Status")
    print("  " + "-" * 60)

    for rb in risk_budgets:
        status = "OVER" if rb.is_over_budget else "OK"
        print(
            f"  {rb.asset:>5}    {rb.allocated_risk:>6.1f}%    {rb.actual_risk:>6.1f}%    "
            f"{rb.utilization:>8.1%}       {status}"
        )

    # ========================================================================
    # 7. Stress Testing
    # ========================================================================
    print_section("7. Stress Testing & Scenario Analysis")

    # Market crash scenario
    print("\n[Scenario 1: Market Crash (-20%)]")
    crash_scenario = StressScenario(
        name="Market Crash",
        shock_type="absolute",
        parameters={"shock": -0.20},
        description="Severe market downturn with 20% decline",
    )

    crash_result = rm.stress_test(crash_scenario)
    print(f"  Scenario: {crash_result['scenario_name']}")
    print(f"  Loss: {crash_result['loss_pct']:.2f}%")
    print(f"  Stressed Value: {crash_result['stressed_value']:.4f}")
    print(f"  Stressed VaR: {crash_result.get('stressed_var_pct', 'N/A')}")

    # Interest rate shock
    print("\n[Scenario 2: Interest Rate Shock]")
    rate_scenario = StressScenario(
        name="Rate Shock",
        shock_type="relative",
        parameters={"shock_pct": -0.10},
        description="10% decline due to rate hikes",
    )

    rate_result = rm.stress_test(rate_scenario)
    print(f"  Scenario: {rate_result['scenario_name']}")
    print(f"  Loss: {rate_result['loss_pct']:.2f}%")

    # Monte Carlo VaR
    print("\n[Monte Carlo VaR Simulation]")
    mc_var = rm.monte_carlo_var(num_simulations=10000, time_horizon=1, confidence=0.95)
    print(f"  Simulations: {mc_var['num_simulations']:,}")
    print(f"  Time Horizon: {mc_var['time_horizon']} day(s)")
    print(f"  MC VaR (95%): {mc_var['mc_var_pct']:.2f}%")
    print(f"  MC CVaR (95%): {mc_var['mc_cvar_pct']:.2f}%")
    print(f"  Simulated Mean: {mc_var['simulated_mean']:.6f}")
    print(f"  Simulated Std Dev: {mc_var['simulated_std']:.6f}")

    # ========================================================================
    # 8. Real-time Risk Monitoring
    # ========================================================================
    print_section("8. Real-time Risk Monitoring Dashboard")

    dashboard = rm.risk_dashboard()

    print(f"\n  Timestamp: {dashboard['timestamp']}")
    print(f"  Risk Level: {dashboard['risk_level'].upper()}")
    print(f"  Number of Assets: {dashboard['num_assets']}")
    print(f"  Observation Periods: {dashboard['observation_periods']}")

    print("\n[Key Metrics Summary]")
    print(f"  Volatility: {dashboard['volatility']['volatility_pct']:.2f}%")
    print(f"  VaR (95%): {dashboard['var_95']['var_pct']:.2f}%")
    print(f"  CVaR (95%): {dashboard['cvar_95']['cvar_pct']:.2f}%")
    print(f"  Sharpe Ratio: {dashboard['sharpe_ratio']['sharpe']:.3f}")
    print(f"  Sortino Ratio: {dashboard['sortino_ratio']['sortino']:.3f}")
    print(f"  Max Drawdown: {dashboard['drawdown']['max_drawdown_pct']:.2f}%")
    print(
        f"  Diversification Ratio: {dashboard['diversification']['diversification_ratio']:.3f}"
    )
    print(f"  Average Correlation: {dashboard['correlation']['average']:.3f}")

    if dashboard["warnings"]:
        print("\n[⚠️  WARNINGS]")
        for warning in dashboard["warnings"]:
            print(f"  • {warning}")
    else:
        print("\n[✓ No warnings - portfolio within normal parameters]")

    # ========================================================================
    # 9. Risk Limits Check
    # ========================================================================
    print_section("9. Risk Limits Compliance Check")

    # Define risk limits
    limits = {
        "max_drawdown": 0.25,  # 25% max drawdown
        "min_sharpe": 0.5,  # Minimum Sharpe ratio
        "max_var_95": 0.05,  # 5% max VaR
    }

    print("\n[Defined Risk Limits]")
    print(f"  Max Drawdown: {limits['max_drawdown'] * 100:.0f}%")
    print(f"  Min Sharpe Ratio: {limits['min_sharpe']:.1f}")
    print(f"  Max VaR (95%): {limits['max_var_95'] * 100:.0f}%")

    compliance = rm.risk_limits_check(limits)

    print(f"\n[Compliance Status]")
    print(
        f"  Overall Status: {'✓ COMPLIANT' if compliance['compliant'] else '✗ BREACHES DETECTED'}"
    )
    print(f"  Number of Breaches: {compliance['num_breaches']}")

    if compliance["breaches"]:
        print("\n  Breach Details:")
        for breach in compliance["breaches"]:
            print(f"\n    Limit: {breach['limit']}")
            print(f"    Threshold: {breach['threshold']:.4f}")
            print(f"    Actual: {breach['actual']:.4f}")
            print(f"    Breach Amount: {breach['breach_amount']:.4f}")

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("Demo Complete - Summary")

    print("\nThis demo demonstrated:")
    print("  ✓ Portfolio construction with multiple asset classes")
    print("  ✓ Comprehensive risk metrics (VaR, CVaR, volatility)")
    print("  ✓ Risk-adjusted performance (Sharpe, Sortino, Calmar)")
    print("  ✓ Drawdown analysis and recovery time")
    print("  ✓ Correlation analysis and diversification benefits")
    print("  ✓ Risk attribution and component VaR")
    print("  ✓ Risk budget monitoring and compliance")
    print("  ✓ Stress testing with multiple scenarios")
    print("  ✓ Monte Carlo simulation for VaR")
    print("  ✓ Real-time risk dashboard")
    print("  ✓ Automated risk limit monitoring")

    print("\n" + "=" * 80)
    print("  End of RiskMetrics Demo")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    demo_risk_metrics()
