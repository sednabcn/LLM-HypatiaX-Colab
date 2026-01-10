"""
Impermanent Loss (IL) Calculator
=================================
Calculate and analyze impermanent loss for liquidity providers in AMM pools.

Impermanent Loss occurs when the price ratio of tokens in a liquidity pool
changes compared to when they were deposited, resulting in less value than
simply holding the tokens.
"""

import math
from decimal import Decimal, getcontext
from typing import Dict, List, Optional, Tuple

# Set precision for financial calculations
getcontext().prec = 28


class ImpermanentLossCalculator:
    """
    Calculator for impermanent loss in constant product AMM pools.
    """

    def __init__(
        self,
        initial_price: float,
        initial_amount0: float,
        initial_amount1: float,
        fee_tier: float = 0.003,
    ):
        """
        Initialize the IL calculator.

        Args:
            initial_price: Initial price of token0 in terms of token1
            initial_amount0: Initial amount of token0 deposited
            initial_amount1: Initial amount of token1 deposited
            fee_tier: Pool fee tier (default 0.3% = 0.003)
        """
        self.initial_price = Decimal(str(initial_price))
        self.initial_amount0 = Decimal(str(initial_amount0))
        self.initial_amount1 = Decimal(str(initial_amount1))
        self.fee_tier = Decimal(str(fee_tier))

        # Calculate initial value
        self.initial_value = (
            self.initial_amount0 * self.initial_price + self.initial_amount1
        )

        # Calculate k constant
        self.k = self.initial_amount0 * self.initial_amount1

    def calculate_il(self, current_price: float) -> Dict[str, float]:
        """
        Calculate impermanent loss at a given price.

        Args:
            current_price: Current price of token0 in terms of token1

        Returns:
            Dictionary with IL metrics
        """
        current_price = Decimal(str(current_price))

        # Calculate price ratio
        price_ratio = current_price / self.initial_price

        # Calculate new amounts based on constant product formula
        # x * y = k, and y = price * x
        # So x * (price * x) = k => x^2 = k / price
        current_amount0 = (self.k / current_price).sqrt()
        current_amount1 = current_price * current_amount0

        # Calculate current value
        current_value_pool = current_amount0 * current_price + current_amount1

        # Calculate hold value (if tokens were not provided as liquidity)
        hold_value = self.initial_amount0 * current_price + self.initial_amount1

        # Calculate impermanent loss
        il_absolute = current_value_pool - hold_value
        il_percentage = (il_absolute / hold_value) * Decimal("100")

        # Calculate value multiplier
        value_multiplier = float(
            price_ratio.sqrt() * Decimal("2") / (price_ratio + Decimal("1"))
        )

        return {
            "current_price": float(current_price),
            "price_ratio": float(price_ratio),
            "price_change_percent": float(
                (price_ratio - Decimal("1")) * Decimal("100")
            ),
            "current_amount0": float(current_amount0),
            "current_amount1": float(current_amount1),
            "pool_value": float(current_value_pool),
            "hold_value": float(hold_value),
            "il_absolute": float(il_absolute),
            "il_percentage": float(il_percentage),
            "value_multiplier": value_multiplier,
        }

    def calculate_il_with_fees(
        self,
        current_price: float,
        volume_as_multiple_of_liquidity: float,
        time_period_days: float = 1,
    ) -> Dict[str, float]:
        """
        Calculate impermanent loss including earned fees.

        Args:
            current_price: Current price of token0 in terms of token1
            volume_as_multiple_of_liquidity: Trading volume as multiple of liquidity
            time_period_days: Time period in days

        Returns:
            Dictionary with IL and fee metrics
        """
        # Calculate base IL
        il_data = self.calculate_il(current_price)

        # Calculate fees earned
        # Fee = volume * fee_tier
        volume = float(self.initial_value) * volume_as_multiple_of_liquidity
        fees_earned = volume * float(self.fee_tier)

        # Calculate net result
        il_absolute = il_data["il_absolute"]
        net_result = fees_earned + il_absolute
        net_percentage = (net_result / il_data["hold_value"]) * 100

        # Calculate APR from fees
        if time_period_days > 0:
            fee_apr = (
                (fees_earned / float(self.initial_value))
                * (365 / time_period_days)
                * 100
            )
        else:
            fee_apr = 0

        return {
            **il_data,
            "fees_earned": fees_earned,
            "net_result": net_result,
            "net_percentage": net_percentage,
            "fee_apr": fee_apr,
            "breakeven_volume_multiple": (
                abs(il_absolute) / (float(self.initial_value) * float(self.fee_tier))
                if il_absolute < 0
                else 0
            ),
        }

    def generate_il_curve(
        self, price_range: Tuple[float, float], steps: int = 50
    ) -> List[Dict[str, float]]:
        """
        Generate IL curve data over a price range.

        Args:
            price_range: (min_price, max_price) tuple
            steps: Number of price points to calculate

        Returns:
            List of dictionaries with IL data at each price point
        """
        min_price, max_price = price_range
        price_step = (max_price - min_price) / (steps - 1)

        curve_data = []
        for i in range(steps):
            price = min_price + (i * price_step)
            il_data = self.calculate_il(price)
            curve_data.append(il_data)

        return curve_data

    def calculate_divergence_loss(self, current_price: float) -> float:
        """
        Calculate divergence loss (alternative term for IL).

        Args:
            current_price: Current price of token0 in terms of token1

        Returns:
            Divergence loss as a percentage
        """
        return self.calculate_il(current_price)["il_percentage"]


def calculate_il_simple(price_change_ratio: float) -> float:
    """
    Calculate IL percentage using simplified formula based on price change ratio.

    Formula: IL = (2 * sqrt(price_ratio)) / (1 + price_ratio) - 1

    Args:
        price_change_ratio: Ratio of current price to initial price

    Returns:
        Impermanent loss as a percentage
    """
    price_ratio = Decimal(str(price_change_ratio))
    il = (Decimal("2") * price_ratio.sqrt()) / (Decimal("1") + price_ratio) - Decimal(
        "1"
    )
    return float(il * Decimal("100"))


def calculate_breakeven_fee_apr(il_percentage: float, time_period_days: float) -> float:
    """
    Calculate the APR from fees needed to break even with IL.

    Args:
        il_percentage: Impermanent loss as a percentage
        time_period_days: Time period in days

    Returns:
        Required fee APR to break even
    """
    if time_period_days <= 0:
        return float("inf")

    # Convert IL to absolute value needed
    il_absolute_needed = abs(il_percentage)

    # Calculate annual rate
    daily_rate = il_absolute_needed / time_period_days
    annual_rate = daily_rate * 365

    return annual_rate


def compare_strategies(
    initial_investment: float,
    initial_price: float,
    current_price: float,
    fee_tier: float = 0.003,
    volume_multiple: float = 1.0,
) -> Dict[str, Dict[str, float]]:
    """
    Compare different investment strategies (hold vs LP).

    Args:
        initial_investment: Total initial investment value
        initial_price: Initial price
        current_price: Current price
        fee_tier: Pool fee tier
        volume_multiple: Trading volume as multiple of liquidity

    Returns:
        Dictionary comparing strategies
    """
    # Calculate 50/50 split
    amount0 = initial_investment / (2 * initial_price)
    amount1 = initial_investment / 2

    calculator = ImpermanentLossCalculator(
        initial_price=initial_price,
        initial_amount0=amount0,
        initial_amount1=amount1,
        fee_tier=fee_tier,
    )

    il_data = calculator.calculate_il_with_fees(current_price, volume_multiple)

    # Hold strategy value
    hold_value = amount0 * current_price + amount1

    # LP strategy value
    lp_value = il_data["pool_value"] + il_data["fees_earned"]

    return {
        "hold_strategy": {
            "initial_value": initial_investment,
            "final_value": hold_value,
            "profit": hold_value - initial_investment,
            "return_percentage": (
                (hold_value - initial_investment) / initial_investment
            )
            * 100,
        },
        "lp_strategy": {
            "initial_value": initial_investment,
            "final_value": lp_value,
            "profit": lp_value - initial_investment,
            "return_percentage": ((lp_value - initial_investment) / initial_investment)
            * 100,
            "il_loss": il_data["il_absolute"],
            "fees_earned": il_data["fees_earned"],
        },
        "comparison": {
            "lp_vs_hold": lp_value - hold_value,
            "lp_vs_hold_percentage": ((lp_value - hold_value) / hold_value) * 100,
            "better_strategy": "LP" if lp_value > hold_value else "Hold",
        },
    }


# Example usage and precomputed IL values for common price changes
COMMON_IL_VALUES = {
    1.25: -0.6,  # 25% price increase
    1.5: -2.0,  # 50% price increase
    2.0: -5.7,  # 100% price increase (2x)
    3.0: -13.4,  # 200% price increase (3x)
    4.0: -20.0,  # 300% price increase (4x)
    5.0: -25.5,  # 400% price increase (5x)
    0.8: -0.6,  # 20% price decrease
    0.5: -2.0,  # 50% price decrease
    0.25: -5.7,  # 75% price decrease
}


if __name__ == "__main__":
    # Example: ETH/USDC pool
    print("Impermanent Loss Calculator Demo")
    print("=" * 50)
    print()

    # Initial setup: 1 ETH at $2000 + $2000 USDC
    calculator = ImpermanentLossCalculator(
        initial_price=2000,  # ETH price in USDC
        initial_amount0=1,  # 1 ETH
        initial_amount1=2000,  # 2000 USDC
        fee_tier=0.003,
    )

    # Scenario 1: Price doubles
    print("Scenario 1: ETH price doubles to $4000")
    il_data = calculator.calculate_il(4000)
    print(f"  Pool value: ${il_data['pool_value']:.2f}")
    print(f"  Hold value: ${il_data['hold_value']:.2f}")
    print(f"  Impermanent Loss: {il_data['il_percentage']:.2f}%")
    print()

    # Scenario 2: Price halves
    print("Scenario 2: ETH price halves to $1000")
    il_data = calculator.calculate_il(1000)
    print(f"  Pool value: ${il_data['pool_value']:.2f}")
    print(f"  Hold value: ${il_data['hold_value']:.2f}")
    print(f"  Impermanent Loss: {il_data['il_percentage']:.2f}%")
    print()

    # Scenario 3: With fees
    print("Scenario 3: Price doubles, but with trading fees")
    il_with_fees = calculator.calculate_il_with_fees(
        current_price=4000,
        volume_as_multiple_of_liquidity=10,
        time_period_days=30,  # 10x volume
    )
    print(f"  IL: {il_with_fees['il_percentage']:.2f}%")
    print(f"  Fees earned: ${il_with_fees['fees_earned']:.2f}")
    print(f"  Net result: {il_with_fees['net_percentage']:.2f}%")
    print(f"  Fee APR: {il_with_fees['fee_apr']:.2f}%")
    print()

    # Compare strategies
    print("Strategy Comparison:")
    comparison = compare_strategies(
        initial_investment=4000,
        initial_price=2000,
        current_price=3000,
        volume_multiple=5,
    )
    print(
        f"  Hold: ${comparison['hold_strategy']['final_value']:.2f} "
        f"({comparison['hold_strategy']['return_percentage']:.2f}%)"
    )
    print(
        f"  LP: ${comparison['lp_strategy']['final_value']:.2f} "
        f"({comparison['lp_strategy']['return_percentage']:.2f}%)"
    )
    print(f"  Better strategy: {comparison['comparison']['better_strategy']}")
