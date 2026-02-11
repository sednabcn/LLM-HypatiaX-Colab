"""
DeFi & Risk Management Experiment Protocol for Pure LLM Formula Discovery
==========================================================================

Domains:
1. Automated Market Makers (AMM) - Impermanent Loss
2. Risk Management - Value at Risk (VaR)
3. Liquidity Provision - Optimal LP Position Sizing
4. Risk Metrics - Expected Shortfall (CVaR)
5. Leveraged Trading - Liquidation Price Calculation
"""

import numpy as np
from typing import List, Tuple, Dict
import json
from scipy import stats


class DeFiExperimentProtocol:
    """
    Experimental protocol for evaluating pure LLM formula discovery in DeFi and quantitative finance.
    """

    @staticmethod
    def get_all_domains() -> List[str]:
        """Return list of all experimental domains."""
        return ["amm", "risk_var", "liquidity", "expected_shortfall", "liquidation"]

    @staticmethod
    def load_test_data(
        domain: str, num_samples: int = 100
    ) -> List[Tuple[str, np.ndarray, np.ndarray, List[str], Dict]]:
        """
        Load test data for evaluation across DeFi and risk management domains.

        Args:
            domain: Domain to load data for
            num_samples: Number of samples to generate

        Returns:
            List of (description, X, y, variable_names, metadata) tuples
        """
        np.random.seed(42)  # For reproducibility
        test_cases = []

        if domain == "amm":
            # ==================== AUTOMATED MARKET MAKER (AMM) DOMAIN ====================

            # 1. Impermanent Loss (CRITICAL TEST CASE)
            # IL = 2*sqrt(price_ratio) / (1 + price_ratio) - 1
            price_ratio = np.random.uniform(0.5, 2.0, num_samples)  # P1/P0
            X = price_ratio.reshape(-1, 1)
            y = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
            test_cases.append(
                (
                    "Impermanent loss in constant product AMM (Uniswap V2)",
                    X,
                    y,
                    ["price_ratio"],
                    {
                        "difficulty": "hard",
                        "formula_type": "algebraic_with_sqrt",
                        "ground_truth": "IL = 2√r/(1+r) - 1",
                        "domain_specific": True,
                        "constants": {},
                        "units": {"price_ratio": "dimensionless", "IL": "fraction"},
                        "extrapolation_test": True,
                        "description": "Price ratio r = P_final/P_initial",
                    },
                )
            )

            # 2. Impermanent Loss (percentage form)
            price_ratio = np.random.uniform(0.5, 2.0, num_samples)
            X = price_ratio.reshape(-1, 1)
            y = (2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1) * 100
            test_cases.append(
                (
                    "Impermanent loss percentage in AMM",
                    X,
                    y,
                    ["price_ratio"],
                    {
                        "difficulty": "hard",
                        "formula_type": "algebraic_with_sqrt",
                        "ground_truth": "IL% = (2√r/(1+r) - 1) × 100",
                        "domain_specific": True,
                        "constants": {},
                        "units": {"price_ratio": "dimensionless", "IL": "percent"},
                    },
                )
            )

            # 3. Constant Product Invariant
            # x * y = k, solving for y given x and k
            reserve_x = np.random.uniform(1000, 100000, num_samples)
            k = np.random.uniform(1e6, 1e9, num_samples)
            X = np.column_stack([reserve_x, k])
            y = k / reserve_x
            test_cases.append(
                (
                    "Constant product formula: reserve Y given reserve X and invariant k",
                    X,
                    y,
                    ["reserve_x", "invariant_k"],
                    {
                        "difficulty": "easy",
                        "formula_type": "algebraic",
                        "ground_truth": "y = k/x",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "reserve_x": "tokens",
                            "invariant_k": "tokens²",
                            "reserve_y": "tokens",
                        },
                    },
                )
            )

            # 4. Price Impact in AMM
            # ΔP/P = Δx/(x + Δx)
            reserve_x = np.random.uniform(10000, 100000, num_samples)
            delta_x = np.random.uniform(100, 5000, num_samples)
            X = np.column_stack([reserve_x, delta_x])
            y = delta_x / (reserve_x + delta_x)
            test_cases.append(
                (
                    "Price impact of swap in constant product AMM",
                    X,
                    y,
                    ["reserve_x", "swap_amount"],
                    {
                        "difficulty": "easy",
                        "formula_type": "algebraic",
                        "ground_truth": "price_impact = Δx/(x + Δx)",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "reserve_x": "tokens",
                            "swap_amount": "tokens",
                            "price_impact": "fraction",
                        },
                    },
                )
            )

        elif domain == "risk_var":
            # ==================== VALUE AT RISK (VaR) DOMAIN ====================

            # 1. Parametric VaR (Normal Distribution) - 95% confidence
            portfolio_value = np.random.uniform(10000, 1000000, num_samples)
            daily_volatility = np.random.uniform(
                0.01, 0.05, num_samples
            )  # 1-5% daily vol
            z_score = 1.645  # 95% confidence level
            X = np.column_stack([portfolio_value, daily_volatility])
            y = portfolio_value * daily_volatility * z_score
            test_cases.append(
                (
                    "Parametric Value at Risk at 95% confidence (1-day)",
                    X,
                    y,
                    ["portfolio_value", "daily_volatility"],
                    {
                        "difficulty": "easy",
                        "formula_type": "linear",
                        "ground_truth": "VaR = V × σ × z",
                        "domain_specific": True,
                        "constants": {"z_score": 1.645},
                        "units": {
                            "portfolio_value": "USD",
                            "daily_volatility": "fraction",
                            "VaR": "USD",
                        },
                        "extrapolation_test": True,
                        "description": "z = 1.645 for 95% confidence",
                    },
                )
            )

            # 2. Parametric VaR (Normal Distribution) - 99% confidence
            portfolio_value = np.random.uniform(10000, 1000000, num_samples)
            daily_volatility = np.random.uniform(0.01, 0.05, num_samples)
            z_score = 2.326  # 99% confidence level
            X = np.column_stack([portfolio_value, daily_volatility])
            y = portfolio_value * daily_volatility * z_score
            test_cases.append(
                (
                    "Parametric Value at Risk at 99% confidence (1-day)",
                    X,
                    y,
                    ["portfolio_value", "daily_volatility"],
                    {
                        "difficulty": "easy",
                        "formula_type": "linear",
                        "ground_truth": "VaR = V × σ × z",
                        "domain_specific": True,
                        "constants": {"z_score": 2.326},
                        "units": {
                            "portfolio_value": "USD",
                            "daily_volatility": "fraction",
                            "VaR": "USD",
                        },
                        "description": "z = 2.326 for 99% confidence",
                    },
                )
            )

            # 3. Multi-day VaR (square root of time rule)
            var_1day = np.random.uniform(1000, 50000, num_samples)
            time_horizon = np.random.uniform(1, 30, num_samples)  # days
            X = np.column_stack([var_1day, time_horizon])
            y = var_1day * np.sqrt(time_horizon)
            test_cases.append(
                (
                    "Multi-day Value at Risk using square root of time rule",
                    X,
                    y,
                    ["var_1day", "time_horizon_days"],
                    {
                        "difficulty": "easy",
                        "formula_type": "power_law",
                        "ground_truth": "VaR_T = VaR_1 × √T",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "var_1day": "USD",
                            "time_horizon_days": "days",
                            "VaR": "USD",
                        },
                    },
                )
            )

            # 4. Portfolio VaR with correlation (2 assets)
            var_asset1 = np.random.uniform(5000, 50000, num_samples)
            var_asset2 = np.random.uniform(5000, 50000, num_samples)
            correlation = np.random.uniform(-0.5, 0.9, num_samples)
            X = np.column_stack([var_asset1, var_asset2, correlation])
            y = np.sqrt(
                var_asset1**2
                + var_asset2**2
                + 2 * correlation * var_asset1 * var_asset2
            )
            test_cases.append(
                (
                    "Portfolio VaR for two correlated assets",
                    X,
                    y,
                    ["var_asset1", "var_asset2", "correlation"],
                    {
                        "difficulty": "medium",
                        "formula_type": "algebraic_with_sqrt",
                        "ground_truth": "VaR_p = √(VaR₁² + VaR₂² + 2ρVaR₁VaR₂)",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "var_asset1": "USD",
                            "var_asset2": "USD",
                            "correlation": "dimensionless",
                            "VaR_portfolio": "USD",
                        },
                    },
                )
            )

        elif domain == "liquidity":
            # ==================== LIQUIDITY PROVISION DOMAIN ====================

            # 1. Optimal LP position size (Kelly Criterion variant)
            expected_fee_apy = np.random.uniform(0.05, 0.30, num_samples)  # 5-30% APY
            il_risk = np.random.uniform(0.02, 0.15, num_samples)  # 2-15% IL risk
            risk_aversion = 2.0  # risk aversion coefficient
            X = np.column_stack([expected_fee_apy, il_risk])
            y = expected_fee_apy / (risk_aversion * il_risk**2)
            # Cap at 1.0 (100% of capital)
            y = np.minimum(y, 1.0)
            test_cases.append(
                (
                    "Optimal LP position size using risk-adjusted Kelly criterion",
                    X,
                    y,
                    ["expected_fee_apy", "il_risk"],
                    {
                        "difficulty": "medium",
                        "formula_type": "algebraic",
                        "ground_truth": "f* = min(μ/(λσ²), 1)",
                        "domain_specific": True,
                        "constants": {"risk_aversion": 2.0},
                        "units": {
                            "expected_fee_apy": "fraction",
                            "il_risk": "fraction",
                            "position_size": "fraction",
                        },
                        "extrapolation_test": True,
                        "description": "λ = 2.0 (risk aversion), capped at 1.0",
                    },
                )
            )

            # 2. LP fee earnings (simple)
            liquidity_provided = np.random.uniform(10000, 1000000, num_samples)
            pool_liquidity = np.random.uniform(1e6, 1e8, num_samples)
            total_fees = np.random.uniform(100, 50000, num_samples)
            X = np.column_stack([liquidity_provided, pool_liquidity, total_fees])
            y = (liquidity_provided / pool_liquidity) * total_fees
            test_cases.append(
                (
                    "LP fee earnings based on liquidity share",
                    X,
                    y,
                    ["liquidity_provided", "pool_liquidity", "total_fees"],
                    {
                        "difficulty": "easy",
                        "formula_type": "algebraic",
                        "ground_truth": "fees = (L_user/L_total) × F",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "liquidity_provided": "USD",
                            "pool_liquidity": "USD",
                            "total_fees": "USD",
                            "user_fees": "USD",
                        },
                    },
                )
            )

            # 3. Concentrated liquidity capital efficiency (Uniswap V3)
            price_lower = np.random.uniform(1500, 1800, num_samples)
            price_upper = np.random.uniform(2000, 2500, num_samples)
            price_current = np.random.uniform(1800, 2000, num_samples)
            X = np.column_stack([price_lower, price_upper, price_current])
            # Simplified capital efficiency multiplier
            price_range = price_upper - price_lower
            full_range = (
                price_upper  # assuming price_lower near 0 for full range comparison
            )
            y = full_range / price_range
            test_cases.append(
                (
                    "Capital efficiency multiplier for concentrated liquidity position",
                    X,
                    y,
                    ["price_lower", "price_upper", "price_current"],
                    {
                        "difficulty": "medium",
                        "formula_type": "algebraic",
                        "ground_truth": "efficiency = P_u/(P_u - P_l)",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "price_lower": "USD",
                            "price_upper": "USD",
                            "price_current": "USD",
                            "efficiency": "multiplier",
                        },
                    },
                )
            )

            # 4. Annual Percentage Yield (APY) from APR with compounding
            apr = np.random.uniform(0.05, 0.50, num_samples)  # 5-50% APR
            compounds_per_year = 365  # daily compounding
            X = apr.reshape(-1, 1)
            y = (1 + apr / compounds_per_year) ** compounds_per_year - 1
            test_cases.append(
                (
                    "APY calculation from APR with daily compounding",
                    X,
                    y,
                    ["apr"],
                    {
                        "difficulty": "easy",
                        "formula_type": "exponential",
                        "ground_truth": "APY = (1 + APR/n)ⁿ - 1",
                        "domain_specific": False,
                        "constants": {"compounds_per_year": 365},
                        "units": {"apr": "fraction", "apy": "fraction"},
                        "description": "n = 365 for daily compounding",
                    },
                )
            )

        elif domain == "expected_shortfall":
            # ==================== EXPECTED SHORTFALL (CVaR) DOMAIN ====================

            # 1. Expected Shortfall at 95% confidence (Normal distribution)
            portfolio_value = np.random.uniform(10000, 1000000, num_samples)
            daily_volatility = np.random.uniform(0.01, 0.05, num_samples)
            # ES = V × σ × φ(z)/α where φ is PDF, α is confidence level
            # For 95% confidence: ES ≈ V × σ × 2.063
            multiplier = 2.063  # derived from normal distribution
            X = np.column_stack([portfolio_value, daily_volatility])
            y = portfolio_value * daily_volatility * multiplier
            test_cases.append(
                (
                    "Expected Shortfall (CVaR) at 95% confidence for normal returns",
                    X,
                    y,
                    ["portfolio_value", "daily_volatility"],
                    {
                        "difficulty": "medium",
                        "formula_type": "linear",
                        "ground_truth": "ES = V × σ × m",
                        "domain_specific": True,
                        "constants": {"multiplier": 2.063},
                        "units": {
                            "portfolio_value": "USD",
                            "daily_volatility": "fraction",
                            "ES": "USD",
                        },
                        "extrapolation_test": True,
                        "description": "m = 2.063 for 95% confidence (normal)",
                    },
                )
            )

            # 2. Expected Shortfall at 99% confidence
            portfolio_value = np.random.uniform(10000, 1000000, num_samples)
            daily_volatility = np.random.uniform(0.01, 0.05, num_samples)
            multiplier = 2.665  # for 99% confidence
            X = np.column_stack([portfolio_value, daily_volatility])
            y = portfolio_value * daily_volatility * multiplier
            test_cases.append(
                (
                    "Expected Shortfall (CVaR) at 99% confidence for normal returns",
                    X,
                    y,
                    ["portfolio_value", "daily_volatility"],
                    {
                        "difficulty": "medium",
                        "formula_type": "linear",
                        "ground_truth": "ES = V × σ × m",
                        "domain_specific": True,
                        "constants": {"multiplier": 2.665},
                        "units": {
                            "portfolio_value": "USD",
                            "daily_volatility": "fraction",
                            "ES": "USD",
                        },
                        "description": "m = 2.665 for 99% confidence (normal)",
                    },
                )
            )

            # 3. ES/VaR ratio (tail risk measure)
            var_95 = np.random.uniform(5000, 100000, num_samples)
            # For normal distribution, ES/VaR ratio at 95% is approximately 1.25
            ratio = 1.25
            X = var_95.reshape(-1, 1)
            y = var_95 * ratio
            test_cases.append(
                (
                    "Expected Shortfall from VaR using tail risk multiplier",
                    X,
                    y,
                    ["var_95"],
                    {
                        "difficulty": "easy",
                        "formula_type": "linear",
                        "ground_truth": "ES = VaR × r",
                        "domain_specific": True,
                        "constants": {"ratio": 1.25},
                        "units": {"var_95": "USD", "ES": "USD"},
                        "description": "r = 1.25 for normal distribution at 95%",
                    },
                )
            )

            # 4. Portfolio ES with multiple positions
            position1_es = np.random.uniform(5000, 50000, num_samples)
            position2_es = np.random.uniform(5000, 50000, num_samples)
            correlation = np.random.uniform(-0.5, 0.9, num_samples)
            X = np.column_stack([position1_es, position2_es, correlation])
            # Simplified: linear combination adjusted by correlation
            y = (
                position1_es
                + position2_es
                + correlation * np.sqrt(position1_es * position2_es)
            )
            test_cases.append(
                (
                    "Portfolio Expected Shortfall for correlated positions",
                    X,
                    y,
                    ["position1_es", "position2_es", "correlation"],
                    {
                        "difficulty": "medium",
                        "formula_type": "algebraic_with_sqrt",
                        "ground_truth": "ES_p = ES₁ + ES₂ + ρ√(ES₁ES₂)",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "position1_es": "USD",
                            "position2_es": "USD",
                            "correlation": "dimensionless",
                            "ES_portfolio": "USD",
                        },
                    },
                )
            )

        elif domain == "liquidation":
            # ==================== LIQUIDATION PRICE DOMAIN ====================

            # 1. Liquidation price for long position (CRITICAL TEST CASE)
            # P_liq = P_entry × (1 - 1/(leverage × (1 - liq_threshold)))
            entry_price = np.random.uniform(20000, 60000, num_samples)
            leverage = np.random.uniform(2, 10, num_samples)
            liquidation_threshold = 0.8  # 80% maintenance margin
            X = np.column_stack([entry_price, leverage])
            y = entry_price * (1 - 1 / (leverage * liquidation_threshold))
            test_cases.append(
                (
                    "Liquidation price for leveraged long position",
                    X,
                    y,
                    ["entry_price", "leverage"],
                    {
                        "difficulty": "hard",
                        "formula_type": "algebraic",
                        "ground_truth": "P_liq = P_e × (1 - 1/(L×m))",
                        "domain_specific": True,
                        "constants": {"liquidation_threshold": 0.8},
                        "units": {
                            "entry_price": "USD",
                            "leverage": "multiplier",
                            "liquidation_price": "USD",
                        },
                        "extrapolation_test": True,
                        "description": "m = 0.8 (80% maintenance margin)",
                    },
                )
            )

            # 2. Liquidation price for short position
            entry_price = np.random.uniform(20000, 60000, num_samples)
            leverage = np.random.uniform(2, 10, num_samples)
            liquidation_threshold = 0.8
            X = np.column_stack([entry_price, leverage])
            y = entry_price * (1 + 1 / (leverage * liquidation_threshold))
            test_cases.append(
                (
                    "Liquidation price for leveraged short position",
                    X,
                    y,
                    ["entry_price", "leverage"],
                    {
                        "difficulty": "hard",
                        "formula_type": "algebraic",
                        "ground_truth": "P_liq = P_e × (1 + 1/(L×m))",
                        "domain_specific": True,
                        "constants": {"liquidation_threshold": 0.8},
                        "units": {
                            "entry_price": "USD",
                            "leverage": "multiplier",
                            "liquidation_price": "USD",
                        },
                        "description": "m = 0.8 (80% maintenance margin)",
                    },
                )
            )

            # 3. Maximum safe leverage given acceptable drawdown
            entry_price = np.random.uniform(20000, 60000, num_samples)
            acceptable_loss = np.random.uniform(
                0.05, 0.20, num_samples
            )  # 5-20% loss acceptable
            liquidation_threshold = 0.8
            X = np.column_stack([entry_price, acceptable_loss])
            y = 1 / (acceptable_loss * liquidation_threshold)
            test_cases.append(
                (
                    "Maximum safe leverage for given acceptable loss tolerance",
                    X,
                    y,
                    ["entry_price", "acceptable_loss_pct"],
                    {
                        "difficulty": "medium",
                        "formula_type": "algebraic",
                        "ground_truth": "L_max = 1/(loss×m)",
                        "domain_specific": True,
                        "constants": {"liquidation_threshold": 0.8},
                        "units": {
                            "entry_price": "USD",
                            "acceptable_loss_pct": "fraction",
                            "max_leverage": "multiplier",
                        },
                    },
                )
            )

            # 4. Collateral requirement for leveraged position
            position_size = np.random.uniform(10000, 100000, num_samples)
            leverage = np.random.uniform(2, 10, num_samples)
            X = np.column_stack([position_size, leverage])
            y = position_size / leverage
            test_cases.append(
                (
                    "Required collateral for leveraged position",
                    X,
                    y,
                    ["position_size", "leverage"],
                    {
                        "difficulty": "easy",
                        "formula_type": "algebraic",
                        "ground_truth": "collateral = position_size/leverage",
                        "domain_specific": True,
                        "constants": {},
                        "units": {
                            "position_size": "USD",
                            "leverage": "multiplier",
                            "collateral": "USD",
                        },
                    },
                )
            )

        return test_cases

    @staticmethod
    def get_domain_description(domain: str) -> str:
        """Get detailed description of each domain."""
        descriptions = {
            "amm": "Automated Market Makers - impermanent loss, price impact, constant product",
            "risk_var": "Value at Risk - parametric VaR, multi-day scaling, portfolio VaR",
            "liquidity": "Liquidity Provision - optimal sizing, fee earnings, capital efficiency",
            "expected_shortfall": "Expected Shortfall (CVaR) - tail risk, ES/VaR ratio, portfolio ES",
            "liquidation": "Liquidation Mechanics - liquidation price, max leverage, collateral",
        }
        return descriptions.get(domain, "Unknown domain")

    @staticmethod
    def generate_experiment_report(results: List[Dict]) -> Dict:
        """
        Generate comprehensive experiment report with analysis across domains.

        Args:
            results: List of experiment results

        Returns:
            Dictionary containing detailed analysis
        """
        report = {
            "overall": {},
            "by_domain": {},
            "by_difficulty": {},
            "by_formula_type": {},
            "extrapolation_tests": [],
        }

        # Overall statistics
        total = len(results)
        successful = sum(
            1 for r in results if r.get("evaluation", {}).get("success", False)
        )

        report["overall"]["total_cases"] = total
        report["overall"]["successful"] = successful
        report["overall"]["success_rate"] = successful / total if total > 0 else 0

        # R² statistics for successful cases
        r2_scores = []
        for r in results:
            eval_dict = r.get("evaluation", {})
            if eval_dict.get("success", False) and "r2" in eval_dict:
                r2_scores.append(eval_dict["r2"])

        if r2_scores:
            report["overall"]["mean_r2"] = float(np.mean(r2_scores))
            report["overall"]["median_r2"] = float(np.median(r2_scores))
            report["overall"]["std_r2"] = float(np.std(r2_scores))
            report["overall"]["min_r2"] = float(np.min(r2_scores))
            report["overall"]["max_r2"] = float(np.max(r2_scores))

        # By domain
        domains = set(r["domain"] for r in results)
        for domain in domains:
            domain_results = [r for r in results if r["domain"] == domain]
            domain_successful = sum(
                1
                for r in domain_results
                if r.get("evaluation", {}).get("success", False)
            )
            domain_r2 = [
                r["evaluation"]["r2"]
                for r in domain_results
                if r.get("evaluation", {}).get("success", False)
                and "r2" in r.get("evaluation", {})
            ]

            report["by_domain"][domain] = {
                "total": len(domain_results),
                "successful": domain_successful,
                "success_rate": domain_successful / len(domain_results)
                if len(domain_results) > 0
                else 0,
                "mean_r2": float(np.mean(domain_r2)) if domain_r2 else None,
            }

        # Track extrapolation test cases
        for r in results:
            desc_lower = r.get("description", "").lower()
            if any(
                keyword in desc_lower
                for keyword in [
                    "impermanent loss",
                    "liquidation price",
                    "optimal lp",
                    "expected shortfall at 95%",
                    "value at risk at 95%",
                ]
            ):
                report["extrapolation_tests"].append(
                    {
                        "description": r.get("description"),
                        "domain": r.get("domain"),
                        "r2": r.get("evaluation", {}).get("r2"),
                        "rmse": r.get("evaluation", {}).get("rmse"),
                        "success": r.get("evaluation", {}).get("success", False),
                    }
                )

        return report

    @staticmethod
    def save_protocol_documentation(
        filepath: str = "docs/experiment_protocol_defi.json",
    ):
        """Save complete protocol documentation."""
        protocol_doc = {
            "title": "Pure LLM Formula Discovery - DeFi and Risk Management",
            "version": "1.0",
            "date": "2025-01-20",
            "focus": "Impermanent Loss, VaR, Liquidation Price, Expected Shortfall, LP Optimization",
            "domains": {},
            "methodology": {
                "approach": "Pure LLM without symbolic regression",
                "model": "Claude Sonnet 4 (claude-sonnet-4-20250514)",
                "evaluation_metrics": ["R²", "RMSE", "MAE", "MSE"],
                "sample_size": 100,
                "extrapolation": "Test on IL, VaR 95%, liquidation price",
            },
        }

        for domain in DeFiExperimentProtocol.get_all_domains():
            test_cases = DeFiExperimentProtocol.load_test_data(domain, num_samples=10)
            protocol_doc["domains"][domain] = {
                "description": DeFiExperimentProtocol.get_domain_description(domain),
                "num_test_cases": len(test_cases),
                "test_cases": [
                    {
                        "description": desc,
                        "variables": vars,
                        "difficulty": meta["difficulty"],
                        "formula_type": meta["formula_type"],
                        "ground_truth": meta["ground_truth"],
                        "extrapolation_test": meta.get("extrapolation_test", False),
                    }
                    for desc, _, _, vars, meta in test_cases
                ],
            }

        import os

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(protocol_doc, f, indent=2)

        print(f"Protocol documentation saved to: {filepath}")
        return protocol_doc


# Example usage
if __name__ == "__main__":
    protocol = DeFiExperimentProtocol()

    # Print protocol overview
    print("=" * 80)
    print("DEFI & RISK MANAGEMENT EXPERIMENT PROTOCOL".center(80))
    print("Pure LLM Formula Discovery - Quantitative Finance".center(80))
    print("=" * 80)

    print("\n🎯 KEY TEST CASES:")
    print("  • Impermanent Loss (AMM): IL = 2√r/(1+r) - 1")
    print("  • Value at Risk 95%: VaR = V × σ × 1.645")
    print("  • Expected Shortfall 95%: ES = V × σ × 2.063")
    print("  • Liquidation Price (Long): P_liq = P_e × (1 - 1/(L×m))")
    print("  • Optimal LP Size: f* = min(μ/(λσ²), 1)")

    for domain in protocol.get_all_domains():
        print(f"\n{'=' * 80}")
        print(f"DOMAIN: {domain.upper()}")
        print(f"Description: {protocol.get_domain_description(domain)}")
        test_cases = protocol.load_test_data(domain, num_samples=10)
        print(f"Number of test cases: {len(test_cases)}")

        for i, (desc, X, y, vars, meta) in enumerate(test_cases, 1):
            print(f"\n  {i}. {desc}")
            print(f"     Variables: {', '.join(vars)}")
            print(f"     Formula: {meta['ground_truth']}")
            print(f"     Difficulty: {meta['difficulty']}")
            if meta.get("extrapolation_test"):
                print(f"     ⚠️  EXTRAPOLATION TEST CASE")

    # Save protocol documentation
    print("\n" + "=" * 80)
    print("Saving protocol documentation...")
    protocol.save_protocol_documentation()

    print("\n" + "=" * 80)
    print("EXPERIMENT READY".center(80))
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run experiments using LLM for formula discovery")
    print("2. Evaluate discovered formulas against ground truth")
    print("3. Generate comprehensive report with extrapolation analysis")
    print("4. Focus on critical test cases: IL, VaR, ES, Liquidation")
