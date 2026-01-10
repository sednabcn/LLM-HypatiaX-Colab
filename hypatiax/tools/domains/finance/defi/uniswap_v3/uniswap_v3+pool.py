"""
Uniswap V3 Pool Implementation with Concentrated Liquidity
Handles price ranges, tick math, and fee calculations
"""

import math
from dataclasses import dataclass
from decimal import Decimal, getcontext
from typing import Dict, Optional, Tuple

# Set high precision for financial calculations
getcontext().prec = 50


@dataclass
class PositionInfo:
    """LP position details"""

    lower_price: float
    upper_price: float
    liquidity: float
    token0_amount: float
    token1_amount: float
    fees_earned: float = 0.0
    entry_price: float = 0.0


class UniswapV3Pool:
    """
    Uniswap V3 Pool with concentrated liquidity support

    Key differences from V2:
    - Liquidity concentrated in price ranges
    - Multiple fee tiers (0.01%, 0.05%, 0.30%, 1.00%)
    - Active liquidity depends on current price
    - Higher capital efficiency
    """

    def __init__(
        self,
        token0_symbol: str,
        token1_symbol: str,
        fee_tier: float = 0.0005,  # 0.05% default
        initial_price: float = None,
    ):
        self.token0 = token0_symbol
        self.token1 = token1_symbol
        self.fee_tier = fee_tier
        self.current_price = initial_price
        self.positions: Dict[str, PositionInfo] = {}

    # ==================== CORE V3 MATH ====================

    @staticmethod
    def price_to_sqrt_price_x96(price: float) -> int:
        """Convert price to sqrtPriceX96 (Uniswap V3 internal format)"""
        sqrt_price = math.sqrt(price)
        return int(sqrt_price * (2**96))

    @staticmethod
    def sqrt_price_x96_to_price(sqrt_price_x96: int) -> float:
        """Convert sqrtPriceX96 back to readable price"""
        sqrt_price = sqrt_price_x96 / (2**96)
        return sqrt_price**2

    @staticmethod
    def price_to_tick(price: float) -> int:
        """Convert price to tick (log base 1.0001)"""
        return int(math.floor(math.log(price) / math.log(1.0001)))

    @staticmethod
    def tick_to_price(tick: int) -> float:
        """Convert tick to price"""
        return 1.0001**tick

    # ==================== LIQUIDITY CALCULATIONS ====================

    def calculate_liquidity(
        self,
        amount0: float,
        amount1: float,
        price_lower: float,
        price_upper: float,
        current_price: float,
    ) -> float:
        """
        Calculate liquidity L for a position
        L = sqrt(x * y) for the virtual reserves in the range
        """
        sqrt_price_current = math.sqrt(current_price)
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)

        if current_price < price_lower:
            # Position is entirely in token0
            liquidity = (
                amount0
                * sqrt_price_lower
                * sqrt_price_upper
                / (sqrt_price_upper - sqrt_price_lower)
            )
        elif current_price > price_upper:
            # Position is entirely in token1
            liquidity = amount1 / (sqrt_price_upper - sqrt_price_lower)
        else:
            # Position spans current price
            liquidity0 = (
                amount0
                * sqrt_price_current
                * sqrt_price_upper
                / (sqrt_price_upper - sqrt_price_current)
            )
            liquidity1 = amount1 / (sqrt_price_current - sqrt_price_lower)
            liquidity = min(liquidity0, liquidity1)

        return liquidity

    def get_amounts_for_liquidity(
        self,
        liquidity: float,
        price_lower: float,
        price_upper: float,
        current_price: float,
    ) -> Tuple[float, float]:
        """
        Calculate token amounts needed for given liquidity
        Returns: (amount0, amount1)
        """
        sqrt_price_current = math.sqrt(current_price)
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)

        if current_price < price_lower:
            # All token0
            amount0 = (
                liquidity
                * (sqrt_price_upper - sqrt_price_lower)
                / (sqrt_price_lower * sqrt_price_upper)
            )
            amount1 = 0.0
        elif current_price > price_upper:
            # All token1
            amount0 = 0.0
            amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
        else:
            # Both tokens
            amount0 = (
                liquidity
                * (sqrt_price_upper - sqrt_price_current)
                / (sqrt_price_current * sqrt_price_upper)
            )
            amount1 = liquidity * (sqrt_price_current - sqrt_price_lower)

        return (amount0, amount1)

    # ==================== POSITION MANAGEMENT ====================

    def create_position(
        self,
        position_id: str,
        token0_amount: float,
        token1_amount: float,
        price_lower: float,
        price_upper: float,
        current_price: Optional[float] = None,
    ) -> PositionInfo:
        """
        Create a new concentrated liquidity position
        """
        if current_price is None:
            current_price = self.current_price

        # Calculate liquidity for this position
        liquidity = self.calculate_liquidity(
            token0_amount, token1_amount, price_lower, price_upper, current_price
        )

        position = PositionInfo(
            lower_price=price_lower,
            upper_price=price_upper,
            liquidity=liquidity,
            token0_amount=token0_amount,
            token1_amount=token1_amount,
            entry_price=current_price,
        )

        self.positions[position_id] = position
        return position

    def is_position_in_range(
        self, position: PositionInfo, current_price: Optional[float] = None
    ) -> bool:
        """Check if position is actively earning fees"""
        if current_price is None:
            current_price = self.current_price
        return position.lower_price <= current_price <= position.upper_price

    # ==================== IMPERMANENT LOSS ====================

    def calculate_il_v3(
        self,
        position: PositionInfo,
        current_price: float,
        initial_price: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Calculate impermanent loss for V3 concentrated position
        More complex than V2 due to price ranges
        """
        if initial_price is None:
            initial_price = position.entry_price

        # Get initial amounts
        initial_amount0, initial_amount1 = self.get_amounts_for_liquidity(
            position.liquidity,
            position.lower_price,
            position.upper_price,
            initial_price,
        )

        # Get current amounts
        current_amount0, current_amount1 = self.get_amounts_for_liquidity(
            position.liquidity,
            position.lower_price,
            position.upper_price,
            current_price,
        )

        # Calculate values
        initial_value = initial_amount0 * initial_price + initial_amount1
        current_lp_value = current_amount0 * current_price + current_amount1
        hodl_value = initial_amount0 * current_price + initial_amount1

        # IL calculations
        il_absolute = current_lp_value - hodl_value
        il_percent = (il_absolute / hodl_value * 100) if hodl_value > 0 else 0

        # Price ratio calculation (for comparison with V2 formula)
        price_ratio = current_price / initial_price

        # Standard IL formula (for full range would match V2)
        il_formula = ((2 * math.sqrt(price_ratio)) / (price_ratio + 1) - 1) * 100

        return {
            "il_percent": il_percent,
            "il_absolute": il_absolute,
            "il_formula_percent": il_formula,  # For comparison
            "initial_value": initial_value,
            "current_lp_value": current_lp_value,
            "hodl_value": hodl_value,
            "price_ratio": price_ratio,
            "in_range": self.is_position_in_range(position, current_price),
        }

    # ==================== FEE CALCULATIONS ====================

    def estimate_daily_fees(
        self,
        position: PositionInfo,
        daily_volume_usd: float,
        pool_tvl_usd: float,
        current_price: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        Estimate daily fees earned by position
        V3 positions only earn when price is in range
        """
        if current_price is None:
            current_price = self.current_price

        in_range = self.is_position_in_range(position, current_price)

        if not in_range:
            return {
                "daily_fees_usd": 0.0,
                "daily_fees_token0": 0.0,
                "daily_fees_token1": 0.0,
                "in_range": False,
                "fee_apr": 0.0,
            }

        # Calculate position's share of liquidity
        position_value = position.token0_amount * current_price + position.token1_amount
        liquidity_share = position_value / pool_tvl_usd if pool_tvl_usd > 0 else 0

        # Fee calculation
        daily_fees_usd = daily_volume_usd * self.fee_tier * liquidity_share

        # Assume fees split proportionally
        daily_fees_token0 = daily_fees_usd / current_price * 0.5
        daily_fees_token1 = daily_fees_usd * 0.5

        # Annualized return
        fee_apr = (
            (daily_fees_usd * 365 / position_value * 100) if position_value > 0 else 0
        )

        return {
            "daily_fees_usd": daily_fees_usd,
            "daily_fees_token0": daily_fees_token0,
            "daily_fees_token1": daily_fees_token1,
            "in_range": True,
            "fee_apr": fee_apr,
            "liquidity_share": liquidity_share,
        }

    # ==================== QUALITY SCORE (from HypatiaX) ====================

    def calculate_quality_score(
        self,
        position: PositionInfo,
        current_price: float,
        daily_volume_usd: float,
        pool_tvl_usd: float,
        days_elapsed: int = 1,
    ) -> Dict[str, float]:
        """
        HypatiaX Quality Score: QS = Daily Fees / Daily IL Rate
        QS > 2.0: Excellent
        QS > 1.0: Good
        QS > 0.5: Moderate
        QS < 0.5: Poor
        """
        # Calculate IL
        il_data = self.calculate_il_v3(position, current_price)
        il_absolute = abs(il_data["il_absolute"])
        daily_il_rate = il_absolute / days_elapsed if days_elapsed > 0 else 0

        # Calculate fees
        fee_data = self.estimate_daily_fees(
            position, daily_volume_usd, pool_tvl_usd, current_price
        )
        daily_fees = fee_data["daily_fees_usd"]

        # Quality score
        if daily_il_rate == 0:
            quality_score = float("inf")  # Perfect - no IL
        else:
            quality_score = daily_fees / daily_il_rate

        # Interpretation
        if quality_score == float("inf"):
            interpretation = "PERFECT - Zero IL, pure fees"
        elif quality_score > 2.0:
            interpretation = "EXCELLENT - Strong fee generation"
        elif quality_score > 1.0:
            interpretation = "GOOD - Fees compensate for IL"
        elif quality_score > 0.5:
            interpretation = "MODERATE - Marginal profitability"
        else:
            interpretation = "POOR - IL exceeds fees"

        return {
            "quality_score": quality_score,
            "interpretation": interpretation,
            "daily_fees": daily_fees,
            "daily_il_rate": daily_il_rate,
            "total_il": il_absolute,
            "fee_apr": fee_data["fee_apr"],
            "in_range": fee_data["in_range"],
        }

    # ==================== PERFORMANCE ANALYSIS ====================

    def analyze_position_performance(
        self,
        position: PositionInfo,
        current_price: float,
        daily_volume_usd: float,
        pool_tvl_usd: float,
        days_elapsed: int,
        gas_costs_usd: float = 0.0,
    ) -> Dict[str, any]:
        """
        Complete performance analysis of a V3 position
        """
        # IL Analysis
        il_data = self.calculate_il_v3(position, current_price)

        # Fee Analysis
        fee_data = self.estimate_daily_fees(
            position, daily_volume_usd, pool_tvl_usd, current_price
        )
        total_fees = fee_data["daily_fees_usd"] * days_elapsed

        # Quality Score
        qs_data = self.calculate_quality_score(
            position, current_price, daily_volume_usd, pool_tvl_usd, days_elapsed
        )

        # Net result
        net_result = total_fees + il_data["il_absolute"] - gas_costs_usd

        # ROI calculations
        initial_value = il_data["initial_value"]
        roi_percent = (net_result / initial_value * 100) if initial_value > 0 else 0

        # Days to breakeven
        if fee_data["daily_fees_usd"] > 0:
            breakeven_days = abs(il_data["il_absolute"]) / fee_data["daily_fees_usd"]
        else:
            breakeven_days = float("inf")

        return {
            "position_id": position,
            "current_price": current_price,
            "price_range": {
                "lower": position.lower_price,
                "upper": position.upper_price,
                "in_range": il_data["in_range"],
            },
            "impermanent_loss": {
                "percent": il_data["il_percent"],
                "absolute_usd": il_data["il_absolute"],
                "formula_percent": il_data["il_formula_percent"],
            },
            "fees": {
                "daily_usd": fee_data["daily_fees_usd"],
                "total_usd": total_fees,
                "apr": fee_data["fee_apr"],
            },
            "quality_metrics": {
                "score": qs_data["quality_score"],
                "interpretation": qs_data["interpretation"],
            },
            "net_performance": {
                "total_return_usd": net_result,
                "roi_percent": roi_percent,
                "gas_costs": gas_costs_usd,
                "breakeven_days": breakeven_days,
            },
            "values": {
                "initial": initial_value,
                "current_lp": il_data["current_lp_value"],
                "hodl": il_data["hodl_value"],
            },
        }


# ==================== HELPER FUNCTIONS ====================


def simulate_price_scenarios(
    pool: UniswapV3Pool,
    position: PositionInfo,
    initial_price: float,
    price_changes: list,
    daily_volume_usd: float,
    pool_tvl_usd: float,
    days_elapsed: int = 90,
):
    """
    Simulate position performance across different price scenarios
    """
    results = []

    for price_change_pct in price_changes:
        new_price = initial_price * (1 + price_change_pct / 100)

        analysis = pool.analyze_position_performance(
            position=position,
            current_price=new_price,
            daily_volume_usd=daily_volume_usd,
            pool_tvl_usd=pool_tvl_usd,
            days_elapsed=days_elapsed,
            gas_costs_usd=100.0,  # Typical V3 gas cost
        )

        results.append(
            {"price_change_pct": price_change_pct, "new_price": new_price, **analysis}
        )

    return results


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example: Position 1 from your document - ETH/USDC Narrow Range
    print("=" * 70)
    print("UNISWAP V3 ETH/USDC POSITION ANALYSIS")
    print("=" * 70)

    # Initialize pool
    pool = UniswapV3Pool(
        token0_symbol="ETH",
        token1_symbol="USDC",
        fee_tier=0.0005,
        initial_price=3000.0,  # 0.05% fee tier
    )

    # Create narrow range position
    position = pool.create_position(
        position_id="LP-001",
        token0_amount=50.0,  # 50 ETH
        token1_amount=150000.0,  # $150k USDC
        price_lower=2800.0,
        price_upper=3200.0,
        current_price=3000.0,
    )

    print(f"\nPosition Created:")
    print(f"  Range: ${position.lower_price:,.0f} - ${position.upper_price:,.0f}")
    print(f"  Current Price: $3,000")
    print(f"  Liquidity: {position.liquidity:,.2f}")
    print(f"  Token0 (ETH): {position.token0_amount:.4f}")
    print(f"  Token1 (USDC): ${position.token1_amount:,.2f}")

    # Analyze at current price
    print(f"\n{'='*70}")
    print("CURRENT PERFORMANCE (90 days)")
    print(f"{'='*70}")

    analysis = pool.analyze_position_performance(
        position=position,
        current_price=3000.0,
        daily_volume_usd=15_000_000,  # $15M daily volume
        pool_tvl_usd=50_000_000,  # $50M TVL
        days_elapsed=90,
        gas_costs_usd=100.0,
    )

    print(f"\nPrice Range Status:")
    print(f"  In Range: {analysis['price_range']['in_range']}")

    print(f"\nImpermanent Loss:")
    print(f"  IL%: {analysis['impermanent_loss']['percent']:.2f}%")
    print(f"  IL (USD): ${analysis['impermanent_loss']['absolute_usd']:,.2f}")

    print(f"\nFee Performance:")
    print(f"  Daily Fees: ${analysis['fees']['daily_usd']:,.2f}")
    print(f"  Total Fees (90d): ${analysis['fees']['total_usd']:,.2f}")
    print(f"  Fee APR: {analysis['fees']['apr']:.2f}%")

    print(f"\nQuality Score:")
    print(f"  Score: {analysis['quality_metrics']['score']:.2f}")
    print(f"  Rating: {analysis['quality_metrics']['interpretation']}")

    print(f"\nNet Performance:")
    print(f"  Total Return: ${analysis['net_performance']['total_return_usd']:,.2f}")
    print(f"  ROI: {analysis['net_performance']['roi_percent']:.2f}%")
    print(f"  Breakeven Days: {analysis['net_performance']['breakeven_days']:.1f}")

    # Test price scenarios
    print(f"\n{'='*70}")
    print("PRICE SCENARIO ANALYSIS")
    print(f"{'='*70}")

    scenarios = simulate_price_scenarios(
        pool=pool,
        position=position,
        initial_price=3000.0,
        price_changes=[-50, -25, 0, +25, +50, +100],
        daily_volume_usd=15_000_000,
        pool_tvl_usd=50_000_000,
        days_elapsed=90,
    )

    print(
        f"\n{'Price Change':<15} {'New Price':<12} {'In Range':<10} {'IL%':<10} {'Fees':<12} {'Net Return':<12} {'QS':<10}"
    )
    print("-" * 95)

    for scenario in scenarios:
        price_change = scenario["price_change_pct"]
        new_price = scenario["new_price"]
        in_range = scenario["price_range"]["in_range"]
        il_pct = scenario["impermanent_loss"]["percent"]
        fees = scenario["fees"]["total_usd"]
        net = scenario["net_performance"]["total_return_usd"]
        qs = scenario["quality_metrics"]["score"]

        in_range_str = "YES" if in_range else "NO"
        qs_str = f"{qs:.2f}" if qs != float("inf") else "∞"

        print(
            f"{price_change:+6.0f}%        ${new_price:>7,.0f}    {in_range_str:<10} {il_pct:>6.2f}%    ${fees:>9,.0f}  ${net:>10,.0f}  {qs_str:<10}"
        )

    print(f"\n{'='*70}")
    print("RECOMMENDATION")
    print(f"{'='*70}")

    current_qs = analysis["quality_metrics"]["score"]
    if current_qs > 2.0:
        print("✅ EXCELLENT position - Strong fee generation relative to IL")
    elif current_qs > 1.0:
        print("✓ GOOD position - Fees adequately compensate for IL")
    elif current_qs > 0.5:
        print("⚠ MODERATE position - Marginal profitability, monitor closely")
    else:
        print("❌ POOR position - IL exceeds fees, consider exiting")
