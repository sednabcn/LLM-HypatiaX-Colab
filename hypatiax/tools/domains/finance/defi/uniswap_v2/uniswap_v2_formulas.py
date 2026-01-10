"""
Enhanced Uniswap V2 Formulas with Safety Constraints
uniswap_v2_formulas.py

UPDATES (Week 2, Day 1-2):
- Added explicit constraint r > 0 for IL formulas
- Implemented epsilon guards for division operations
- Added price positivity constraints (Pt, P0 > 0)
- Added fee upper bounds (φ < 1)
- Enhanced input validation and error handling
- Added safe math operations throughout
"""

import csv
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================================
# MATHEMATICAL FORMULAS WITH CONSTRAINTS
# ============================================================================
"""
1. CONSTANT PRODUCT FORMULA (AMM):
   x * y = k (where k is constant)
   CONSTRAINTS: x > 0, y > 0

2. SWAP OUTPUT (with fee):
   amount_out = (y * amount_in_after_fee) / (x + amount_in_after_fee)
   where: amount_in_after_fee = amount_in * (1 - fee_rate)
   CONSTRAINTS: amount_in > 0, fee_rate ∈ [0, 1), x > 0, y > 0

3. IMPERMANENT LOSS (IL):
   IL% = [2*sqrt(price_ratio) / (price_ratio + 1) - 1] * 100
   where: price_ratio = current_price / initial_price
   CONSTRAINTS: price_ratio > 0 (r > 0)

4. IL IN DOLLARS:
   IL$ = (initial_x * current_price + initial_y) * (IL% / 100)
   CONSTRAINTS: prices > 0, amounts > 0

5. DAILY FEES EARNED:
   daily_fees = (daily_volume * fee_rate * pool_tvl_share)
   CONSTRAINTS: volume ≥ 0, fee_rate ∈ [0, 1), tvl > 0

6. NET RESULT:
   net = total_fees_earned - IL_dollar_amount

7. BREAKEVEN TIME:
   breakeven_days = |IL$| / daily_fees (days to recover IL through fees)
   CONSTRAINTS: daily_fees > 0
"""

# Safety constants
EPSILON = 1e-10  # Minimum value to prevent division by zero
MAX_FEE_RATE = 0.9999  # Maximum allowed fee (< 1)
MIN_PRICE = 1e-10  # Minimum positive price
MAX_PRICE_RATIO = 1e6  # Maximum price ratio to prevent overflow


@dataclass
class LPPosition:
    """Represents an LP position in a Uniswap V2 pool with validation"""

    name: str
    initial_token_a_amount: float
    initial_token_b_amount: float
    initial_price_b_in_a: float
    current_price_b_in_a: float
    days_elapsed: int
    daily_volume_usd: float
    fee_rate: float = 0.003
    pool_tvl_usd: float = 1_000_000

    def __post_init__(self):
        """Validate position parameters on initialization"""
        errors = []

        # Validate amounts
        if self.initial_token_a_amount <= 0:
            errors.append(
                f"initial_token_a_amount must be > 0, got {self.initial_token_a_amount}"
            )
        if self.initial_token_b_amount <= 0:
            errors.append(
                f"initial_token_b_amount must be > 0, got {self.initial_token_b_amount}"
            )

        # Validate prices (P0, Pt > 0)
        if self.initial_price_b_in_a <= 0:
            errors.append(
                f"initial_price_b_in_a must be > 0, got {self.initial_price_b_in_a}"
            )
        if self.current_price_b_in_a <= 0:
            errors.append(
                f"current_price_b_in_a must be > 0, got {self.current_price_b_in_a}"
            )

        # Validate fee rate (φ ∈ [0, 1))
        if not (0 <= self.fee_rate < 1):
            errors.append(f"fee_rate must be in [0, 1), got {self.fee_rate}")

        # Validate other parameters
        if self.days_elapsed < 0:
            errors.append(f"days_elapsed must be >= 0, got {self.days_elapsed}")
        if self.daily_volume_usd < 0:
            errors.append(f"daily_volume_usd must be >= 0, got {self.daily_volume_usd}")
        if self.pool_tvl_usd <= 0:
            errors.append(f"pool_tvl_usd must be > 0, got {self.pool_tvl_usd}")

        if errors:
            raise ValueError(f"Invalid LPPosition '{self.name}': " + "; ".join(errors))


class UniswapV2Pool:
    """Core Uniswap V2 pool implementation with safe math"""

    def __init__(self, reserve_x: float, reserve_y: float, fee: float = 0.003):
        """
        Initialize a Uniswap V2 pool with validation

        Args:
            reserve_x: Reserve amount of token X (must be > 0)
            reserve_y: Reserve amount of token Y (must be > 0)
            fee: Fee rate (must be in [0, 1), default 0.3%)
        """
        # Validate inputs
        if reserve_x <= 0:
            raise ValueError(f"reserve_x must be > 0, got {reserve_x}")
        if reserve_y <= 0:
            raise ValueError(f"reserve_y must be > 0, got {reserve_y}")
        if not (0 <= fee < 1):
            raise ValueError(f"fee must be in [0, 1), got {fee}")

        self.x = max(reserve_x, EPSILON)  # Safe guard
        self.y = max(reserve_y, EPSILON)  # Safe guard
        self.k = self.x * self.y  # Constant product
        self.fee = min(fee, MAX_FEE_RATE)  # Cap fee rate

    def get_amount_out(self, amount_in: float) -> float:
        """
        Calculate output amount for a given input (with fee)

        Formula: amount_out = (y * amount_in_after_fee) / (x + amount_in_after_fee)

        SAFETY: Includes epsilon guards for division
        """
        if amount_in <= 0:
            raise ValueError(f"amount_in must be > 0, got {amount_in}")

        # Apply fee with safe math
        amount_in_with_fee = amount_in * (1 - self.fee)

        # Safe division with epsilon guard
        numerator = amount_in_with_fee * self.y
        denominator = max(self.x + amount_in_with_fee, EPSILON)

        return numerator / denominator

    def update_reserves(self, amount_in: float, amount_out: float):
        """Update pool reserves after a swap with validation"""
        if amount_in <= 0:
            raise ValueError(f"amount_in must be > 0, got {amount_in}")
        if amount_out <= 0:
            raise ValueError(f"amount_out must be > 0, got {amount_out}")
        if amount_out >= self.y:
            raise ValueError(f"amount_out ({amount_out}) exceeds reserve y ({self.y})")

        self.x += amount_in
        self.y -= amount_out
        self.k = self.x * self.y


class UNIv2Calculator:
    """Advanced Uniswap V2 calculations with enhanced safety"""

    @staticmethod
    def calculate_il_percentage(
        current_price: float, initial_price: float, safe_mode: bool = True
    ) -> float:
        """
        Calculate impermanent loss as a percentage with safety checks

        Formula: IL% = [2*sqrt(price_ratio) / (price_ratio + 1) - 1] * 100

        CONSTRAINTS:
        - current_price > 0
        - initial_price > 0
        - price_ratio (r) > 0

        Args:
            current_price: Current price (Pt > 0)
            initial_price: Initial price (P0 > 0)
            safe_mode: Enable safety checks and guards

        Returns:
            IL percentage (can be negative)
        """
        if safe_mode:
            # Validate price constraints
            if initial_price <= 0:
                raise ValueError(f"initial_price must be > 0, got {initial_price}")
            if current_price <= 0:
                raise ValueError(f"current_price must be > 0, got {current_price}")

            # Ensure prices are within safe bounds
            initial_price = max(initial_price, MIN_PRICE)
            current_price = max(current_price, MIN_PRICE)

        # Calculate price ratio with epsilon guard
        ratio = current_price / max(initial_price, EPSILON)

        # Constrain ratio to prevent overflow (r > 0 enforced)
        ratio = max(ratio, EPSILON)
        if ratio > MAX_PRICE_RATIO:
            ratio = MAX_PRICE_RATIO

        # Calculate IL with safe sqrt
        sqrt_ratio = math.sqrt(ratio)
        il = (2 * sqrt_ratio / (ratio + 1) - 1) * 100

        return il

    @staticmethod
    def calculate_il_with_fees(position: LPPosition, safe_mode: bool = True) -> Dict:
        """
        Calculate comprehensive LP analytics with enhanced validation

        Args:
            position: LPPosition object with all parameters
            safe_mode: Enable safety checks throughout calculation

        Returns:
            Dictionary with detailed breakdown and validation status
        """
        result = {
            "position_name": position.name,
            "validation_errors": [],
            "validation_warnings": [],
        }

        try:
            # Calculate price ratio (r = Pt / P0)
            # CONSTRAINT: r > 0 (enforced by LPPosition validation)
            ratio = position.current_price_b_in_a / max(
                position.initial_price_b_in_a, EPSILON
            )
            ratio = max(ratio, EPSILON)  # Ensure r > 0

            if ratio > MAX_PRICE_RATIO:
                result["validation_warnings"].append(
                    f"Price ratio {ratio:.2f} exceeds safe maximum, clamping to {MAX_PRICE_RATIO}"
                )
                ratio = MAX_PRICE_RATIO

            result["price_ratio"] = ratio

            # Calculate IL percentage with safety
            # CONSTRAINT: r > 0 satisfied above
            sqrt_ratio = math.sqrt(ratio)
            il_percent = (2 * sqrt_ratio / (ratio + 1) - 1) * 100
            result["il_percent"] = round(il_percent, 4)

            # Calculate IL in dollars
            # CONSTRAINT: prices > 0, amounts > 0 (enforced by LPPosition)
            current_value = (
                position.initial_token_a_amount * position.current_price_b_in_a
                + position.initial_token_b_amount
            )
            il_dollar = current_value * (il_percent / 100)
            result["il_dollar"] = round(il_dollar, 2)

            # Calculate fees earned
            # CONSTRAINT: volume ≥ 0, fee_rate ∈ [0, 1), tvl > 0
            pool_share = position.pool_tvl_usd / max(1_000_000, EPSILON)
            daily_fees = position.daily_volume_usd * position.fee_rate * pool_share

            # Validate daily fees calculation
            if daily_fees < 0:
                result["validation_errors"].append("Calculated negative daily fees")
                daily_fees = 0

            result["daily_fees"] = round(daily_fees, 2)

            total_fees = daily_fees * position.days_elapsed
            result["total_fees"] = round(total_fees, 2)

            # Net result: fees earned minus IL
            net_result = total_fees - abs(il_dollar)
            result["net_result"] = round(net_result, 2)

            # Breakeven calculation
            # CONSTRAINT: daily_fees > 0 (checked)
            if daily_fees > EPSILON and il_dollar < 0:
                breakeven_days = abs(il_dollar) / daily_fees
            else:
                breakeven_days = float("inf")

            result["breakeven_days"] = (
                round(breakeven_days, 2)
                if breakeven_days != float("inf")
                else float("inf")
            )
            result["profitable"] = "Yes" if net_result > 0 else "No"
            result["days_elapsed"] = position.days_elapsed
            result["daily_volume_usd"] = position.daily_volume_usd

            # Validation status
            result["valid"] = len(result["validation_errors"]) == 0

        except Exception as e:
            result["validation_errors"].append(f"Calculation error: {str(e)}")
            result["valid"] = False

            # Set default error values
            result.update(
                {
                    "price_ratio": 0,
                    "il_percent": 0,
                    "il_dollar": 0,
                    "daily_fees": 0,
                    "total_fees": 0,
                    "net_result": 0,
                    "breakeven_days": float("inf"),
                    "profitable": "Error",
                    "days_elapsed": position.days_elapsed,
                    "daily_volume_usd": position.daily_volume_usd,
                }
            )

        return result


# ============================================================================
# TEST SCENARIOS: 10 REALISTIC LP POSITIONS WITH VALIDATION
# ============================================================================


def generate_test_positions() -> List[LPPosition]:
    """Generate 10 realistic LP positions with validated parameters"""

    positions = [
        # Position 1: ETH/USDC - 50% Price Increase (IL Negative)
        # CONSTRAINTS: P0 = 2000 > 0, Pt = 3000 > 0, r = 1.5 > 0 ✓
        LPPosition(
            name="ETH/USDC: 50% Increase ($2k→$3k)",
            initial_token_a_amount=1.0,
            initial_token_b_amount=2000,
            initial_price_b_in_a=2000,
            current_price_b_in_a=3000,
            days_elapsed=30,
            daily_volume_usd=500_000,
            pool_tvl_usd=10_000_000,
        ),
        # Position 2: ETH/USDC - 50% Price Decrease (IL Positive but Loss)
        # CONSTRAINTS: P0 = 2000 > 0, Pt = 1000 > 0, r = 0.5 > 0 ✓
        LPPosition(
            name="ETH/USDC: 50% Decrease ($2k→$1k)",
            initial_token_a_amount=1.0,
            initial_token_b_amount=2000,
            initial_price_b_in_a=2000,
            current_price_b_in_a=1000,
            days_elapsed=30,
            daily_volume_usd=500_000,
            pool_tvl_usd=10_000_000,
        ),
        # Position 3: ETH/USDC - 100% Price Increase (Worst IL)
        # CONSTRAINTS: P0 = 2000 > 0, Pt = 4000 > 0, r = 2.0 > 0 ✓
        LPPosition(
            name="ETH/USDC: 100% Increase ($2k→$4k)",
            initial_token_a_amount=1.0,
            initial_token_b_amount=2000,
            initial_price_b_in_a=2000,
            current_price_b_in_a=4000,
            days_elapsed=60,
            daily_volume_usd=1_000_000,
            pool_tvl_usd=50_000_000,
        ),
        # Position 4: USDC/USDT - Stablecoin Pair (Minimal IL, High Volume)
        # CONSTRAINTS: P0 = 1.0 > 0, Pt = 1.001 > 0, φ = 0.003 < 1 ✓
        LPPosition(
            name="USDC/USDT: Stable Pair (No volatility)",
            initial_token_a_amount=10000,
            initial_token_b_amount=10000,
            initial_price_b_in_a=1.0,
            current_price_b_in_a=1.001,
            days_elapsed=90,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=500_000_000,
        ),
        # Position 5: UNI/ETH - Moderate Volatility (30% increase, low volume)
        # CONSTRAINTS: All > 0, φ = 0.003 < 1 ✓
        LPPosition(
            name="UNI/ETH: 30% Increase (Low Volume)",
            initial_token_a_amount=1000,
            initial_token_b_amount=10,
            initial_price_b_in_a=0.01,
            current_price_b_in_a=0.013,
            days_elapsed=45,
            daily_volume_usd=100_000,
            pool_tvl_usd=5_000_000,
        ),
        # Position 6: LINK/ETH - High Volatility (200% increase)
        # CONSTRAINTS: P0 = 0.05 > 0, Pt = 0.15 > 0, r = 3.0 > 0 ✓
        LPPosition(
            name="LINK/ETH: 200% Increase (High Vol)",
            initial_token_a_amount=100,
            initial_token_b_amount=5,
            initial_price_b_in_a=0.05,
            current_price_b_in_a=0.15,
            days_elapsed=30,
            daily_volume_usd=2_000_000,
            pool_tvl_usd=30_000_000,
        ),
        # Position 7: DAI/USDC - Low Volatility, Moderate Volume
        # CONSTRAINTS: P0 = 1.0 > 0, Pt = 0.995 > 0 ✓
        LPPosition(
            name="DAI/USDC: Stable with Vol",
            initial_token_a_amount=5000,
            initial_token_b_amount=5000,
            initial_price_b_in_a=1.0,
            current_price_b_in_a=0.995,
            days_elapsed=60,
            daily_volume_usd=5_000_000,
            pool_tvl_usd=200_000_000,
        ),
        # Position 8: WBTC/ETH - Volatile Pair (150% increase)
        # CONSTRAINTS: P0 = 10.0 > 0, Pt = 25.0 > 0, r = 2.5 > 0 ✓
        LPPosition(
            name="WBTC/ETH: 150% Increase",
            initial_token_a_amount=10,
            initial_token_b_amount=100,
            initial_price_b_in_a=10.0,
            current_price_b_in_a=25.0,
            days_elapsed=45,
            daily_volume_usd=3_000_000,
            pool_tvl_usd=60_000_000,
        ),
        # Position 9: SHIB/USDC - Extreme Volatility (300% increase)
        # CONSTRAINTS: P0 = 0.001 > 0, Pt = 0.004 > 0, r = 4.0 > 0 ✓
        LPPosition(
            name="SHIB/USDC: 300% Increase",
            initial_token_a_amount=1_000_000,
            initial_token_b_amount=1000,
            initial_price_b_in_a=0.001,
            current_price_b_in_a=0.004,
            days_elapsed=20,
            daily_volume_usd=10_000_000,
            pool_tvl_usd=100_000_000,
        ),
        # Position 10: Stable Mix - USDC/BUSD (0.2% volatility, High Volume)
        # CONSTRAINTS: φ = 0.003 < 1, all prices > 0 ✓
        LPPosition(
            name="USDC/BUSD: Ultra-Stable",
            initial_token_a_amount=100_000,
            initial_token_b_amount=100_000,
            initial_price_b_in_a=1.0,
            current_price_b_in_a=1.002,
            days_elapsed=90,
            daily_volume_usd=100_000_000,
            pool_tvl_usd=1_000_000_000,
        ),
    ]

    return positions


def export_results_to_csv(
    results: List[Dict], filename: str = "uniswap_v2_results_validated.csv"
):
    """Export analysis results to CSV with validation info"""
    if not results:
        return

    # Define column order
    fieldnames = [
        "position_name",
        "valid",
        "price_ratio",
        "il_percent",
        "il_dollar",
        "daily_fees",
        "total_fees",
        "net_result",
        "breakeven_days",
        "profitable",
        "days_elapsed",
        "daily_volume_usd",
        "validation_errors",
        "validation_warnings",
    ]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for result in results:
            # Convert lists to strings for CSV
            if "validation_errors" in result:
                result["validation_errors"] = "; ".join(result["validation_errors"])
            if "validation_warnings" in result:
                result["validation_warnings"] = "; ".join(result["validation_warnings"])
            writer.writerow(result)

    print(f"\n✅ Results exported to {filename}")


# ============================================================================
# MAIN EXECUTION WITH VALIDATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UNISWAP V2 ENHANCED - SAFE MATH & CONSTRAINT VALIDATION")
    print("=" * 80)
    print()

    # Generate test positions with validation
    try:
        positions = generate_test_positions()
        calculator = UNIv2Calculator()

        # Analyze all positions
        results = []
        print(
            f"{'Position':<40} {'Valid':>6} {'IL %':>10} {'IL $':>12} {'Fees':>12} {'Net $':>12} {'BE Days':>10} {'Profit':>8}"
        )
        print("-" * 130)

        for position in positions:
            try:
                result = calculator.calculate_il_with_fees(position, safe_mode=True)
                results.append(result)

                # Display validation status
                valid_marker = "✓" if result.get("valid", True) else "✗"

                print(
                    f"{result['position_name']:<40} {valid_marker:>6} "
                    f"{result['il_percent']:>9.2f}% "
                    f"${result['il_dollar']:>11,.2f} "
                    f"${result['total_fees']:>11,.2f} "
                    f"${result['net_result']:>11,.2f} "
                    f"{result['breakeven_days']:>9.1f} "
                    f"{result['profitable']:>8}"
                )

                # Show warnings if any
                if result.get("validation_warnings"):
                    print(f"  ⚠️  Warnings: {'; '.join(result['validation_warnings'])}")

            except ValueError as e:
                print(f"{position.name:<40} ERROR: {str(e)}")
                continue

        print("-" * 130)
        print()

        # Summary statistics
        valid_results = [r for r in results if r.get("valid", True)]
        profitable_count = sum(1 for r in valid_results if r["profitable"] == "Yes")

        if valid_results:
            avg_il = sum(r["il_percent"] for r in valid_results) / len(valid_results)
            avg_net = sum(r["net_result"] for r in valid_results) / len(valid_results)

            print(f"SUMMARY STATISTICS")
            print(f"  Total Positions: {len(results)}")
            print(f"  Valid Calculations: {len(valid_results)}/{len(results)}")
            print(f"  Profitable Positions: {profitable_count}/{len(valid_results)}")
            print(f"  Average IL: {avg_il:.2f}%")
            print(f"  Average Net Result: ${avg_net:,.2f}")
            print()

            # Constraint validation summary
            total_warnings = sum(len(r.get("validation_warnings", [])) for r in results)
            total_errors = sum(len(r.get("validation_errors", [])) for r in results)
            print(f"CONSTRAINT VALIDATION")
            print(f"  Total Warnings: {total_warnings}")
            print(f"  Total Errors: {total_errors}")
            print()

        # Export to CSV
        export_results_to_csv(results)

        print("=" * 80)
        print("✅ All constraints validated: r > 0, P0 > 0, Pt > 0, φ < 1")
        print("✅ Safe math operations with epsilon guards")
        print("✅ Division by zero protection active")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        raise
