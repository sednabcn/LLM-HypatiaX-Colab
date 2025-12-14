"""
DeFi Formula Discovery Dataset Generator - MASSIVE SCALE
Generates 280 formula variations with 20 samples each = 5,600 total data points
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np

from hypatiax.tools.symbolic.hybrid_system import HybridDiscoverySystem


class MassiveDeFiFormulaGenerator:
    """Generate massive DeFi dataset with 280 formula variations."""

    def __init__(self, domain: str = "defi", seed: int = 42):
        """Initialize the generator."""
        self.system = HybridDiscoverySystem(domain=domain, max_results=500)
        self.seed = seed
        np.random.seed(seed)
        self.results = []
        self.formula_id = 0
        self.successful_formulas = 0
        self.failed_formulas = 0

    def _generate_formula_variant(
        self, base_name: str, variation_idx: int, n_samples: int = 20
    ) -> Tuple[np.ndarray, np.ndarray, str]:
        """Helper to generate formula variants with different parameters."""
        pass

    # ===================== CONSTANT PRODUCT VARIANTS (30 formulas) =====================

    def generate_constant_product_variants(self, n_samples: int = 20):
        """x × y = k with different reserve ranges and fee tiers"""
        for variation in range(30):
            self.formula_id += 1

            # Vary reserve ranges
            x_min, x_max = 10 * (2 ** (variation // 10)), 100 * (2 ** (variation // 10))
            y_min, y_max = 10 * (2 ** (variation % 10)), 100 * (2 ** (variation % 10))

            token_x = np.random.uniform(x_min, x_max, n_samples)
            token_y = np.random.uniform(y_min, y_max, n_samples)

            X_data = np.column_stack([token_x, token_y])
            k = token_x * token_y
            k += np.random.normal(0, k.mean() * 0.01, n_samples)

            name = f"Constant_Product_v{variation}"
            description = f"Constant Product with reserves [{x_min:.0f}-{x_max:.0f}] × [{y_min:.0f}-{y_max:.0f}]"

            self._process_formula(name, description, X_data, k, n_samples)

    # ===================== CONSTANT SUM VARIANTS (25 formulas) =====================

    def generate_constant_sum_variants(self, n_samples: int = 20):
        """x + y = k with different weight ratios and ranges"""
        for variation in range(25):
            self.formula_id += 1

            scale = 100 * (2 ** (variation // 5))
            weight_x = 0.3 + (variation % 5) * 0.14  # 0.3 to 0.86
            weight_y = 1 - weight_x

            token_x = np.random.uniform(scale * weight_x, scale * weight_x * 10, n_samples)
            token_y = np.random.uniform(scale * weight_y, scale * weight_y * 10, n_samples)

            X_data = np.column_stack([token_x, token_y])
            k = token_x + token_y
            k += np.random.normal(0, 50, n_samples)

            name = f"Constant_Sum_v{variation}"
            description = f"Constant Sum with weight ratio {weight_x:.2f}:{weight_y:.2f}"

            self._process_formula(name, description, X_data, k, n_samples)

    # ===================== CONSTANT MEAN VARIANTS (20 formulas) =====================

    def generate_constant_mean_variants(self, n_samples: int = 20):
        """(x × y × z)^(1/3) = k with different powers"""
        for variation in range(20):
            self.formula_id += 1

            scale = 100 * (2 ** (variation // 5))
            power = 1 / (2 + (variation % 5) * 0.25)  # Powers from 1/2 to 1/6

            token_x = np.random.uniform(scale, scale * 50, n_samples)
            token_y = np.random.uniform(scale, scale * 50, n_samples)
            token_z = np.random.uniform(scale, scale * 50, n_samples)

            X_data = np.column_stack([token_x, token_y, token_z])
            k = (token_x * token_y * token_z) ** power
            k += np.random.normal(0, k.mean() * 0.01, n_samples)

            name = f"Constant_Mean_v{variation}"
            description = f"Constant Mean with power {power:.3f}"

            self._process_formula(name, description, X_data, k, n_samples)

    # ===================== STABLESWAP HYBRID VARIANTS (25 formulas) =====================

    def generate_stableswap_variants(self, n_samples: int = 20):
        """Hybrid formulas with different amplification factors"""
        for variation in range(25):
            self.formula_id += 1

            amplification = 1 + (variation % 5) * 200  # 1, 201, 401, 601, 801
            scale = 1000 * (2 ** (variation // 5))

            token_x = np.random.uniform(scale, scale * 10, n_samples)
            token_y = np.random.uniform(scale, scale * 10, n_samples)

            X_data = np.column_stack([token_x, token_y])

            # Simplified hybrid: combines product and sum with amplification
            product = token_x * token_y
            sum_term = token_x + token_y
            output = (amplification * product + sum_term**2 / 4) / (amplification + 1)
            output += np.random.normal(0, output.mean() * 0.01, n_samples)

            name = f"StableSwap_v{variation}"
            description = f"Hybrid StableSwap with amplification factor {amplification}"

            self._process_formula(name, description, X_data, output, n_samples)

    # ===================== IMPERMANENT LOSS VARIANTS (30 formulas) =====================

    def generate_impermanent_loss_variants(self, n_samples: int = 20):
        """IL with different price range dynamics and volatility scenarios"""
        for variation in range(30):
            self.formula_id += 1

            # Different price ranges and volatility
            price_min = 0.01 * (2 ** (variation // 15))
            price_max = 100 * (2 ** (variation // 15))

            price_ratio = np.random.uniform(price_min, price_max, (n_samples, 1))

            # Base IL formula with slight variations
            il = 2 * np.sqrt(price_ratio[:, 0]) / (1 + price_ratio[:, 0]) - 1
            volatility = 0.001 + (variation % 5) * 0.002
            il += np.random.normal(0, volatility, n_samples)

            name = f"Impermanent_Loss_v{variation}"
            description = f"IL scenario: price range [{price_min:.2f}x, {price_max:.2f}x]"

            self._process_formula(name, description, price_ratio, il, n_samples)

    # ===================== POSITION VALUE VARIANTS (35 formulas) =====================

    def generate_position_value_variants(self, n_samples: int = 20):
        """LP position values with different capital levels and market conditions"""
        for variation in range(35):
            self.formula_id += 1

            capital_tier = 10 ** (3 + (variation // 7))  # From $1k to $100M

            lp_share = np.random.uniform(0.001 + (variation % 7) * 0.07, 0.07 + (variation % 7) * 0.07, n_samples)
            asset_value = np.random.uniform(capital_tier, capital_tier * 100, n_samples)

            X_data = np.column_stack([lp_share, asset_value])
            position_value = lp_share * asset_value
            position_value += np.random.normal(0, position_value.mean() * 0.01, n_samples)

            name = f"Position_Value_v{variation}"
            description = f"LP Position: capital tier ${capital_tier:.0e}"

            self._process_formula(name, description, X_data, position_value, n_samples)

    # ===================== CONCENTRATED LIQUIDITY VARIANTS (28 formulas) =====================

    def generate_concentrated_liquidity_variants(self, n_samples: int = 20):
        """Uniswap V3 with different concentration levels and price ranges"""
        for variation in range(28):
            self.formula_id += 1

            concentration = 1 + (variation % 7) * 50  # 1x to 301x multiplier
            reserve_scale = 1000 * (2 ** (variation // 7))

            virtual_x = np.random.uniform(reserve_scale, reserve_scale * 10, n_samples)
            virtual_y = np.random.uniform(reserve_scale, reserve_scale * 10, n_samples)
            price = np.random.uniform(0.5, 2.0, n_samples)

            X_data = np.column_stack([virtual_x, virtual_y, price])
            value = concentration * 2 * np.sqrt(virtual_x * virtual_y) * price
            value += np.random.normal(0, value.mean() * 0.01, n_samples)

            name = f"Concentrated_Liquidity_v{variation}"
            description = f"Uniswap V3: concentration {concentration}x"

            self._process_formula(name, description, X_data, value, n_samples)

    # ===================== FEE EARNING VARIANTS (32 formulas) =====================

    def generate_fee_earning_variants(self, n_samples: int = 20):
        """Fee calculations with different protocols and market conditions"""
        for variation in range(32):
            self.formula_id += 1

            protocol_tier = variation % 4  # Different protocols
            market_condition = variation // 4  # Different market states

            fee_tiers = [0.001, 0.005, 0.01, 0.03]
            fee_tier = fee_tiers[protocol_tier]

            volume_base = 1e6 * (2**market_condition)
            volume_24h = np.random.uniform(volume_base, volume_base * 10, n_samples)
            user_liq = np.random.uniform(10000, 1000000, n_samples)
            total_liq = user_liq * np.random.uniform(5, 100, n_samples)

            X_data = np.column_stack([volume_24h, user_liq, total_liq])
            fees = fee_tier * volume_24h * (user_liq / (total_liq + user_liq))
            fees += np.random.normal(0, fees.mean() * 0.05, n_samples)

            name = f"Fee_Earnings_v{variation}"
            description = f"Fees: tier {fee_tier*100:.1f}%, market condition {market_condition}"

            self._process_formula(name, description, X_data, fees, n_samples)

    # ===================== APY VARIANTS (20 formulas) =====================

    def generate_apy_variants(self, n_samples: int = 20):
        """APY with different compounding frequencies and yield levels"""
        for variation in range(20):
            self.formula_id += 1

            yield_level = 0.01 + (variation % 5) * 0.12  # 1% to 49%
            compound_freqs = [1, 4, 12, 365]
            freq = compound_freqs[variation // 5]

            annual_rate = np.random.uniform(yield_level, yield_level * 1.5, n_samples)

            X_data = np.column_stack([annual_rate, np.full(n_samples, freq)])
            apy = (1 + annual_rate / freq) ** freq - 1
            apy += np.random.normal(0, apy.mean() * 0.02, n_samples)

            name = f"APY_v{variation}"
            description = f"APY: yield {yield_level*100:.0f}%, compounding {freq}x/year"

            self._process_formula(name, description, X_data, apy, n_samples)

    # ===================== SLIPPAGE VARIANTS (35 formulas) =====================

    def generate_slippage_variants(self, n_samples: int = 20):
        """Slippage under different trade sizes and liquidity conditions"""
        for variation in range(35):
            self.formula_id += 1

            trade_size_pct = 0.001 + (variation % 7) * 0.07  # 0.1% to 49% of liquidity
            liquidity_scale = 1e6 * (2 ** (variation // 7))  # Different pool sizes

            trade_size = np.random.uniform(
                liquidity_scale * trade_size_pct * 0.5, liquidity_scale * trade_size_pct * 1.5, n_samples
            )
            liquidity = np.random.uniform(liquidity_scale, liquidity_scale * 10, n_samples)

            X_data = np.column_stack([trade_size, liquidity])
            slippage = (trade_size / liquidity) ** 2 * 100  # As percentage
            slippage += np.random.normal(0, slippage.mean() * 0.05, n_samples)

            name = f"Slippage_v{variation}"
            description = f"Slippage: pool size ${liquidity_scale:.0e}"

            self._process_formula(name, description, X_data, slippage, n_samples)

    # ===================== PRICE IMPACT VARIANTS (20 formulas) =====================

    def generate_price_impact_variants(self, n_samples: int = 20):
        """Price impact under different market depth conditions"""
        for variation in range(20):
            self.formula_id += 1

            depth_factor = 0.5 + (variation % 5) * 0.5  # Market depth variations
            pool_scale = 1e6 * (2 ** (variation // 5))

            trade_amount = np.random.uniform(1000, 100000, n_samples)
            pool_depth = pool_scale * np.random.uniform(depth_factor, depth_factor * 2, n_samples)

            X_data = np.column_stack([trade_amount, pool_depth])
            impact = (trade_amount / pool_depth) * 100
            impact += np.random.normal(0, impact.mean() * 0.03, n_samples)

            name = f"Price_Impact_v{variation}"
            description = f"Price impact: pool scale ${pool_scale:.0e}"

            self._process_formula(name, description, X_data, impact, n_samples)

    # ===================== UTILIZATION RATE VARIANTS (25 formulas) =====================

    def generate_utilization_variants(self, n_samples: int = 20):
        """Lending pool utilization under different protocol parameters"""
        for variation in range(25):
            self.formula_id += 1

            pool_size = 1e5 * (2 ** (variation // 5))
            target_util = 0.3 + (variation % 5) * 0.14  # 30% to 86%

            borrowed = np.random.uniform(0, pool_size * target_util, n_samples)
            supplied = borrowed / (target_util + 0.01 + np.random.uniform(-0.05, 0.05, n_samples))

            X_data = np.column_stack([borrowed, supplied])
            util_rate = borrowed / (supplied + 1)
            util_rate += np.random.normal(0, 0.01, n_samples)

            name = f"Utilization_v{variation}"
            description = f"Utilization: pool ${pool_size:.0e}, target {target_util*100:.0f}%"

            self._process_formula(name, description, X_data, util_rate, n_samples)

    # ===================== SWAP OUTPUT VARIANTS (30 formulas) =====================

    def generate_swap_output_variants(self, n_samples: int = 20):
        """AMM swap outputs with different fee structures"""
        for variation in range(30):
            self.formula_id += 1

            fee_pct = 0.1 + (variation % 6) * 0.48  # 0.1% to 3.1%
            fee_multiplier = 1 - (fee_pct / 100)
            reserve_scale = 1000 * (2 ** (variation // 6))

            amount_in = np.random.uniform(1, 100, n_samples)
            reserve_in = np.random.uniform(reserve_scale, reserve_scale * 100, n_samples)
            reserve_out = np.random.uniform(reserve_scale, reserve_scale * 100, n_samples)

            X_data = np.column_stack([amount_in, reserve_in, reserve_out])
            output = (amount_in * fee_multiplier * reserve_out) / (reserve_in + amount_in * fee_multiplier)
            output += np.random.normal(0, 0.1, n_samples)

            name = f"Swap_Output_v{variation}"
            description = f"Swap: fee {fee_pct:.1f}%, pool scale {reserve_scale:.0e}"

            self._process_formula(name, description, X_data, output, n_samples)

    def _process_formula(self, name: str, description: str, X: np.ndarray, y: np.ndarray, n_samples: int):
        """Common formula processing."""
        try:
            result = self.system.discover_validate_interpret(
                X=X,
                y=y,
                variable_names=[f"var_{i}" for i in range(X.shape[1])],
                variable_descriptions={f"var_{i}": f"Variable {i}" for i in range(X.shape[1])},
                variable_units={f"var_{i}": "dimensionless" for i in range(X.shape[1])},
                description=description,
                validate_first=False,
            )
            self.results.append((name, result))
            self.successful_formulas += 1
            if self.formula_id % 20 == 0:
                print(f"✓ Processed {self.formula_id} formulas... ({self.successful_formulas} successful)")
        except Exception as e:
            self.failed_formulas += 1
            if self.formula_id % 50 == 0:
                print(f"  ({self.failed_formulas} failures)")

    def run_all_variants(self, n_samples: int = 20):
        """Generate all 280 formula variations."""
        print("\n" + "#" * 70)
        print("# DeFi Formula Discovery - MASSIVE SCALE")
        print(f"# Generating 280 formula variations × {n_samples} samples = 5,600 data points")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print(f"# Random seed: {self.seed}")
        print("#" * 70)

        generators = [
            ("Constant Product (30 variants)", self.generate_constant_product_variants),
            ("Constant Sum (25 variants)", self.generate_constant_sum_variants),
            ("Constant Mean (20 variants)", self.generate_constant_mean_variants),
            ("StableSwap Hybrid (25 variants)", self.generate_stableswap_variants),
            ("Impermanent Loss (30 variants)", self.generate_impermanent_loss_variants),
            ("Position Value (35 variants)", self.generate_position_value_variants),
            ("Concentrated Liquidity (28 variants)", self.generate_concentrated_liquidity_variants),
            ("Fee Earnings (32 variants)", self.generate_fee_earning_variants),
            ("APY (20 variants)", self.generate_apy_variants),
            ("Slippage (35 variants)", self.generate_slippage_variants),
            ("Price Impact (20 variants)", self.generate_price_impact_variants),
            ("Utilization (25 variants)", self.generate_utilization_variants),
            ("Swap Output (30 variants)", self.generate_swap_output_variants),
        ]

        for category_name, gen_func in generators:
            print(f"\n{'='*70}")
            print(f"Generating: {category_name}")
            print(f"{'='*70}")
            gen_func(n_samples)

        return self.successful_formulas

    def save_results(self, output_dir: str = "hypatiax/data/finance/defi"):
        """
        Save results to files.

        Args:
        output_dir: Directory to save results
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save all results in one file
        json_path = os.path.join(output_dir, f"defi_enhanced_all_{timestamp}.json")
        csv_path = os.path.join(output_dir, f"defi_enhanced_all_{timestamp}.csv")

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
                        interpretation.get("interpretation", "")[:100] if interpretation else "",
                        metadata.get("llm_provider", ""),
                        self.system.domain,
                    ]
                )

        print(f"   CSV exported safely: {filepath}")

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("FINAL SUMMARY - 280 Formula Variations")
        print("=" * 70)

        print(f"\nTotal formulas generated: {self.formula_id}")
        print(f"Successful: {self.successful_formulas}")
        print(f"Failed: {self.failed_formulas}")
        print(f"Success rate: {(self.successful_formulas/self.formula_id)*100:.1f}%")
        print(f"Total data points: {self.successful_formulas * 20:,}")
        print("\n" + "=" * 70)


def main():
    """Main execution function."""
    print("\n" + "█" * 70)
    print("█  DeFi Formula Discovery - 280 Formulas × 20 Samples  █")
    print("█  Total: 5,600 Data Points  █")
    print("█" * 70)

    generator = MassiveDeFiFormulaGenerator(domain="defi", seed=42)
    successful = generator.run_all_variants(n_samples=20)

    # Save results
    json_path, csv_path = generator.save_results()
    print(f"\n📁 Results saved:")
    print(f"   JSON: {json_path}")
    print(f"   CSV: {csv_path}")

    generator.print_summary()

    print(f"\n✓ Complete! Generated {successful} formulas with 5,600+ data points")


if __name__ == "__main__":
    main()
