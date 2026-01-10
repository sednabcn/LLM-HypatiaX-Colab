import csv
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

# ============================================================================
# MATHEMATICAL FORMULAS
# ============================================================================
"""
1. CONSTANT PRODUCT FORMULA (AMM):
   x * y = k (where k is constant)

2. SWAP OUTPUT (with fee):
   amount_out = (y * amount_in_after_fee) / (x + amount_in_after_fee)
   where: amount_in_after_fee = amount_in * (1 - fee_rate)

3. IMPERMANENT LOSS (IL):
   IL% = [2*sqrt(price_ratio) / (price_ratio + 1) - 1] * 100
   where: price_ratio = current_price / initial_price

4. IL IN DOLLARS:
   IL$ = (initial_x * current_price + initial_y) * (IL% / 100)

5. DAILY FEES EARNED:
   daily_fees = (daily_volume * fee_rate * pool_tvl_share)

6. NET RESULT:
   net = total_fees_earned - IL_dollar_amount

7. BREAKEVEN TIME:
   breakeven_days = |IL$| / daily_fees (days to recover IL through fees)
"""


@dataclass
class LPPosition:
    """Represents an LP position in a Uniswap V2 pool"""

    name: str
    initial_token_a_amount: float
    initial_token_b_amount: float
    initial_price_b_in_a: float
    current_price_b_in_a: float
    days_elapsed: int
    daily_volume_usd: float
    fee_rate: float = 0.003
    pool_tvl_usd: float = 1_000_000  # Estimated pool TVL


class UniswapV2Pool:
    """Core Uniswap V2 pool implementation"""

    def __init__(self, reserve_x: float, reserve_y: float, fee: float = 0.003):
        """
        Initialize a Uniswap V2 pool

        Args:
            reserve_x: Reserve amount of token X
            reserve_y: Reserve amount of token Y
            fee: Fee rate (default 0.3%)
        """
        self.x = reserve_x
        self.y = reserve_y
        self.k = reserve_x * reserve_y  # Constant product
        self.fee = fee

    def get_amount_out(self, amount_in: float) -> float:
        """
        Calculate output amount for a given input (with 0.3% fee)

        Formula: amount_out = (y * amount_in_after_fee) / (x + amount_in_after_fee)
        """
        amount_in_with_fee = amount_in * (1 - self.fee)
        numerator = amount_in_with_fee * self.y
        denominator = self.x + amount_in_with_fee
        return numerator / denominator

    def update_reserves(self, amount_in: float, amount_out: float):
        """Update pool reserves after a swap"""
        self.x += amount_in
        self.y -= amount_out
        self.k = self.x * self.y


class UNIv2Calculator:
    """Advanced Uniswap V2 calculations including impermanent loss"""

    @staticmethod
    def calculate_il_percentage(current_price: float, initial_price: float) -> float:
        """
        Calculate impermanent loss as a percentage

        Formula: IL% = [2*sqrt(price_ratio) / (price_ratio + 1) - 1] * 100
        """
        if initial_price == 0:
            return 0
        ratio = current_price / initial_price
        il = (2 * (ratio**0.5) / (ratio + 1) - 1) * 100
        return il

    @staticmethod
    def calculate_il_with_fees(position: LPPosition) -> Dict:
        """
        Calculate comprehensive LP analytics including IL, fees, and net result

        Args:
            position: LPPosition object with all parameters

        Returns:
            Dictionary with detailed breakdown
        """
        # Calculate IL percentage
        ratio = position.current_price_b_in_a / position.initial_price_b_in_a
        il_percent = (2 * (ratio**0.5) / (ratio + 1) - 1) * 100

        # Calculate IL in dollars
        # Total value = (token_a * current_price_a) + (token_b * current_price_b_in_a)
        # Assuming token_a = 1 unit for simplicity
        current_value = (
            position.initial_token_a_amount * position.current_price_b_in_a
            + position.initial_token_b_amount
        )
        il_dollar = current_value * (il_percent / 100)

        # Calculate fees earned
        # Fee earnings depend on trading volume and pool share
        daily_fees = (
            position.daily_volume_usd
            * position.fee_rate
            * (position.pool_tvl_usd / 1_000_000)
        )
        total_fees = daily_fees * position.days_elapsed

        # Net result: fees earned minus IL
        net_result = total_fees - abs(il_dollar)

        # Breakeven calculation
        breakeven_days = float("inf")
        if daily_fees > 0 and il_dollar < 0:
            breakeven_days = abs(il_dollar) / daily_fees

        return {
            "position_name": position.name,
            "price_ratio": ratio,
            "il_percent": round(il_percent, 4),
            "il_dollar": round(il_dollar, 2),
            "daily_fees": round(daily_fees, 2),
            "total_fees": round(total_fees, 2),
            "net_result": round(net_result, 2),
            "breakeven_days": round(breakeven_days, 2),
            "profitable": "Yes" if net_result > 0 else "No",
            "days_elapsed": position.days_elapsed,
            "daily_volume_usd": position.daily_volume_usd,
        }


# ============================================================================
# TEST SCENARIOS: 10 REALISTIC LP POSITIONS
# ============================================================================


def generate_test_positions() -> List[LPPosition]:
    """Generate 10 realistic LP positions with varied scenarios"""

    positions = [
        # Position 1: ETH/USDC - 50% Price Increase (IL Negative)
        LPPosition(
            name="ETH/USDC: 50% Increase ($2k→$3k)",
            initial_token_a_amount=1.0,  # 1 ETH
            initial_token_b_amount=2000,  # 2000 USDC
            initial_price_b_in_a=2000,
            current_price_b_in_a=3000,
            days_elapsed=30,
            daily_volume_usd=500_000,
            pool_tvl_usd=10_000_000,
        ),
        # Position 2: ETH/USDC - 50% Price Decrease (IL Positive but Loss)
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
        LPPosition(
            name="USDC/USDT: Stable Pair (No volatility)",
            initial_token_a_amount=10000,
            initial_token_b_amount=10000,
            initial_price_b_in_a=1.0,
            current_price_b_in_a=1.001,  # 0.1% drift
            days_elapsed=90,
            daily_volume_usd=50_000_000,
            pool_tvl_usd=500_000_000,
        ),
        # Position 5: UNI/ETH - Moderate Volatility (30% increase, low volume)
        LPPosition(
            name="UNI/ETH: 30% Increase (Low Volume)",
            initial_token_a_amount=1000,  # 1000 UNI
            initial_token_b_amount=10,  # 10 ETH
            initial_price_b_in_a=0.01,
            current_price_b_in_a=0.013,
            days_elapsed=45,
            daily_volume_usd=100_000,
            pool_tvl_usd=5_000_000,
        ),
        # Position 6: LINK/ETH - High Volatility (200% increase)
        LPPosition(
            name="LINK/ETH: 200% Increase (High Vol)",
            initial_token_a_amount=100,  # 100 LINK
            initial_token_b_amount=5,  # 5 ETH
            initial_price_b_in_a=0.05,
            current_price_b_in_a=0.15,
            days_elapsed=30,
            daily_volume_usd=2_000_000,
            pool_tvl_usd=30_000_000,
        ),
        # Position 7: DAI/USDC - Low Volatility, Moderate Volume
        LPPosition(
            name="DAI/USDC: Stable with Vol",
            initial_token_a_amount=5000,
            initial_token_b_amount=5000,
            initial_price_b_in_a=1.0,
            current_price_b_in_a=0.995,  # -0.5% drift
            days_elapsed=60,
            daily_volume_usd=5_000_000,
            pool_tvl_usd=200_000_000,
        ),
        # Position 8: WBTC/ETH - Volatile Altair (150% increase)
        LPPosition(
            name="WBTC/ETH: 150% Increase",
            initial_token_a_amount=10,  # 10 WBTC
            initial_token_b_amount=100,  # 100 ETH
            initial_price_b_in_a=10.0,
            current_price_b_in_a=25.0,
            days_elapsed=45,
            daily_volume_usd=3_000_000,
            pool_tvl_usd=60_000_000,
        ),
        # Position 9: SHIB/USDC - Extreme Volatility (300% increase)
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
        LPPosition(
            name="USDC/BUSD: Ultra-Stable",
            initial_token_a_amount=100_000,
            initial_token_b_amount=100_000,
            initial_price_b_in_a=1.0,
            current_price_b_in_a=1.002,  # 0.2% drift
            days_elapsed=90,
            daily_volume_usd=100_000_000,
            pool_tvl_usd=1_000_000_000,
        ),
    ]

    return positions


def export_results_to_csv(
    results: List[Dict], filename: str = "uniswap_v2_results.csv"
):
    """Export analysis results to CSV"""
    if not results:
        return

    keys = results[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ Results exported to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UNISWAP V2 IMPLEMENTATION - ADVANCED IL CALCULATOR")
    print("=" * 80)
    print()

    # Generate test positions
    positions = generate_test_positions()
    calculator = UNIv2Calculator()

    # Analyze all positions
    results = []
    print(
        f"{'Position':<35} {'IL %':>10} {'IL $':>12} {'Fees':>12} {'Net $':>12} {'BE Days':>10} {'Profitable':>12}"
    )
    print("-" * 120)

    for position in positions:
        result = calculator.calculate_il_with_fees(position)
        results.append(result)

        print(
            f"{result['position_name']:<35} {result['il_percent']:>9.2f}% "
            f"${result['il_dollar']:>11,.2f} ${result['total_fees']:>11,.2f} "
            f"${result['net_result']:>11,.2f} {result['breakeven_days']:>9.1f} "
            f"{result['profitable']:>12}"
        )

    print("-" * 120)
    print()

    # Summary statistics
    profitable_count = sum(1 for r in results if r["profitable"] == "Yes")
    avg_il = sum(r["il_percent"] for r in results) / len(results)
    avg_net = sum(r["net_result"] for r in results) / len(results)

    print(f"SUMMARY STATISTICS")
    print(f"  Total Positions: {len(results)}")
    print(f"  Profitable Positions: {profitable_count}/{len(results)}")
    print(f"  Average IL: {avg_il:.2f}%")
    print(f"  Average Net Result: ${avg_net:,.2f}")
    print()

    # Export to CSV
    export_results_to_csv(results)
