"""
experiment_protocol_defi.py - ENHANCED
Fixes for Kelly criterion, better test case generation, improved metadata
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import json


class DeFiExperimentProtocol:
    """Enhanced DeFi experiment protocol with fixed formulas"""

    def __init__(self):
        self.domains = {
            "amm": self._generate_amm_tests,
            "risk_var": self._generate_var_tests,
            "liquidity": self._generate_liquidity_tests,
            "expected_shortfall": self._generate_es_tests,
            "liquidation": self._generate_liquidation_tests,
        }

    def get_all_domains(self) -> List[str]:
        """Get all available domains"""
        return list(self.domains.keys())

    def load_test_data(self, domain: str, num_samples: int = 100) -> List[Tuple]:
        """Load test data for a domain"""
        if domain not in self.domains:
            raise ValueError(f"Unknown domain: {domain}")
        return self.domains[domain](num_samples)

    # ========================================================================
    # AMM DOMAIN
    # ========================================================================

    def _generate_amm_tests(self, n: int) -> List[Tuple]:
        """AMM test cases"""
        tests = []

        # Test 1: Impermanent loss (EXTRAPOLATION TEST)
        np.random.seed(42)
        price_ratio = np.concatenate(
            [
                np.linspace(0.5, 1.5, n // 2),  # Training range
                np.linspace(1.6, 2.5, n // 2),  # Extrapolation range
            ]
        )
        np.random.shuffle(price_ratio)

        # Correct IL formula: 2*sqrt(r)/(1+r) - 1
        il = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1

        tests.append(
            (
                "Impermanent loss in constant product AMM (Uniswap V2)",
                price_ratio.reshape(-1, 1),
                il,
                ["price_ratio"],
                {
                    "domain": "amm",
                    "extrapolation_test": True,
                    "ground_truth": "2*sqrt(r)/(1+r) - 1",
                    "train_range": "0.5-1.5",
                    "test_range": "1.6-2.5",
                },
            )
        )

        # Test 2: IL Percentage
        price_ratio = np.linspace(0.5, 2.0, n)
        il_pct = (2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1) * 100

        tests.append(
            (
                "Impermanent loss percentage in AMM",
                price_ratio.reshape(-1, 1),
                il_pct,
                ["price_ratio"],
                {
                    "domain": "amm",
                    "ground_truth": "(2*sqrt(r)/(1+r) - 1) * 100",
                    "extrapolation_test": False,
                },
            )
        )

        # Test 3: Constant product - reserve Y
        reserve_x = np.linspace(100, 10000, n)
        invariant_k = np.random.uniform(1e6, 1e8, n)
        reserve_y = invariant_k / reserve_x

        tests.append(
            (
                "Constant product formula: reserve Y given reserve X and invariant k",
                np.column_stack([reserve_x, invariant_k]),
                reserve_y,
                ["reserve_x", "invariant_k"],
                {"domain": "amm", "ground_truth": "k / x", "extrapolation_test": False},
            )
        )

        # Test 4: Price impact
        reserve_x = np.linspace(10000, 100000, n)
        swap_amount = reserve_x * np.random.uniform(0.001, 0.1, n)
        price_impact = swap_amount / (reserve_x + swap_amount)

        tests.append(
            (
                "Price impact of swap in constant product AMM",
                np.column_stack([reserve_x, swap_amount]),
                price_impact,
                ["reserve_x", "swap_amount"],
                {
                    "domain": "amm",
                    "ground_truth": "dx / (x + dx)",
                    "extrapolation_test": False,
                },
            )
        )

        return tests

    # ========================================================================
    # RISK VAR DOMAIN
    # ========================================================================

    def _generate_var_tests(self, n: int) -> List[Tuple]:
        """Value at Risk test cases"""
        tests = []

        # Test 1: VaR 95% (EXTRAPOLATION TEST)
        np.random.seed(43)
        portfolio_value = np.linspace(10000, 1000000, n)
        daily_vol = np.concatenate(
            [
                np.linspace(0.01, 0.03, n // 2),  # Training
                np.linspace(0.035, 0.05, n // 2),  # Extrapolation
            ]
        )
        np.random.shuffle(daily_vol)

        z_95 = 1.645
        var_95 = portfolio_value * daily_vol * z_95

        tests.append(
            (
                "Parametric Value at Risk at 95% confidence (1-day)",
                np.column_stack([portfolio_value, daily_vol]),
                var_95,
                ["portfolio_value", "daily_volatility"],
                {
                    "domain": "risk_var",
                    "extrapolation_test": True,
                    "ground_truth": "portfolio_value * volatility * 1.645",
                    "constants": {"z_score_95": 1.645},
                    "train_range": "vol 0.01-0.03",
                    "test_range": "vol 0.035-0.05",
                },
            )
        )

        # Test 2: VaR 99%
        portfolio_value = np.linspace(10000, 1000000, n)
        daily_vol = np.linspace(0.01, 0.05, n)
        z_99 = 2.326
        var_99 = portfolio_value * daily_vol * z_99

        tests.append(
            (
                "Parametric Value at Risk at 99% confidence (1-day)",
                np.column_stack([portfolio_value, daily_vol]),
                var_99,
                ["portfolio_value", "daily_volatility"],
                {
                    "domain": "risk_var",
                    "ground_truth": "portfolio_value * volatility * 2.326",
                    "constants": {"z_score_99": 2.326},
                    "extrapolation_test": False,
                },
            )
        )

        # Test 3: Multi-day VaR
        var_1day = np.linspace(1000, 100000, n)
        time_horizon = np.random.choice([5, 10, 21, 30], n)
        var_multiday = var_1day * np.sqrt(time_horizon)

        tests.append(
            (
                "Multi-day Value at Risk using square root of time rule",
                np.column_stack([var_1day, time_horizon]),
                var_multiday,
                ["var_1day", "time_horizon_days"],
                {
                    "domain": "risk_var",
                    "ground_truth": "var_1day * sqrt(days)",
                    "extrapolation_test": False,
                },
            )
        )

        # Test 4: Portfolio VaR with correlation
        var_asset1 = np.linspace(5000, 50000, n)
        var_asset2 = np.linspace(3000, 30000, n)
        correlation = np.linspace(-0.5, 0.9, n)

        var_portfolio = np.sqrt(
            var_asset1**2 + var_asset2**2 + 2 * correlation * var_asset1 * var_asset2
        )

        tests.append(
            (
                "Portfolio VaR for two correlated assets",
                np.column_stack([var_asset1, var_asset2, correlation]),
                var_portfolio,
                ["var_asset1", "var_asset2", "correlation"],
                {
                    "domain": "risk_var",
                    "ground_truth": "sqrt(var1^2 + var2^2 + 2*rho*var1*var2)",
                    "extrapolation_test": False,
                },
            )
        )

        return tests

    # ========================================================================
    # LIQUIDITY DOMAIN - FIXED KELLY
    # ========================================================================

    def _generate_liquidity_tests(self, n: int) -> List[Tuple]:
        """Liquidity test cases with FIXED Kelly criterion"""
        tests = []

        # Test 1: FIXED Kelly Criterion (EXTRAPOLATION TEST)
        np.random.seed(44)
        expected_apy = np.concatenate(
            [
                np.linspace(0.05, 0.18, n // 2),  # Training
                np.linspace(0.22, 0.30, n // 2),  # Extrapolation
            ]
        )
        np.random.shuffle(expected_apy)

        il_risk = np.linspace(0.05, 0.25, n)

        # CORRECT Kelly formula: f* = min(μ / (λ * σ²), 1.0)
        # where λ = 2.0 (risk aversion)
        risk_aversion = 2.0
        f_star = expected_apy / (risk_aversion * il_risk**2)
        f_star = np.minimum(f_star, 1.0)  # Cap at 100%

        tests.append(
            (
                "Optimal LP position size using risk-adjusted Kelly criterion",
                np.column_stack([expected_apy, il_risk]),
                f_star,
                ["expected_fee_apy", "il_risk"],
                {
                    "domain": "liquidity",
                    "extrapolation_test": True,
                    "ground_truth": "min(μ / (2 * σ²), 1.0)",
                    "constants": {"risk_aversion": 2.0},
                    "train_range": "apy 0.05-0.18",
                    "test_range": "apy 0.22-0.30",
                    "note": "Risk-adjusted Kelly with cap at 100%",
                },
            )
        )

        # Test 2: LP fee earnings
        liquidity_provided = np.linspace(10000, 1000000, n)
        pool_liquidity = liquidity_provided * np.random.uniform(10, 100, n)
        total_fees = np.random.uniform(1000, 50000, n)

        fee_share = (liquidity_provided / pool_liquidity) * total_fees

        tests.append(
            (
                "LP fee earnings based on liquidity share",
                np.column_stack([liquidity_provided, pool_liquidity, total_fees]),
                fee_share,
                ["liquidity_provided", "pool_liquidity", "total_fees"],
                {
                    "domain": "liquidity",
                    "ground_truth": "(liq_provided / pool_liq) * total_fees",
                    "extrapolation_test": False,
                },
            )
        )

        # Test 3: Capital efficiency (concentrated liquidity)
        price_lower = np.linspace(1800, 2000, n)
        price_upper = np.linspace(2200, 2400, n)
        price_current = np.linspace(1900, 2300, n)

        # Simplified capital efficiency
        efficiency = price_upper / (price_upper - price_lower)

        tests.append(
            (
                "Capital efficiency multiplier for concentrated liquidity position",
                np.column_stack([price_lower, price_upper, price_current]),
                efficiency,
                ["price_lower", "price_upper", "price_current"],
                {
                    "domain": "liquidity",
                    "ground_truth": "P_upper / (P_upper - P_lower)",
                    "extrapolation_test": False,
                    "note": "Simplified efficiency measure",
                },
            )
        )

        # Test 4: APY from APR
        apr = np.linspace(0.05, 0.50, n)
        apy = (1 + apr / 365) ** 365 - 1

        tests.append(
            (
                "APY calculation from APR with daily compounding",
                apr.reshape(-1, 1),
                apy,
                ["apr"],
                {
                    "domain": "liquidity",
                    "ground_truth": "(1 + apr/365)^365 - 1",
                    "extrapolation_test": False,
                },
            )
        )

        return tests

    # ========================================================================
    # EXPECTED SHORTFALL DOMAIN
    # ========================================================================

    def _generate_es_tests(self, n: int) -> List[Tuple]:
        """Expected Shortfall test cases"""
        tests = []

        # Test 1: ES 95% (EXTRAPOLATION TEST)
        np.random.seed(45)
        portfolio_value = np.linspace(10000, 1000000, n)
        daily_vol = np.concatenate(
            [np.linspace(0.01, 0.03, n // 2), np.linspace(0.035, 0.05, n // 2)]
        )
        np.random.shuffle(daily_vol)

        # ES = portfolio * vol * 2.063 (for 95% confidence, normal dist)
        es_95 = portfolio_value * daily_vol * 2.063

        tests.append(
            (
                "Expected Shortfall (CVaR) at 95% confidence for normal returns",
                np.column_stack([portfolio_value, daily_vol]),
                es_95,
                ["portfolio_value", "daily_volatility"],
                {
                    "domain": "expected_shortfall",
                    "extrapolation_test": True,
                    "ground_truth": "portfolio * volatility * 2.063",
                    "constants": {"es_multiplier_95": 2.063},
                    "train_range": "vol 0.01-0.03",
                    "test_range": "vol 0.035-0.05",
                },
            )
        )

        # Test 2: ES 99%
        portfolio_value = np.linspace(10000, 1000000, n)
        daily_vol = np.linspace(0.01, 0.05, n)
        es_99 = portfolio_value * daily_vol * 2.665

        tests.append(
            (
                "Expected Shortfall (CVaR) at 99% confidence for normal returns",
                np.column_stack([portfolio_value, daily_vol]),
                es_99,
                ["portfolio_value", "daily_volatility"],
                {
                    "domain": "expected_shortfall",
                    "ground_truth": "portfolio * volatility * 2.665",
                    "constants": {"es_multiplier_99": 2.665},
                    "extrapolation_test": False,
                },
            )
        )

        # Test 3: ES from VaR
        var_95 = np.linspace(5000, 100000, n)
        es_from_var = var_95 * 1.254  # Tail multiplier for normal dist

        tests.append(
            (
                "Expected Shortfall from VaR using tail risk multiplier",
                var_95.reshape(-1, 1),
                es_from_var,
                ["var_95"],
                {
                    "domain": "expected_shortfall",
                    "ground_truth": "var_95 * 1.254",
                    "constants": {"tail_multiplier": 1.254},
                    "extrapolation_test": False,
                },
            )
        )

        # Test 4: Portfolio ES with correlation
        pos1_es = np.linspace(10000, 100000, n)
        pos2_es = np.linspace(5000, 50000, n)
        correlation = np.linspace(-0.3, 0.8, n)

        # Simplified portfolio ES (linear with correlation term)
        portfolio_es = pos1_es + pos2_es + correlation * np.sqrt(pos1_es * pos2_es)

        tests.append(
            (
                "Portfolio Expected Shortfall for correlated positions",
                np.column_stack([pos1_es, pos2_es, correlation]),
                portfolio_es,
                ["position1_es", "position2_es", "correlation"],
                {
                    "domain": "expected_shortfall",
                    "ground_truth": "ES1 + ES2 + ρ*sqrt(ES1*ES2)",
                    "extrapolation_test": False,
                    "note": "Simplified correlation adjustment",
                },
            )
        )

        return tests

    # ========================================================================
    # LIQUIDATION DOMAIN - FIXED
    # ========================================================================

    def _generate_liquidation_tests(self, n: int) -> List[Tuple]:
        """Liquidation test cases with CORRECT formulas"""
        tests = []

        # Test 1: Liquidation price LONG (EXTRAPOLATION TEST)
        np.random.seed(46)
        entry_price = np.linspace(30000, 50000, n)
        leverage = np.concatenate(
            [
                np.linspace(2, 5, n // 2),  # Training
                np.linspace(7, 10, n // 2),  # Extrapolation
            ]
        )
        np.random.shuffle(leverage)

        # CORRECT: P_liq = P_entry * (1 - 1/(L * 0.8))
        maintenance_margin = 0.8
        liq_price_long = entry_price * (1 - 1 / (leverage * maintenance_margin))

        tests.append(
            (
                "Liquidation price for leveraged long position",
                np.column_stack([entry_price, leverage]),
                liq_price_long,
                ["entry_price", "leverage"],
                {
                    "domain": "liquidation",
                    "extrapolation_test": True,
                    "ground_truth": "entry_price * (1 - 1/(leverage * 0.8))",
                    "constants": {"maintenance_margin": 0.8},
                    "train_range": "leverage 2-5",
                    "test_range": "leverage 7-10",
                },
            )
        )

        # Test 2: Liquidation price SHORT
        entry_price = np.linspace(30000, 50000, n)
        leverage = np.linspace(2, 10, n)

        # CORRECT: P_liq = P_entry * (1 + 1/(L * 0.8))
        liq_price_short = entry_price * (1 + 1 / (leverage * maintenance_margin))

        tests.append(
            (
                "Liquidation price for leveraged short position",
                np.column_stack([entry_price, leverage]),
                liq_price_short,
                ["entry_price", "leverage"],
                {
                    "domain": "liquidation",
                    "ground_truth": "entry_price * (1 + 1/(leverage * 0.8))",
                    "constants": {"maintenance_margin": 0.8},
                    "extrapolation_test": False,
                },
            )
        )

        # Test 3: Maximum safe leverage
        entry_price = np.linspace(30000, 50000, n)
        acceptable_loss_pct = np.linspace(0.05, 0.20, n)

        # CORRECT: L_max = 1 / (loss * 0.8)
        max_leverage = 1 / (acceptable_loss_pct * maintenance_margin)

        tests.append(
            (
                "Maximum safe leverage for given acceptable loss tolerance",
                np.column_stack([entry_price, acceptable_loss_pct]),
                max_leverage,
                ["entry_price", "acceptable_loss_pct"],
                {
                    "domain": "liquidation",
                    "ground_truth": "1 / (loss_pct * 0.8)",
                    "constants": {"maintenance_margin": 0.8},
                    "extrapolation_test": False,
                    "note": "entry_price not used in calculation",
                },
            )
        )

        # Test 4: Required collateral
        position_size = np.linspace(10000, 1000000, n)
        leverage = np.linspace(2, 10, n)

        # Simple inverse relationship
        collateral = position_size / leverage

        tests.append(
            (
                "Required collateral for leveraged position",
                np.column_stack([position_size, leverage]),
                collateral,
                ["position_size", "leverage"],
                {
                    "domain": "liquidation",
                    "ground_truth": "position_size / leverage",
                    "extrapolation_test": False,
                },
            )
        )

        return tests

    # ========================================================================
    # REPORTING
    # ========================================================================

    def generate_experiment_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive experiment report"""

        successful = [
            r for r in results if r.get("evaluation", {}).get("success", False)
        ]

        r2_scores = [
            r["evaluation"]["r2"] for r in successful if "r2" in r.get("evaluation", {})
        ]

        # By domain
        by_domain = {}
        for r in results:
            domain = r.get("domain", r.get("metadata", {}).get("domain", "unknown"))
            if domain not in by_domain:
                by_domain[domain] = {"total": 0, "successful": 0, "r2_scores": []}

            by_domain[domain]["total"] += 1
            if r.get("evaluation", {}).get("success"):
                by_domain[domain]["successful"] += 1
                if "r2" in r.get("evaluation", {}):
                    by_domain[domain]["r2_scores"].append(r["evaluation"]["r2"])

        # Calculate domain stats
        for domain in by_domain:
            scores = by_domain[domain]["r2_scores"]
            by_domain[domain]["mean_r2"] = np.mean(scores) if scores else None
            by_domain[domain]["median_r2"] = np.median(scores) if scores else None

        # Extrapolation tests
        extrap_tests = [
            {
                "description": r.get("description", "N/A"),
                "domain": r.get("domain", "N/A"),
                "r2": r.get("evaluation", {}).get("r2"),
                "success": r.get("evaluation", {}).get("success", False),
            }
            for r in results
            if r.get("metadata", {}).get("extrapolation_test", False)
        ]

        return {
            "overall": {
                "total_cases": len(results),
                "successful": len(successful),
                "success_rate": len(successful) / len(results) if results else 0,
                "mean_r2": np.mean(r2_scores) if r2_scores else None,
                "median_r2": np.median(r2_scores) if r2_scores else None,
                "std_r2": np.std(r2_scores) if r2_scores else None,
            },
            "by_domain": by_domain,
            "extrapolation_tests": extrap_tests,
        }
