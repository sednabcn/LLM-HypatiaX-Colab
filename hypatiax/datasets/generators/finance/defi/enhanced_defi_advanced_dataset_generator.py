"""
Enhanced DeFi Advanced Formula Discovery Dataset Generator
Fixed class structure with proper imports and two-phase generation:
  - Phase 1: 10 Advanced DeFi formulas
  - Phase 2: 5 Fee Optimization formulas
Total: 15 formulas
"""

import os
from datetime import datetime
from typing import Dict, Tuple

import numpy as np

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class EnhancedDeFiAdvancedGenerator:
    """Generate enhanced advanced DeFi formulas with two phases."""

    def __init__(self, domain: str = "defi", seed: int = 42, noise_level: float = 0.01):
        """
        Initialize the enhanced generator.

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
        Generate data for each formula (1-15).

        Args:
            formula_num: Formula number (1-15)
            n_samples: Number of samples to generate
        """

        # PHASE 1: Advanced DeFi Formulas (1-10)
        if formula_num == 1:  # Price Impact
            print("\n1. Price Impact (Constant Product AMM)")
            amount_in = np.random.uniform(1, 1000, n_samples)
            reserve_in = np.random.uniform(10000, 1000000, n_samples)
            reserve_out = np.random.uniform(10000, 1000000, n_samples)
            fee = 0.003

            X = np.column_stack([amount_in, reserve_in, reserve_out])

            amount_in_with_fee = amount_in * (1 - fee)
            amount_out = reserve_out * amount_in_with_fee / (reserve_in + amount_in_with_fee)
            expected_price = reserve_out / reserve_in
            actual_price = amount_out / amount_in
            price_impact = (expected_price - actual_price) / expected_price
            price_impact += np.random.normal(0, self.noise_level * np.mean(price_impact), n_samples)

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

        elif formula_num == 2:  # Optimal LP Position
            print("\n2. Optimal LP Position Sizing")
            capital = np.random.uniform(1000, 500000, n_samples)
            fee_apy = np.random.uniform(0.05, 0.50, n_samples)
            volatility = np.random.uniform(0.3, 2.0, n_samples)
            risk_tolerance = np.random.uniform(0.1, 0.5, n_samples)

            X = np.column_stack([capital, fee_apy, volatility, risk_tolerance])

            expected_return = fee_apy
            kelly_fraction = expected_return / (volatility**2)
            position_size = capital * kelly_fraction * risk_tolerance
            position_size = np.clip(position_size, 0, capital)
            position_size += np.random.normal(0, self.noise_level * np.mean(position_size), n_samples)

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

        elif formula_num == 3:  # Time-Weighted IL
            print("\n3. Time-Weighted Impermanent Loss")
            days_held = np.random.uniform(1, 365, n_samples)
            price_ratio = np.random.uniform(0.5, 2.0, n_samples)
            initial_volatility = np.random.uniform(0.5, 2.5, n_samples)

            X = np.column_stack([days_held, price_ratio, initial_volatility])

            il_pct = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
            time_factor = 1 - np.exp(-days_held / 30)
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

        elif formula_num == 4:  # Liquidation Long
            print("\n4. Liquidation Price - Long Position")
            leverage = np.random.uniform(2, 20, n_samples)
            entry_price = np.random.uniform(1000, 50000, n_samples)
            maintenance_margin = np.random.uniform(0.03, 0.10, n_samples)

            X = np.column_stack([leverage, entry_price, maintenance_margin])

            liq_price_long = entry_price * (1 - 1 / leverage + maintenance_margin)
            liq_price_long += np.random.normal(0, self.noise_level * entry_price * 0.01, n_samples)

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

        elif formula_num == 5:  # Liquidation Short
            print("\n5. Liquidation Price - Short Position")
            leverage_short = np.random.uniform(2, 20, n_samples)
            entry_price_short = np.random.uniform(1000, 50000, n_samples)
            maintenance_margin_short = np.random.uniform(0.03, 0.10, n_samples)

            X = np.column_stack([leverage_short, entry_price_short, maintenance_margin_short])

            liq_price_short = entry_price_short * (1 + 1 / leverage_short - maintenance_margin_short)
            liq_price_short += np.random.normal(0, self.noise_level * entry_price_short * 0.01, n_samples)

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

        elif formula_num == 6:  # Flash Loan Arbitrage
            print("\n6. Flash Loan Arbitrage Profit")
            loan_amount = np.random.uniform(10000, 1000000, n_samples)
            price_diff = np.random.uniform(0.001, 0.05, n_samples)
            gas_cost = np.random.uniform(10, 200, n_samples)
            flash_loan_fee = 0.0009

            X = np.column_stack([loan_amount, price_diff, gas_cost])

            profit = loan_amount * price_diff - loan_amount * flash_loan_fee - gas_cost
            profit += np.random.normal(0, self.noise_level * np.abs(profit.mean()), n_samples)

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

        elif formula_num == 7:  # Concentrated Liquidity
            print("\n7. Concentrated Liquidity Range (Uniswap V3)")
            current_price = np.random.uniform(1000, 5000, n_samples)
            volatility_daily = np.random.uniform(0.01, 0.10, n_samples)
            days_horizon = np.random.uniform(1, 30, n_samples)

            X = np.column_stack([current_price, volatility_daily, days_horizon])

            z_score = 1.96
            range_width = current_price * volatility_daily * np.sqrt(days_horizon) * z_score
            range_width += np.random.normal(0, self.noise_level * range_width.mean(), n_samples)

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
            base_rate = np.random.uniform(0.01, 0.05, n_samples)
            optimal_util = 0.80
            slope1 = 0.05
            slope2 = 0.50

            X = np.column_stack([utilization_rate, base_rate])

            borrow_apy = np.where(
                utilization_rate <= optimal_util,
                base_rate + slope1 * (utilization_rate / optimal_util),
                base_rate + slope1 + slope2 * ((utilization_rate - optimal_util) / (1 - optimal_util)),
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
                variable_units={"utilization": "dimensionless", "base_rate": "dimensionless"},
                description="Dynamic borrow APY with kinked rate model",
                validate_first=False,
            )

        elif formula_num == 10:  # Health Factor
            print("\n10. Lending Protocol Health Factor")
            collateral_value = np.random.uniform(10000, 500000, n_samples)
            borrowed_value = np.random.uniform(1000, 300000, n_samples)
            liquidation_threshold = np.random.uniform(0.75, 0.85, n_samples)
            borrowed_value = np.minimum(borrowed_value, collateral_value * liquidation_threshold * 0.95)

            X = np.column_stack([collateral_value, borrowed_value, liquidation_threshold])

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

        # PHASE 2: Fee Optimization Formulas (11-15)
        elif formula_num == 11:  # Low Volatility Fee
            print("\n11. Optimal Fee - Low Volatility Market")
            volume_24h = np.random.uniform(100000, 10000000, n_samples)
            liquidity_low = np.random.uniform(1000000, 50000000, n_samples)
            volatility_low = np.random.uniform(0.05, 0.3, n_samples)

            X = np.column_stack([volume_24h, liquidity_low, volatility_low])

            volume_to_liquidity = volume_24h / liquidity_low
            optimal_fee_low = 0.0005 + 0.002 * (1 / (1 + volume_to_liquidity * 10))
            optimal_fee_low = np.clip(optimal_fee_low, 0.0001, 0.01)
            optimal_fee_low += np.random.normal(0, 0.0001, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=optimal_fee_low,
                variable_names=["volume_24h", "liquidity", "volatility"],
                variable_descriptions={
                    "volume_24h": "24-hour trading volume",
                    "liquidity": "Total pool liquidity",
                    "volatility": "Annualized volatility",
                },
                variable_units={
                    "volume_24h": "dimensionless",
                    "liquidity": "dimensionless",
                    "volatility": "dimensionless",
                },
                description="Optimal fee for low volatility, competitive market",
                validate_first=False,
            )

        elif formula_num == 12:  # High Volatility Fee
            print("\n12. Optimal Fee - High Volatility Market")
            volume_high = np.random.uniform(100000, 10000000, n_samples)
            liquidity_high = np.random.uniform(1000000, 50000000, n_samples)
            volatility_high = np.random.uniform(0.5, 3.0, n_samples)

            X = np.column_stack([volume_high, liquidity_high, volatility_high])

            expected_il_annual = 0.5 * volatility_high**2
            turnover_rate = volume_high / liquidity_high
            optimal_fee_high = 0.003 + expected_il_annual / (turnover_rate * 365)
            optimal_fee_high = np.clip(optimal_fee_high, 0.001, 0.03)
            optimal_fee_high += np.random.normal(0, 0.001, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=optimal_fee_high,
                variable_names=["volume_24h", "liquidity", "volatility"],
                variable_descriptions={
                    "volume_24h": "24-hour trading volume",
                    "liquidity": "Total pool liquidity",
                    "volatility": "Annualized volatility",
                },
                variable_units={
                    "volume_24h": "dimensionless",
                    "liquidity": "dimensionless",
                    "volatility": "dimensionless",
                },
                description="Optimal fee for high volatility market (IL compensation)",
                validate_first=False,
            )

        elif formula_num == 13:  # Trending Market Fee
            print("\n13. Optimal Fee - Trending Market")
            volume_trend = np.random.uniform(100000, 10000000, n_samples)
            price_momentum = np.random.uniform(-0.5, 0.5, n_samples)
            liquidity_depth = np.random.uniform(1000000, 50000000, n_samples)
            volatility_trend = np.random.uniform(0.3, 1.5, n_samples)

            X = np.column_stack([volume_trend, price_momentum, liquidity_depth, volatility_trend])

            momentum_factor = 1 + np.abs(price_momentum)
            base_fee = 0.003
            optimal_fee_trend = base_fee * momentum_factor * (1 + volatility_trend * 0.2)
            optimal_fee_trend = np.clip(optimal_fee_trend, 0.001, 0.02)
            optimal_fee_trend += np.random.normal(0, 0.001, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=optimal_fee_trend,
                variable_names=["volume", "momentum", "liquidity", "volatility"],
                variable_descriptions={
                    "volume": "24-hour trading volume",
                    "momentum": "Price momentum (daily change)",
                    "liquidity": "Pool liquidity depth",
                    "volatility": "Annualized volatility",
                },
                variable_units={
                    "volume": "dimensionless",
                    "momentum": "dimensionless",
                    "liquidity": "dimensionless",
                    "volatility": "dimensionless",
                },
                description="Dynamic fee for trending market (momentum-adjusted)",
                validate_first=False,
            )

        elif formula_num == 14:  # Ranging Market Fee
            print("\n14. Optimal Fee - Ranging Market")
            volume_range = np.random.uniform(100000, 10000000, n_samples)
            price_range_width = np.random.uniform(0.02, 0.15, n_samples)
            liquidity_range = np.random.uniform(1000000, 50000000, n_samples)
            competitor_fee = np.random.uniform(0.001, 0.01, n_samples)

            X = np.column_stack([volume_range, price_range_width, liquidity_range, competitor_fee])

            optimal_fee_range = competitor_fee * 0.8
            min_fee = 0.0005 + price_range_width * 0.01
            optimal_fee_range = np.maximum(optimal_fee_range, min_fee)
            optimal_fee_range = np.clip(optimal_fee_range, 0.0001, 0.01)
            optimal_fee_range += np.random.normal(0, 0.0005, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=optimal_fee_range,
                variable_names=["volume", "price_range", "liquidity", "competitor_fee"],
                variable_descriptions={
                    "volume": "24-hour trading volume",
                    "price_range": "Price range width",
                    "liquidity": "Pool liquidity",
                    "competitor_fee": "Competitor pool fee",
                },
                variable_units={
                    "volume": "dimensionless",
                    "price_range": "dimensionless",
                    "liquidity": "dimensionless",
                    "competitor_fee": "dimensionless",
                },
                description="Optimal fee for ranging market (volume-maximizing)",
                validate_first=False,
            )

        elif formula_num == 15:  # Volatile/Choppy Fee
            print("\n15. Optimal Fee - Volatile/Choppy Market")
            volume_vol = np.random.uniform(100000, 10000000, n_samples)
            realized_vol = np.random.uniform(1.0, 5.0, n_samples)
            liquidity_vol = np.random.uniform(1000000, 50000000, n_samples)
            daily_trades = np.random.uniform(100, 10000, n_samples)

            X = np.column_stack([volume_vol, realized_vol, liquidity_vol, daily_trades])

            avg_trade_size = volume_vol / daily_trades
            size_factor = 1 + np.log1p(avg_trade_size / 10000) * 0.1
            optimal_fee_vol = 0.005 + 0.002 * realized_vol * size_factor
            optimal_fee_vol = np.clip(optimal_fee_vol, 0.003, 0.05)
            optimal_fee_vol += np.random.normal(0, 0.002, n_samples)

            self.system.discover_validate_interpret(
                X=X,
                y=optimal_fee_vol,
                variable_names=["volume", "volatility", "liquidity", "trades"],
                variable_descriptions={
                    "volume": "24-hour trading volume",
                    "volatility": "Realized volatility (very high)",
                    "liquidity": "Pool liquidity",
                    "trades": "Number of daily trades",
                },
                variable_units={
                    "volume": "dimensionless",
                    "volatility": "dimensionless",
                    "liquidity": "dimensionless",
                    "trades": "dimensionless",
                },
                description="Optimal fee for volatile/choppy market (high IL protection)",
                validate_first=False,
            )

    def run_phase1(self, n_samples: int = 150):
        """Generate Phase 1: Advanced DeFi formulas (1-10)."""
        self.phase = "Phase 1"
        print("\n" + "#" * 70)
        print("# PHASE 1: Advanced DeFi Formula Discovery (10 Formulas)")
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
        """Generate Phase 2: Fee Optimization formulas (11-15)."""
        self.phase = "Phase 2"
        print("\n" + "#" * 70)
        print("# PHASE 2: Fee Optimization Formula Discovery (5 Formulas)")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print(f"# Fee noise level: 0.0001")
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

    def run_all_formulas(self, n_samples_phase1: int = 150, n_samples_phase2: int = 120):
        """Generate all 15 formulas in two phases."""
        self.run_phase1(n_samples_phase1)
        self.run_phase2(n_samples_phase2)

    def save_results(self, output_dir: str = "hypatiax/data/finance/defi", separate_phases: bool = True):
        """
        Save results to files.

        Args:
            output_dir: Directory to save results
            separate_phases: If True, save phase1 and phase2 separately
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if separate_phases:
            # Save combined
            json_path = os.path.join(output_dir, f"defi_enhanced_all_{timestamp}.json")
            csv_path = os.path.join(output_dir, f"defi_enhanced_all_{timestamp}.csv")
        else:
            json_path = os.path.join(output_dir, f"defi_enhanced_{timestamp}.json")
            csv_path = os.path.join(output_dir, f"defi_enhanced_{timestamp}.csv")

        self.system.export_results(json_path, format="json")

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

        print(f"   ✅ CSV exported safely: {filepath}")

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("FINAL SUMMARY - ENHANCED DEFI FORMULAS (15 Total)")
        print("=" * 70)

        stats = self.system.get_statistics()
        print(f"\nOverall Statistics:")
        print(f"  Total formulas: {stats['total_runs']}")
        print(f"  Valid formulas: {stats['valid_count']}")
        print(f"  Invalid formulas: {stats['invalid_count']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        print(f"  Average R² score: {stats['average_r2']:.4f}")
        print(f"  Average validation score: {stats['average_validation_score']:.1f}/100")

        # Phase breakdown
        results = self.system.get_results()
        if len(results) >= 10:
            print(f"\nPhase Breakdown:")
            print(f"  Phase 1 (Advanced DeFi): Formulas 1-10")
            print(f"  Phase 2 (Fee Optimization): Formulas 11-15")

        # Individual results
        print("\n" + "-" * 70)
        print("Individual Formula Results:")
        print("-" * 70)

        for i, result in enumerate(results, 1):
            discovery = result.get("discovery", {})
            validation = result.get("validation", {})

            valid_symbol = "✅" if validation.get("valid") else "❌"
            phase_label = "P1" if i <= 10 else "P2"

            print(f"\n{i}. [{phase_label}] {result.get('description', 'Unknown')}")
            print(
                f"   {valid_symbol} R²: {discovery.get('r2_score', 0):.4f} | "
                f"Valid: {validation.get('valid', False)} | "
                f"Score: {validation.get('total_score', 0):.1f}/100"
            )
            print(f"   Expression: {discovery.get('expression', 'N/A')[:80]}")

        print("\n" + "=" * 70)


def main():
    """Main execution function."""
    generator = EnhancedDeFiAdvancedGenerator(domain="defi", seed=42, noise_level=0.01)

    # Run both phases
    generator.run_all_formulas(n_samples_phase1=150, n_samples_phase2=120)

    # Save results
    json_path, csv_path = generator.save_results()
    print(f"\n📁 Results saved:")
    print(f"   JSON: {json_path}")
    print(f"   CSV: {csv_path}")

    # Print summary
    generator.print_summary()


if __name__ == "__main__":
    main()
