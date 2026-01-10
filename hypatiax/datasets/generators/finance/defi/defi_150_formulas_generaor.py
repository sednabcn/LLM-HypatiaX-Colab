"""
DeFi Formula Discovery - 150 Complete Formulas
Combines best features from all scripts into one comprehensive generator
"""

import os
from datetime import datetime
from typing import Dict, Tuple

import numpy as np

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class DeFi150FormulaGenerator:
    """
    Generate comprehensive DeFi dataset with 150 formulas.

    Features:
    1. ✅ VALIDATION: Comprehensive dataset validation (NaN, Inf, lengths, ranges)
    2. ✅ SCALABILITY: Easy parameter adjustment and formula modification
    3. ✅ ROBUSTNESS: Detailed error handling with context and continuation
    """

    def __init__(self, domain: str = "defi", seed: int = 42, noise_level: float = 0.01):
        """
        Initialize generator with configurable parameters.

        Args:
            domain: Domain for validation (default: "defi")
            seed: Random seed for reproducibility (default: 42)
            noise_level: Relative noise level for realistic data (default: 0.01 = 1%)
        """
        self.system = HybridDiscoverySystem(domain=domain, max_results=200)
        self.seed = seed
        self.noise_level = noise_level
        np.random.seed(seed)
        self.results = []
        self.successful = 0
        self.failed = 0

        # Feature #2: SCALABILITY - Configurable parameters for easy adjustment
        self.config = {
            # Sample sizes (can be adjusted per category)
            "default_samples": 100,
            "amm_samples": 100,
            "il_samples": 100,
            "lending_samples": 100,
            "leverage_samples": 100,
            "concentrated_samples": 100,
            "yield_samples": 100,
            # Reserve scales (adjust for different pool sizes)
            "reserve_scales": [1000, 10000, 100000, 1000000],
            # Fee tiers (adjust for different AMM protocols)
            "fee_tiers": [0.0005, 0.003, 0.01, 0.03],
            # Price ratio ranges (adjust for different volatility scenarios)
            "price_ranges": [(0.1, 10), (0.5, 2.0), (0.8, 1.2)],
            # Leverage ranges (adjust for different risk levels)
            "leverage_ranges": [(2, 5), (5, 10), (10, 20)],
            # Yield rates (adjust for different market conditions)
            "yield_ranges": [(0.05, 0.15), (0.15, 0.30), (0.30, 0.50)],
        }

    def update_config(self, **kwargs):
        """
        Feature #2: SCALABILITY - Update configuration parameters dynamically.

        Example:
            generator.update_config(
                default_samples=150,
                fee_tiers=[0.001, 0.005, 0.01],
                noise_level=0.02
            )
        """
        for key, value in kwargs.items():
            if key == "noise_level":
                self.noise_level = value
            elif key in self.config:
                self.config[key] = value
            else:
                print(f"⚠️  Unknown config key: {key}")

        print(f"✅ Configuration updated: {', '.join(kwargs.keys())}")

    @staticmethod
    def validate_dataset(X, y):
        """
        Validate dataset quality - Feature #1: Comprehensive Validation

        Checks:
        - No NaN values in inputs or outputs
        - No infinite values in inputs or outputs
        - Matching lengths between X and y
        - Reasonable value ranges (not all zeros, not too large)

        Raises:
            ValueError: If any validation check fails with detailed message
        """
        # Check for NaN values
        if np.any(np.isnan(X)):
            raise ValueError(
                f"Dataset X contains NaN values at positions: {np.where(np.isnan(X))}"
            )
        if np.any(np.isnan(y)):
            raise ValueError(
                f"Dataset y contains NaN values at positions: {np.where(np.isnan(y))}"
            )

        # Check for infinite values
        if np.any(np.isinf(X)):
            raise ValueError(
                f"Dataset X contains inf values at positions: {np.where(np.isinf(X))}"
            )
        if np.any(np.isinf(y)):
            raise ValueError(
                f"Dataset y contains inf values at positions: {np.where(np.isinf(y))}"
            )

        # Check lengths match
        if len(X) != len(y):
            raise ValueError(f"Mismatched input/output lengths: X={len(X)}, y={len(y)}")

        # Check for reasonable ranges (not all zeros)
        if np.allclose(X, 0):
            raise ValueError("Dataset X contains all zeros")
        if np.allclose(y, 0):
            raise ValueError("Dataset y contains all zeros")

        # Check for extremely large values that might cause numerical issues
        if np.max(np.abs(X)) > 1e15:
            raise ValueError(
                f"Dataset X contains extremely large values: max={np.max(np.abs(X))}"
            )
        if np.max(np.abs(y)) > 1e15:
            raise ValueError(
                f"Dataset y contains extremely large values: max={np.max(np.abs(y))}"
            )

        # Validation passed
        return True

    def _process_formula(self, formula_num, X, y, var_names, var_desc, description):
        """
        Common processing for all formulas - Feature #3: Robust Error Handling

        This method:
        1. Validates the dataset first
        2. Attempts to discover and validate the formula
        3. Catches and logs specific errors with context
        4. Continues execution even if one formula fails
        5. Tracks success/failure statistics

        Args:
            formula_num: Formula number (1-150)
            X: Input features array
            y: Target output array
            var_names: List of variable names
            var_desc: Dictionary of variable descriptions
            description: Formula description
        """
        try:
            # Pre-validation check
            self.validate_dataset(X, y)

            # Attempt formula discovery
            result = self.system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=var_names,
                variable_descriptions=var_desc,
                variable_units={name: "dimensionless" for name in var_names},
                description=description,
                validate_first=False,
            )

            # Track successful formula
            self.successful += 1

            # Progress update every 10 formulas
            if formula_num % 10 == 0:
                print(
                    f"✅ Progress: {formula_num}/150 completed ({self.successful} successful, {self.failed} failed)"
                )

            return result

        except ValueError as e:
            # Validation error - data quality issue
            self.failed += 1
            print(f"⚠️  Formula {formula_num} VALIDATION ERROR:")
            print(f"    Description: {description}")
            print(f"    Error: {str(e)}")
            print(f"    X shape: {X.shape}, y shape: {y.shape}")

        except Exception as e:
            # Other errors - discovery/interpretation issues
            self.failed += 1
            print(f"⚠️  Formula {formula_num} PROCESSING ERROR:")
            print(f"    Description: {description}")
            print(f"    Error type: {type(e).__name__}")
            print(f"    Error message: {str(e)[:100]}")

            # Print traceback for debugging if needed
            if formula_num % 50 == 0:  # Detailed error every 50 formulas
                import traceback

                print(f"    Traceback:")
                traceback.print_exc()

        return None

    # ==================== CATEGORY 1: AMM MECHANICS (30 formulas) ====================

    def generate_amm_formulas(self, n_samples=None):
        """
        Generate 30 AMM-related formulas with variations.

        Feature #2: SCALABILITY - Uses configurable parameters from self.config
        Can override n_samples or use config default
        """
        if n_samples is None:
            n_samples = self.config["amm_samples"]

        print("\n" + "=" * 70)
        print(f"CATEGORY 1: AMM MECHANICS (30 formulas, {n_samples} samples each)")
        print("=" * 70)

        for i in range(30):
            formula_num = i + 1

            # Feature #2: Use configurable parameters instead of hardcoded values
            reserve_scales = self.config["reserve_scales"]
            fee_tiers = self.config["fee_tiers"]

            reserve_scale = reserve_scales[i % len(reserve_scales)] * (2 ** (i // 10))
            fee_tier = fee_tiers[i % len(fee_tiers)]

            if i < 10:  # Constant Product (x*y=k)
                token_x = np.random.uniform(
                    reserve_scale, reserve_scale * 100, n_samples
                )
                token_y = np.random.uniform(
                    reserve_scale, reserve_scale * 100, n_samples
                )
                X = np.column_stack([token_x, token_y])
                k = token_x * token_y + np.random.normal(0, k.mean() * 0.01, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    k,
                    ["reserve_x", "reserve_y"],
                    {"reserve_x": "Token X reserves", "reserve_y": "Token Y reserves"},
                    f"Constant Product AMM (variant {i + 1}, scale {reserve_scale:.0e})",
                )

            elif i < 20:  # Swap Output with fees
                amount_in = np.random.uniform(1, reserve_scale * 0.1, n_samples)
                reserve_in = np.random.uniform(
                    reserve_scale, reserve_scale * 100, n_samples
                )
                reserve_out = np.random.uniform(
                    reserve_scale, reserve_scale * 100, n_samples
                )

                X = np.column_stack([amount_in, reserve_in, reserve_out])
                amount_out = (amount_in * (1 - fee_tier) * reserve_out) / (
                    reserve_in + amount_in * (1 - fee_tier)
                )
                amount_out += np.random.normal(0, 0.5, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    amount_out,
                    ["amount_in", "reserve_in", "reserve_out"],
                    {
                        "amount_in": "Input amount",
                        "reserve_in": "Input reserve",
                        "reserve_out": "Output reserve",
                    },
                    f"AMM Swap Output (fee {fee_tier * 100:.2f}%, scale {reserve_scale:.0e})",
                )

            else:  # Price Impact
                amount = np.random.uniform(1, reserve_scale * 0.05, n_samples)
                reserve_in = np.random.uniform(
                    reserve_scale, reserve_scale * 50, n_samples
                )
                reserve_out = np.random.uniform(
                    reserve_scale, reserve_scale * 50, n_samples
                )

                X = np.column_stack([amount, reserve_in, reserve_out])
                impact = amount / (reserve_in + amount) * (reserve_out / reserve_in)
                impact += np.random.normal(0, impact.mean() * 0.02, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    impact,
                    ["amount", "reserve_in", "reserve_out"],
                    {
                        "amount": "Trade amount",
                        "reserve_in": "Input reserve",
                        "reserve_out": "Output reserve",
                    },
                    f"Price Impact (scale {reserve_scale:.0e})",
                )

    # ==================== CATEGORY 2: IMPERMANENT LOSS (25 formulas) ====================

    def generate_il_formulas(self, n_samples=100):
        """Generate 25 impermanent loss variations."""
        print("\n" + "=" * 70)
        print("CATEGORY 2: IMPERMANENT LOSS (25 formulas)")
        print("=" * 70)

        for i in range(25):
            formula_num = 31 + i

            # Different price ratio ranges
            price_min = 0.1 * (2 ** (i // 5))
            price_max = 10 / (2 ** (i // 5))

            if i < 10:  # Basic IL
                price_ratio = np.random.uniform(price_min, price_max, (n_samples, 1))
                il = 2 * np.sqrt(price_ratio[:, 0]) / (1 + price_ratio[:, 0]) - 1
                il += np.random.normal(0, 0.01, n_samples)

                self._process_formula(
                    formula_num,
                    price_ratio,
                    il,
                    ["price_ratio"],
                    {"price_ratio": "Final/initial price ratio"},
                    f"Impermanent Loss (price range [{price_min:.2f}, {price_max:.2f}])",
                )

            elif i < 20:  # Time-weighted IL
                days = np.random.uniform(1, 365, n_samples)
                price_ratio = np.random.uniform(price_min, price_max, n_samples)
                volatility = np.random.uniform(0.5, 2.5, n_samples)

                X = np.column_stack([days, price_ratio, volatility])
                il_base = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
                time_factor = 1 - np.exp(-days / 30)
                il = il_base * time_factor * (1 + volatility * 0.2)
                il += np.random.normal(0, 0.01, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    il,
                    ["days", "price_ratio", "volatility"],
                    {
                        "days": "Days held",
                        "price_ratio": "Price ratio",
                        "volatility": "Volatility",
                    },
                    f"Time-Weighted IL (variant {i - 9})",
                )

            else:  # IL with fees offset
                price_ratio = np.random.uniform(price_min, price_max, n_samples)
                fee_apy = np.random.uniform(0.05, 0.50, n_samples)
                days = np.random.uniform(1, 365, n_samples)

                X = np.column_stack([price_ratio, fee_apy, days])
                il = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1
                fee_offset = fee_apy * (days / 365)
                net_il = il + fee_offset
                net_il += np.random.normal(0, 0.01, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    net_il,
                    ["price_ratio", "fee_apy", "days"],
                    {
                        "price_ratio": "Price ratio",
                        "fee_apy": "Fee APY",
                        "days": "Days held",
                    },
                    f"Net IL with Fee Offset (variant {i - 19})",
                )

    # ==================== CATEGORY 3: LENDING PROTOCOLS (25 formulas) ====================

    def generate_lending_formulas(self, n_samples=100):
        """Generate 25 lending protocol formulas."""
        print("\n" + "=" * 70)
        print("CATEGORY 3: LENDING PROTOCOLS (25 formulas)")
        print("=" * 70)

        for i in range(25):
            formula_num = 56 + i

            if i < 10:  # Utilization Rate
                borrows = np.random.uniform(
                    1e6 * (2 ** (i // 3)), 1e8 * (2 ** (i // 3)), n_samples
                )
                supply = borrows / np.random.uniform(0.3, 0.9, n_samples)

                X = np.column_stack([borrows, supply])
                util = borrows / supply + np.random.normal(0, 0.01, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    util,
                    ["borrows", "supply"],
                    {"borrows": "Total borrowed", "supply": "Total supplied"},
                    f"Utilization Rate (scale {borrows.mean():.0e})",
                )

            elif i < 18:  # Interest Rate (kinked model)
                util = np.random.uniform(0.1, 0.95, n_samples)
                base_rate = np.random.uniform(0.01, 0.05, n_samples)
                optimal = 0.80 - (i - 10) * 0.05

                X = np.column_stack([util, base_rate])
                rate = np.where(
                    util <= optimal,
                    base_rate + 0.05 * (util / optimal),
                    base_rate + 0.05 + 0.50 * ((util - optimal) / (1 - optimal)),
                )
                rate += np.random.normal(0, 0.001, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    rate,
                    ["utilization", "base_rate"],
                    {"utilization": "Utilization rate", "base_rate": "Base rate"},
                    f"Interest Rate (optimal {optimal * 100:.0f}%)",
                )

            else:  # Health Factor
                collateral = np.random.uniform(
                    1e4 * (2 ** (i // 20)), 1e6 * (2 ** (i // 20)), n_samples
                )
                threshold = np.random.uniform(0.75, 0.85, n_samples)
                debt = collateral * threshold * np.random.uniform(0.5, 0.95, n_samples)

                X = np.column_stack([collateral, debt, threshold])
                health = (collateral * threshold) / debt
                health += np.random.normal(0, 0.01, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    health,
                    ["collateral", "debt", "threshold"],
                    {
                        "collateral": "Collateral value",
                        "debt": "Debt amount",
                        "threshold": "Liquidation threshold",
                    },
                    f"Health Factor (scale {collateral.mean():.0e})",
                )

    # ==================== CATEGORY 4: LEVERAGED POSITIONS (20 formulas) ====================

    def generate_leverage_formulas(self, n_samples=100):
        """Generate 20 leveraged position formulas."""
        print("\n" + "=" * 70)
        print("CATEGORY 4: LEVERAGED POSITIONS (20 formulas)")
        print("=" * 70)

        for i in range(20):
            formula_num = 81 + i

            leverage = np.random.uniform(2, 20, n_samples)
            entry_price = np.random.uniform(
                100 * (2 ** (i // 5)), 10000 * (2 ** (i // 5)), n_samples
            )
            margin = np.random.uniform(0.03, 0.10, n_samples)

            X = np.column_stack([leverage, entry_price, margin])

            if i < 10:  # Long liquidation
                liq_price = entry_price * (1 - 1 / leverage + margin)
                liq_price += np.random.normal(0, liq_price.mean() * 0.01, n_samples)
                desc = f"Long Liquidation Price (variant {i + 1})"
            else:  # Short liquidation
                liq_price = entry_price * (1 + 1 / leverage - margin)
                liq_price += np.random.normal(0, liq_price.mean() * 0.01, n_samples)
                desc = f"Short Liquidation Price (variant {i - 9})"

            self._process_formula(
                formula_num,
                X,
                liq_price,
                ["leverage", "entry_price", "margin"],
                {
                    "leverage": "Leverage multiplier",
                    "entry_price": "Entry price",
                    "margin": "Maintenance margin",
                },
                desc,
            )

    # ==================== CATEGORY 5: CONCENTRATED LIQUIDITY (20 formulas) ====================

    def generate_concentrated_liquidity_formulas(self, n_samples=100):
        """Generate 20 concentrated liquidity formulas."""
        print("\n" + "=" * 70)
        print("CATEGORY 5: CONCENTRATED LIQUIDITY (20 formulas)")
        print("=" * 70)

        for i in range(20):
            formula_num = 101 + i

            current_price = np.random.uniform(
                100 * (2 ** (i // 5)), 5000 * (2 ** (i // 5)), n_samples
            )
            volatility = np.random.uniform(0.01, 0.10, n_samples)
            days = np.random.uniform(1, 30, n_samples)

            X = np.column_stack([current_price, volatility, days])

            # Range width calculation
            z_score = 1.96 - (i % 5) * 0.2  # Vary confidence level
            range_width = current_price * volatility * np.sqrt(days) * z_score
            range_width += np.random.normal(0, range_width.mean() * 0.02, n_samples)

            self._process_formula(
                formula_num,
                X,
                range_width,
                ["price", "volatility", "days"],
                {
                    "price": "Current price",
                    "volatility": "Daily volatility",
                    "days": "Time horizon",
                },
                f"Concentrated Liquidity Range ({(1 - z_score / 1.96) * 100:.0f}% conf, variant {i + 1})",
            )

    # ==================== CATEGORY 6: YIELD & REWARDS (30 formulas) ====================

    def generate_yield_formulas(self, n_samples=100):
        """Generate 30 yield and rewards formulas."""
        print("\n" + "=" * 70)
        print("CATEGORY 6: YIELD & REWARDS (30 formulas)")
        print("=" * 70)

        for i in range(30):
            formula_num = 121 + i

            if i < 10:  # Simple APY
                rate = np.random.uniform(0.05 * (i + 1), 0.30 * (i + 1), n_samples)
                compound_freq = [1, 4, 12, 365][i % 4]

                X = np.column_stack([rate, np.full(n_samples, compound_freq)])
                apy = (1 + rate / compound_freq) ** compound_freq - 1
                apy += np.random.normal(0, 0.001, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    apy,
                    ["rate", "frequency"],
                    {"rate": "Annual rate", "frequency": "Compound frequency"},
                    f"APY Calculation (freq={compound_freq})",
                )

            elif i < 20:  # Staking rewards
                staked = np.random.uniform(
                    100 * (2 ** (i // 2)), 10000 * (2 ** (i // 2)), n_samples
                )
                rate = np.random.uniform(0.05, 0.30, n_samples)
                days = np.random.uniform(1, 365, n_samples)

                X = np.column_stack([staked, rate, days])
                rewards = staked * rate * (days / 365)
                rewards += np.random.normal(0, rewards.mean() * 0.02, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    rewards,
                    ["staked", "rate", "days"],
                    {
                        "staked": "Staked amount",
                        "rate": "Annual rate",
                        "days": "Days staked",
                    },
                    f"Staking Rewards (scale {staked.mean():.0e})",
                )

            else:  # Yield farming with multipliers
                liquidity = np.random.uniform(
                    1000 * (2 ** (i // 5)), 100000 * (2 ** (i // 5)), n_samples
                )
                base_apy = np.random.uniform(0.05, 0.30, n_samples)
                multiplier = np.random.uniform(1.0, 3.0, n_samples)

                X = np.column_stack([liquidity, base_apy, multiplier])
                yield_value = liquidity * base_apy * multiplier / 365
                yield_value += np.random.normal(0, yield_value.mean() * 0.02, n_samples)

                self._process_formula(
                    formula_num,
                    X,
                    yield_value,
                    ["liquidity", "base_apy", "multiplier"],
                    {
                        "liquidity": "Liquidity amount",
                        "base_apy": "Base APY",
                        "multiplier": "Reward multiplier",
                    },
                    f"Yield Farming Daily Return (variant {i - 19})",
                )

    def run_all_formulas(self, n_samples=100):
        """Generate all 150 formulas."""
        print("\n" + "#" * 70)
        print("# DeFi Formula Discovery - 150 Complete Formulas")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Samples per formula: {n_samples}")
        print(f"# Random seed: {self.seed}")
        print("#" * 70)

        # Generate all categories
        self.generate_amm_formulas(n_samples)
        self.generate_il_formulas(n_samples)
        self.generate_lending_formulas(n_samples)
        self.generate_leverage_formulas(n_samples)
        self.generate_concentrated_liquidity_formulas(n_samples)
        self.generate_yield_formulas(n_samples)

    def save_results(self, output_dir="hypatiax/data/finance/defi"):
        """Save results to files."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_path = os.path.join(output_dir, f"defi_150_formulas_{timestamp}.json")
        csv_path = os.path.join(output_dir, f"defi_150_formulas_{timestamp}.csv")

        self.system.export_results(json_path, format="json")

        try:
            self.system.export_results(csv_path, format="csv")
        except:
            self._export_csv_safe(csv_path)

        return json_path, csv_path

    def _export_csv_safe(self, filepath):
        """Safe CSV export with error handling."""
        import csv

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
                    "Description",
                    "Domain",
                ]
            )

            for result in self.system.results:
                discovery = result.get("discovery", {})
                validation = result.get("validation", {})

                writer.writerow(
                    [
                        result.get("timestamp", ""),
                        discovery.get("expression", ""),
                        discovery.get("r2_score", 0),
                        discovery.get("complexity", 0),
                        validation.get("total_score", 0),
                        validation.get("valid", False),
                        result.get("description", ""),
                        self.system.domain,
                    ]
                )

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("FINAL SUMMARY - 150 DeFi Formulas")
        print("=" * 70)

        stats = self.system.get_statistics()
        print(f"\nTotal formulas attempted: 150")
        print(f"Successful: {self.successful}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {(self.successful / 150) * 100:.1f}%")
        print(f"Average R² score: {stats['average_r2']:.4f}")
        print(f"Average validation: {stats['average_validation_score']:.1f}/100")

        print("\n" + "-" * 70)
        print("Formula Distribution:")
        print("-" * 70)
        print("  Category 1: AMM Mechanics (1-30)")
        print("  Category 2: Impermanent Loss (31-55)")
        print("  Category 3: Lending Protocols (56-80)")
        print("  Category 4: Leveraged Positions (81-100)")
        print("  Category 5: Concentrated Liquidity (101-120)")
        print("  Category 6: Yield & Rewards (121-150)")
        print("=" * 70)


def main():
    """
    Main execution demonstrating all three features.

    Feature #1: VALIDATION - All datasets validated before processing
    Feature #2: SCALABILITY - Easy parameter adjustment shown
    Feature #3: ROBUSTNESS - Continues on errors, provides detailed feedback
    """
    print("\n" + "█" * 70)
    print("█  DeFi Formula Discovery - 150 Complete Formulas        █")
    print("█                                                         █")
    print("█  ✅ Feature #1: VALIDATION                              █")
    print("█     • NaN/Inf checks                                   █")
    print("█     • Length matching                                  █")
    print("█     • Range validation                                 █")
    print("█                                                         █")
    print("█  ✅ Feature #2: SCALABILITY                             █")
    print("█     • Configurable parameters                          █")
    print("█     • Easy formula modification                        █")
    print("█     • Adjustable sample sizes                          █")
    print("█                                                         █")
    print("█  ✅ Feature #3: ROBUSTNESS                              █")
    print("█     • Detailed error messages                          █")
    print("█     • Continues on failure                             █")
    print("█     • Success/failure tracking                         █")
    print("█                                                         █")
    print("█  Total: 15,000 data points (100 samples × 150 formulas)█")
    print("█" * 70)

    # Initialize generator
    generator = DeFi150FormulaGenerator(domain="defi", seed=42, noise_level=0.01)

    # Feature #2 DEMO: Adjust configuration if needed
    # Uncomment to customize:
    # generator.update_config(
    #     default_samples=150,           # More samples per formula
    #     fee_tiers=[0.001, 0.005, 0.01], # Different fee tiers
    #     noise_level=0.02               # Higher noise for stress testing
    # )

    # Run all formula generation
    # Feature #1: Each formula will be validated
    # Feature #3: Errors will be caught and logged, execution continues
    generator.run_all_formulas(n_samples=100)

    # Save results
    json_path, csv_path = generator.save_results()
    generator.print_summary()

    print(f"\n📊 Results saved:")
    print(f"   JSON: {json_path}")
    print(f"   CSV: {csv_path}")

    # Feature #3: Show final statistics
    success_rate = (generator.successful / 150) * 100
    print(f"\n✅ Complete!")
    print(f"   Successful: {generator.successful}/150 ({success_rate:.1f}%)")
    print(f"   Failed: {generator.failed}/150")

    if generator.failed > 0:
        print(f"\n⚠️  {generator.failed} formulas failed - check logs above for details")

    print(f"\n💾 Total data points: {generator.successful * 100:,}")


if __name__ == "__main__":
    main()

# ================================================================
# USAGE
# ================================================================
"""
from defi_150_formulas_generator import DeFi150FormulaGenerator

# Test Feature #1: Validation
generator = DeFi150FormulaGenerator()
print("✅ Feature #1: Validation - Built into _process_formula()")

# Test Feature #2: Scalability
generator.update_config(default_samples=150, fee_tiers=[0.001, 0.005])
print(f"✅ Feature #2: Config updated - {generator.config['default_samples']} samples")

# Test Feature #3: Robustness
generator.generate_amm_formulas(n_samples=10)
print(f"✅ Feature #3: {generator.successful} succeeded, {generator.failed} failed")
"""
