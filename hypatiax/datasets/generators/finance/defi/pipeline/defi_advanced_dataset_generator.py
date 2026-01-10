"""
DeFi Advanced Formula Discovery Dataset Generator
Uses class structure like defi_dataset_20_generator.py
Includes 10 advanced DeFi formulas with realistic market dynamics
"""

import os
from datetime import datetime
from typing import Dict, Tuple

import numpy as np

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class DeFiAdvancedFormulaGenerator:
    """Generate advanced synthetic DeFi data and discover formulas."""

    def __init__(self, domain: str = "defi", seed: int = 42, noise_level: float = 0.01):
        """
        Initialize the advanced generator.

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

    def generate_formula(self, formula_num: int, n_samples: int = 150):
        """
        Generate data for each advanced formula.

        Args:
            formula_num: Formula number (1-10)
            n_samples: Number of samples to generate
        """

        if formula_num == 1:  # Price Impact (Constant Product AMM)
            print("\n1. Price Impact (Constant Product AMM)")
            amount_in = np.random.uniform(1, 1000, n_samples)
            reserve_in = np.random.uniform(10000, 1000000, n_samples)
            reserve_out = np.random.uniform(10000, 1000000, n_samples)
            fee = 0.003  # 0.3% fee

            X = np.column_stack([amount_in, reserve_in, reserve_out])

            # x * y = k formula with fee
            amount_in_with_fee = amount_in * (1 - fee)
            amount_out = (
                reserve_out * amount_in_with_fee / (reserve_in + amount_in_with_fee)
            )
            expected_price = reserve_out / reserve_in
            actual_price = amount_out / amount_in
            price_impact = (expected_price - actual_price) / expected_price
            price_impact += np.random.normal(
                0, self.noise_level * np.mean(price_impact), n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=price_impact,
                variable_names=["amount_in", "reserve_in", "reserve_out"],
                variable_descriptions={
                    "amount_in": "Swap input amount",
                    "reserve_in": "Input token reserves",
                    "reserve_out": "Output token reserves",
                },
                variable_units={
                    "amount_in": "dimensionless",
                    "reserve_in": "dimensionless",
                    "reserve_out": "dimensionless",
                },
                description="Price impact percentage in constant product AMM (Uniswap V2 style)",
                validate_first=False,
            )

        elif formula_num == 2:  # Optimal LP Position Size
            print("\n2. Optimal LP Position Sizing")
            capital = np.random.uniform(1000, 500000, n_samples)
            fee_apy = np.random.uniform(0.05, 0.50, n_samples)  # 5-50% APY
            volatility = np.random.uniform(0.3, 2.0, n_samples)  # Annualized volatility
            risk_tolerance = np.random.uniform(0.1, 0.5, n_samples)

            X = np.column_stack([capital, fee_apy, volatility, risk_tolerance])

            # Kelly-inspired position sizing
            expected_return = fee_apy
            kelly_fraction = expected_return / (volatility**2)
            position_size = capital * kelly_fraction * risk_tolerance
            position_size = np.clip(position_size, 0, capital)
            position_size += np.random.normal(
                0, self.noise_level * np.mean(position_size), n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=position_size,
                variable_names=["capital", "fee_apy", "volatility", "risk_tolerance"],
                variable_descriptions={
                    "capital": "Available capital",
                    "fee_apy": "Expected fee APY",
                    "volatility": "Pool price volatility (annualized)",
                    "risk_tolerance": "Risk tolerance (0-1 scale)",
                },
                variable_units={
                    "capital": "dimensionless",
                    "fee_apy": "dimensionless",
                    "volatility": "dimensionless",
                    "risk_tolerance": "dimensionless",
                },
                description="Optimal LP position size balancing fee income and IL risk",
                validate_first=False,
            )

        elif formula_num == 3:  # Time-Weighted Impermanent Loss
            print("\n3. Time-Weighted Impermanent Loss")
            days_held = np.random.uniform(1, 365, n_samples)
            price_ratio = np.random.uniform(0.5, 2.0, n_samples)
            initial_volatility = np.random.uniform(0.5, 2.5, n_samples)

            X = np.column_stack([days_held, price_ratio, initial_volatility])

            # Standard IL with time decay
            il_pct = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
            time_factor = 1 - np.exp(-days_held / 30)  # 30-day half-life
            vol_scaling = 1 + (initial_volatility - 1) * 0.2
            time_weighted_il = il_pct * time_factor * vol_scaling
            time_weighted_il += np.random.normal(0, self.noise_level * 0.5, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=time_weighted_il,
                variable_names=["days_held", "price_ratio", "volatility"],
                variable_descriptions={
                    "days_held": "Days position held",
                    "price_ratio": "Final/initial price ratio",
                    "volatility": "Pool volatility parameter",
                },
                variable_units={
                    "days_held": "dimensionless",
                    "price_ratio": "dimensionless",
                    "volatility": "dimensionless",
                },
                description="Time-weighted impermanent loss with volatility adjustment",
                validate_first=False,
            )

        elif formula_num == 4:  # Liquidation Price (Long Position)
            print("\n4. Liquidation Price - Long Position")
            leverage = np.random.uniform(2, 20, n_samples)
            entry_price = np.random.uniform(1000, 50000, n_samples)
            maintenance_margin = np.random.uniform(0.03, 0.10, n_samples)

            X = np.column_stack([leverage, entry_price, maintenance_margin])

            # Long liquidation formula
            liq_price_long = entry_price * (1 - 1 / leverage + maintenance_margin)
            liq_price_long += np.random.normal(
                0, self.noise_level * entry_price * 0.01, n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=liq_price_long,
                variable_names=["leverage", "entry_price", "maintenance_margin"],
                variable_descriptions={
                    "leverage": "Position leverage multiplier",
                    "entry_price": "Entry price",
                    "maintenance_margin": "Maintenance margin ratio",
                },
                variable_units={
                    "leverage": "dimensionless",
                    "entry_price": "dimensionless",
                    "maintenance_margin": "dimensionless",
                },
                description="Liquidation price for leveraged long position",
                validate_first=False,
            )

        elif formula_num == 5:  # Liquidation Price (Short Position)
            print("\n5. Liquidation Price - Short Position")
            leverage_short = np.random.uniform(2, 20, n_samples)
            entry_price_short = np.random.uniform(1000, 50000, n_samples)
            maintenance_margin_short = np.random.uniform(0.03, 0.10, n_samples)

            X = np.column_stack(
                [leverage_short, entry_price_short, maintenance_margin_short]
            )

            # Short liquidation formula
            liq_price_short = entry_price_short * (
                1 + 1 / leverage_short - maintenance_margin_short
            )
            liq_price_short += np.random.normal(
                0, self.noise_level * entry_price_short * 0.01, n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=liq_price_short,
                variable_names=["leverage", "entry_price", "maintenance_margin"],
                variable_descriptions={
                    "leverage": "Position leverage multiplier",
                    "entry_price": "Entry price",
                    "maintenance_margin": "Maintenance margin ratio",
                },
                variable_units={
                    "leverage": "dimensionless",
                    "entry_price": "dimensionless",
                    "maintenance_margin": "dimensionless",
                },
                description="Liquidation price for leveraged short position",
                validate_first=False,
            )

        elif formula_num == 6:  # Flash Loan Arbitrage Profit
            print("\n6. Flash Loan Arbitrage Profit")
            loan_amount = np.random.uniform(10000, 1000000, n_samples)
            price_diff = np.random.uniform(0.001, 0.05, n_samples)  # 0.1% to 5%
            gas_cost = np.random.uniform(10, 200, n_samples)
            flash_loan_fee = 0.0009  # 0.09%

            X = np.column_stack([loan_amount, price_diff, gas_cost])

            # Profit calculation
            profit = loan_amount * price_diff - loan_amount * flash_loan_fee - gas_cost
            profit += np.random.normal(
                0, self.noise_level * np.abs(profit.mean()), n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=profit,
                variable_names=["loan_amount", "price_diff", "gas_cost"],
                variable_descriptions={
                    "loan_amount": "Flash loan amount",
                    "price_diff": "Price difference between venues",
                    "gas_cost": "Transaction gas cost",
                },
                variable_units={
                    "loan_amount": "dimensionless",
                    "price_diff": "dimensionless",
                    "gas_cost": "dimensionless",
                },
                description="Expected profit from flash loan arbitrage",
                validate_first=False,
            )

        elif formula_num == 7:  # Concentrated Liquidity Range
            print("\n7. Concentrated Liquidity Range (Uniswap V3)")
            current_price = np.random.uniform(1000, 5000, n_samples)
            volatility_daily = np.random.uniform(0.01, 0.10, n_samples)  # 1-10% daily
            days_horizon = np.random.uniform(1, 30, n_samples)
            confidence = 0.95  # 95% confidence

            X = np.column_stack([current_price, volatility_daily, days_horizon])

            # Range width using volatility
            z_score = 1.96  # 95% confidence
            range_width = (
                current_price * volatility_daily * np.sqrt(days_horizon) * z_score
            )
            range_width += np.random.normal(
                0, self.noise_level * range_width.mean(), n_samples
            )

            self.system.discover_validate_interpret(
                X=X,
                y=range_width,
                variable_names=["current_price", "volatility", "days"],
                variable_descriptions={
                    "current_price": "Current asset price",
                    "volatility": "Daily volatility",
                    "days": "Time horizon in days",
                },
                variable_units={
                    "current_price": "dimensionless",
                    "volatility": "dimensionless",
                    "days": "dimensionless",
                },
                description="Optimal concentrated liquidity range width (95% confidence)",
                validate_first=False,
            )

        elif formula_num == 8:  # Utilization Rate
            print("\n8. Lending Protocol Utilization Rate")
            total_borrows = np.random.uniform(1000000, 50000000, n_samples)
            total_supply = np.random.uniform(2000000, 100000000, n_samples)
            # Ensure borrows <= supply
            total_borrows = np.minimum(total_borrows, total_supply * 0.95)

            X = np.column_stack([total_borrows, total_supply])

            utilization = total_borrows / total_supply
            utilization += np.random.normal(0, self.noise_level * 0.1, n_samples)
            utilization = np.clip(utilization, 0, 1)

            self.system.discover_validate_interpret(
                X=X,
                y=utilization,
                variable_names=["borrows", "supply"],
                variable_descriptions={
                    "borrows": "Total borrowed amount",
                    "supply": "Total supplied amount",
                },
                variable_units={"borrows": "dimensionless", "supply": "dimensionless"},
                description="Lending protocol utilization rate",
                validate_first=False,
            )

        elif formula_num == 9:  # Dynamic Borrow APY
            print("\n9. Dynamic Borrow Interest Rate")
            utilization_rate = np.random.uniform(0.1, 0.95, n_samples)
            base_rate = np.random.uniform(0.01, 0.05, n_samples)  # 1-5%
            optimal_util = 0.80  # Target 80%
            slope1 = 0.05
            slope2 = 0.50

            X = np.column_stack([utilization_rate, base_rate])

            # Kinked interest rate model (Aave-style)
            borrow_apy = np.where(
                utilization_rate <= optimal_util,
                base_rate + slope1 * (utilization_rate / optimal_util),
                base_rate
                + slope1
                + slope2 * ((utilization_rate - optimal_util) / (1 - optimal_util)),
            )
            borrow_apy += np.random.normal(0, self.noise_level * 0.1, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=borrow_apy,
                variable_names=["utilization", "base_rate"],
                variable_descriptions={
                    "utilization": "Protocol utilization rate",
                    "base_rate": "Base interest rate",
                },
                variable_units={
                    "utilization": "dimensionless",
                    "base_rate": "dimensionless",
                },
                description="Dynamic borrow APY with kinked rate model",
                validate_first=False,
            )

        elif formula_num == 10:  # Health Factor
            print("\n10. Lending Protocol Health Factor")
            collateral_value = np.random.uniform(10000, 500000, n_samples)
            borrowed_value = np.random.uniform(1000, 300000, n_samples)
            liquidation_threshold = np.random.uniform(0.75, 0.85, n_samples)
            # Ensure borrowed <= collateral * threshold
            borrowed_value = np.minimum(
                borrowed_value, collateral_value * liquidation_threshold * 0.95
            )

            X = np.column_stack(
                [collateral_value, borrowed_value, liquidation_threshold]
            )

            # Health factor = (collateral * liquidation_threshold) / borrowed
            health_factor = (collateral_value * liquidation_threshold) / borrowed_value
            health_factor += np.random.normal(0, self.noise_level * 0.1, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=health_factor,
                variable_names=["collateral", "borrowed", "liq_threshold"],
                variable_descriptions={
                    "collateral": "Collateral value in USD",
                    "borrowed": "Borrowed value in USD",
                    "liq_threshold": "Liquidation threshold ratio",
                },
                variable_units={
                    "collateral": "dimensionless",
                    "borrowed": "dimensionless",
                    "liq_threshold": "dimensionless",
                },
                description="Health factor for lending positions (>1 = safe, <1 = liquidatable)",
                validate_first=False,
            )

    def run_all_formulas(self, n_samples: int = 150):
        """Generate and discover all 10 advanced DeFi formulas."""
        print("\n" + "#" * 70)
        print("# DeFi Advanced Formula Discovery - 10 Formulas")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print(f"# Noise level: {self.noise_level}")
        print("#" * 70)

        for i in range(1, 11):
            try:
                print(f"\n{'=' * 70}")
                print(f"Processing Formula {i}/10")
                print(f"{'=' * 70}")
                self.generate_formula(i, n_samples)
                print(f"✅ Formula {i} completed")
            except Exception as e:
                print(f"❌ Error in Formula {i}: {str(e)}")
                import traceback

                traceback.print_exc()

    def save_results(self, output_dir: str = "hypatiax/data/finance/defi"):
        """Save results to files."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_path = os.path.join(output_dir, f"defi_advanced_{timestamp}.json")
        csv_path = os.path.join(output_dir, f"defi_advanced_summary_{timestamp}.csv")

        self.system.export_results(json_path, format="json")

        # Try standard CSV export, use fallback if needed
        try:
            self.system.export_results(csv_path, format="csv")
        except AttributeError:
            print("   ⚠️  Using fallback CSV export...")
            self._export_csv_safe(csv_path)

        return json_path, csv_path

    def _export_csv_safe(self, filepath: str):
        """Safely export to CSV with None handling."""
        import csv

        results_list = list(self.system.results)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(
                [
                    "Timestamp",
                    "Expression",
                    "R² Score",
                    "Complexity",
                    "Validation Score",
                    "Valid",
                    "Interpretation",
                    "Provider",
                    "Domain",
                ]
            )

            # Rows with safe None handling
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

        print(f"   ✅ CSV exported safely: {filepath}")

    def print_summary(self):
        """Print summary statistics."""
        print("\n" + "=" * 70)
        print("FINAL SUMMARY - ADVANCED DEFI FORMULAS")
        print("=" * 70)

        stats = self.system.get_statistics()
        print(f"\nTotal formulas: {stats['total_runs']}")
        print(f"Valid formulas: {stats['valid_count']}")
        print(f"Invalid formulas: {stats['invalid_count']}")
        print(f"Success rate: {stats['success_rate']:.1%}")
        print(f"Average R² score: {stats['average_r2']:.4f}")
        print(f"Average validation score: {stats['average_validation_score']:.1f}/100")

        # Show individual results summary
        print("\n" + "-" * 70)
        print("Individual Formula Results:")
        print("-" * 70)

        for i, result in enumerate(self.system.get_results(), 1):
            discovery = result.get("discovery", {})
            validation = result.get("validation", {})

            valid_symbol = "✅" if validation.get("valid") else "❌"

            print(f"\n{i}. {result.get('description', 'Unknown')}")
            print(
                f"   {valid_symbol} R²: {discovery.get('r2_score', 0):.4f} | "
                f"Validation: {validation.get('total_score', 0):.1f}/100"
            )
            print(f"   Expression: {discovery.get('expression', 'N/A')[:60]}...")

        print("\n" + "=" * 70)


def main():
    """Main execution function."""
    print("\n" + "█" * 70)
    print("█  DeFi Advanced Formula Discovery - 10 Formulas           █")
    print("█  Features:                                                █")
    print("█    • Realistic market dynamics                            █")
    print("█    • Advanced DeFi concepts (V3, flash loans, etc.)       █")
    print("█    • Leveraged positions and liquidations                 █")
    print("█    • Lending protocol mechanics                           █")
    print("█" * 70)

    generator = DeFiAdvancedFormulaGenerator(domain="defi", seed=42, noise_level=0.01)
    generator.run_all_formulas(n_samples=150)

    json_path, csv_path = generator.save_results()
    generator.print_summary()

    print(f"\n✅ Results saved to:")
    print(f"  JSON: {json_path}")
    print(f"  CSV:  {csv_path}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

"""
5. 10 Advanced Formulas Included:

Price Impact - Constant product AMM with fees
Optimal LP Position - Kelly-inspired sizing
Time-Weighted IL - Decay factor + volatility
Liquidation (Long) - Leveraged long positions
Liquidation (Short) - Leveraged short positions
Flash Loan Arbitrage - Profit with fees
Concentrated Liquidity - V3 range optimization
Utilization Rate - Lending protocol metric
Dynamic Borrow APY - Kinked rate model (Aave)
Health Factor - Lending safety metric

Usage:
bashpython defi_advanced_dataset_generator.py
Or with monitoring:
bashpython script_monitor.py defi_advanced_dataset_generator.py
The structure now perfectly matches the 20-formula generator, making it easy to maintain and extend! 🚀
"""
