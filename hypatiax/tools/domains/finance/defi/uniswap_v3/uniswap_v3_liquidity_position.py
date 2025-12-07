"""
Uniswap V3 Liquidity Position Management
=========================================
Calculate LP tokens, position value, and manage concentrated liquidity ranges.

Key V3 Differences:
- Each position is unique (NFT-based, not fungible)
- Liquidity concentrated in custom price ranges
- Position value depends on current price vs range
- Complex minting/burning formulas
"""

import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class V3PositionInfo:
    """V3 Position metadata"""

    token_id: int
    price_lower: float
    price_upper: float
    liquidity: float
    token0_owed: float = 0
    token1_owed: float = 0
    fee_growth_inside0: float = 0
    fee_growth_inside1: float = 0


class UniswapV3Position:
    """
    Uniswap V3 Position Manager

    Unlike V2, V3 positions are:
    - Non-fungible (each is unique NFT)
    - Concentrated in specific price range
    - Complex liquidity calculations
    """

    def __init__(self, fee_tier: float = 0.003):
        """
        Initialize V3 position manager

        Args:
            fee_tier: Pool fee tier (0.0001, 0.0005, 0.003, 0.01)
        """
        self.fee_tier = fee_tier
        self.reserve0 = 0
        self.reserve1 = 0
        self.total_liquidity = 0  # Total liquidity in pool
        self.positions = {}  # Position ID -> V3PositionInfo
        self.next_position_id = 1

        # Fee tracking
        self.fee_growth_global0 = 0
        self.fee_growth_global1 = 0

    def _sqrt_price_x96(self, price: float) -> int:
        """Convert price to sqrtPriceX96 format (V3 internal)"""
        sqrt_price = math.sqrt(price)
        return int(sqrt_price * (2**96))

    def _price_from_sqrt_x96(self, sqrt_price_x96: int) -> float:
        """Convert sqrtPriceX96 to price"""
        sqrt_price = sqrt_price_x96 / (2**96)
        return sqrt_price**2

    def _get_amount0_for_liquidity(self, sqrt_price_a: float, sqrt_price_b: float, liquidity: float) -> float:
        """Calculate amount0 for given liquidity between two sqrt prices"""
        if sqrt_price_a > sqrt_price_b:
            sqrt_price_a, sqrt_price_b = sqrt_price_b, sqrt_price_a

        return liquidity * (sqrt_price_b - sqrt_price_a) / (sqrt_price_a * sqrt_price_b)

    def _get_amount1_for_liquidity(self, sqrt_price_a: float, sqrt_price_b: float, liquidity: float) -> float:
        """Calculate amount1 for given liquidity between two sqrt prices"""
        if sqrt_price_a > sqrt_price_b:
            sqrt_price_a, sqrt_price_b = sqrt_price_b, sqrt_price_a

        return liquidity * (sqrt_price_b - sqrt_price_a)

    def _get_liquidity_for_amount0(self, sqrt_price_a: float, sqrt_price_b: float, amount0: float) -> float:
        """Calculate liquidity for given amount0"""
        if sqrt_price_a > sqrt_price_b:
            sqrt_price_a, sqrt_price_b = sqrt_price_b, sqrt_price_a

        return amount0 * sqrt_price_a * sqrt_price_b / (sqrt_price_b - sqrt_price_a)

    def _get_liquidity_for_amount1(self, sqrt_price_a: float, sqrt_price_b: float, amount1: float) -> float:
        """Calculate liquidity for given amount1"""
        if sqrt_price_a > sqrt_price_b:
            sqrt_price_a, sqrt_price_b = sqrt_price_b, sqrt_price_a

        return amount1 / (sqrt_price_b - sqrt_price_a)

    def calculate_liquidity_amounts(
        self, price_current: float, price_lower: float, price_upper: float, amount0: float, amount1: float
    ) -> Dict[str, float]:
        """
        Calculate optimal liquidity and actual amounts needed

        This is the core V3 calculation - given desired deposits, calculate
        how much liquidity can be minted and actual token amounts needed.

        Args:
            price_current: Current pool price
            price_lower: Lower price bound
            price_upper: Upper price bound
            amount0: Desired amount of token0
            amount1: Desired amount of token1

        Returns:
            Dictionary with liquidity and actual amounts
        """
        sqrt_price_current = math.sqrt(price_current)
        sqrt_price_lower = math.sqrt(price_lower)
        sqrt_price_upper = math.sqrt(price_upper)

        if price_current <= price_lower:
            # Price below range - only need token0
            liquidity = self._get_liquidity_for_amount0(sqrt_price_lower, sqrt_price_upper, amount0)
            amount0_actual = amount0
            amount1_actual = 0

        elif price_current >= price_upper:
            # Price above range - only need token1
            liquidity = self._get_liquidity_for_amount1(sqrt_price_lower, sqrt_price_upper, amount1)
            amount0_actual = 0
            amount1_actual = amount1

        else:
            # Price in range - need both tokens
            # Calculate liquidity from each token
            liquidity0 = self._get_liquidity_for_amount0(sqrt_price_current, sqrt_price_upper, amount0)
            liquidity1 = self._get_liquidity_for_amount1(sqrt_price_lower, sqrt_price_current, amount1)

            # Take minimum to maintain correct ratio
            liquidity = min(liquidity0, liquidity1)

            # Calculate actual amounts needed for this liquidity
            amount0_actual = self._get_amount0_for_liquidity(sqrt_price_current, sqrt_price_upper, liquidity)
            amount1_actual = self._get_amount1_for_liquidity(sqrt_price_lower, sqrt_price_current, liquidity)

        return {
            "liquidity": liquidity,
            "amount0": amount0_actual,
            "amount1": amount1_actual,
            "amount0_max": amount0,
            "amount1_max": amount1,
            "amount0_unused": amount0 - amount0_actual,
            "amount1_unused": amount1 - amount1_actual,
        }

    def mint_position(
        self,
        price_current: float,
        price_lower: float,
        price_upper: float,
        amount0_desired: float,
        amount1_desired: float,
    ) -> Dict:
        """
        Mint a new V3 liquidity position (NFT)

        Args:
            price_current: Current price
            price_lower: Lower price bound
            price_upper: Upper price bound
            amount0_desired: Desired token0 amount
            amount1_desired: Desired token1 amount

        Returns:
            Position details including NFT token ID
        """
        # Calculate liquidity and amounts
        calc = self.calculate_liquidity_amounts(
            price_current, price_lower, price_upper, amount0_desired, amount1_desired
        )

        liquidity = calc["liquidity"]
        amount0 = calc["amount0"]
        amount1 = calc["amount1"]

        # Create position NFT
        position_id = self.next_position_id
        self.next_position_id += 1

        position = V3PositionInfo(
            token_id=position_id,
            price_lower=price_lower,
            price_upper=price_upper,
            liquidity=liquidity,
            fee_growth_inside0=self.fee_growth_global0,
            fee_growth_inside1=self.fee_growth_global1,
        )

        self.positions[position_id] = position

        # Update pool state
        self.total_liquidity += liquidity

        # Update reserves
        self.reserve0 += amount0
        self.reserve1 += amount1

        return {
            "position_id": position_id,
            "liquidity": liquidity,
            "amount0_deposited": amount0,
            "amount1_deposited": amount1,
            "amount0_refunded": calc["amount0_unused"],
            "amount1_refunded": calc["amount1_unused"],
            "price_lower": price_lower,
            "price_upper": price_upper,
            "price_current": price_current,
            "in_range": price_lower <= price_current <= price_upper,
        }

    def get_position_value(self, position_id: int, price_current: float) -> Dict:
        """
        Calculate current value of a position

        Args:
            position_id: Position NFT token ID
            price_current: Current price

        Returns:
            Position value breakdown
        """
        if position_id not in self.positions:
            raise ValueError(f"Position {position_id} not found")

        position = self.positions[position_id]

        sqrt_price_current = math.sqrt(price_current)
        sqrt_price_lower = math.sqrt(position.price_lower)
        sqrt_price_upper = math.sqrt(position.price_upper)

        # Calculate current token amounts
        if price_current <= position.price_lower:
            # All token0
            amount0 = self._get_amount0_for_liquidity(sqrt_price_lower, sqrt_price_upper, position.liquidity)
            amount1 = 0

        elif price_current >= position.price_upper:
            # All token1
            amount0 = 0
            amount1 = self._get_amount1_for_liquidity(sqrt_price_lower, sqrt_price_upper, position.liquidity)

        else:
            # Both tokens
            amount0 = self._get_amount0_for_liquidity(sqrt_price_current, sqrt_price_upper, position.liquidity)
            amount1 = self._get_amount1_for_liquidity(sqrt_price_lower, sqrt_price_current, position.liquidity)

        # Calculate values
        value_token0 = amount0 * price_current
        value_token1 = amount1
        total_value = value_token0 + value_token1

        # Check if in range
        in_range = position.price_lower <= price_current <= position.price_upper

        # Calculate position as % of range
        if in_range:
            range_position_pct = (
                (price_current - position.price_lower) / (position.price_upper - position.price_lower)
            ) * 100
        else:
            range_position_pct = None

        return {
            "position_id": position_id,
            "price_current": price_current,
            "price_lower": position.price_lower,
            "price_upper": position.price_upper,
            "in_range": in_range,
            "range_position_pct": range_position_pct,
            "liquidity": position.liquidity,
            "amount0": amount0,
            "amount1": amount1,
            "value_token0": value_token0,
            "value_token1": value_token1,
            "total_value": total_value,
            "fees_owed_0": position.token0_owed,
            "fees_owed_1": position.token1_owed,
        }

    def burn_position(self, position_id: int, price_current: float) -> Dict:
        """
        Burn (remove) a V3 position

        Args:
            position_id: Position NFT token ID
            price_current: Current price

        Returns:
            Amounts withdrawn
        """
        if position_id not in self.positions:
            raise ValueError(f"Position {position_id} not found")

        # Get position value
        value_data = self.get_position_value(position_id, price_current)

        position = self.positions[position_id]

        # Update pool liquidity
        self.total_liquidity -= position.liquidity

        # Update reserves
        self.reserve0 -= value_data["amount0"]
        self.reserve1 -= value_data["amount1"]

        # Calculate fees owed
        fees_token0 = position.token0_owed
        fees_token1 = position.token1_owed

        # Remove position
        del self.positions[position_id]

        return {
            "position_id": position_id,
            "amount0_withdrawn": value_data["amount0"],
            "amount1_withdrawn": value_data["amount1"],
            "fees_token0": fees_token0,
            "fees_token1": fees_token1,
            "total_token0": value_data["amount0"] + fees_token0,
            "total_token1": value_data["amount1"] + fees_token1,
            "total_value": value_data["total_value"] + (fees_token0 * price_current) + fees_token1,
        }

    def collect_fees(self, position_id: int) -> Dict:
        """
        Collect accumulated fees from a position

        Args:
            position_id: Position NFT token ID

        Returns:
            Fees collected
        """
        if position_id not in self.positions:
            raise ValueError(f"Position {position_id} not found")

        position = self.positions[position_id]

        fees_token0 = position.token0_owed
        fees_token1 = position.token1_owed

        # Reset fees owed
        position.token0_owed = 0
        position.token1_owed = 0

        return {"position_id": position_id, "fees_token0": fees_token0, "fees_token1": fees_token1}

    def simulate_fees(self, position_id: int, volume: float, time_in_range: float = 1.0):
        """
        Simulate fee accumulation

        Args:
            position_id: Position NFT token ID
            volume: Trading volume
            time_in_range: Fraction of time position was in range (0-1)
        """
        if position_id not in self.positions:
            return

        position = self.positions[position_id]

        # Calculate fees
        total_fees = volume * self.fee_tier

        # Position's share of fees (proportional to liquidity)
        if self.total_liquidity > 0:
            position_share = position.liquidity / self.total_liquidity
        else:
            position_share = 0

        # Fees only earned when in range
        fees_earned = total_fees * position_share * time_in_range

        # Split fees between token0 and token1 (simplified - assume 50/50)
        position.token0_owed += fees_earned * 0.5
        position.token1_owed += fees_earned * 0.5

        # Update global fee growth
        if self.total_liquidity > 0:
            self.fee_growth_global0 += (total_fees * 0.5) / self.total_liquidity
            self.fee_growth_global1 += (total_fees * 0.5) / self.total_liquidity

    def get_all_positions(self, price_current: float) -> list:
        """Get all positions with current values"""
        positions = []
        for position_id in self.positions:
            value_data = self.get_position_value(position_id, price_current)
            positions.append(value_data)
        return positions


# ===== EXAMPLES =====


def example_v3_position_management():
    """Example of V3 position lifecycle"""

    print("=" * 80)
    print("UNISWAP V3 POSITION MANAGEMENT EXAMPLE")
    print("=" * 80)
    print()

    # Initialize V3 pool manager
    pool = UniswapV3Position(fee_tier=0.003)

    current_price = 2000  # ETH = $2000

    print("SCENARIO 1: CREATE TIGHT RANGE POSITION")
    print("-" * 80)

    # Alice creates a tight range position (±5%)
    alice_position = pool.mint_position(
        price_current=current_price,
        price_lower=1900,  # -5%
        price_upper=2100,  # +5%
        amount0_desired=1.0,  # 1 ETH
        amount1_desired=2000,  # $2000 USDC
    )

    print(f"Alice creates position:")
    print(f"  Position NFT ID: #{alice_position['position_id']}")
    print(f"  Range: ${alice_position['price_lower']:.0f} - ${alice_position['price_upper']:.0f}")
    print(
        f"  Deposited: {alice_position['amount0_deposited']:.4f} ETH + ${alice_position['amount1_deposited']:.2f} USDC"
    )
    print(f"  Liquidity: {alice_position['liquidity']:.2f}")
    print(f"  In Range: {alice_position['in_range']}")
    if alice_position["amount0_refunded"] > 0 or alice_position["amount1_refunded"] > 0:
        print(
            f"  Refunded: {alice_position['amount0_refunded']:.4f} ETH + ${alice_position['amount1_refunded']:.2f} USDC"
        )
    print()

    print("SCENARIO 2: CREATE WIDE RANGE POSITION")
    print("-" * 80)

    # Bob creates a wide range position (±20%)
    bob_position = pool.mint_position(
        price_current=current_price,
        price_lower=1600,  # -20%
        price_upper=2400,  # +20%
        amount0_desired=0.5,
        amount1_desired=1000,
    )

    print(f"Bob creates position:")
    print(f"  Position NFT ID: #{bob_position['position_id']}")
    print(f"  Range: ${bob_position['price_lower']:.0f} - ${bob_position['price_upper']:.0f}")
    print(f"  Deposited: {bob_position['amount0_deposited']:.4f} ETH + ${bob_position['amount1_deposited']:.2f} USDC")
    print(f"  Liquidity: {bob_position['liquidity']:.2f}")
    print()

    print("SCENARIO 3: PRICE MOVEMENT - STILL IN RANGE")
    print("-" * 80)

    new_price = 2050
    print(f"Price moves to ${new_price}")
    print()

    alice_value = pool.get_position_value(alice_position["position_id"], new_price)
    bob_value = pool.get_position_value(bob_position["position_id"], new_price)

    print(f"Alice's position:")
    print(f"  In Range: {alice_value['in_range']} ({'✓' if alice_value['in_range'] else '✗'})")
    print(f"  Current: {alice_value['amount0']:.4f} ETH + ${alice_value['amount1']:.2f} USDC")
    print(f"  Total Value: ${alice_value['total_value']:.2f}")
    print()

    print(f"Bob's position:")
    print(f"  In Range: {bob_value['in_range']} ({'✓' if bob_value['in_range'] else '✗'})")
    print(f"  Current: {bob_value['amount0']:.4f} ETH + ${bob_value['amount1']:.2f} USDC")
    print(f"  Total Value: ${bob_value['total_value']:.2f}")
    print()

    print("SCENARIO 4: SIMULATE FEE ACCUMULATION")
    print("-" * 80)

    # Simulate 30 days of trading
    daily_volume = 10_000_000  # $10M daily volume

    for day in range(30):
        # Alice's tight range is in range 100% of time
        pool.simulate_fees(alice_position["position_id"], daily_volume, time_in_range=1.0)
        # Bob's wide range is also in range
        pool.simulate_fees(bob_position["position_id"], daily_volume, time_in_range=1.0)

    print(f"After 30 days of trading (${daily_volume:,} daily volume):")
    print()

    alice_value = pool.get_position_value(alice_position["position_id"], new_price)
    print(f"Alice's fees earned:")
    print(f"  Token0 fees: {alice_value['fees_owed_0']:.4f} ETH (${alice_value['fees_owed_0'] * new_price:.2f})")
    print(f"  Token1 fees: ${alice_value['fees_owed_1']:.2f} USDC")
    print(f"  Total fees: ${alice_value['fees_owed_0'] * new_price + alice_value['fees_owed_1']:.2f}")
    print()

    bob_value = pool.get_position_value(bob_position["position_id"], new_price)
    print(f"Bob's fees earned:")
    print(f"  Token0 fees: {bob_value['fees_owed_0']:.4f} ETH (${bob_value['fees_owed_0'] * new_price:.2f})")
    print(f"  Token1 fees: ${bob_value['fees_owed_1']:.2f} USDC")
    print(f"  Total fees: ${bob_value['fees_owed_0'] * new_price + bob_value['fees_owed_1']:.2f}")
    print()

    print("💡 Note: Alice (tight range) earned more fees due to higher capital efficiency!")
    print()

    print("SCENARIO 5: PRICE MOVES OUT OF ALICE'S RANGE")
    print("-" * 80)

    new_price = 2200  # Above Alice's upper bound
    print(f"Price moves to ${new_price}")
    print()

    alice_value = pool.get_position_value(alice_position["position_id"], new_price)
    bob_value = pool.get_position_value(bob_position["position_id"], new_price)

    print(f"Alice's position:")
    print(f"  In Range: {alice_value['in_range']} ({'✓' if alice_value['in_range'] else '✗'})")
    print(f"  Current: {alice_value['amount0']:.4f} ETH + ${alice_value['amount1']:.2f} USDC")
    print(f"  Total Value: ${alice_value['total_value']:.2f}")
    print(f"  ⚠️  Position is now 100% USDC, earning ZERO fees!")
    print()

    print(f"Bob's position:")
    print(f"  In Range: {bob_value['in_range']} ({'✓' if bob_value['in_range'] else '✗'})")
    print(f"  Current: {bob_value['amount0']:.4f} ETH + ${bob_value['amount1']:.2f} USDC")
    print(f"  Total Value: ${bob_value['total_value']:.2f}")
    print(f"  ✅ Still earning fees!")
    print()

    print("SCENARIO 6: REMOVE LIQUIDITY")
    print("-" * 80)

    # Alice removes her position
    alice_withdraw = pool.burn_position(alice_position["position_id"], new_price)

    print(f"Alice removes position #{alice_withdraw['position_id']}:")
    print(f"  Withdrew: {alice_withdraw['total_token0']:.4f} ETH + ${alice_withdraw['total_token1']:.2f} USDC")
    print(f"  Total Value: ${alice_withdraw['total_value']:.2f}")
    print()

    print("=" * 80)
    print("KEY V3 POSITION TAKEAWAYS:")
    print("=" * 80)
    print("✅ Each position is a unique NFT (non-fungible)")
    print("✅ Tighter ranges = higher capital efficiency = more fees per $")
    print("✅ Out of range = 100% one token + ZERO fees")
    print("✅ Requires active management to rebalance")
    print("✅ Choose range based on volatility expectations")
    print("=" * 80)


if __name__ == "__main__":
    example_v3_position_management()
