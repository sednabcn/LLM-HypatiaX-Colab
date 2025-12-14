#!/usr/bin/env python3
"""
HypatiaX Complete Dataset Generator
====================================
Generates comprehensive datasets for DeFi formula testing and validation:
  - Historical price data
  - Uniswap pool simulations
  - Impermanent loss scenarios
  - Formula validation cases
  - Risk scoring examples
"""

import csv
import json
import math
import os
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List


class HypatiaXDatasetGenerator:
    """Generate datasets for DeFi formula testing and validation."""

    def __init__(self, seed: int = 42, output_dir: str = "datasets"):
        """
        Initialize the dataset generator.

        Args:
            seed: Random seed for reproducibility
            output_dir: Directory to save generated datasets
        """
        random.seed(seed)
        self.seed = seed
        self.output_dir = output_dir
        self.start_date = datetime(2024, 8, 1)
        os.makedirs(output_dir, exist_ok=True)

    def generate_historical_prices(self, days: int = 90) -> List[Dict]:
        """
        Generate realistic historical price data for ETH/USDC.
        Simulates actual market conditions with trends and volatility.

        Args:
            days: Number of days of historical data
        """
        print("\n" + "=" * 70)
        print(f"Generating Historical Prices ({days} days)")
        print("=" * 70)

        prices = []
        current_price = 1800.0  # Starting ETH price

        for day in range(days):
            date = self.start_date + timedelta(days=day)

            # Add trend (slight upward bias)
            trend = random.gauss(0.002, 0.01)

            # Add volatility
            volatility = random.gauss(0, 0.03)

            # Calculate new price
            change = trend + volatility
            current_price *= 1 + change

            # Ensure reasonable bounds
            current_price = max(1000, min(4000, current_price))

            prices.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "timestamp": int(date.timestamp()),
                    "price_usd": round(current_price, 2),
                    "volume_24h": round(random.uniform(500000000, 2000000000), 2),
                    "volatility_7d": round(abs(random.gauss(0.45, 0.15)), 4),
                    "volatility_30d": round(abs(random.gauss(0.55, 0.20)), 4),
                }
            )

        print(f"✅ Generated {len(prices)} historical price records")
        return prices

    def generate_uniswap_scenarios(self) -> List[Dict]:
        """
        Generate test scenarios for Uniswap pool simulations.
        Covers various market conditions and edge cases.
        """
        print("\n" + "=" * 70)
        print("Generating Uniswap Scenarios")
        print("=" * 70)

        scenarios = []

        # Scenario 1: Stable market
        scenarios.append(
            {
                "name": "Stable Market",
                "description": "Price changes ±5% over 30 days",
                "initial_eth": 100,
                "initial_usdc": 180000,
                "initial_price": 1800,
                "final_price": 1890,
                "fee_rate": 0.003,
                "days": 30,
                "expected_il_percent": -0.31,
                "trade_count": 150,
            }
        )

        # Scenario 2: Bull market
        scenarios.append(
            {
                "name": "Bull Market",
                "description": "ETH price increases 50%",
                "initial_eth": 100,
                "initial_usdc": 180000,
                "initial_price": 1800,
                "final_price": 2700,
                "fee_rate": 0.003,
                "days": 60,
                "expected_il_percent": -5.72,
                "trade_count": 300,
            }
        )

        # Scenario 3: Bear market
        scenarios.append(
            {
                "name": "Bear Market",
                "description": "ETH price decreases 40%",
                "initial_eth": 100,
                "initial_usdc": 180000,
                "initial_price": 1800,
                "final_price": 1080,
                "fee_rate": 0.003,
                "days": 45,
                "expected_il_percent": -5.72,
                "trade_count": 225,
            }
        )

        # Scenario 4: High volatility
        scenarios.append(
            {
                "name": "High Volatility",
                "description": "Price swings ±30% multiple times",
                "initial_eth": 100,
                "initial_usdc": 180000,
                "initial_price": 1800,
                "final_price": 1800,
                "fee_rate": 0.003,
                "days": 30,
                "expected_il_percent": 0.0,
                "trade_count": 450,
            }
        )

        # Scenario 5: Large single trade
        scenarios.append(
            {
                "name": "Whale Trade",
                "description": "Single large trade impacts pool significantly",
                "initial_eth": 100,
                "initial_usdc": 180000,
                "initial_price": 1800,
                "final_price": 1850,
                "fee_rate": 0.003,
                "days": 1,
                "expected_il_percent": -0.08,
                "trade_count": 1,
            }
        )

        print(f"✅ Generated {len(scenarios)} Uniswap scenarios")
        return scenarios

    def generate_il_test_cases(self) -> List[Dict]:
        """
        Generate comprehensive IL calculation test cases.
        For validation of formula implementations.
        """
        print("\n" + "=" * 70)
        print("Generating IL Test Cases")
        print("=" * 70)

        test_cases = []

        # Test case template
        initial_prices = [1000, 1500, 2000, 2500, 3000]
        price_changes = [0.5, 0.75, 0.9, 1.0, 1.1, 1.25, 1.5, 2.0]

        for initial in initial_prices:
            for ratio in price_changes:
                final = initial * ratio

                # Calculate theoretical IL
                il_percent = (2 * math.sqrt(ratio) / (ratio + 1) - 1) * 100

                test_cases.append(
                    {
                        "initial_price": initial,
                        "final_price": final,
                        "price_ratio": ratio,
                        "initial_eth": 100,
                        "initial_usdc": 100 * initial,
                        "expected_il_percent": round(il_percent, 4),
                        "hodl_value_usd": 100 * final + 100 * initial,
                        "lp_value_usd": round(200 * math.sqrt(initial * final), 2),
                    }
                )

        print(f"✅ Generated {len(test_cases)} IL test cases")
        return test_cases

    def generate_formula_validation_cases(self) -> List[Dict]:
        """
        Generate test cases for symbolic validation.
        Tests edge cases, numerical stability, etc.
        """
        print("\n" + "=" * 70)
        print("Generating Formula Validation Cases")
        print("=" * 70)

        cases = []

        # Valid formulas
        cases.extend(
            [
                {
                    "formula_latex": r"\frac{x \cdot y}{z + 1}",
                    "domain": "defi",
                    "expected_valid": True,
                    "test_x": 100,
                    "test_y": 200,
                    "test_z": 50,
                    "expected_output": 3.92,
                    "notes": "Basic division, safe denominator",
                },
                {
                    "formula_latex": r"\sqrt{x^2 + y^2}",
                    "domain": "finance",
                    "expected_valid": True,
                    "test_x": 3,
                    "test_y": 4,
                    "test_z": 0,
                    "expected_output": 5.0,
                    "notes": "Pythagorean theorem, always positive",
                },
                {
                    "formula_latex": r"\frac{r - r_f}{\sigma}",
                    "domain": "finance",
                    "expected_valid": True,
                    "test_x": 0.12,
                    "test_y": 0.02,
                    "test_z": 0.15,
                    "expected_output": 0.667,
                    "notes": "Sharpe ratio variant",
                },
            ]
        )

        # Problematic formulas (for testing validation)
        cases.extend(
            [
                {
                    "formula_latex": r"\frac{1}{x - y}",
                    "domain": "defi",
                    "expected_valid": False,
                    "test_x": 100,
                    "test_y": 99.99,
                    "test_z": 0,
                    "expected_output": None,
                    "notes": "Division by zero risk when x = y",
                },
                {
                    "formula_latex": r"e^{x \cdot y}",
                    "domain": "risk",
                    "expected_valid": False,
                    "test_x": 10,
                    "test_y": 10,
                    "test_z": 0,
                    "expected_output": None,
                    "notes": "Exponential overflow",
                },
                {
                    "formula_latex": r"\sqrt{x - y}",
                    "domain": "defi",
                    "expected_valid": False,
                    "test_x": 100,
                    "test_y": 101,
                    "test_z": 0,
                    "expected_output": None,
                    "notes": "Sqrt of negative",
                },
            ]
        )

        print(f"✅ Generated {len(cases)} formula validation cases")
        return cases

    def generate_risk_scoring_examples(self) -> List[Dict]:
        """Generate examples for risk scoring system testing."""
        print("\n" + "=" * 70)
        print("Generating Risk Scoring Examples")
        print("=" * 70)

        examples = []

        risk_profiles = [
            {
                "name": "Conservative LP",
                "il_percent": -2.5,
                "volatility_30d": 0.25,
                "range_width": 0.5,
                "days_in_position": 90,
                "expected_risk_score": 35,
                "risk_category": "Low",
            },
            {
                "name": "Moderate LP",
                "il_percent": -8.0,
                "volatility_30d": 0.45,
                "range_width": 0.3,
                "days_in_position": 45,
                "expected_risk_score": 58,
                "risk_category": "Medium",
            },
            {
                "name": "Aggressive LP",
                "il_percent": -15.0,
                "volatility_30d": 0.75,
                "range_width": 0.15,
                "days_in_position": 14,
                "expected_risk_score": 82,
                "risk_category": "High",
            },
        ]

        examples.extend(risk_profiles)
        print(f"✅ Generated {len(examples)} risk scoring examples")
        return examples

    def generate_real_pool_snapshots(self) -> List[Dict]:
        """
        Generate realistic pool snapshots for testing.
        Based on actual Uniswap v2 ETH/USDC data patterns.
        """
        print("\n" + "=" * 70)
        print("Generating Real Pool Snapshots")
        print("=" * 70)

        snapshots = []

        # Popular pool states
        snapshots.append(
            {
                "pool_address": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",
                "name": "ETH/USDC 0.3%",
                "timestamp": "2024-11-01T12:00:00Z",
                "eth_reserves": 45678.234,
                "usdc_reserves": 89234567.89,
                "price": 1953.45,
                "tvl_usd": 178469135.78,
                "volume_24h": 125678234.56,
                "fees_24h": 377034.70,
                "apr_7d": 0.187,
            }
        )

        print(f"✅ Generated {len(snapshots)} pool snapshots")
        return snapshots

    def save_datasets(self):
        """Save all datasets to files."""
        print("\n" + "#" * 70)
        print("# SAVING DATASETS")
        print(f"# Output directory: {self.output_dir}")
        print(f"# Timestamp: {datetime.now().isoformat()}")
        print("#" * 70)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}

        # Generate all datasets
        datasets = {
            "historical_prices": self.generate_historical_prices(),
            "uniswap_scenarios": self.generate_uniswap_scenarios(),
            "il_test_cases": self.generate_il_test_cases(),
            "formula_validation_cases": self.generate_formula_validation_cases(),
            "risk_scoring_examples": self.generate_risk_scoring_examples(),
            "real_pool_snapshots": self.generate_real_pool_snapshots(),
        }

        for name, data in datasets.items():
            # Save as JSON
            json_path = os.path.join(self.output_dir, f"{name}_{timestamp}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            saved_files[f"{name}_json"] = json_path

            # Save as CSV if list of dicts with consistent keys
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                csv_path = os.path.join(self.output_dir, f"{name}_{timestamp}.csv")
                try:
                    # Get all unique keys from all records
                    all_keys = set()
                    for record in data:
                        all_keys.update(record.keys())

                    fieldnames = sorted(all_keys)

                    with open(csv_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                        writer.writeheader()

                        # Fill missing keys with empty strings
                        for record in data:
                            row = {key: record.get(key, "") for key in fieldnames}
                            writer.writerow(row)

                    saved_files[f"{name}_csv"] = csv_path
                    print(f"✅ Saved CSV: {csv_path}")
                except Exception as e:
                    print(f"⚠️  Warning: Could not save {name} as CSV: {e}")

        return saved_files

    def print_summary(self):
        """Print comprehensive summary."""
        print("\n" + "=" * 70)
        print("DATASET GENERATION SUMMARY")
        print("=" * 70)

        print(f"\nGenerated Datasets:")
        print(f"  1. Historical Prices - 90 days of ETH/USDC data")
        print(f"  2. Uniswap Scenarios - 5 market condition scenarios")
        print(f"  3. IL Test Cases - 40 comprehensive test cases")
        print(f"  4. Formula Validation - 6 validation cases")
        print(f"  5. Risk Scoring - 3 risk profile examples")
        print(f"  6. Pool Snapshots - Real pool data patterns")

        print(f"\nOutput Format:")
        print(f"  - JSON (programmatic use)")
        print(f"  - CSV (Excel, visualization)")

        print("=" * 70)

    def run_all(self):
        """Generate all datasets and save."""
        print("\n" + "=" * 70)
        print("HYPATIAX DATASET GENERATOR")
        print("=" * 70)

        # Save all datasets
        saved_files = self.save_datasets()

        # Print summary
        self.print_summary()

        return saved_files


def main():
    """Main execution function."""
    generator = HypatiaXDatasetGenerator(seed=42, output_dir="hypatiax/data/datasets")

    # Generate and save all datasets
    files = generator.run_all()

    print(f"\n📁 Files saved:")
    for name, path in files.items():
        print(f"   {name}: {path}")


if __name__ == "__main__":
    try:
        main()
        print("\n✅ Dataset generation completed successfully!\n")
    except Exception as e:
        print(f"\n❌ Error during dataset generation: {e}\n")
        import traceback

        traceback.print_exc()
