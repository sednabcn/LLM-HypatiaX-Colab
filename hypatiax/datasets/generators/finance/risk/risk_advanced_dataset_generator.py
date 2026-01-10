"""
Advanced Risk Management Formula Discovery Dataset Generator
Class-based structure with three phases:
  - Phase 1: 10 Advanced Risk Metrics
  - Phase 2: 5 Stress Testing Scenarios
  - Phase 3: 5 Margin & Leverage Formulas
Total: 20 formulas
"""

import os
from datetime import datetime

import numpy as np
from scipy import stats

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class AdvancedRiskGenerator:
    """Generate advanced risk management formulas with three phases."""

    def __init__(
        self, domain: str = "risk", seed: int = 42, noise_level: float = 0.001
    ):
        """
        Initialize the advanced risk generator.

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
        self.phase = None

    def generate_formula(self, formula_num: int, n_samples: int = 150):
        """
        Generate data for each formula (1-20).

        Args:
            formula_num: Formula number (1-20)
            n_samples: Number of samples to generate
        """

        # PHASE 1: Advanced Risk Metrics (1-10)
        if formula_num == 1:  # VaR with Cornish-Fisher
            print("\n1. VaR with Cornish-Fisher Adjustment")
            mu = np.random.uniform(-0.1, 0.1, n_samples)
            sigma = np.random.uniform(0.1, 0.5, n_samples)
            skewness = np.random.uniform(-1.5, 1.5, n_samples)
            kurtosis = np.random.uniform(0, 3, n_samples)

            X = np.column_stack([mu, sigma, skewness, kurtosis])

            z = 1.645
            z_cf = (
                z
                + (z**2 - 1) * skewness / 6
                + (z**3 - 3 * z) * kurtosis / 24
                - (2 * z**3 - 5 * z) * skewness**2 / 36
            )
            var_cf = mu - z_cf * sigma
            var_cf += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=var_cf,
                variable_names=["mu", "sigma", "skewness", "kurtosis"],
                variable_descriptions={
                    "mu": "Expected return",
                    "sigma": "Volatility",
                    "skewness": "Distribution skewness",
                    "kurtosis": "Excess kurtosis",
                },
                variable_units={
                    "mu": "dimensionless",
                    "sigma": "dimensionless",
                    "skewness": "dimensionless",
                    "kurtosis": "dimensionless",
                },
                description="VaR at 95% with Cornish-Fisher adjustment for non-normal returns",
                validate_first=False,
            )

        elif formula_num == 2:  # Expected Shortfall
            print("\n2. Expected Shortfall (CVaR)")
            mu = np.random.uniform(-0.1, 0.1, n_samples)
            sigma = np.random.uniform(0.1, 0.5, n_samples)
            alpha = 0.95

            X = np.column_stack([mu, sigma])

            z_alpha = stats.norm.ppf(alpha)
            pdf_z = stats.norm.pdf(z_alpha)
            es = mu - sigma * pdf_z / (1 - alpha)
            es += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=es,
                variable_names=["mu", "sigma"],
                variable_descriptions={"mu": "Expected return", "sigma": "Volatility"},
                variable_units={"mu": "dimensionless", "sigma": "dimensionless"},
                description="Expected Shortfall (CVaR) at 95% confidence",
                validate_first=False,
            )

        elif formula_num == 3:  # Modified VaR t-distribution
            print("\n3. Modified VaR for Heavy-Tailed Returns")
            mu = np.random.uniform(-0.1, 0.1, n_samples)
            sigma = np.random.uniform(0.1, 0.5, n_samples)
            df = np.random.uniform(3, 10, n_samples)

            X = np.column_stack([mu, sigma, df])

            t_quantile = np.array([stats.t.ppf(0.05, d) for d in df])
            var_t = mu + t_quantile * sigma * np.sqrt((df - 2) / df)
            var_t += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=var_t,
                variable_names=["mu", "sigma", "df"],
                variable_descriptions={
                    "mu": "Expected return",
                    "sigma": "Volatility",
                    "df": "Degrees of freedom (t-distribution)",
                },
                variable_units={
                    "mu": "dimensionless",
                    "sigma": "dimensionless",
                    "df": "dimensionless",
                },
                description="Modified VaR using Student's t-distribution (heavy tails)",
                validate_first=False,
            )

        elif formula_num == 4:  # Portfolio VaR
            print("\n4. Two-Asset Portfolio VaR")
            w1 = np.random.uniform(0, 1, n_samples)
            w2 = 1 - w1
            sigma1 = np.random.uniform(0.1, 0.4, n_samples)
            sigma2 = np.random.uniform(0.1, 0.4, n_samples)
            rho = np.random.uniform(-0.5, 0.9, n_samples)

            X = np.column_stack([w1, w2, sigma1, sigma2, rho])

            portfolio_vol = np.sqrt(
                w1**2 * sigma1**2
                + w2**2 * sigma2**2
                + 2 * w1 * w2 * sigma1 * sigma2 * rho
            )
            portfolio_var = -1.645 * portfolio_vol
            portfolio_var += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=portfolio_var,
                variable_names=["w1", "w2", "sigma1", "sigma2", "rho"],
                variable_descriptions={
                    "w1": "Weight of asset 1",
                    "w2": "Weight of asset 2",
                    "sigma1": "Volatility of asset 1",
                    "sigma2": "Volatility of asset 2",
                    "rho": "Correlation between assets",
                },
                variable_units={
                    "w1": "dimensionless",
                    "w2": "dimensionless",
                    "sigma1": "dimensionless",
                    "sigma2": "dimensionless",
                    "rho": "dimensionless",
                },
                description="Two-asset portfolio VaR with correlation",
                validate_first=False,
            )

        elif formula_num == 5:  # Diversification Benefit
            print("\n5. Portfolio Diversification Benefit")
            sigma1 = np.random.uniform(0.15, 0.4, n_samples)
            sigma2 = np.random.uniform(0.15, 0.4, n_samples)
            w1 = np.random.uniform(0.3, 0.7, n_samples)
            w2 = 1 - w1
            correlation = np.random.uniform(-0.3, 0.9, n_samples)

            X = np.column_stack([sigma1, sigma2, w1, w2, correlation])

            individual_var_sum = w1 * sigma1 + w2 * sigma2
            portfolio_vol = np.sqrt(
                w1**2 * sigma1**2
                + w2**2 * sigma2**2
                + 2 * w1 * w2 * sigma1 * sigma2 * correlation
            )
            div_benefit = individual_var_sum - portfolio_vol
            div_benefit += np.random.normal(0, self.noise_level * 0.1, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=div_benefit,
                variable_names=["sigma1", "sigma2", "w1", "w2", "correlation"],
                variable_descriptions={
                    "sigma1": "Volatility of asset 1",
                    "sigma2": "Volatility of asset 2",
                    "w1": "Weight of asset 1",
                    "w2": "Weight of asset 2",
                    "correlation": "Correlation coefficient",
                },
                variable_units={
                    "sigma1": "dimensionless",
                    "sigma2": "dimensionless",
                    "w1": "dimensionless",
                    "w2": "dimensionless",
                    "correlation": "dimensionless",
                },
                description="Portfolio diversification benefit (risk reduction)",
                validate_first=False,
            )

        elif formula_num == 6:  # Marginal VaR
            print("\n6. Marginal VaR (Risk Contribution)")
            portfolio_var = np.random.uniform(10000, 100000, n_samples)
            asset_weight = np.random.uniform(0.1, 0.5, n_samples)
            asset_beta = np.random.uniform(0.5, 2.0, n_samples)

            X = np.column_stack([portfolio_var, asset_weight, asset_beta])

            marginal_var = portfolio_var * asset_beta
            marginal_var += np.random.normal(0, self.noise_level * 1000, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=marginal_var,
                variable_names=["portfolio_var", "weight", "beta"],
                variable_descriptions={
                    "portfolio_var": "Portfolio VaR",
                    "weight": "Asset weight in portfolio",
                    "beta": "Asset beta to portfolio",
                },
                variable_units={
                    "portfolio_var": "dimensionless",
                    "weight": "dimensionless",
                    "beta": "dimensionless",
                },
                description="Marginal VaR - risk contribution of individual asset",
                validate_first=False,
            )

        elif formula_num == 7:  # Component VaR
            print("\n7. Component VaR")
            portfolio_var = np.random.uniform(10000, 100000, n_samples)
            weight = np.random.uniform(0.1, 0.5, n_samples)
            beta = np.random.uniform(0.5, 2.0, n_samples)

            X = np.column_stack([portfolio_var, weight, beta])

            component_var = weight * portfolio_var * beta
            component_var += np.random.normal(0, self.noise_level * 1000, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=component_var,
                variable_names=["portfolio_var", "weight", "beta"],
                variable_descriptions={
                    "portfolio_var": "Portfolio VaR",
                    "weight": "Asset weight",
                    "beta": "Asset beta to portfolio",
                },
                variable_units={
                    "portfolio_var": "dimensionless",
                    "weight": "dimensionless",
                    "beta": "dimensionless",
                },
                description="Component VaR - total contribution to portfolio risk",
                validate_first=False,
            )

        elif formula_num == 8:  # Tail Risk Ratio
            print("\n8. Tail Risk Ratio")
            cvar = np.random.uniform(5, 20, n_samples)
            var = np.random.uniform(3, 15, n_samples)
            cvar = np.maximum(cvar, var * 1.1)

            X = np.column_stack([cvar, var])

            tail_ratio = cvar / var
            tail_ratio += np.random.normal(0, self.noise_level * 0.1, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=tail_ratio,
                variable_names=["cvar", "var"],
                variable_descriptions={
                    "cvar": "Expected Shortfall (CVaR)",
                    "var": "Value at Risk (VaR)",
                },
                variable_units={"cvar": "dimensionless", "var": "dimensionless"},
                description="Tail Risk Ratio - measures severity of tail events",
                validate_first=False,
            )

        elif formula_num == 9:  # RAROC
            print("\n9. Risk-Adjusted Return on Capital")
            expected_return = np.random.uniform(0.05, 0.25, n_samples)
            expected_loss = np.random.uniform(0.01, 0.05, n_samples)
            economic_capital = np.random.uniform(10000, 100000, n_samples)

            X = np.column_stack([expected_return, expected_loss, economic_capital])

            raroc = expected_return - expected_loss
            raroc += np.random.normal(0, self.noise_level, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=raroc,
                variable_names=["return", "loss", "capital"],
                variable_descriptions={
                    "return": "Expected return",
                    "loss": "Expected loss",
                    "capital": "Economic capital (risk measure)",
                },
                variable_units={
                    "return": "dimensionless",
                    "loss": "dimensionless",
                    "capital": "dimensionless",
                },
                description="Risk-Adjusted Return on Capital (RAROC)",
                validate_first=False,
            )

        elif formula_num == 10:  # Expected Max Drawdown
            print("\n10. Expected Maximum Drawdown")
            volatility = np.random.uniform(0.1, 0.5, n_samples)
            sharpe_ratio = np.random.uniform(0.5, 2.0, n_samples)
            time_horizon = np.random.uniform(1, 10, n_samples)

            X = np.column_stack([volatility, sharpe_ratio, time_horizon])

            expected_mdd = (
                0.63 * volatility * np.sqrt(time_horizon) / (sharpe_ratio + 0.1)
            )
            expected_mdd += np.random.normal(0, self.noise_level * 0.1, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=expected_mdd,
                variable_names=["volatility", "sharpe", "horizon"],
                variable_descriptions={
                    "volatility": "Return volatility",
                    "sharpe": "Sharpe ratio",
                    "horizon": "Time horizon",
                },
                variable_units={
                    "volatility": "dimensionless",
                    "sharpe": "dimensionless",
                    "horizon": "dimensionless",
                },
                description="Expected maximum drawdown over time horizon",
                validate_first=False,
            )

        # PHASE 2: Stress Testing (11-15)
        elif formula_num == 11:  # Market Crash
            print("\n11. Market Crash Stress Test")
            portfolio_value = np.random.uniform(100000, 10000000, n_samples)
            market_beta = np.random.uniform(0.5, 2.0, n_samples)
            crash_pct = np.random.uniform(-0.3, -0.10, n_samples)
            diversification = np.random.uniform(0.5, 0.95, n_samples)

            X = np.column_stack(
                [portfolio_value, market_beta, crash_pct, diversification]
            )

            stressed_loss = (
                portfolio_value * market_beta * abs(crash_pct) * (2 - diversification)
            )
            stressed_loss += np.random.normal(
                0, self.noise_level * portfolio_value.mean() * 0.01, n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=stressed_loss,
                variable_names=[
                    "portfolio_value",
                    "beta",
                    "crash_pct",
                    "diversification",
                ],
                variable_descriptions={
                    "portfolio_value": "Base portfolio value",
                    "beta": "Market beta",
                    "crash_pct": "Market crash percentage",
                    "diversification": "Diversification score (0-1)",
                },
                variable_units={
                    "portfolio_value": "dimensionless",
                    "beta": "dimensionless",
                    "crash_pct": "dimensionless",
                    "diversification": "dimensionless",
                },
                description="Market crash stress test - portfolio loss under severe market decline",
                validate_first=False,
            )

        elif formula_num == 12:  # Interest Rate Shock
            print("\n12. Interest Rate Shock Stress Test")
            bond_portfolio = np.random.uniform(50000, 5000000, n_samples)
            duration = np.random.uniform(2, 15, n_samples)
            rate_shock = np.random.uniform(0.01, 0.05, n_samples)
            convexity = np.random.uniform(20, 200, n_samples)

            X = np.column_stack([bond_portfolio, duration, rate_shock, convexity])

            price_change_pct = -duration * rate_shock + 0.5 * convexity * rate_shock**2
            portfolio_loss = bond_portfolio * abs(price_change_pct)
            portfolio_loss += np.random.normal(
                0, self.noise_level * bond_portfolio.mean() * 0.01, n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=portfolio_loss,
                variable_names=["portfolio", "duration", "rate_shock", "convexity"],
                variable_descriptions={
                    "portfolio": "Bond portfolio value",
                    "duration": "Modified duration",
                    "rate_shock": "Interest rate increase",
                    "convexity": "Portfolio convexity",
                },
                variable_units={
                    "portfolio": "dimensionless",
                    "duration": "dimensionless",
                    "rate_shock": "dimensionless",
                    "convexity": "dimensionless",
                },
                description="Interest rate shock - bond portfolio loss from rate increases",
                validate_first=False,
            )

        elif formula_num == 13:  # Volatility Spike
            print("\n13. Volatility Spike Stress Test")
            option_portfolio = np.random.uniform(10000, 1000000, n_samples)
            vega = np.random.uniform(100, 10000, n_samples)
            vol_increase = np.random.uniform(0.05, 0.30, n_samples)
            gamma = np.random.uniform(-1000, 1000, n_samples)

            X = np.column_stack([option_portfolio, vega, vol_increase, gamma])

            pnl = vega * vol_increase - abs(gamma) * vol_increase**2 * 100
            pnl += np.random.normal(0, self.noise_level * 1000, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=pnl,
                variable_names=["portfolio", "vega", "vol_increase", "gamma"],
                variable_descriptions={
                    "portfolio": "Option portfolio value",
                    "vega": "Vega exposure (P&L per 1% vol)",
                    "vol_increase": "Volatility increase",
                    "gamma": "Gamma exposure",
                },
                variable_units={
                    "portfolio": "dimensionless",
                    "vega": "dimensionless",
                    "vol_increase": "dimensionless",
                    "gamma": "dimensionless",
                },
                description="Volatility spike - option portfolio P&L from vol increase",
                validate_first=False,
            )

        elif formula_num == 14:  # Liquidity Crisis
            print("\n14. Liquidity Crisis Stress Test")
            portfolio_size = np.random.uniform(100000, 5000000, n_samples)
            daily_volume = np.random.uniform(1000000, 50000000, n_samples)
            liquidity_ratio = portfolio_size / daily_volume
            bid_ask_spread = np.random.uniform(0.001, 0.05, n_samples)

            X = np.column_stack([portfolio_size, daily_volume, bid_ask_spread])

            liquidation_cost = (
                portfolio_size * bid_ask_spread * np.sqrt(liquidity_ratio * 10)
            )
            liquidation_cost = np.clip(liquidation_cost, 0, portfolio_size * 0.5)
            liquidation_cost += np.random.normal(
                0, self.noise_level * portfolio_size.mean() * 0.001, n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=liquidation_cost,
                variable_names=["portfolio_size", "daily_volume", "spread"],
                variable_descriptions={
                    "portfolio_size": "Portfolio size to liquidate",
                    "daily_volume": "Market daily volume",
                    "spread": "Bid-ask spread",
                },
                variable_units={
                    "portfolio_size": "dimensionless",
                    "daily_volume": "dimensionless",
                    "spread": "dimensionless",
                },
                description="Liquidity crisis - cost to liquidate portfolio in stressed market",
                validate_first=False,
            )

        elif formula_num == 15:  # Correlation Breakdown
            print("\n15. Correlation Breakdown Stress Test")
            asset1_exposure = np.random.uniform(100000, 2000000, n_samples)
            asset2_exposure = np.random.uniform(100000, 2000000, n_samples)
            normal_correlation = np.random.uniform(0.3, 0.7, n_samples)
            stress_correlation = np.random.uniform(0.85, 0.99, n_samples)
            volatility_mult = np.random.uniform(1.5, 3.0, n_samples)

            X = np.column_stack(
                [
                    asset1_exposure,
                    asset2_exposure,
                    normal_correlation,
                    stress_correlation,
                    volatility_mult,
                ]
            )

            normal_vol = np.sqrt(
                asset1_exposure
                + asset2_exposure
                + 2 * np.sqrt(asset1_exposure * asset2_exposure) * normal_correlation
            )
            stress_vol = np.sqrt(
                asset1_exposure
                + asset2_exposure
                + 2 * np.sqrt(asset1_exposure * asset2_exposure) * stress_correlation
            )
            correlation_impact = (stress_vol - normal_vol) * volatility_mult
            correlation_impact += np.random.normal(
                0, self.noise_level * 1000, n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=correlation_impact,
                variable_names=[
                    "asset1",
                    "asset2",
                    "normal_corr",
                    "stress_corr",
                    "vol_mult",
                ],
                variable_descriptions={
                    "asset1": "Asset 1 exposure",
                    "asset2": "Asset 2 exposure",
                    "normal_corr": "Normal correlation",
                    "stress_corr": "Stressed correlation",
                    "vol_mult": "Volatility multiplier in crisis",
                },
                variable_units={
                    "asset1": "dimensionless",
                    "asset2": "dimensionless",
                    "normal_corr": "dimensionless",
                    "stress_corr": "dimensionless",
                    "vol_mult": "dimensionless",
                },
                description="Correlation breakdown - additional risk when correlations go to 1",
                validate_first=False,
            )

        # PHASE 3: Margin & Leverage (16-20)
        elif formula_num == 16:  # Initial Margin
            print("\n16. Initial Margin Requirement")
            position_size = np.random.uniform(10000, 1000000, n_samples)
            leverage = np.random.uniform(2, 20, n_samples)
            volatility = np.random.uniform(0.1, 2.0, n_samples)
            liquidity_factor = np.random.uniform(1.0, 1.5, n_samples)

            X = np.column_stack([position_size, leverage, volatility, liquidity_factor])

            base_margin = position_size / leverage
            vol_adjustment = 0.5 * volatility
            initial_margin = base_margin * (1 + vol_adjustment) * liquidity_factor
            initial_margin += np.random.normal(0, 100, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=initial_margin,
                variable_names=["position", "leverage", "volatility", "liquidity"],
                variable_descriptions={
                    "position": "Position notional value",
                    "leverage": "Leverage ratio",
                    "volatility": "Asset volatility",
                    "liquidity": "Liquidity adjustment factor",
                },
                variable_units={
                    "position": "dimensionless",
                    "leverage": "dimensionless",
                    "volatility": "dimensionless",
                    "liquidity": "dimensionless",
                },
                description="Initial margin requirement with volatility and liquidity adjustments",
                validate_first=False,
            )

        elif formula_num == 17:  # Maintenance Margin
            print("\n17. Maintenance Margin Requirement")
            position_value = np.random.uniform(10000, 1000000, n_samples)
            leverage = np.random.uniform(2, 20, n_samples)
            margin_ratio = np.random.uniform(0.25, 0.50, n_samples)

            X = np.column_stack([position_value, leverage, margin_ratio])

            initial_req = position_value / leverage
            maintenance_margin = initial_req * margin_ratio
            maintenance_margin += np.random.normal(0, 50, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=maintenance_margin,
                variable_names=["position", "leverage", "maint_ratio"],
                variable_descriptions={
                    "position": "Position value",
                    "leverage": "Leverage ratio",
                    "maint_ratio": "Maintenance margin ratio",
                },
                variable_units={
                    "position": "dimensionless",
                    "leverage": "dimensionless",
                    "maint_ratio": "dimensionless",
                },
                description="Maintenance margin - minimum equity to avoid margin call",
                validate_first=False,
            )

        elif formula_num == 18:  # Margin Call Level
            print("\n18. Margin Call Level")
            entry_price = np.random.uniform(100, 10000, n_samples)
            leverage = np.random.uniform(2, 20, n_samples)
            maint_margin_pct = np.random.uniform(0.03, 0.10, n_samples)

            X = np.column_stack([entry_price, leverage, maint_margin_pct])

            margin_call_price = entry_price * (1 - 1 / leverage + maint_margin_pct)
            margin_call_price += np.random.normal(0, 0.01, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=margin_call_price,
                variable_names=["entry_price", "leverage", "maint_margin"],
                variable_descriptions={
                    "entry_price": "Entry price",
                    "leverage": "Leverage ratio",
                    "maint_margin": "Maintenance margin %",
                },
                variable_units={
                    "entry_price": "dimensionless",
                    "leverage": "dimensionless",
                    "maint_margin": "dimensionless",
                },
                description="Margin call price - level that triggers margin call",
                validate_first=False,
            )

        elif formula_num == 19:  # Maximum Leverage
            print("\n19. Maximum Safe Leverage")
            account_equity = np.random.uniform(10000, 500000, n_samples)
            risk_tolerance = np.random.uniform(0.01, 0.05, n_samples)
            stop_loss_distance = np.random.uniform(0.02, 0.10, n_samples)

            X = np.column_stack([account_equity, risk_tolerance, stop_loss_distance])

            max_leverage = risk_tolerance / stop_loss_distance
            max_leverage = np.clip(max_leverage, 1, 50)
            max_leverage += np.random.normal(0, 0.01, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=max_leverage,
                variable_names=["equity", "risk_tolerance", "stop_distance"],
                variable_descriptions={
                    "equity": "Account equity",
                    "risk_tolerance": "Maximum risk per trade (% of equity)",
                    "stop_distance": "Stop loss distance (%)",
                },
                variable_units={
                    "equity": "dimensionless",
                    "risk_tolerance": "dimensionless",
                    "stop_distance": "dimensionless",
                },
                description="Maximum safe leverage based on risk management",
                validate_first=False,
            )

        elif formula_num == 20:  # Kelly Criterion
            print("\n20. Optimal Position Size (Kelly)")
            win_rate = np.random.uniform(0.4, 0.7, n_samples)
            avg_win = np.random.uniform(0.02, 0.10, n_samples)
            avg_loss = np.random.uniform(0.01, 0.05, n_samples)
            capital = np.random.uniform(10000, 500000, n_samples)

            X = np.column_stack([win_rate, avg_win, avg_loss, capital])

            win_loss_ratio = avg_win / avg_loss
            kelly_pct = win_rate - (1 - win_rate) / win_loss_ratio
            kelly_pct = np.clip(kelly_pct, 0, 0.25)
            position_size = capital * kelly_pct
            position_size += np.random.normal(0, 100, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=position_size,
                variable_names=["win_rate", "avg_win", "avg_loss", "capital"],
                variable_descriptions={
                    "win_rate": "Historical win rate",
                    "avg_win": "Average win size",
                    "avg_loss": "Average loss size",
                    "capital": "Available capital",
                },
                variable_units={
                    "win_rate": "dimensionless",
                    "avg_win": "dimensionless",
                    "avg_loss": "dimensionless",
                    "capital": "dimensionless",
                },
                description="Optimal position size using Kelly Criterion",
                validate_first=False,
            )

    def run_phase1(self, n_samples: int = 150):
        """Generate Phase 1: Advanced Risk Metrics (1-10)."""
        self.phase = "Phase 1"
        print("\n" + "#" * 70)
        print("# PHASE 1: Advanced Risk Metrics (10 Formulas)")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print(f"# Noise level: {self.noise_level}")
        print("#" * 70)

        for i in range(1, 11):
            try:
                print(f"\n{'='*70}")
                print(f"Processing Formula {i}/10")
                print(f"{'='*70}")
                self.generate_formula(i, n_samples)
                print(f"✅ Formula {i} completed")
            except Exception as e:
                print(f"❌ Error in Formula {i}: {str(e)}")
                import traceback

                traceback.print_exc()

    def run_phase2(self, n_samples: int = 120):
        """Generate Phase 2: Stress Testing (11-15)."""
        self.phase = "Phase 2"
        print("\n" + "#" * 70)
        print("# PHASE 2: Stress Testing Scenarios (5 Formulas)")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print("#" * 70)

        for i in range(11, 16):
            try:
                print(f"\n{'='*70}")
                print(f"Processing Formula {i}/15")
                print(f"{'='*70}")
                self.generate_formula(i, n_samples)
                print(f"✅ Formula {i} completed")
            except Exception as e:
                print(f"❌ Error in Formula {i}: {str(e)}")
                import traceback

                traceback.print_exc()

    def run_phase3(self, n_samples: int = 120):
        """Generate Phase 3: Margin & Leverage (16-20)."""
        self.phase = "Phase 3"
        print("\n" + "#" * 70)
        print("# PHASE 3: Margin & Leverage Formulas (5 Formulas)")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print("#" * 70)

        for i in range(16, 21):
            try:
                print(f"\n{'='*70}")
                print(f"Processing Formula {i}/20")
                print(f"{'='*70}")
                self.generate_formula(i, n_samples)
                print(f"✅ Formula {i} completed")
            except Exception as e:
                print(f"❌ Error in Formula {i}: {str(e)}")
                import traceback

                traceback.print_exc()

    def run_all_formulas(
        self, n_samples_p1: int = 150, n_samples_p2: int = 120, n_samples_p3: int = 120
    ):
        """Generate all 20 formulas in three phases."""
        self.run_phase1(n_samples_p1)
        self.run_phase2(n_samples_p2)
        self.run_phase3(n_samples_p3)

    def save_results(self, output_dir: str = "hypatiax/data/finance/risk"):
        """Save results to files."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_path = os.path.join(output_dir, f"risk_advanced_20_{timestamp}.json")
        csv_path = os.path.join(output_dir, f"risk_advanced_20_{timestamp}.csv")

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
        print("FINAL SUMMARY - ADVANCED RISK FORMULAS (20 Total)")
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

        results = self.system.get_results()
        if len(results) >= 15:
            print(f"\nPhase Breakdown:")
            print(f"  Phase 1 (Advanced Risk): Formulas 1-10")
            print(f"  Phase 2 (Stress Testing): Formulas 11-15")
            print(f"  Phase 3 (Margin & Leverage): Formulas 16-20")

        print("\n" + "-" * 70)
        print("Individual Formula Results:")
        print("-" * 70)

        for i, result in enumerate(results, 1):
            discovery = result.get("discovery", {})
            validation = result.get("validation", {})
            valid_symbol = "✅" if validation.get("valid") else "❌"

            if i <= 10:
                phase_label = "P1"
            elif i <= 15:
                phase_label = "P2"
            else:
                phase_label = "P3"

            print(f"\n{i}. [{phase_label}] {result.get('description', 'Unknown')}")
            print(
                f"   {valid_symbol} R2: {discovery.get('r2_score', 0):.4f} | "
                f"Valid: {validation.get('valid', False)} | "
                f"Score: {validation.get('total_score', 0):.1f}/100"
            )
            print(f"   Expression: {discovery.get('expression', 'N/A')[:80]}")

        print("\n" + "=" * 70)


def main():
    """Main execution function."""
    generator = AdvancedRiskGenerator(domain="risk", seed=42, noise_level=0.001)

    # Run all three phases
    generator.run_all_formulas(n_samples_p1=150, n_samples_p2=120, n_samples_p3=120)

    # Save results
    json_path, csv_path = generator.save_results()
    print(f"\n📁 Results saved:")
    print(f"   JSON: {json_path}")
    print(f"   CSV: {csv_path}")

    # Print summary
    generator.print_summary()


if __name__ == "__main__":
    main()
