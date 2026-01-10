#!/usr/bin/env python3
"""
Generate PURE TEST DATA for DeFi formulas (no discovery, just data)
This creates the input datasets that run_discovery.py will process
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


class DeFiTestDataGenerator:
    """Generate test data for DeFi formulas WITHOUT running discovery."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        np.random.seed(seed)

    def generate_impermanent_loss_data(self, n_samples: int = 100) -> List[Dict]:
        """Generate IL test cases with ground truth."""
        print(f"Generating {n_samples} IL test cases...")

        test_cases = []
        for i in range(n_samples):
            initial_price = np.random.uniform(100, 5000)
            final_price = initial_price * np.random.uniform(0.5, 2.0)
            price_ratio = final_price / initial_price

            # Ground truth IL formula
            expected_il = 2 * np.sqrt(price_ratio) / (1 + price_ratio) - 1

            # Initial positions
            initial_eth = np.random.uniform(1, 100)
            initial_usdc = initial_eth * initial_price

            # Calculate values
            hodl_value = initial_eth * final_price + initial_usdc

            # LP value with IL
            k = initial_eth * initial_usdc
            final_eth = np.sqrt(k / final_price)
            final_usdc = np.sqrt(k * final_price)
            lp_value = final_eth * final_price + final_usdc

            test_cases.append(
                {
                    "test_id": i + 1,
                    "initial_price": initial_price,
                    "final_price": final_price,
                    "price_ratio": price_ratio,
                    "initial_eth": initial_eth,
                    "initial_usdc": initial_usdc,
                    "expected_il_percent": expected_il * 100,
                    "hodl_value_usd": hodl_value,
                    "lp_value_usd": lp_value,
                    "actual_il_percent": ((lp_value - hodl_value) / hodl_value) * 100,
                }
            )

        return test_cases

    def generate_amm_swap_data(self, n_samples: int = 100) -> List[Dict]:
        """Generate AMM swap test cases."""
        print(f"Generating {n_samples} AMM swap test cases...")

        test_cases = []
        for i in range(n_samples):
            reserve_in = np.random.uniform(10000, 1000000)
            reserve_out = np.random.uniform(10000, 1000000)
            amount_in = np.random.uniform(10, reserve_in * 0.1)
            fee_rate = 0.003  # 0.3%

            # Ground truth: constant product formula
            amount_in_with_fee = amount_in * (1 - fee_rate)
            amount_out = (amount_in_with_fee * reserve_out) / (
                reserve_in + amount_in_with_fee
            )

            # Price impact
            spot_price_before = reserve_out / reserve_in
            effective_price = amount_out / amount_in
            price_impact = (spot_price_before - effective_price) / spot_price_before

            test_cases.append(
                {
                    "test_id": i + 1,
                    "reserve_in": reserve_in,
                    "reserve_out": reserve_out,
                    "amount_in": amount_in,
                    "fee_rate": fee_rate,
                    "expected_amount_out": amount_out,
                    "spot_price_before": spot_price_before,
                    "effective_price": effective_price,
                    "price_impact_percent": price_impact * 100,
                }
            )

        return test_cases

    def generate_utilization_data(self, n_samples: int = 100) -> List[Dict]:
        """Generate utilization rate test cases."""
        print(f"Generating {n_samples} utilization test cases...")

        test_cases = []
        for i in range(n_samples):
            total_supplied = np.random.uniform(1000000, 100000000)
            target_util = np.random.uniform(0.3, 0.9)
            total_borrowed = (
                total_supplied * target_util * np.random.uniform(0.95, 1.05)
            )
            total_borrowed = min(total_borrowed, total_supplied * 0.99)

            utilization_rate = total_borrowed / total_supplied

            test_cases.append(
                {
                    "test_id": i + 1,
                    "total_supplied": total_supplied,
                    "total_borrowed": total_borrowed,
                    "utilization_rate": utilization_rate,
                    "utilization_percent": utilization_rate * 100,
                }
            )

        return test_cases

    def generate_liquidity_value_data(self, n_samples: int = 100) -> List[Dict]:
        """Generate liquidity pool value test cases."""
        print(f"Generating {n_samples} liquidity value test cases...")

        test_cases = []
        for i in range(n_samples):
            reserve0 = np.random.uniform(1000, 100000)
            reserve1 = np.random.uniform(1000, 100000)

            # Constant product: k = x * y
            k = reserve0 * reserve1
            liquidity = np.sqrt(k)

            # Total value (assuming equal USD value)
            total_value = 2 * liquidity

            test_cases.append(
                {
                    "test_id": i + 1,
                    "reserve0": reserve0,
                    "reserve1": reserve1,
                    "k": k,
                    "liquidity": liquidity,
                    "total_value_usd": total_value,
                }
            )

        return test_cases

    def generate_concentrated_liquidity_data(self, n_samples: int = 100) -> List[Dict]:
        """Generate Uniswap V3 concentrated liquidity test cases."""
        print(f"Generating {n_samples} concentrated liquidity test cases...")

        test_cases = []
        for i in range(n_samples):
            current_price = np.random.uniform(1000, 5000)
            volatility_daily = np.random.uniform(0.01, 0.10)
            days_horizon = np.random.uniform(1, 30)

            # Optimal range: ±2σ (95% confidence)
            price_std = current_price * volatility_daily * np.sqrt(days_horizon)
            lower_price = current_price - 1.96 * price_std
            upper_price = current_price + 1.96 * price_std

            range_width = upper_price - lower_price

            test_cases.append(
                {
                    "test_id": i + 1,
                    "current_price": current_price,
                    "daily_volatility": volatility_daily,
                    "days_horizon": days_horizon,
                    "lower_price": lower_price,
                    "upper_price": upper_price,
                    "range_width": range_width,
                    "concentration_factor": current_price / range_width,
                }
            )

        return test_cases

    def generate_health_factor_data(self, n_samples: int = 100) -> List[Dict]:
        """Generate health factor test cases."""
        print(f"Generating {n_samples} health factor test cases...")

        test_cases = []
        for i in range(n_samples):
            collateral_value = np.random.uniform(10000, 500000)
            liquidation_threshold = np.random.uniform(0.75, 0.85)
            borrowed_value = (
                collateral_value * liquidation_threshold * np.random.uniform(0.5, 0.95)
            )

            # Health factor formula: (collateral * liq_threshold) / borrowed
            health_factor = (collateral_value * liquidation_threshold) / borrowed_value

            is_safe = health_factor >= 1.0
            liquidation_price_change = (1 / health_factor - 1) * 100

            test_cases.append(
                {
                    "test_id": i + 1,
                    "collateral_value_usd": collateral_value,
                    "borrowed_value_usd": borrowed_value,
                    "liquidation_threshold": liquidation_threshold,
                    "health_factor": health_factor,
                    "is_safe": is_safe,
                    "liquidation_price_change_percent": liquidation_price_change,
                }
            )

        return test_cases

    def save_all_datasets(self, output_dir: str = "test_data", n_samples: int = 100):
        """Generate and save all test datasets."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print("\n" + "=" * 70)
        print("GENERATING DEFI TEST DATA".center(70))
        print("=" * 70)
        print(f"\nOutput directory: {output_path}")
        print(f"Samples per dataset: {n_samples}")
        print(f"Timestamp: {timestamp}\n")

        datasets = {
            "impermanent_loss": self.generate_impermanent_loss_data(n_samples),
            "amm_swaps": self.generate_amm_swap_data(n_samples),
            "utilization_rates": self.generate_utilization_data(n_samples),
            "liquidity_values": self.generate_liquidity_value_data(n_samples),
            "concentrated_liquidity": self.generate_concentrated_liquidity_data(
                n_samples
            ),
            "health_factors": self.generate_health_factor_data(n_samples),
        }

        saved_files = []
        for name, data in datasets.items():
            filename = f"{name}_{timestamp}.json"
            filepath = output_path / filename

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            saved_files.append(filepath)
            print(f"✅ Saved: {filename} ({len(data)} test cases)")

        # Create manifest
        manifest = {
            "generated_at": timestamp,
            "seed": self.seed,
            "datasets": {
                name: {
                    "filename": f"{name}_{timestamp}.json",
                    "samples": len(data),
                    "description": self._get_description(name),
                }
                for name, data in datasets.items()
            },
        }

        manifest_path = output_path / f"manifest_{timestamp}.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Manifest: {manifest_path.name}")

        print("\n" + "=" * 70)
        print("TEST DATA GENERATION COMPLETE".center(70))
        print("=" * 70)
        print(
            f"\nGenerated {len(datasets)} datasets with {sum(len(d) for d in datasets.values())} total test cases"
        )
        print(f"\nNext step: Run discovery")
        print(f"  python run_discovery.py --test-data {output_dir}")

        return saved_files

    def _get_description(self, name: str) -> str:
        descriptions = {
            "impermanent_loss": "IL test cases with price ratios and expected losses",
            "amm_swaps": "AMM swap calculations with reserves and amounts",
            "utilization_rates": "Lending pool utilization rates",
            "liquidity_values": "Pool liquidity and TVL calculations",
            "concentrated_liquidity": "Uniswap V3 range calculations",
            "health_factors": "Lending position health factors",
        }
        return descriptions.get(name, "DeFi test data")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate DeFi test datasets")
    parser.add_argument(
        "--output",
        "-o",
        default="test_data",
        help="Output directory (default: test_data)",
    )
    parser.add_argument(
        "--samples",
        "-n",
        type=int,
        default=100,
        help="Samples per dataset (default: 100)",
    )
    parser.add_argument(
        "--seed", "-s", type=int, default=42, help="Random seed (default: 42)"
    )

    args = parser.parse_args()

    generator = DeFiTestDataGenerator(seed=args.seed)
    generator.save_all_datasets(output_dir=args.output, n_samples=args.samples)


if __name__ == "__main__":
    main()
